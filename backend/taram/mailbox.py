from attrs import Factory, define, field
from passlib.hash import bcrypt
from sqlalchemy import or_
from sqlalchemy.sql import func

from taram.db import DBSession
from taram.models import (
    AliasModel,
    BccMapsModel,
    DomainModel,
    FilterconfModel,
    ImapsyncModel,
    MailboxModel,
    Quota2Model,
    Quota2ReplicaModel,
    SaslLogModel,
    SenderAclModel,
    SpamaliasModel,
    UserAclModel,
    UserAttributesModel,
)
from taram.schemas import (
    MailboxCreate,
    MailboxDetails,
    MailboxUpdate,
)
from taram.sogo import Sogo
from taram.units import mebi


@define(frozen=True)
class MailboxManager:

    db: DBSession
    sogo: Sogo = field(
        default=Factory(lambda self: Sogo(self.db), takes_self=True),
    )

    def get_mailbox_details(self, username):
        mailbox, quota2, attributes = (
            self.db.query(MailboxModel, Quota2Model, UserAttributesModel)
            .filter_by(kind="", username=username)
            .join(Quota2Model, Quota2Model.username == MailboxModel.username)
            .join(UserAttributesModel, UserAttributesModel.username == MailboxModel.username)
            .one()
        )

        logs = (
            self.db.query(func.max(SaslLogModel.datetime), SaslLogModel.service)
            .filter_by(username=username)
            .order_by(SaslLogModel.service.desc())
            .all()
        )
        last_logins = {service: datetime for datetime, service in logs}

        # TODO: ratelimit

        return MailboxDetails(
            username=mailbox.username,
            active=mailbox.active,
            domain=mailbox.domain,
            name=mailbox.name,
            local_part=mailbox.local_part,
            quota=mailbox.quota,
            quota_used=quota2.bytes,
            messages=quota2.messages,
            quarantine_notification=attributes.quarantine_notification,
            quarantine_category=attributes.quarantine_category,
            force_pw_update=attributes.force_pw_update,
            tls_enforce_in=attributes.tls_enforce_in,
            tls_enforce_out=attributes.tls_enforce_out,
            relayhost=attributes.relayhost,
            sogo_access=attributes.sogo_access,
            imap_access=attributes.imap_access,
            pop3_access=attributes.pop3_access,
            smtp_access=attributes.smtp_access,
            sieve_access=attributes.sieve_access,
            last_imap_login=last_logins.get("imap"),
            last_smtp_login=last_logins.get("smtp"),
            last_pop3_login=last_logins.get("pop3"),
            last_sso_login=last_logins.get("SSO"),
        )

    def create_mailbox(self, mailbox_create: MailboxCreate):
        local_part = mailbox_create.local_part.lower().strip()
        if not local_part:
            raise ValueError("local_part empty")

        domain = mailbox_create.domain.lower().strip()
        username = f"{local_part}@{domain}"
        # validate username as email
        name = mailbox_create.name or local_part
        name = name.lstrip("<").rstrip(">")

        domain_data = self._get_domain_data(domain)
        mailbox_data = self._get_mailbox_data(domain)
        if mailbox_data.count >= domain_data.mailboxes:
            raise KeyError("Max mailbox exceeded")
        if mailbox_create.quota > domain_data.maxquota:
            raise KeyError("Mailbox quota exceeded")
        if mailbox_data.quota + mailbox_create.quota > domain_data.quota:
            raise KeyError("Mailbox quota left exceeded")

        if mailbox_create.password != mailbox_create.password2:
            raise ValueError("passwords don't match")

        hashed_password = bcrypt.hash(mailbox_create.password)

        mailbox = MailboxModel(
            username=username,
            password=hashed_password,
            name=name,
            local_part=local_part,
            domain=domain,
            quota=mailbox_create.quota,
            active=mailbox_create.active,
        )
        quota2 = Quota2Model(
            username=username,
            bytes=0,
            messages=0,
        )
        quota2replica = Quota2ReplicaModel(
            username=username,
            bytes=0,
            messages=0,
        )
        alias = AliasModel(
            address=username,
            goto=username,
            domain=domain,
            active=mailbox_create.active,
        )
        user_acl = UserAclModel(
            username=username,
            spam_alias=mailbox_create.acl_spam_alias,
            tls_policy=mailbox_create.acl_tls_policy,
            spam_score=mailbox_create.acl_spam_score,
            spam_policy=mailbox_create.acl_spam_policy,
            delimiter_action=mailbox_create.acl_delimiter_action,
            syncjobs=mailbox_create.acl_syncjobs,
            eas_reset=mailbox_create.acl_eas_reset,
            sogo_profile_reset=mailbox_create.acl_sogo_profile_reset,
            pushover=mailbox_create.acl_pushover,
            quarantine=mailbox_create.acl_quarantine,
            quarantine_attachments=mailbox_create.acl_quarantine_attachments,
            quarantine_notification=mailbox_create.acl_quarantine_notification,
            quarantine_category=mailbox_create.acl_quarantine_category,
        )
        user_attributes = UserAttributesModel(
            username=username,
            force_pw_update=mailbox_create.force_pw_update,
            tls_enforce_in=mailbox_create.tls_enforce_in,
            tls_enforce_out=mailbox_create.tls_enforce_out,
            sogo_access=mailbox_create.sogo_access,
            imap_access=mailbox_create.imap_access,
            pop3_access=mailbox_create.pop3_access,
            smtp_access=mailbox_create.smtp_access,
            sieve_access=mailbox_create.sieve_access,
            relayhost=mailbox_create.relayhost,
            quarantine_notification=mailbox_create.quarantine_notification,
            quarantine_category=mailbox_create.quarantine_category,
        )
        self.db.add_all([
            mailbox,
            quota2,
            quota2replica,
            alias,
            user_acl,
            user_attributes,
        ])

        # TODO: ratelimit

        self.sogo.update_static_view(username)

        return mailbox

    def update_mailbox(self, username, mailbox_update: MailboxUpdate):
        details = self.get_mailbox_details(username)

        # Update mailbox values.
        mailbox = self.db.query(MailboxModel).filter_by(username=username).one()
        if mailbox_update.name is not None:
            mailbox.name = mailbox_update.name

        if mailbox_update.active is not None:
            self.db.query(AliasModel).filter_by(username=username).update({"active": mailbox_update.active})
            mailbox.active = mailbox_update.active

        if mailbox_update.password:
            if mailbox_update.password != mailbox_update.password2:
                raise ValueError("passwords don't match")

            mailbox.password = bcrypt.hash(mailbox_update.password)

        if mailbox_update.quota is not None:
            domain_data = self._get_domain_data(details.domain)
            if mailbox_update.quota > domain_data.maxquota:
                raise KeyError("Mailbox quota exceeded")

            mailbox_data = self._get_mailbox_data(details.domain)
            if mailbox_data.quota - details.quota + mailbox_update.quota > domain_data.quota:
                raise KeyError("Mailbox quota left exceeded")

            mailbox.quota = mailbox_update.quota

        # Update mailbox attributes.
        attributes = self.db.query(UserAttributesModel).filter_by(username=username).one()
        for key, value in mailbox_update.model_dump().items():
            if value is not None and hasattr(attributes, key):
                setattr(attributes, key, value)

        # TODO: recovery email?

        self.sogo.update_static_view(username)

        return mailbox

    def delete_mailbox(self, username):
        self.db.query(AliasModel).filter_by(goto=username).delete()
        # self.db.query(PushoverModel).filter_by(username=username).delete()
        # self.db.query(QuarantineModel).filter_by(rcpt=username).delete()
        self.db.query(Quota2Model).filter_by(username=username).delete()
        self.db.query(Quota2ReplicaModel).filter_by(username=username).delete()
        self.db.query(MailboxModel).filter_by(username=username).delete()
        self.db.query(SenderAclModel).filter_by(
            or_(
                SenderAclModel.logged_in_as == username,
                SenderAclModel.send_as == username,
            )
        ).delete()
        self.db.query(UserAclModel).filter_by(username=username).delete()
        self.db.query(SpamaliasModel).filter_by(goto=username).delete()
        self.db.query(ImapsyncModel).filter_by(user2=username).delete()
        self.db.query(FilterconfModel).filter_by(object=username).delete()
        self.db.query(BccMapsModel).filter_by(local_dest=username).delete()
        self.sogo.delete_user(username)
        self.sogo.update_static_view(username)

        # TODO: auth
        # TODO: update aliases
        # TODO: redis

    def _get_mailbox_data(self, domain):
        return (
            self.db.query(
                func.count(MailboxModel.username).label("count"),
                func.coalesce(func.round(func.sum(MailboxModel.quota) / mebi), 0).label("quota"),
            )
            .filter_by(kind="")
            .filter_by(domain=domain)
            .one()
        )

    def _get_domain_data(self, domain):
        return self.db.query(DomainModel).filter_by(domain=domain).one()
