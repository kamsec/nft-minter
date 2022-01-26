"""File with tests.

WARNING - tests use settings.json and secrets.json files and work with ExampleContract.
To run them against your contract you have to treat this as an example and adjust them manually.
"""

import unittest

from src.accounts import get_master_account, get_derived_accounts, display_accounts
from src.splitter import send_one_to_many, send_many_to_one, send_many_to_many
from src.interactions import contract_read, contract_write, contract_write_from_one
from src.utils import estimate_single_mint_fee, estimate_multi_mint_fees
from settings import w3, logger, LOGGING, MINT_PRICE


class TestMinter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestMinter, cls).setUpClass()
        # this way it runs only once
        if LOGGING == True:
            logger.info('[Test Mode]')

    def test_accounts_new(self):
        master_account = get_master_account(default=False)
        self.assertEqual(master_account.privateKey.hex()[:2], '0x')

    # @unittest.skip('Skipped, takes ~30 seconds')
    def test_splitter_split_mix_send_back(self):
        split_amount = int(MINT_PRICE * 1.2 * 10 ** 18)  # not estimating fees here, just * 1.2 instead
        master_account = get_master_account(default=True)
        accounts = get_derived_accounts(master_account, number_of_accounts=6)
        self.assertEqual(len(accounts), 6)
        self.assertGreaterEqual(master_account.get_balance(), len(accounts) * split_amount)

        accounts_part_1 = accounts[:int(len(accounts) / 2)]
        accounts_part_2 = accounts[int(len(accounts) / 2):]
        display_accounts([master_account] + accounts, balances=True)
        self.assertEqual(accounts_part_1[2].get_balance(), 0)

        send_one_to_many(master_account, accounts_part_1, split_amount)
        self.assertEqual(accounts_part_1[2].get_balance(), split_amount)
        master_balance_after_split = master_account.get_balance()

        send_many_to_many(accounts_part_1, accounts_part_2)
        self.assertEqual(accounts_part_1[2].get_balance(), 0)
        self.assertGreater(accounts_part_2[2].get_balance(), 0)

        send_many_to_one(accounts_part_2, master_account)
        self.assertEqual(accounts_part_2[2].get_balance(), 0)
        self.assertGreater(master_account.get_balance(), master_balance_after_split)

    def test_interactions_read_write(self):
        master_account = get_master_account(default=True)
        mint_price = contract_read('claimPrice', None)
        last_tx_hash = contract_write(master_account, 'mint', None, mint_price)
        receipt = w3.eth.wait_for_transaction_receipt(last_tx_hash)
        self.assertEqual(receipt['status'], 1)

    def test_interactions_write_from_one(self):
        master_account = get_master_account(default=True)
        old_nonce = master_account.get_nonce()
        number_of_mints = 3
        contract_write_from_one(master_account, 'mint', None, number_of_mints, amount=w3.toWei(MINT_PRICE, 'ether'))
        self.assertEqual(old_nonce + number_of_mints, master_account.get_nonce())

    def test_utils_estimate_single(self):
        estimated_mint_fee = estimate_single_mint_fee()
        self.assertGreater(estimated_mint_fee, 0)

    def test_utils_estimate_multi(self):
        total_fees = estimate_multi_mint_fees()
        self.assertGreater(total_fees, 0)


if __name__ == '__main__':
    unittest.main()
