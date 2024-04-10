from hive_agent.wallet.wallet import Wallet


def test_wallet_creation():
    wallet = Wallet()
    assert wallet.get_address() is not None
    assert isinstance(wallet.get_address(), str)


def test_sign_message():
    wallet = Wallet()
    message = "<msg>"
    signed_message = wallet.sign_message(message)

    assert signed_message is not None

