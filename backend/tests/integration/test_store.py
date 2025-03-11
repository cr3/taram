"""Integration tests for the store module."""

import pytest


def test_get_unknown(store, unique):
    """Getting an unknown key should return None."""
    key = unique("text")
    assert store.get(key) is None


def test_set_and_get(store, unique):
    """Setting a key, then getting it should return the value."""
    key, value = unique("text"), unique("text")
    store.set(key, value)
    assert store.get(key) == value


def test_set_non_str(store, unique):
    """Setting a key to a non-string should cast to string."""
    key, value = unique("text"), unique("integer")
    assert store.set(key, value) is True
    assert store.get(key) == str(value)


def test_set_twice(store, unique):
    """Setting the same key twice should keep the last value."""
    key, value1, value2 = unique("text"), unique("text"), unique("text")
    assert store.set(key, value1) is True
    assert store.set(key, value2) is True
    assert store.get(key) == value2


def test_delete_unknown(store, unique):
    """Deleting an unknown key should do nothing."""
    key = unique("text")
    assert store.delete(key) == 0


def test_delete_set(store, unique):
    """Deleting a key should remove it from the store."""
    key = unique("text")
    store.set(key, "")
    assert store.delete(key) == 1
    assert store.get(key) is None


def test_delete_hset(store, unique):
    """Deleting a key should also remove fields from the store."""
    key, field = unique("text"), unique("text")
    store.hset(key, field, "")
    assert store.delete(key) == 1
    assert store.hget(key, field) is None


def test_delete_twice(store, unique):
    """Deleting the same key twice should return 0."""
    key = unique("text")
    store.set(key, "")
    assert store.delete(key) == 1
    assert store.delete(key) == 0


def test_delete_many(store, unique):
    """Deleting many keys should return the number of deleted keys."""
    key1, key2, key3 = unique("text"), unique("text"), unique("text")
    store.set(key1, "")
    store.set(key2, "")
    assert store.delete(key1, key2, key3) == 2


def test_hget_unknown_key(store, unique):
    """Calling hget with an unknown key should return None."""
    key, field = unique("text"), unique("text")
    assert store.hget(key, field) is None


def test_hget_unknown_field(store, unique):
    """Calling hget with an unknown field should return None."""
    key, field1, field2 = unique("text"), unique("text"), unique("text")
    store.hset(key, field1, "")
    assert store.hget(key, field2) is None


def test_hset_and_hget(store, unique):
    """Setting a key and field, then getting it should return the value."""
    key, field, value = unique("text"), unique("text"), unique("text")
    store.hset(key, field, value)
    assert store.hget(key, field) == value


def test_hgetall_unknown(store, unique):
    """Calling hgetall with an unknown key should return an empty dict."""
    key = unique("text")
    assert store.hgetall(key) == {}


def test_hgetall_single(store, unique):
    """Calling hgetall with a single field should return a dict with the field."""
    key, field, value = unique("text"), unique("text"), unique("text")
    store.hset(key, field, value)
    assert store.hgetall(key) == {field: value}


def test_hgetall_many(store, unique):
    """Calling hgetall with many fields should return a dict with all fields."""
    key, field1, field2, value1, value2 = unique("text"), unique("text"), unique("text"), unique("text"), unique("text")
    store.hset(key, field1, value1)
    store.hset(key, field2, value2)
    assert store.hgetall(key) == {field1: value1, field2: value2}


def test_hset_non_str(store, unique):
    """Setting a key and field to a non-string should cast to string."""
    key, field, value = unique("text"), unique("text"), unique("integer")
    assert store.hset(key, field, value) == 1
    assert store.hget(key, field) == str(value)


def test_hset_twice(store, unique):
    """Setting the same key and field twice should keep the last value."""
    key, field, value1, value2 = unique("text"), unique("text"), unique("text"), unique("text")
    assert store.hset(key, field, value1) == 1
    assert store.hset(key, field, value2) == 0
    assert store.hget(key, field) == value2


def test_hset_multiple(store, unique):
    """Setting multiple fields for a key should store each value."""
    key, field1, field2, value1, value2 = unique("text"), unique("text"), unique("text"), unique("text"), unique("text")
    assert store.hset(key, field1, value1) == 1
    assert store.hset(key, field2, value2) == 1
    assert store.hget(key, field1) == value1
    assert store.hget(key, field2) == value2


def test_hset_get(store, unique):
    """Calling get after hset should raise."""
    key, field = unique("text"), unique("text")
    store.hset(key, field, "")
    with pytest.raises(TypeError):
        store.get(key)


def test_hset_set(store, unique):
    """Calling set after hset should overwrite."""
    key, field, value = unique("text"), unique("text"), unique("text")
    store.hset(key, field, "")
    store.set(key, value)
    assert store.get(key) == value


def test_set_hget(store, unique):
    """Calling hget after set should raise."""
    key, field = unique("text"), unique("text")
    store.set(key, "")
    with pytest.raises(TypeError):
        store.hget(key, field)


def test_set_hgetall(store, unique):
    """Calling hgetall after set should raise."""
    key = unique("text")
    store.set(key, "")
    with pytest.raises(TypeError):
        store.hgetall(key)


def test_set_hset(store, unique):
    """Calling hset after set should raise."""
    key, field = unique("text"), unique("text")
    store.set(key, "")
    with pytest.raises(TypeError):
        store.hset(key, field, "")


def test_hdel_unknown(store, unique):
    """Deleting an unknown key and field should do nothing."""
    key, field = unique("text"), unique("text")
    assert store.hdel(key, field) == 0


def test_hdel_once(store, unique):
    """Deleting a key and field should remove it from the store."""
    key, field = unique("text"), unique("text")
    store.hset(key, field, "")
    assert store.hdel(key, field) == 1
    assert store.hget(key, field) is None


def test_hdel_twice(store, unique):
    """Deleting the same key and field should return 0."""
    key, field = unique("text"), unique("text")
    store.hset(key, field, "")
    assert store.hdel(key, field) == 1
    assert store.hdel(key, field) == 0


def test_hdel_many(store, unique):
    """Deleting many fields should return the number of deleted fields."""
    key, field1, field2, field3 = unique("text"), unique("text"), unique("text"), unique("text")
    store.hset(key, field1, "")
    store.hset(key, field2, "")
    assert store.hdel(key, field1, field2, field3) == 2
