import logging
import sys
from datetime import datetime

from typing import Any, Dict, List

from eth_account import Account
from eth_account.datastructures import SignedMessage
from eth_account.signers.local import LocalAccount
from eth_account.messages import encode_defunct

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


class ImmutableDict:
    def __init__(self):
        self._dict = {}
        logging.info("created new ImmutableDict")
        
    def add(self, key, value):
        if key in self._dict:
            logging.error(f"key '{key}' already exists. Cannot add the value.")
            raise KeyError(f"key '{key}' already exists. Cannot update the value.")
        self._dict[key] = value
        logger.info(f"Added key: {key}")

    def get(self, key):
        value = self._dict.get(key, None)
        logger.info(f"Retrieved key: {key} with value: {value}")
        return value

    def delete(self, key):
        if key in self._dict:
            del self._dict[key]
            logger.info(f"Deleted key: {key}")
        else:
            logger.error(f"key '{key}' not found.")
            raise KeyError(f"key '{key}' not found.")

    def values(self):
        return self._dict.values()

    def __str__(self):
        return str(self._dict)


class Wallet:
    __account: LocalAccount

    def __init__(self, entropy=""):
        self.__account: LocalAccount = Account.create(extra_entropy=entropy)
        logging.info(f"Created new wallet with address: {self.__account.address}")

    def get_address(self) -> str:
        return self.__account.address

    def sign_message(self, message: str) -> SignedMessage:
        msg = encode_defunct(text=message)
        signed_message = self.__account.sign_message(msg)
        logger.info(f"Signed message for account: {self.__account.address}")
        return signed_message

     def sign_transaction(self, transaction: Dict) -> Any:
        signed_transaction = self.__account.sign_transaction(transaction)
        logger.info(f"Signed transaction for account: {self.__account.address}")
        return signed_transaction


class WalletStore:
    __wallets: ImmutableDict

    def __init__(self):
        self.__wallets = ImmutableDict()

    def add_wallet(self, entropy="") -> str:
        wallet = Wallet(entropy)
        address = wallet.get_address()
        self.__wallets.add(address, wallet)
        logger.info(f"Added wallet with address: {address}")
        return address

    def get_all_wallets(self) -> List[str]:
        wallets_list = [wallet.get_address() for wallet in self.__wallets.values()]
        logger.info("Retrieved all wallet addresses.")
        return wallets_list

    def get_wallet(self, address: str) -> Wallet:
        wallet = self.__wallets.get(address)
         logger.info(f"Retrieved wallet for address: {address}")
        return wallet

    def remove_wallet(self, address: str):
        self.__wallets.delete(address)
        logger.info(f"Removed wallet with address: {address}")
