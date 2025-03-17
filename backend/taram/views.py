"""Database views."""

from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy_utils.view import (
    CreateView,
    DropView,
    create_view,
)

from taram.models import (
    AliasDomainModel,
    AliasModel,
    MailboxModel,
    SenderAclModel,
    SQLModel,
)


class SQLViewMixin:
    @classmethod
    def create(cls, op):
        cls.drop(op)
        create_sql = CreateView(cls.__table__.fullname, cls.selectable)
        op.execute(create_sql)
        for idx in cls.__table__.indexes:
            idx.create(op.get_bind())

    @classmethod
    def drop(cls, op):
        drop_sql = DropView(cls.__table__.fullname, cascade=False)
        op.execute(drop_sql)


class GroupedMailAliasesView(SQLViewMixin, SQLModel):
    """View of mail aliases grouped by goto.

    CREATE VIEW grouped_mail_aliases (username, aliases) AS
        SELECT goto, IFNULL(GROUP_CONCAT(address ORDER BY address SEPARATOR ' '), '') AS address FROM alias
        WHERE address!=goto
        AND active = '1'
        AND sogo_visible = '1'
        AND address NOT LIKE '@%'
        GROUP BY goto;",
    """

    selectable = (
        select(
            AliasModel.goto.label("username"),
            func.coalesce(func.group_concat(AliasModel.address), "").label("aliases"),
        )
        .filter_by(address=AliasModel.goto)
        .filter_by(active=True)
        .filter_by(sogo_visible=True)
        .filter(AliasModel.address.not_like("@%"))
        .group_by(AliasModel.goto)
    )

    __table__ = create_view(
        "grouped_mail_aliases",
        selectable,
        SQLModel.metadata,
        cascade_on_drop=False,
    )


class GroupedDomainAliasAddressView(SQLViewMixin, SQLModel):
    """View of domain alias addresses grouped by username.

    CREATE VIEW grouped_domain_alias_address (username, ad_alias) AS
        SELECT username, IFNULL(GROUP_CONCAT(local_part, '@', alias_domain SEPARATOR ' '), '') AS ad_alias FROM mailbox
        LEFT OUTER JOIN alias_domain ON target_domain=domain
        GROUP BY username;",
    """

    selectable = (
        select(
            MailboxModel.username.label("username"),
            func.coalesce(
                func.group_concat(MailboxModel.local_part + '@' + AliasDomainModel.alias_domain, ' '),
                "",
            ).label("ad_alias"),
        )
        .select_from(
            MailboxModel.__table__.outerjoin(AliasDomainModel, AliasDomainModel.target_domain == MailboxModel.domain)
        )
        .group_by(MailboxModel.username)
    )

    __table__ = create_view(
        "grouped_domain_alias_address",
        selectable,
        SQLModel.metadata,
        cascade_on_drop=False,
    )


class GroupedSenderAclView(SQLViewMixin, SQLModel):
    """View of sender ACLs grouped by logged_in_as.

    CREATE VIEW grouped_sender_acl (username, send_as_acl) AS
        SELECT logged_in_as, IFNULL(GROUP_CONCAT(send_as SEPARATOR ' '), '') AS send_as_acl FROM sender_acl
        WHERE send_as NOT LIKE '@%'
        GROUP BY logged_in_as;",
    """

    selectable = (
        select(
            SenderAclModel.logged_in_as.label("username"),
            func.coalesce(func.group_concat(SenderAclModel.send_as), "").label("send_as_acl"),
        )
        .filter(SenderAclModel.send_as.not_like("@%"))
        .group_by(SenderAclModel.logged_in_as)
    )

    __table__ = create_view(
        "grouped_sender_acl",
        selectable,
        SQLModel.metadata,
        cascade_on_drop=False,
    )


class GroupedSenderAclExternalView(SQLViewMixin, SQLModel):
    """View of sender ACLs that are external only grouped by logged_in_as.

    CREATE VIEW grouped_sender_acl_external (username, send_as_acl) AS
        SELECT logged_in_as, IFNULL(GROUP_CONCAT(send_as SEPARATOR ' '), '') AS send_as_acl FROM sender_acl
        WHERE send_as NOT LIKE '@%' AND external = '1'
        GROUP BY logged_in_as;",
    """

    selectable = (
        select(
            SenderAclModel.logged_in_as.label("username"),
            func.coalesce(func.group_concat(SenderAclModel.send_as), "").label("send_as_acl"),
        )
        .filter(SenderAclModel.send_as.not_like("@%"))
        .filter_by(external=True)
        .group_by(SenderAclModel.logged_in_as)
    )

    __table__ = create_view(
        "grouped_sender_acl_external",
        selectable,
        SQLModel.metadata,
        cascade_on_drop=False,
    )
