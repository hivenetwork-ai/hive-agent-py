import pytest

from hive_agent.wallet.wallet import ImmutableDict


def test_immutable_dict():
    imm_dict = ImmutableDict()

    imm_dict.add("key1", "value1")
    assert imm_dict.get("key1") == "value1"

    with pytest.raises(KeyError):
        imm_dict.add("key1", "value2")

    imm_dict.delete("key1")
    assert imm_dict.get("key1") is None

    with pytest.raises(KeyError):
        imm_dict.delete("key1")
