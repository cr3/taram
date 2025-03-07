"""Unit tests for the model testing module."""

import pytest
from hamcrest import assert_that, has_length, has_properties, is_

from ...models import (
    DefaultTest,
    DualForeignKeysTest,
    ForeignKeyTest,
    NotNullableTest,
    NullableForeignKeyTest,
    NullableTest,
    ServerDefaultTest,
)


@pytest.mark.parametrize(
    "model, matches",
    [
        (DefaultTest, has_properties(value=0)),
        (ForeignKeyTest, has_properties(value=has_properties(value=0))),
        (NotNullableTest, has_properties(value=is_(str))),
        (NullableTest, has_properties(value=None)),
        (ServerDefaultTest, has_properties(value=0)),
        (DualForeignKeysTest, has_properties(value=has_properties(value=0))),
        (NullableForeignKeyTest, has_properties(value=None)),
    ],
)
def test_db_model(model, matches, db_model):
    """The db_model fixture should return a valid model."""
    result = db_model(model)

    assert_that(result, matches)


def test_db_model_foreign_key_field_override(db_model):
    """A database-model should be parameterizable with a foreign key."""
    value = db_model(DefaultTest)

    result = db_model(ForeignKeyTest, test_id=value.test_id)

    assert_that(result, has_properties(value=value, test_id=value.test_id))


def test_db_model_foreign_key_relationship_override(db_model):
    """A database-model should be parameterizable with a relationship."""
    value = db_model(DefaultTest)

    result = db_model(ForeignKeyTest, value=value)

    assert_that(result, has_properties(value=value, test_id=value.test_id))


def test_db_model_foreign_key_relationship_skip_create(db_model, db_session):
    """Overriding a relationship should not attempt to create relation.

    When passing a relationship, db_model was no associating it with the
    primary keys and actually creating a relation, adding it to kwargs.
    So the final invocation would look like
    model(relation=obj, relation_id=another_object_id)
    Which worked because sql alchemy ignores the relation_id if the relation
    is given.
    """
    db_session.query(DefaultTest).delete()  # Clean slate

    relation = db_model(DefaultTest)

    db_model(ForeignKeyTest, value=relation)

    # Should not have created another DefaultTest
    assert_that(db_session.query(DefaultTest).all(), has_length(1))
