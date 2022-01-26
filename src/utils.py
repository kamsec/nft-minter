"""This file contains functions for estimating gas fees.
"""
from settings import MINT_FUNCTION_NAME, NUMBER_OF_MINTS, EXTRA_MIXING_LAYERS, MINT_PRICE,\
    DEFAULT_GAS, CONTRACT_ADDRESS, CONTRACT_ABI, CHAIN_ID, CONTRACT_FUNCTION_GAS, w3


def estimate_single_mint_fee() -> int:
    """Estimates single mint fee in Wei unit.
    """
    current_gas_price = w3.eth.gas_price
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    contract_mint = contract.functions[MINT_FUNCTION_NAME]()
    contract_tx = contract_mint.buildTransaction({
        'from': '0x000000000000000000000000000000000000dEaD',
        'value': w3.toWei(MINT_PRICE, 'ether'),
        'chainId': CHAIN_ID,
        'gas': CONTRACT_FUNCTION_GAS,
        'maxFeePerGas': w3.toWei('2', 'gwei'),
        'maxPriorityFeePerGas': w3.toWei('1', 'gwei')
    })
    estimated_gas_used = w3.eth.estimate_gas(contract_tx)
    estimated_mint_fee = estimated_gas_used * current_gas_price
    return estimated_mint_fee


def estimate_multi_mint_fees(single_mint_fee: int = None) -> int:
    """Estimates total fees used by multi_accounts_mint() function from minter.py in Wei unit.
    """
    current_gas_price = w3.eth.gas_price
    single_tx_fee = DEFAULT_GAS * current_gas_price
    number_of_tx = NUMBER_OF_MINTS + NUMBER_OF_MINTS * EXTRA_MIXING_LAYERS
    if single_mint_fee is None:
        single_mint_fee = estimate_single_mint_fee()

    total_fees = single_tx_fee * number_of_tx + single_mint_fee * NUMBER_OF_MINTS
    return total_fees
