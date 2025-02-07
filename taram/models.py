"""SQLAlchemy models."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Enum,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
)
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

SQLModel = declarative_base()


class AliasModel(SQLModel):

    __tablename__ = "alias"
    __table_args__ = (
        Index("alias_address_key", "address", unique=True),
        Index("alias_domain_key", "domain"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    address: Mapped[str] = mapped_column(String(255))
    goto: Mapped[str] = mapped_column(Text)
    domain: Mapped[str] = mapped_column(String(255))
    created: datetime = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    modified: datetime = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
    private_comment: Mapped[Optional[str]] = mapped_column(Text)
    public_comment: Mapped[Optional[str]] = mapped_column(Text)
    sogo_visible: Mapped[bool] = mapped_column(server_default="1")
    active: Mapped[bool] = mapped_column(server_default="0")


class AliasDomainModel(SQLModel):

    __tablename__ = "alias_domain"
    __table_args__ = (
        Index("alias_domain_active_key", "active"),
        Index("alias_domain_target_domain_key", "target_domain"),
    )

    alias_domain: Mapped[str] = mapped_column(String(255), primary_key=True)
    target_domain: Mapped[str] = mapped_column(String(255))
    created: datetime = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    modified: datetime = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
    active: Mapped[bool] = mapped_column(server_default="1")


class BccMapsModel(SQLModel):

    __tablename__ = "bcc_maps"
    __table_args__ = (Index("bcc_maps_local_dest_key", "local_dest"),)

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    local_dest: Mapped[str] = mapped_column(String(255))
    bcc_dest: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(255))
    type: Mapped[Optional[str]] = mapped_column(Enum("sender", "rcpt"))  # noqa: A003
    created: datetime = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    modified: datetime = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
    active: Mapped[bool] = mapped_column(server_default="1")


class DomainModel(SQLModel):

    __tablename__ = "domain"

    domain: Mapped[str] = mapped_column(String(255), primary_key=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    aliases: Mapped[int] = mapped_column(Integer, server_default="0")
    mailboxes: Mapped[int] = mapped_column(Integer, server_default="0")
    defquota: Mapped[int] = mapped_column(BigInteger, server_default="3072")
    maxquota: Mapped[int] = mapped_column(BigInteger, server_default="102400")
    quota: Mapped[int] = mapped_column(BigInteger, server_default="102400")
    relayhost: Mapped[str] = mapped_column(String(255), server_default="0")
    backupmx: Mapped[bool] = mapped_column(server_default="0")
    gal: Mapped[bool] = mapped_column(server_default="1")
    relay_all_recipients: Mapped[bool] = mapped_column(server_default="0")
    relay_unknown_only: Mapped[bool] = mapped_column(server_default="0")
    created: datetime = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    modified: datetime = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
    active: Mapped[bool] = mapped_column(server_default="1")

    def validate(self):
        if not self.defquota:
            raise ValueError("mailbox defquota is empty")
        if self.defquota > self.maxquota:
            raise ValueError("mailbox defquota exceeds mailbox maxquota")
        if not self.maxquota:
            raise ValueError("mailbox maxquota is empty")
        if self.maxquota > self.quota:
            raise ValueError("mailbox quota exceeds domain quota")

        if self.relay_all_recipients:
            self.backupmx = True

        if self.relay_unknown_only:
            self.backupmx = True
            self.relay_all_recipients = True

        return self


class MailboxModel(SQLModel):

    __tablename__ = "mailbox"
    __table_args__ = (
        Index("mailbox_domain_key", "domain"),
        Index("mailbox_kind_key", "kind"),
    )

    username: Mapped[str] = mapped_column(String(255), primary_key=True)
    password: Mapped[str] = mapped_column(String(255))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(255))
    mailbox_path_prefix: Mapped[Optional[str]] = mapped_column(String(150), server_default="/var/mail")
    quota: Mapped[int] = mapped_column(BigInteger, server_default="102400")
    local_part: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(255))
    attributes: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)
    custom_attributes: Mapped[dict[str, Any]] = mapped_column(JSON, server_default="{}")
    kind: Mapped[str] = mapped_column(String(100), server_default="")
    multiple_bookings: Mapped[int] = mapped_column(Integer, server_default="-1")
    created: datetime = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    modified: datetime = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
    active: Mapped[bool] = mapped_column(server_default="1")


class Quota2Model(SQLModel):

    __tablename__ = "quota2"

    username: Mapped[str] = mapped_column(String(255), primary_key=True)
    bytes: Mapped[int] = mapped_column(BigInteger, server_default="0")  # noqa: A003
    messages: Mapped[int] = mapped_column(BigInteger, server_default="0")


class Quota2ReplicaModel(SQLModel):

    __tablename__ = "quota2replica"

    username: Mapped[str] = mapped_column(String(255), primary_key=True)
    bytes: Mapped[int] = mapped_column(BigInteger, server_default="0")  # noqa: A003
    messages: Mapped[int] = mapped_column(BigInteger, server_default="0")


class RecipientMapsModel(SQLModel):

    __tablename__ = "recipient_maps"
    __table_args__ = (Index("recipient_maps_old_dest_key", "old_dest"),)

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    old_dest: Mapped[str] = mapped_column(String(255))
    new_dest: Mapped[str] = mapped_column(String(255))
    created: datetime = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    modified: datetime = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
    active: Mapped[bool] = mapped_column(server_default="0")


class RelayHostsModel(SQLModel):

    __tablename__ = "relayhosts"
    __table_args__ = (Index("relayhosts_hostname_key", "hostname"),)

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    hostname: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(server_default="1")


class SenderAclModel(SQLModel):

    __tablename__ = "sender_acl"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    logged_in_as: Mapped[str] = mapped_column(String(255))
    send_as: Mapped[str] = mapped_column(String(255))
    external: Mapped[bool] = mapped_column(server_default="0")


class SogoStaticView(SQLModel):

    __tablename__ = "_sogo_static_view"
    __table_args__ = (Index("_sogo_static_view_domain_key", "domain"),)

    c_uid: Mapped[int] = mapped_column(primary_key=True)
    domain: Mapped[str] = mapped_column(String(255))
    c_name: Mapped[str] = mapped_column(String(255))
    c_password: Mapped[str] = mapped_column(String(255), server_default="")
    c_cn: Mapped[Optional[str]] = mapped_column(String(255))
    c_l: Mapped[Optional[str]] = mapped_column(String(255))
    c_o: Mapped[Optional[str]] = mapped_column(String(255))
    c_ou: Mapped[Optional[str]] = mapped_column(String(255))
    c_telephonenumber: Mapped[Optional[str]] = mapped_column(String(255))
    mail: Mapped[str] = mapped_column(String(255))
    aliases: Mapped[str] = mapped_column(Text)
    ad_aliases: Mapped[str] = mapped_column(String(6144), server_default="")
    ext_acl: Mapped[str] = mapped_column(String(6144), server_default="")
    kind: Mapped[str] = mapped_column(String(100), server_default="")
    multiple_bookings: Mapped[int] = mapped_column(Integer, server_default="1")


class SpamaliasModel(SQLModel):

    __tablename__ = "spamalias"

    address: Mapped[str] = mapped_column(String(255), primary_key=True)
    goto: Mapped[str] = mapped_column(Text)
    created: datetime = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    modified: datetime = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
    validity: Mapped[int] = mapped_column(Integer)


class TlsPolicyOverrideModel(SQLModel):

    __tablename__ = "tls_policy_override"
    __table_args__ = (Index("tls_policy_override_dest_key", "dest"),)

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    dest: Mapped[str] = mapped_column(String(255))
    policy: Mapped[str] = mapped_column(
        Enum("none", "may", "encrypt", "dane", "dane-only", "fingerprint", "verify", "secure")
    )
    parameters: Mapped[Optional[str]] = mapped_column(String(255), server_default="")
    created: datetime = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    modified: datetime = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
    active: Mapped[bool] = mapped_column(server_default="1")


class TransportsModel(SQLModel):

    __tablename__ = "transports"
    __table_args__ = (
        Index("transports_destination_key", "destination"),
        Index("transports_nexthop_key", "nexthop"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    destination: Mapped[str] = mapped_column(String(255))
    nexthop: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255), server_default="")
    password: Mapped[str] = mapped_column(String(255), server_default="")
    is_mx_based: Mapped[bool] = mapped_column(server_default="0")
    active: Mapped[bool] = mapped_column(server_default="1")
