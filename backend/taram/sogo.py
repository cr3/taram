"""SOGo functions."""

from attrs import define, field
from sqlalchemy import insert, select, text
from sqlalchemy.orm import Session
from sqlalchemy.sql import case, func

from taram.memcached import Memcached
from taram.models import (
    MailboxModel,
    SogoAclModel,
    SogoCacheFolderModel,
    SogoFolderInfoModel,
    SogoQuickAppointmentModel,
    SogoQuickContactModel,
    SogoStaticView,
    SogoStoreModel,
    SogoUserProfileModel,
    UserAttributesModel,
)
from taram.views import (
    GroupedDomainAliasAddressView,
    GroupedMailAliasesView,
    GroupedSenderAclExternalView,
)


@define(frozen=True)
class Sogo:

    db_session: Session
    memcached: Memcached = field(factory=Memcached.from_default)
    default_password: str = "{SSHA256}A123A123A321A321A321B321B321B123B123B321B432F123E321123123321321"

    def update_static_view(self, mailbox: str):

        # Conditional password logic
        password_expr = case(
            (
                UserAttributesModel.force_pw_update.is_(False),
                case(
                    (UserAttributesModel.sogo_access.is_(True), MailboxModel.password),
                    else_=self.default_password,
                ),
            ),
            else_=self.default_password,
        )

        # Aliases concatenation
        aliases_concat = func.IFNULL(func.GROUP_CONCAT(GroupedMailAliasesView.aliases), "")
        ad_aliases = func.IFNULL(GroupedDomainAliasAddressView.ad_alias, "")
        ext_acl = func.IFNULL(GroupedSenderAclExternalView.send_as_acl, "")

        select_stmt = (
            select(
                MailboxModel.username,
                MailboxModel.domain,
                MailboxModel.username,
                password_expr,
                MailboxModel.name,
                MailboxModel.username,
                aliases_concat,
                ad_aliases,
                ext_acl,
                MailboxModel.kind,
                MailboxModel.multiple_bookings,
            )
            .select_from(MailboxModel)
            .outerjoin(UserAttributesModel, MailboxModel.username == UserAttributesModel.username)
            .outerjoin(
                GroupedMailAliasesView,
                text("grouped_mail_aliases.username REGEXP '(^|,)' || mailbox.username || '($|,)'"),
            )
            .outerjoin(GroupedDomainAliasAddressView, MailboxModel.username == GroupedDomainAliasAddressView.username)
            .outerjoin(GroupedSenderAclExternalView, MailboxModel.username == GroupedSenderAclExternalView.username)
            .where(MailboxModel.active.is_(True))
        )

        if self.db_session.query(MailboxModel).filter_by(username=mailbox).count():
            select_stmt = select_stmt.where(MailboxModel.username == mailbox)
        else:
            select_stmt = select_stmt.group_by(MailboxModel.username)

        insert_stmt = insert(SogoStaticView).from_select(
            [
                "c_uid",
                "domain",
                "c_name",
                "c_password",
                "c_cn",
                "mail",
                "aliases",
                "ad_aliases",
                "ext_acl",
                "kind",
                "multiple_bookings",
            ],
            select_stmt,
        )

        self.db_session.execute(insert_stmt)

        self.db_session.query(SogoStaticView).filter(
            SogoStaticView.c_uid.not_in(select(MailboxModel.username).filter_by(active=True))
        ).delete()

        self.memcached.flush()

    def delete_user(self, username):
        self.db_session.query(SogoUserProfileModel).filter_by(c_uid=username).delete()
        self.db_session.query(SogoCacheFolderModel).filter_by(c_uid=username).delete()
        # TODO: Also delete by c_object
        self.db_session.query(SogoAclModel).filter_by(c_uid=username).delete()
        folder_ids = self.db_session.query(SogoFolderInfoModel.c_folder_id).filter(
            SogoFolderInfoModel.c_path2 == username
        )
        self.db_session.query(SogoStoreModel).filter(
            SogoStoreModel.c_folder_id.in_(folder_ids.subquery()),
        ).delete()
        self.db_session.query(SogoQuickContactModel).filter(
            SogoQuickContactModel.c_folder_id.in_(folder_ids.subquery()),
        ).delete()
        self.db_session.query(SogoQuickAppointmentModel).filter(
            SogoQuickAppointmentModel.c_folder_id.in_(folder_ids.subquery()),
        ).delete()
        folder_ids.delete()
