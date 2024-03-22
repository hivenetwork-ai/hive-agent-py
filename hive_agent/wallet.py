from typing import Any, Dict, List

from eth_account import Account
from eth_account.datastructures import SignedMessage
from eth_account.signers.local import LocalAccount
from eth_account.messages import encode_defunct


class ImmutableDict:
    def __init__(self):
        self._dict = {}

    def add(self, key, value):
        if key in self._dict:
            raise KeyError(f"key '{key}' already exists. Cannot update the value.")
        self._dict[key] = value

    def get(self, key):
        return self._dict.get(key, None)

    def delete(self, key):
        if key in self._dict:
            del self._dict[key]
        else:
            raise KeyError(f"key '{key}' not found.")

    def values(self):
        return self._dict.values()

    def __str__(self):
        return str(self._dict)


class Wallet:
    __account: LocalAccount

    def __init__(self, entropy=""):
        self.__account: LocalAccount = Account.create(extra_entropy=entropy)
        print(f"created new account={self.__account.address}")

    def get_address(self) -> str:
        return self.__account.address

    def sign_message(self, message: str) -> SignedMessage:
        msg = encode_defunct(text=message)
        return self.__account.sign_message(msg)

    def sign_transaction(self, transaction: Dict) -> Any:
        return self.__account.sign_transaction(transaction)


class WalletStore:
    __wallets: ImmutableDict

    def __init__(self):
        self.__wallets = ImmutableDict()

    def add_wallet(self, entropy="") -> str:
        wallet = Wallet(entropy)
        address = wallet.get_address()
        self.__wallets.add(address, wallet)

        return address

    def get_all_wallets(self) -> List[str]:
        wallets_list = [wallet.get_address() for wallet in self.__wallets.values()]
        return wallets_list

    def get_wallet(self, address: str) -> Wallet:
        return self.__wallets.get(address)

    def remove_wallet(self, address: str):
        self.__wallets.delete(address)
