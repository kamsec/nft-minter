"""This file contains functions for sending coins between accounts,
supports one to many, many to many, many to one.
"""

from typing import List

from src.accounts import AccountExt
from settings import w3, CHAIN_ID, DEFAULT_GAS, logger, LOGGING


def send_tx(sender: AccountExt,
            receiver: AccountExt,
            amount: int,
            gas_price: int = None,
            nonce: int = None):
    """Examples:
    >>> send_tx(sender_account, receiver_account, sender_account.get_balance())
    """
    if nonce is None:
        nonce = sender.get_nonce()
    if gas_price is None:
        gas_price = w3.eth.gas_price
    tx = {
        'to': receiver.address,
        'value': int(amount),
        'nonce': nonce,
        'gas': DEFAULT_GAS,
        'gasPrice': gas_price,
        'chainId': CHAIN_ID
    }
    signed_tx = w3.eth.account.sign_transaction(tx, sender.privateKey.hex())
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
    return tx_hash


def send_one_to_many(master_account: AccountExt,
                     accounts: List[AccountExt],
                     amount: int):
    """Examples:
    >>> send_one_to_many(master_account, accounts, int(0.01 * 10 ** 18))
    """
    master_account_balance = master_account.get_balance()
    required_balance_estimation = len(accounts) * (DEFAULT_GAS * w3.eth.gas_price + amount)
    if master_account_balance < required_balance_estimation:
        raise Exception(f'Inufficient funds! master_account: '
                        f'{master_account_balance / 10 ** 18}, required: {required_balance_estimation / 10 ** 18}')

    gas_price = w3.eth.gas_price
    nonce = master_account.get_nonce()
    for account in accounts:
        try:
            last_tx_hash = send_tx(master_account, account, amount, gas_price, nonce)
            nonce += 1
            if LOGGING == True:
                info_msg = f'Sending {amount / 10 ** 18} from ({master_account.id}) {master_account.address[:6]}... '\
                           f'to ({account.id}) {account.address[:6]}... in {last_tx_hash}'
                print(info_msg)
                logger.info(info_msg)
        except Exception as e:
            print(e)
    w3.eth.wait_for_transaction_receipt(last_tx_hash, timeout=10)


def send_many_to_one(accounts: List[AccountExt],
                     master_account: AccountExt):
    """Examples:
    >>> send_many_to_one(accounts_part_2, master_account)
    """
    old_balances = {account.address: account.get_balance() for account in accounts}
    gas_price = w3.eth.gas_price
    tx_fee = DEFAULT_GAS * gas_price
    available_balances = {account.address: old_balances[account.address] - tx_fee for account in accounts}

    for account in accounts:
        nonce = account.get_nonce()
        try:
            last_tx_hash = send_tx(account, master_account, available_balances[account.address], gas_price, nonce)
            if LOGGING == True:
                info_msg = f'Sending {available_balances[account.address] / 10 ** 18} from ({account.id}) '\
                           f'{account.address[:6]}... to ({master_account.id}) {master_account.address[:6]}... in {last_tx_hash}'
                print(info_msg)
                logger.info(info_msg)
        except Exception as e:
            print(e)
    w3.eth.wait_for_transaction_receipt(last_tx_hash, timeout=10)


def send_many_to_many(senders_accounts: List[AccountExt],
                      receivers_accounts: List[AccountExt]):
    """Examples:
    >>> send_many_to_many(accounts_part_1, accounts_part_2)
    """
    if len(senders_accounts) != len(receivers_accounts):
        raise Exception('Number of senders must be equal to number of receivers')
    old_balances = {sender_account.address: sender_account.get_balance() for sender_account in senders_accounts}
    gas_price = w3.eth.gas_price
    tx_fee = DEFAULT_GAS * gas_price
    available_balances = {sender_account.address: old_balances[sender_account.address] - tx_fee for sender_account in senders_accounts}

    for sender_account, receiver_account in zip(senders_accounts, receivers_accounts):
        nonce = sender_account.get_nonce()
        try:
            last_tx_hash = send_tx(sender_account, receiver_account, available_balances[sender_account.address], gas_price, nonce)
            if LOGGING == True:
                info_msg = f'Sending {available_balances[sender_account.address] / 10 ** 18} from ({sender_account.id}) '\
                           f'{sender_account.address[:6]}... to ({receiver_account.id}) {receiver_account.address[:6]}... in {last_tx_hash}'
                print(info_msg)
                logger.info(info_msg)
        except Exception as e:
            print(e)
    w3.eth.wait_for_transaction_receipt(last_tx_hash, timeout=10)
