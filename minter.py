"""
======================= NFT-MINTER =======================
usage: minter.py [-h] [-single | -multi | -newacc]

This program allows you to mint NFTs in a batch from single or multiple addresses.

Configure by editing settings.json and secrets.json.
Run with one of the following command-line arguments:
  -h, --help  show this help message and exit
  -single     - Single mode - uses master account to mint
  -multi      - Multi mode - uses master account to derive more accounts and mint using them
  -newacc     - New account mode - generates a new account, displays keys and quits the program

Example: python minter.py -multi
"""

from src.accounts import get_master_account, get_derived_accounts, display_accounts
from src.splitter import send_many_to_many, send_one_to_many, send_many_to_one
from src.interactions import contract_write, contract_write_from_one
from src.utils import estimate_single_mint_fee, estimate_multi_mint_fees
from settings import w3, MINT_FUNCTION_NAME, MINT_PRICE, NUMBER_OF_MINTS, EXTRA_MIXING_LAYERS,\
    LOGGING, CONTRACT_ADDRESS, CHAIN_NAME, SEND_BACK, FEES_MULT_FACTOR, logger, parser


def single_account_mint(master_account):
    """Mints the NFT of smart contract defined in settings.py from single account.

    EXTRA_MIXING_LAYERS and SEND_BACK don't have any effect here.
    """
    contract_write_from_one(master_account, MINT_FUNCTION_NAME, None, NUMBER_OF_MINTS, w3.toWei(MINT_PRICE, 'ether'))
    display_accounts([master_account], balances=True)


def multi_accounts_mint(master_account, total_fees):
    """Mints the NFT of smart contract defined in settings.py from multiple accounts.
    """

    total_accounts_num = NUMBER_OF_MINTS + NUMBER_OF_MINTS * EXTRA_MIXING_LAYERS
    accounts = get_derived_accounts(master_account, number_of_accounts=total_accounts_num)
    display_accounts([master_account] + accounts, balances=True, secrets=True)

    accounts_layers = []
    if EXTRA_MIXING_LAYERS > 0:
        for i in range(EXTRA_MIXING_LAYERS + 1):
            accounts_layers.append(accounts[i * NUMBER_OF_MINTS: i * NUMBER_OF_MINTS + NUMBER_OF_MINTS])
    else:
        accounts_layers.append(accounts)

    send_one_to_many(master_account, accounts_layers[0], int(w3.toWei(MINT_PRICE, 'ether') + total_fees))
    display_accounts([master_account] + accounts_layers[0], balances=True)

    if EXTRA_MIXING_LAYERS > 0:
        for i in range(EXTRA_MIXING_LAYERS):
            send_many_to_many(accounts_layers[i], accounts_layers[i + 1])
            display_accounts(accounts_layers[i] + accounts_layers[i + 1], balances=True)

    for account in accounts_layers[-1]:
        last_tx_hash = contract_write(account, MINT_FUNCTION_NAME, None, w3.toWei(MINT_PRICE, 'ether'))

    w3.eth.wait_for_transaction_receipt(last_tx_hash, timeout=10)
    display_accounts([master_account] + accounts_layers[-1], balances=True)

    if SEND_BACK == True:
        send_many_to_one(accounts_layers[-1], master_account)
        display_accounts([master_account] + accounts_layers[-1], balances=True)


if __name__ == '__main__':
    args = vars(parser.parse_args())
    if args['newacc'] == True:
        # default=False in get_master_account also logs and prints the private key
        master_account = get_master_account(default=False)
        exit(0)
    elif args['single'] == True:
        single_mint_fee = estimate_single_mint_fee()
        total_fees = single_mint_fee * NUMBER_OF_MINTS
        required_balance = w3.toWei(MINT_PRICE, 'ether') * NUMBER_OF_MINTS + total_fees
    elif args['multi'] == True:
        total_fees = estimate_multi_mint_fees() * FEES_MULT_FACTOR
        required_balance = w3.toWei(MINT_PRICE, 'ether') * NUMBER_OF_MINTS + total_fees
    else:
        parser.print_help()
        exit(0)

    master_account = get_master_account(default=True)
    master_account_balance = master_account.get_balance()
    print('======================= NFT-MINTER =======================')
    print(f'[{"Single" if args["single"] == True else "Multi"} mode]')
    print('Settings:')
    print(f'- CHAIN_NAME: {CHAIN_NAME}')
    print(f'- CONTRACT_ADDRESS: {CONTRACT_ADDRESS}')
    print(f'- MINT_FUNCTION_NAME: {MINT_FUNCTION_NAME}')
    print(f'- MINT_PRICE: {MINT_PRICE}')
    print(f'- NUMBER_OF_MINTS: {NUMBER_OF_MINTS}')
    print(f'- EXTRA_MIXING_LAYERS: {EXTRA_MIXING_LAYERS}') if args['multi'] == True else None
    print(f'- SEND_BACK: {SEND_BACK}') if args['multi'] == True else None
    print(f'- LOGGING: {LOGGING}')
    print(f'Using master_account {master_account.address} | balance: {w3.fromWei(master_account_balance, "ether")}')
    print(f'Estimated required balance: {w3.fromWei(required_balance, "ether")}')
    print(f'Estimated total transaction fees, not including mint prices: {w3.fromWei(total_fees, "ether")}')
    if master_account_balance < required_balance:
        raise Exception(f'Too low balance on master_acount. Balance: {master_account.get_balance()}'
                        f'Estimated required balance: {required_balance}')

    if input('Run? Enter y for yes ') in ['y', 'Y']:
        print('Running...')
        logger.info('======================= NFT-MINTER =======================')
        logger.info(f'[{"Single" if args["single"] == True else "Multi"} mode]')
        logger.info('Settings:')
        logger.info(f'- CHAIN_NAME: {CHAIN_NAME}')
        logger.info(f'- CONTRACT_ADDRESS: {CONTRACT_ADDRESS}')
        logger.info(f'- MINT_FUNCTION_NAME: {MINT_FUNCTION_NAME}')
        logger.info(f'- MINT_PRICE: {MINT_PRICE}')
        logger.info(f'- NUMBER_OF_MINTS: {NUMBER_OF_MINTS}')
        logger.info(f'- EXTRA_MIXING_LAYERS: {EXTRA_MIXING_LAYERS}') if args['multi'] == True else None
        logger.info(f'- SEND_BACK: {SEND_BACK}') if args['multi'] == True else None
        logger.info(f'- LOGGING: {LOGGING}')
        logger.info(f'Using master_account {master_account.address} | balance: {w3.fromWei(master_account_balance, "ether")}')
        logger.info(f'Estimated required balance: {w3.fromWei(required_balance, "ether")}')
        logger.info(f'Estimated total transaction fees, not including mint prices: {w3.fromWei(total_fees, "ether")}')
        logger.info('Running...')

        if args['single'] == True:
            single_account_mint(master_account)
        elif args['multi'] == True:
            multi_accounts_mint(master_account, total_fees)
    else:
        print('Not executed.')
