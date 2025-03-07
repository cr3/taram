"""Testing models."""


from sqlalchemy import (
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint

from taram.models import SQLModel


class NotNullableTest(SQLModel):
    """Table for testing not nullable columns."""

    __tablename__ = "not_nullable_test"

    test_id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(Text)


class NullableTest(SQLModel):
    """Table for testing nullable columns."""

    __tablename__ = "nullable_test"

    test_id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str | None] = mapped_column(Text)


class DefaultTest(SQLModel):
    """Table for testing default columns."""

    __tablename__ = "default_test"

    test_id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(default=0)


class ServerDefaultTest(SQLModel):
    """Table for testing default columns."""

    __tablename__ = "server_default_test"

    test_id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(server_default="0")


class ForeignKeyTest(SQLModel):
    """Table for testing foreign keys."""

    __tablename__ = "foreign_key_test"

    test_id: Mapped[int] = mapped_column(ForeignKey("default_test.test_id"), primary_key=True)
    value = relationship("DefaultTest", foreign_keys=[test_id])


class NullableForeignKeyTest(SQLModel):
    """Table for testing foreign keys."""

    __tablename__ = "nullable_foreign_key_test"

    key: Mapped[int] = mapped_column(primary_key=True)
    test_id: Mapped[int | None] = mapped_column(ForeignKey("default_test.test_id"))
    value = relationship("DefaultTest", foreign_keys=[test_id])


class DualKeysTest(SQLModel):
    """Table for testing foreign keys."""

    __tablename__ = "dual_keys_test"

    test_id1: Mapped[int] = mapped_column(primary_key=True)
    test_id2: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(default=0)


class DualForeignKeysTest(SQLModel):
    """Table for testing foreign keys."""

    __tablename__ = "dual_foreign_keys_test"

    test_id1: Mapped[int] = mapped_column(primary_key=True)
    test_id2: Mapped[int] = mapped_column(primary_key=True)

    value = relationship("DualKeysTest", foreign_keys=[test_id1, test_id2])

    __table_args__ = (
        ForeignKeyConstraint([test_id1, test_id2], [DualKeysTest.test_id1, DualKeysTest.test_id2]),
        {},
    )


class TextTest(SQLModel):
    """Table for testing Text types."""

    __tablename__ = "text_test"

    test_id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str | None] = mapped_column(Text)
