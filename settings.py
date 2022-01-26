"""This file loads settings, secrets and contin some advanced configuration.
For common uses editing settings.json should be enough.
"""
import json
import logging
import time
import argparse

from web3 import Web3
from requests import get


with open('settings.json') as f:
    SETTINGS = json.load(f)
    CHAIN_NAME = SETTINGS['CHAIN_NAME']
    CONTRACT_ADDRESS = SETTINGS['CONTRACT_ADDRESS']
    MINT_FUNCTION_NAME = SETTINGS['MINT_FUNCTION_NAME']
    NUMBER_OF_MINTS = SETTINGS['NUMBER_OF_MINTS']
    MINT_PRICE = SETTINGS['MINT_PRICE']
    EXTRA_MIXING_LAYERS = SETTINGS['EXTRA_MIXING_LAYERS']
    LOGGING = SETTINGS['LOGGING']
    SEND_BACK = SETTINGS['SEND_BACK']


with open('secrets.json') as f:
    SECRETS = json.load(f)
    PRIVATE_KEY = SECRETS['PRIVATE_KEY']
    PROVIDER = SECRETS['PROVIDER']
    w3 = Web3(Web3.HTTPProvider(PROVIDER))


# =========================================
# =========== ADVANCED Settings ===========
# =========================================

# The higher NUMBER_OF_MINTS and EXTRA_MIXING_LAYERS, the more transaction fees will occur
# We send higher amount to ensure that transactions will pass, you can edit this
# The excess payment is send back to master_account in the last step of main() function
# Used only in utils.py in estimate_total_fees
FEES_MULT_FACTOR = 1.001

# When sending eth another address, it's always 21000
DEFAULT_GAS = 21000

# This is maximum gas allowed to be consumed by single contract function execution when using contract_write().
# It can be estimated with estimate_mint_fee() but it's safer to use large hardcoded value.
# If set to higher value than contract function will consume, you will keep the remaining gas.
# Try increasing it if encountering 'exceeds block gas limit' error.
CONTRACT_FUNCTION_GAS = 500000

# Dict with supported chains
CHAINS = {'Ethereum': {'ID': 1,
                       'API': f'https://api.etherscan.io/api?module=contract&action=getabi&address={CONTRACT_ADDRESS}'},
          'Ropsten':  {'ID': 3,
                       'API': f'https://api-ropsten.etherscan.io/api?module=contract&action=getabi&address={CONTRACT_ADDRESS}'},
          'Rinkeby':  {'ID': 4,
                       'API': f'https://api-rinkeby.etherscan.io/api?module=contract&action=getabi&address={CONTRACT_ADDRESS}'},
          'Kovan':    {'ID': 42,
                       'API': f'https://api-kovan.etherscan.io/api?module=contract&action=getabi&address={CONTRACT_ADDRESS}'},
          'Polygon':  {'ID': 137,
                       'API': f'https://api.polygonscan.com/api?module=contract&action=getabi&address={CONTRACT_ADDRESS}'},
          'Mumbai':   {'ID': 80001,
                       'API': f'https://api-testnet.polygonscan.com/api?module=contract&action=getabi&address={CONTRACT_ADDRESS}'}
          }

CHAIN_ID = CHAINS[CHAIN_NAME]['ID']

CONTRACT_ABI = get(CHAINS[CHAIN_NAME]['API'], timeout=20).json()['result']

if CONTRACT_ABI == 'Contract source code not verified':
    raise Exception(f'Contract source code not verified ({CHAINS[CHAIN_NAME]["API"]})')

if not any(d.get('name') == MINT_FUNCTION_NAME for d in json.loads(CONTRACT_ABI)):
    raise Exception(f'Function "{MINT_FUNCTION_NAME}" not found in CONTRACT_ABI')

if LOGGING is True:
    LOG_FILENAME = f'logs/log_{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}.txt'  # or time.gmttime()
    file_handler = logging.FileHandler(filename=LOG_FILENAME, delay=True)
    logging.basicConfig(level=logging.INFO,  # DEBUG is the lowest - the most information
                        handlers=[file_handler],
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        datefmt='%Y-%m-%d %H:%M:%S')
    # logging.Formatter.converter = time.gmtime  # set to make logs timestamps in gmt (UTC+0)
    logger = logging.getLogger(__name__)
else:
    logger = None

parser = argparse.ArgumentParser(allow_abbrev=False,
                                 description='This program allows you to mint NFTs in a batch from single or multiple addresses. ')
parser._optionals.title = "Configure by editing settings.json and secrets.json.\n"\
                          "Run with one of the following command-line arguments"

parser.epilog = 'Example: python minter.py -multi'

mut_ex_group = parser.add_mutually_exclusive_group()
mut_ex_group.add_argument("-single", action='store_true', default=False, required=False,
                          help='- Single mode - uses master account to mint')
mut_ex_group.add_argument("-multi", action='store_true', default=False, required=False,
                          help='- Multi mode - uses master account to derive more accounts and mint using them')
mut_ex_group.add_argument("-newacc", action='store_true', default=False, required=False,
                          help='- New account mode - generates a new account, displays keys and quits the program')
