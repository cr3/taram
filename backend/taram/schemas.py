"""Pydantic schemas."""

from datetime import datetime as dt

from pydantic import BaseModel

from taram.units import gibi, kebi


class DomainCreate(BaseModel):

    domain: str
    description: str = ""
    aliases: int = 400
    mailboxes: int = 10
    defquota: int = 3 * gibi
    maxquota: int = 10 * gibi
    quota: int = 10 * gibi
    active: bool = True
    gal: bool = True
    backupmx: int = False
    relay_all_recipients: bool = False
    relay_unknown_only: bool = False
    dkim_selector: str = "dkim"
    key_size: int = 2 * kebi
    restart_sogo: bool = True


class DomainDetails(BaseModel):
    max_new_mailbox_quota: int
    def_new_mailbox_quota: int
    quota_used_in_domain: int
    bytes_total: int
    msgs_total: int
    mboxes_in_domain: int
    mboxes_left: int
    domain: str
    description: str | None
    max_num_aliases_for_domain: int
    max_num_mboxes_for_domain: int
    def_quota_for_mbox: int
    max_quota_for_mbox: int
    max_quota_for_domain: int
    relayhost: int
    backupmx: bool
    gal: bool
    active: bool
    relay_all_recipients: bool
    relay_unknown_only: bool
    aliases_in_domain: int
    aliases_left: int


class DomainUpdate(BaseModel):

    description: str | None = None
    aliases: int | None = None
    mailboxes: int | None = None
    defquota: int | None = None
    maxquota: int | None = None
    quota: int | None = None
    active: bool | None = None
    gal: bool | None = None
    backupmx: int | None = None
    relay_all_recipients: bool | None = None
    relay_unknown_only: bool | None = None


class MailboxCreate(BaseModel):

    local_part: str
    domain: str
    password: str
    password2: str
    name: str = ""
    quota: int = 10 * gibi
    quarantine_notification: str = "hourly"
    quarantine_category: str = "reject"
    active: bool = True
    force_pw_update: bool = False
    tls_enforce_in: bool = False
    tls_enforce_out: bool = False
    relayhost: int = 0
    sogo_access: bool = True
    imap_access: bool = True
    pop3_access: bool = True
    smtp_access: bool = True
    sieve_access: bool = True
    acl_spam_alias: bool = True
    acl_tls_policy: bool = True
    acl_spam_score: bool = True
    acl_spam_policy: bool = True
    acl_delimiter_action: bool = True
    acl_syncjobs: bool = False
    acl_eas_reset: bool = True
    acl_sogo_profile_reset: bool = False
    acl_pushover: bool = True
    acl_quarantine: bool = True
    acl_quarantine_attachments: bool = True
    acl_quarantine_notification: bool = True
    acl_quarantine_category: bool = True


class MailboxDetails(BaseModel):

    username: str
    active: bool
    domain: str
    name: str
    local_part: str
    quota: int
    quota_used: int
    messages: int
    quarantine_notification: str
    quarantine_category: str
    force_pw_update: bool
    tls_enforce_in: bool
    tls_enforce_out: bool
    relayhost: int
    sogo_access: bool
    imap_access: bool
    pop3_access: bool
    smtp_access: bool
    sieve_access: bool
    last_imap_login: dt | None
    last_smtp_login: dt | None
    last_pop3_login: dt | None
    last_sso_login: dt | None


class MailboxUpdate(BaseModel):

    password: str | None = None
    password2: str | None = None
    name: str | None = None
    quota: int | None = None
    quarantine_notification: str | None = None
    quarantine_category: str | None = None
    active: bool | None = None
    force_pw_update: bool | None = None
    tls_enforce_in: bool | None = None
    tls_enforce_out: bool | None = None
    relayhost: int | None = None
    sogo_access: bool | None = None
    imap_access: bool | None = None
    pop3_access: bool | None = None
    smtp_access: bool | None = None
    sieve_access: bool | None = None
