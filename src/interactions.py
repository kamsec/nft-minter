"""This file contains functions for interactions with smart contract,
reading and writing to the blockchain.
"""

from typing import List, Union

from src.accounts import AccountExt
from settings import CONTRACT_ADDRESS, CONTRACT_ABI, CHAIN_ID, w3, logger, LOGGING, CONTRACT_FUNCTION_GAS


def contract_read(contract_func_name: str,
                  contract_func_args: List[Union[str, int]] = None):
    """Examples:
    >>> contract_read('claimPrice', None)
    >>> contract_read('ownerOf', [63])
    >>> contract_read('tokenOfOwnerByIndex', ['0xDD844943B20B327C5219d6710aDFDa492DAEFE50', 0])
    """
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    if contract_func_args is None:
        contract_function = getattr(contract.functions, contract_func_name)()
    else:
        contract_function = getattr(contract.functions, contract_func_name)(*contract_func_args)
    response = contract_function.call()

    if LOGGING == True:
        info_msg = f'Reading contract "{contract_func_name}({contract_func_args if contract_func_args else ""})". '\
                   f'Value: {response}'
        print(info_msg)
        logger.info(info_msg)
    return response


def contract_write(sender: AccountExt,
                   contract_func_name: str,
                   contract_func_args: List[Union[str, int]],
                   amount: int,
                   gas: int = CONTRACT_FUNCTION_GAS,
                   nonce: int = None,
                   ) -> str:
    """Examples:
    >>> contract_write(master_account, 'mint', None, int(0.1 * 10 ** 18))
    >>> contract_write(master_account, 'offerTokenForSale', [63, int(0.2 * 10 ** 18)], 0)
    >>> contract_write(accounts[0], 'buyToken', [63], w3.toWei('0.2', 'ether'))
    """
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    if contract_func_args is None:
        contract_function = getattr(contract.functions, contract_func_name)()
    else:
        contract_function = getattr(contract.functions, contract_func_name)(*contract_func_args)

    if nonce is None:
        nonce = sender.get_nonce()
    contract_tx = contract_function.buildTransaction({
        'value': amount,
        'chainId': CHAIN_ID,
        'gas': gas,  # using CONTRACT_FUNCTION_GAS - choose optimal amount when working with new contract, it varies
        'maxFeePerGas': w3.toWei('2', 'gwei'),
        'maxPriorityFeePerGas': w3.toWei('1', 'gwei'),
        'nonce': nonce,
    })

    signed_tx = w3.eth.account.sign_transaction(contract_tx, private_key=sender.privateKey.hex())
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()

    if LOGGING == True:
        info_msg = f'Calling contract function "{contract_func_name}({contract_func_args if contract_func_args else ""})" '\
                   f'from address ({sender.id}) {sender.address[:6]}... in tx {tx_hash}'
        print(info_msg)
        logger.info(info_msg)
    return tx_hash


def contract_write_from_one(sender: AccountExt,
                            contract_func_name: str,
                            contract_func_args: List[Union[str, int]],
                            number_of_mints: int,
                            amount: int,
                            gas: int = CONTRACT_FUNCTION_GAS,
                            ) -> None:
    """Examples:
    >>> contract_write_from_one(master_account, 'mint', None, 10, amount=w3.toWei(0.1, 'ether'))
    """
    nonce = sender.get_nonce()
    for _ in range(number_of_mints):
        try:
            last_tx_hash = contract_write(sender, contract_func_name, contract_func_args, amount, gas, nonce)
            nonce += 1
        except Exception as e:
            print(e)
    w3.eth.wait_for_transaction_receipt(last_tx_hash, timeout=10)
