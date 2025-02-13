"""Pydantic schemas."""

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
