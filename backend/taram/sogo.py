"""SOGo functions."""

from functools import partial

from attrs import define, field
from sqlalchemy import insert, select
from sqlalchemy.sql import case, func

from taram.db import DBSession
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
from taram.store import (
    MemcachedStore,
    Store,
)
from taram.views import (
    GroupedDomainAliasAddressView,
    GroupedMailAliasesView,
    GroupedSenderAclExternalView,
)


@define(frozen=True)
class Sogo:

    db: DBSession
    memcached: Store = field(factory=partial(MemcachedStore.from_host, "memcached"))
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
            .outerjoin(GroupedMailAliasesView, GroupedMailAliasesView.username == MailboxModel.username)
            .outerjoin(GroupedDomainAliasAddressView, MailboxModel.username == GroupedDomainAliasAddressView.username)
            .outerjoin(GroupedSenderAclExternalView, MailboxModel.username == GroupedSenderAclExternalView.username)
            .where(MailboxModel.active.is_(True))
        )

        if self.db.query(MailboxModel).filter_by(username=mailbox).count():
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

        self.db.execute(insert_stmt)

        self.db.query(SogoStaticView).filter(
            SogoStaticView.c_uid.not_in(select(MailboxModel.username).filter_by(active=True))
        ).delete()

        self.memcached.flushall()

    def delete_user(self, username):
        self.db.query(SogoUserProfileModel).filter_by(c_uid=username).delete()
        self.db.query(SogoCacheFolderModel).filter_by(c_uid=username).delete()
        # TODO: Also delete by c_object
        self.db.query(SogoAclModel).filter_by(c_uid=username).delete()
        folder_ids = select(SogoFolderInfoModel.c_folder_id).where(
            SogoFolderInfoModel.c_path2 == username
        )
        self.db.query(SogoStoreModel).filter(
            SogoStoreModel.c_folder_id.in_(folder_ids),
        ).delete()
        self.db.query(SogoQuickContactModel).filter(
            SogoQuickContactModel.c_folder_id.in_(folder_ids),
        ).delete()
        self.db.query(SogoQuickAppointmentModel).filter(
            SogoQuickAppointmentModel.c_folder_id.in_(folder_ids),
        ).delete()
        self.db.query(SogoFolderInfoModel).filter_by(c_path2=username).delete()
