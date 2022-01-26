"""This file contains functions for creating, derivating and displaying accounts,
and it introduces new AccountExt class to add custom methods to Account from web3.py.
"""

import itertools
import secrets

from hashlib import sha256
from typing import Generator, List

from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_utils.curried import combomethod

from settings import w3, PRIVATE_KEY, logger, LOGGING


class LocalAccountExt(LocalAccount):
    """Subclassed eth_account.LocalAccount to add custom methods.
    """
    iter_id = itertools.count()

    def __init__(self, *args):
        self.id = next(self.iter_id)
        super().__init__(*args)

    def get_balance(self):
        return w3.eth.get_balance(self.address)

    def get_nonce(self):
        return w3.eth.get_transaction_count(self.address)


class AccountExt(Account):
    """Subclassed eth_account.Account to add custom methods.
    """
    @combomethod
    def from_key(self, private_key):
        key = self._parsePrivateKey(private_key)
        return LocalAccountExt(key, self)


def get_master_account(default: bool = True) -> AccountExt:
    """Examples:
    >>> master_account = get_master_account()  # takes default account from settings.py
    >>> master_account = get_master_account(False)  # generates new account and saves the private key in logs
    """
    if default:
        account = AccountExt.from_key(PRIVATE_KEY)
    else:
        temp_private_key = '0x' + secrets.token_hex(32)
        account = AccountExt.from_key(temp_private_key)
        print('[New account mode]')
        print("Generated new master account! Save the private key!")
        print(f"PRIVATE_KEY: {temp_private_key}")
        print(f"Address: {AccountExt.from_key(temp_private_key).address}")
        if LOGGING == True:
            logger.warning("[New account mode]")
            logger.warning("Generated new master account! Save the private key!")
            logger.warning(f"PRIVATE KEY: {temp_private_key}")
            logger.warning(f"Address: {AccountExt.from_key(temp_private_key).address}")
    return account


def create_account_generator(master_account: AccountExt) -> Generator[AccountExt, None, None]:
    """Examples:
    >>> account_gen = create_account_generator(master_account)
    """
    private_key = master_account.privateKey.hex()
    while True:
        private_key = sha256(private_key.encode('utf-8')).hexdigest()
        account = AccountExt.from_key(private_key)
        yield account


def display_accounts(accounts: List[AccountExt],
                     balances: bool = False,
                     secrets: bool = False):
    """Examples:
    >>> display_accounts([master_account] + accounts, balances=True, secrets=False)
    """
    if LOGGING == True:
        for account in accounts:
            logger.info(f'Address ({account.id}): {account.address}  |  '
                        f'Balance: {account.get_balance() / 10 ** 18 if balances else "?"}')
            if secrets:
                logger.info(f'PRIVATE KEY: {account.privateKey.hex()}')
    for account in accounts:
        print(f'Address ({account.id}): {account.address}  |  '
              f'Balance: {account.get_balance() / 10 ** 18 if balances else "?"}')
        if secrets:
            print(f'PRIVATE KEY: {account.privateKey.hex()}')
            # print(f'PRIVATE KEY (int): {int(account.privateKey.hex(), 16)}')


def get_derived_accounts(master_account: AccountExt,
                         number_of_accounts: int):
    """Examples:
    >>> accounts = get_derived_accounts(default=True, number_of_accounts=10)
    """
    account_gen = create_account_generator(master_account)
    derived_accounts = []
    for _ in range(0, number_of_accounts):
        derived_accounts.append(next(account_gen))
    return derived_accounts
