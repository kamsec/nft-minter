# NFT-minter

This project allows you to mint NFTs of deployed smart contracts in a batch from single or multiple addresses.
It supports Ethereum and Polygon, including test networks.

### Table of contents:
1. <a href="#1-requirements">Requirements</a>
2. <a href="#2-installation">Installation</a>
3. <a href="#3-usage">Usage</a>
4. <a href="#4-configuration">Configuration</a>
5. <a href="#5-examples">Examples</a>


### 1. Requirements:
- Python 3.8
- <a href="https://web3py.readthedocs.io/en/stable/">web3.py</a> 
- Blockchain API provider key e.g. from <a href="https://infura.io/">Infura</a>, <a href="https://www.alchemy.com/">Alchemy</a> or similar


### 2. Installation

1. `git clone https://github.com/kamsec/nft-minter.git`
2. `cd nft-minter`
2. `pip install -r requirements.txt` \
    (or just `pip install web3==5.25.0`)

### 3. Usage

1. Specify settings in `settings.json` (example values):
    ```json
    {
        "CHAIN_NAME": "Mumbai",
        "CONTRACT_ADDRESS": "0xF83C73a44C4a919aB3DF1B515B470e452032eeF4",
        "MINT_FUNCTION_NAME": "mint",
        "NUMBER_OF_MINTS": 6,
        "MINT_PRICE": 0.1,
        "EXTRA_MIXING_LAYERS": 0,
        "SEND_BACK": true,
        "LOGGING": true
    }
    ```

2. Specify secrets in `secrets.json` (replace `***`):
    ```json
    {
        "PRIVATE_KEY": "0x***",
        "PROVIDER": "***"
    }
    ```

3. Run the program in one of the available modes, e.g.:
    ```
    python minter.py -multi
    ```
    It will display selected settings, estimate transaction fees, and ask if you want to proceed. Enter `y` to run the program or anything else to exit.

### 4. Configuration

Settings (`settings.json`):
- `CHAIN_NAME` - set to one of available chains:\
    `Ethereum`, `Ropsten`, `Rinkeby`, `Kovan`, `Polygon`, `Mumbai`\
     If you need to add other chain, you can modify `CHAINS` dict in `settings.py`
- `CONTRACT_ADDRESS` - the address of smart contract deployed on selected chain, with `verified` source code (available on corresponding blockchain explorer api)
- `MINT_FUNCTION_NAME` - the exact name of the minting function of smart contract to execute
- `NUMBER_OF_MINTS` - the number of times for minting function to be executed.\
In Multi mode this is also the number of accounts derived, each account will execute mint function once
- `MINT_PRICE` - the minimum price of single mint in Ether (or MATIC if we are on Polygon/Mumbai blockchain), not including transaction fee
- `EXTRA_MIXING_LAYERS` - only for `-multi` option - creates additional sets of addresses to mix coins and hide slightly the origin of funds
- `SEND_BACK` - only for `-multi` option - after minting, sends the remaining funds back to the master account
- `LOGGING` - enables printing transactions and logging in `logs/` directory

In `settings.py` you can find additional advanced settings, but normally they don't require adjustments.

Secrets (`secrets.json`):
- `PRIVATE_KEY` - Private key of an address, starting with 0x\
    You can generate new one by running
    ```
    python minter.py -newacc
    ```
- `PROVIDER` - Blockchain API provider key e.g. from <a href="https://infura.io/">Infura</a>, <a href="https://www.alchemy.com/">Alchemy</a> or similar

Modes (command-line arguments):
- `-h` - help page
- `-newacc` - New account mode - generates a new account, displays keys and quits the program
- `-single` - Single mode - initializes master_account from `PRIVATE_KEY` specified in `secrets.json` and calls specified mint function from it  multiple (`NUMBER_OF_MINTS`) times.
- `-multi` - Multi mode - initializes master_account like in Single mode, by hashing the private key derives another `NUMBER_OF_MINTS` accounts, sends funds to them and mints once from every derived account

### 5. Examples
Example runs with different settings and modes can be found in `logs/` directory. 
