"""Pydantic schemas."""

from datetime import datetime as dt
from typing import Optional

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
    description: Optional[str]
    max_num_aliases_for_domain: int
    max_num_mboxes_for_domain: int
    def_quota_for_mbox: int
    max_quota_for_mbox: int
    max_quota_for_domain: int
    relayhost: str
    backupmx: bool
    gal: bool
    active: bool
    relay_all_recipients: bool
    relay_unknown_only: bool
    aliases_in_domain: int
    aliases_left: int


class DomainUpdate(BaseModel):

    description: Optional[str] = None
    aliases: Optional[int] = None
    mailboxes: Optional[int] = None
    defquota: Optional[int] = None
    maxquota: Optional[int] = None
    quota: Optional[int] = None
    active: Optional[bool] = None
    gal: Optional[bool] = None
    backupmx: Optional[int] = None
    relay_all_recipients: Optional[bool] = None
    relay_unknown_only: Optional[bool] = None


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
    relayhost: bool = False
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
    relayhost: bool
    sogo_access: bool
    imap_access: bool
    pop3_access: bool
    smtp_access: bool
    sieve_access: bool
    last_imap_login: Optional[dt]
    last_smtp_login: Optional[dt]
    last_pop3_login: Optional[dt]
    last_sso_login: Optional[dt]


class MailboxUpdate(BaseModel):

    password: Optional[str] = None
    password2: Optional[str] = None
    name: Optional[str] = None
    quota: Optional[int] = None
    quarantine_notification: Optional[str] = None
    quarantine_category: Optional[str] = None
    active: Optional[bool] = None
    force_pw_update: Optional[bool] = None
    tls_enforce_in: Optional[bool] = None
    tls_enforce_out: Optional[bool] = None
    relayhost: Optional[bool] = None
    sogo_access: Optional[bool] = None
    imap_access: Optional[bool] = None
    pop3_access: Optional[bool] = None
    smtp_access: Optional[bool] = None
    sieve_access: Optional[bool] = None
