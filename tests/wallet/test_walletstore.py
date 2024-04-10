from hive_agent.wallet.wallet import WalletStore


def test_wallet_store():
    store = WalletStore()
    address = store.add_wallet()

    wallet = store.get_wallet(address)
    assert wallet is not None
    assert wallet.get_address() == address

    assert address in store.get_all_wallets()

    store.remove_wallet(address)
    assert store.get_wallet(address) is None
