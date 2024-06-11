from hive_agent.wallet.wallet import Wallet
from hive_agent.wallet.wallet import WalletStore


# Testing Wallet Class
def test_wallet_creation():
    wallet = Wallet()


def test_get_address():
    wallet = Wallet()
    address = wallet.get_address()
    assert address is not None
    assert isinstance(address, str)


def test_sign_message():
    wallet = Wallet()
    signed_message = wallet.sign_message("<msg>")
    assert signed_message is not None


def test_sign_transaction():
    wallet = Wallet()
    transaction = {
        "nonce": 0,
        "gasPrice": 20000000000,
        "gas": 2000000,
        "value": 100,
        "data": b"",
        "chainId": 1,
    }
    signed_transaction = wallet.sign_transaction(transaction)
    assert signed_transaction is not None


# Testing WalletStore Class
def test_wallet_store_creation():
    wallet_store = WalletStore()


def test_add_wallet():
    wallet_store = WalletStore()
    address = wallet_store.add_wallet()
    wallet = wallet_store.get_wallet(address)
    assert wallet is not None
    assert isinstance(wallet.get_address(), str)


def test_get_all_wallets():
    wallet_store = WalletStore()
    addresses = []

    for _ in range(3):
        address = wallet_store.add_wallet()
        addresses.append(address)

    retrieved_addresses = wallet_store.get_all_wallets()
    assert set(retrieved_addresses) == set(addresses)
    assert len(retrieved_addresses) == len(addresses)


def test_get_wallet():
    wallet_store = WalletStore()
    address = wallet_store.add_wallet()
    wallet = wallet_store.get_wallet(address)
    assert wallet is not None
    assert isinstance(wallet.get_address(), str)


def test_remove_wallet():
    wallet_store = WalletStore()
    address = wallet_store.add_wallet()
    wallet_store.remove_wallet(address)
    wallet = wallet_store.get_wallet(address)
    assert wallet is None
    assert wallet_store.get_all_wallets() == []
