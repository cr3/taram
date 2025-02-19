"""SQLAlchemy models."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
)
from sqlalchemy.sql import func

from taram.units import gibi

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
    defquota: Mapped[int] = mapped_column(BigInteger, server_default=f"{3 * gibi}")
    maxquota: Mapped[int] = mapped_column(BigInteger, server_default=f"{10 * gibi}")
    quota: Mapped[int] = mapped_column(BigInteger, server_default=f"{10 * gibi}")
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
    quota: Mapped[int] = mapped_column(BigInteger, server_default=f"{10 * gibi}")
    local_part: Mapped[str] = mapped_column(String(255))
    domain: Mapped[str] = mapped_column(String(255))
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


class SaslLogModel(SQLModel):

    app_password: Mapped[int] = mapped_column()
    service: Mapped[str] = mapped_column(String(32))
    username: Mapped[str] = mapped_column(String(255))
    real_ip: Mapped[str] = mapped_column(String(64))
    datetime: datetime = Column(DateTime(timezone=True), server_default=func.current_timestamp())

    __tablename__ = "sasl_log"
    __table_args__ = (
        PrimaryKeyConstraint(service, real_ip, username),
        Index("sasl_log_username_key", username),
        Index("sasl_log_service_key", service),
        Index("sasl_log_datetime_key", datetime),
        Index("sasl_log_real_ip_key", real_ip),
    )


class SenderAclModel(SQLModel):

    __tablename__ = "sender_acl"

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    logged_in_as: Mapped[str] = mapped_column(String(255))
    send_as: Mapped[str] = mapped_column(String(255))
    external: Mapped[bool] = mapped_column(server_default="0")


class SogoStaticView(SQLModel):

    __tablename__ = "_sogo_static_view"
    __table_args__ = (Index("_sogo_static_view_domain_key", "domain"),)

    c_uid: Mapped[str] = mapped_column(String(255), primary_key=True)
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


class SogoAclModel(SQLModel):

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    c_folder_id: Mapped[int] = mapped_column()
    c_object: Mapped[str] = mapped_column(String(255))
    c_uid: Mapped[str] = mapped_column(String(255))
    c_role: Mapped[str] = mapped_column(String(80))

    __tablename__ = "sogo_acl"
    __table_args__ = (
        Index("sogo_acl_c_folder_id_key", c_folder_id),
        Index("sogo_acl_c_uid_key", c_uid),
    )


class SogoAlarmsFolderModel(SQLModel):

    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    c_path: Mapped[str] = mapped_column(String(255))
    c_name: Mapped[str] = mapped_column(String(255))
    c_uid: Mapped[str] = mapped_column(String(255))
    c_recurrence_id: Mapped[Optional[int]] = mapped_column()
    c_alarm_number: Mapped[int] = mapped_column()
    c_alarm_date: Mapped[int] = mapped_column()

    __tablename__ = "sogo_alarms_folder"


class SogoCacheFolderModel(SQLModel):

    c_uid: Mapped[str] = mapped_column(String(255))
    c_path: Mapped[str] = mapped_column(String(255))
    c_parent_path: Mapped[Optional[str]] = mapped_column(String(255))
    c_type: Mapped[int] = mapped_column()
    c_creationdate: Mapped[int] = mapped_column()
    c_lastmodified: Mapped[int] = mapped_column()
    c_version: Mapped[int] = mapped_column(server_default="0")
    c_deleted: Mapped[bool] = mapped_column(server_default="0")
    c_content: Mapped[str] = mapped_column(Text)

    __tablename__ = "sogo_cache_folder"
    __table_args__ = (PrimaryKeyConstraint(c_uid, c_path),)


class SogoFolderInfoModel(SQLModel):

    c_folder_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    c_path: Mapped[str] = mapped_column(String(255))
    c_path1: Mapped[str] = mapped_column(String(255))
    c_path2: Mapped[Optional[str]] = mapped_column(String(255))
    c_path3: Mapped[Optional[str]] = mapped_column(String(255))
    c_path4: Mapped[Optional[str]] = mapped_column(String(255))
    c_foldername: Mapped[str] = mapped_column(String(255))
    c_location: Mapped[Optional[str]] = mapped_column(String(2048))
    c_quick_location: Mapped[Optional[str]] = mapped_column(String(2048))
    c_acl_location: Mapped[Optional[str]] = mapped_column(String(2048))
    c_folder_type: Mapped[str] = mapped_column(String(255))

    __tablename__ = "sogo_folder_info"
    __table_args__ = (Index("sogo_folder_info_c_path_key", c_path, unique=True),)


class SogoQuickAppointmentModel(SQLModel):

    c_folder_id: Mapped[int] = mapped_column()
    c_name: Mapped[str] = mapped_column(String(255))
    c_uid: Mapped[str] = mapped_column(String(255))
    c_startdate: Mapped[Optional[int]] = mapped_column()
    c_enddate: Mapped[Optional[int]] = mapped_column()
    c_cycleenddate: Mapped[Optional[int]] = mapped_column()
    c_title: Mapped[str] = mapped_column(String(1000))
    c_participants: Mapped[Optional[str]] = mapped_column(Text)
    c_isallday: Mapped[Optional[bool]] = mapped_column()
    c_iscycle: Mapped[Optional[bool]] = mapped_column()
    c_cycleinfo: Mapped[Optional[str]] = mapped_column(Text)
    c_classification: Mapped[int] = mapped_column()
    c_isopaque: Mapped[bool] = mapped_column()
    c_status: Mapped[int] = mapped_column()
    c_priority: Mapped[Optional[int]] = mapped_column()
    c_location: Mapped[Optional[str]] = mapped_column(String(255))
    c_orgmail: Mapped[Optional[str]] = mapped_column(String(255))
    c_partmails: Mapped[Optional[str]] = mapped_column(Text)
    c_partstates: Mapped[Optional[str]] = mapped_column(Text)
    c_category: Mapped[Optional[str]] = mapped_column(String(255))
    c_sequence: Mapped[Optional[int]] = mapped_column()
    c_component: Mapped[str] = mapped_column(String(10))
    c_nextalarm: Mapped[Optional[int]] = mapped_column()
    c_description: Mapped[Optional[str]] = mapped_column(Text)

    __tablename__ = "sogo_quick_appointment"
    __table_args__ = (PrimaryKeyConstraint(c_folder_id, c_name),)


class SogoQuickContactModel(SQLModel):

    c_folder_id: Mapped[int] = mapped_column()
    c_name: Mapped[str] = mapped_column(String(255))
    c_givenname: Mapped[Optional[str]] = mapped_column(String(255))
    c_cn: Mapped[Optional[str]] = mapped_column(String(255))
    c_sn: Mapped[Optional[str]] = mapped_column(String(255))
    c_screenname: Mapped[Optional[str]] = mapped_column(String(255))
    c_l: Mapped[Optional[str]] = mapped_column(String(255))
    c_mail: Mapped[Optional[str]] = mapped_column(Text)
    c_o: Mapped[Optional[str]] = mapped_column(String(255))
    c_ou: Mapped[Optional[str]] = mapped_column(String(255))
    c_telephonenumber: Mapped[Optional[str]] = mapped_column(String(255))
    c_categories: Mapped[Optional[str]] = mapped_column(String(255))
    c_component: Mapped[str] = mapped_column(String(10))
    c_hascertificate: Mapped[bool] = mapped_column(server_default="0")

    __tablename__ = "sogo_quick_contact"
    __table_args__ = (PrimaryKeyConstraint(c_folder_id, c_name),)


class SogoSessionsFolderModel(SQLModel):

    c_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    c_value: Mapped[str] = mapped_column(String(255))
    c_creationdate: Mapped[int] = mapped_column()
    c_lastseen: Mapped[int] = mapped_column()

    __tablename__ = "sogo_sessions_folder"


class SogoStoreModel(SQLModel):

    c_folder_id: Mapped[int] = mapped_column()
    c_name: Mapped[str] = mapped_column(String(255), server_default="")
    c_content: Mapped[str] = mapped_column(Text)
    c_creationdate: Mapped[int] = mapped_column()
    c_lastmodified: Mapped[int] = mapped_column()
    c_version: Mapped[int] = mapped_column()
    c_deleted: Mapped[Optional[int]] = mapped_column()

    __tablename__ = "sogo_store"
    __table_args__ = (PrimaryKeyConstraint(c_folder_id, c_name),)


class SogoAdminModel(SQLModel):

    c_key: Mapped[str] = mapped_column(String(255), primary_key=True, server_default="")
    c_content: Mapped[str] = mapped_column(Text)

    __tablename__ = "sogo_admin"


class SogoUserProfileModel(SQLModel):

    c_uid: Mapped[str] = mapped_column(String(255), primary_key=True)
    c_defaults: Mapped[Optional[str]] = mapped_column(Text)
    c_settings: Mapped[Optional[str]] = mapped_column(Text)

    __tablename__ = "sogo_user_profile"


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


class UserAclModel(SQLModel):

    __tablename__ = "user_acl"

    username: Mapped[str] = mapped_column(ForeignKey("mailbox.username"), primary_key=True)
    spam_alias: Mapped[bool] = mapped_column(server_default="1")
    tls_policy: Mapped[bool] = mapped_column(server_default="1")
    spam_score: Mapped[bool] = mapped_column(server_default="1")
    spam_policy: Mapped[bool] = mapped_column(server_default="1")
    delimiter_action: Mapped[bool] = mapped_column(server_default="1")
    syncjobs: Mapped[bool] = mapped_column(server_default="0")
    eas_reset: Mapped[bool] = mapped_column(server_default="1")
    sogo_profile_reset: Mapped[bool] = mapped_column(server_default="0")
    pushover: Mapped[bool] = mapped_column(server_default="1")
    # TODO: rename quarantine to quarantine_actions
    quarantine: Mapped[bool] = mapped_column(server_default="1")
    quarantine_attachments: Mapped[bool] = mapped_column(server_default="1")
    quarantine_notification: Mapped[bool] = mapped_column(server_default="1")
    quarantine_category: Mapped[bool] = mapped_column(server_default="1")
    app_passwds: Mapped[bool] = mapped_column(server_default="1")
    pw_reset: Mapped[bool] = mapped_column(server_default="1")


class UserAttributesModel(SQLModel):

    __tablename__ = "user_attributes"

    username: Mapped[str] = mapped_column(ForeignKey("mailbox.username"), primary_key=True)
    force_pw_update: Mapped[bool] = mapped_column(server_default="0")
    tls_enforce_in: Mapped[bool] = mapped_column(server_default="0")
    tls_enforce_out: Mapped[bool] = mapped_column(server_default="0")
    relayhost: Mapped[bool] = mapped_column(server_default="0")
    sogo_access: Mapped[bool] = mapped_column(server_default="1")
    imap_access: Mapped[bool] = mapped_column(server_default="1")
    pop3_access: Mapped[bool] = mapped_column(server_default="1")
    smtp_access: Mapped[bool] = mapped_column(server_default="1")
    sieve_access: Mapped[bool] = mapped_column(server_default="1")
    quarantine_notification: Mapped[str] = mapped_column(String(255), server_default="hourly")
    quarantine_category: Mapped[str] = mapped_column(String(255), server_default="reject")
