"""Unit tests for the sogo module."""

from unittest.mock import Mock

import pytest

from taram.models import (
    AliasDomainModel,
    MailboxModel,
    SogoStaticView,
    UserAttributesModel,
)
from taram.sogo import Sogo


@pytest.mark.parametrize(
    "force_pw_update, sogo_access, expected",
    [
        (False, False, "default"),
        (False, True, "original"),
        (True, False, "default"),
        (True, True, "default"),
    ],
)
def test_sogo_update_static_view_password(force_pw_update, sogo_access, expected, db_model, db_session):
    """The password should only be the same when force_pw_update is False and sogo_access is True."""
    mailbox = db_model(MailboxModel, password="original")  # noqa: S106
    db_model(UserAttributesModel, username=mailbox.username, force_pw_update=force_pw_update, sogo_access=sogo_access)
    Sogo(db_session, Mock(), default_password="default").update_static_view(mailbox.username)  # noqa: S106
    result = db_session.query(SogoStaticView).one()
    assert result.c_password == expected


def test_sogo_update_static_view_aliases(db_model, db_session, unique):
    """The ad_alias should contain the alias domains."""
    mailbox = db_model(MailboxModel)
    alias = db_model(AliasDomainModel, target_domain=mailbox.domain)
    Sogo(db_session, Mock()).update_static_view("a@b.com")
    result = db_session.query(SogoStaticView).one()
    assert result.ad_aliases == f"{mailbox.local_part}@{alias.alias_domain}"
