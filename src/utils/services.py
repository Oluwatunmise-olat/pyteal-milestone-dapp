from algosdk.v2client.algod import AlgodClient
from algosdk import mnemonic, encoding, account, ALGORAND_MIN_TX_FEE
from algosdk.logic import get_application_address
from algosdk.future import transaction
from dotenv import load_dotenv

import os
import base64

load_dotenv()


class WebService:
    deployer_mnemonic = os.environ.get("deployer_mnemonic", None)
    testnet_address = os.environ.get("testnet_address", None)

    if not deployer_mnemonic or not testnet_address:
        raise Exception("Environment variable has to be set")

    @property
    def algod_client(self):
        token = "a" * 64
        return AlgodClient(token, self.testnet_address)

    @property
    def get_deployer_private_key(self):
        return mnemonic.to_private_key(self.deployer_mnemonic)

    @staticmethod
    def address_to_bytes(address):
        return encoding.decode_address(address)

    @staticmethod
    def get_smart_contract_address(contract_id):
        return get_application_address(contract_id)

    @staticmethod
    def get_address_from_pk(pk):
        return account.address_from_private_key(pk)


class AccountService:
    client_mnemonic = os.environ.get("client_mnemonic", None)
    freelancer_mnemonic = os.environ.get("freelancer_mnemonic", None)

    if not client_mnemonic or not freelancer_mnemonic:
        raise Exception("Environment variable has to be set")

    @property
    def get_client_private_key(self):
        return mnemonic.to_private_key(self.client_mnemonic)

    @property
    def get_freelancer_private_key(self):
        return mnemonic.to_private_key(self.freelancer_mnemonic)


class TransactionService:
    algod_client = WebService.algod_client
    deployer_private_key = WebService.get_deployer_private_key
    deployer_address = WebService.get_address_from_pk(deployer_private_key)

    def create_contract(
        self,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
        args
    ):
        on_complete = transaction.OnComplete.NoOpOC.real
        suggested_params = self.algod_client.suggested_params()

        txn = transaction.ApplicationCreateTxn(
            self.deployer_address,
            suggested_params,
            on_complete,
            approval_program,
            clear_program,
            global_schema,
            local_schema,
            args
        )

        signed_txn = txn.sign(self.deployer_private_key)
        txn_id = signed_txn.transaction.get_txid()
        self.algod_client.send_transactions([signed_txn])

        self.wait_for_confirmation(txn_id, 60)

        txn_response = self.algod_client.pending_transaction_info(txn_id)
        application_id = txn_response["application-index"]
        return application_id

    def wait_for_confirmation(self, txn_id, timeout):
        start_round = self.client.status()["last-round"] + 1
        current_round = start_round

        while current_round < start_round + timeout:
            try:
                pending_txn = self.client.pending_transaction_info(txn_id)
            except Exception:
                return
            if pending_txn.get("confirmed-round", 0) > 0:
                return pending_txn
            elif pending_txn["pool-error"]:
                raise Exception(
                    'pool error: {}'.format(pending_txn["pool-error"]))
            self.client.status_after_block(current_round)
            current_round += 1
        raise Exception(
            'pending txn not found in timeout rounds, timeout value = : {}'.format(timeout))

    def set_up_call(self, app_id, app_args, receiver, amount, sender, sender_pk):
        # This is an atomic transaction consisting of two groups of transactions

        app_call_txn = self.no_op_call(
            sender=sender,
            app_id=app_id,
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=app_args,
            sender_pk=sender_pk,
            sign_txn=False,
        )

        payment_call_txn = self.payment_transaction(
            sender=sender, sender_pk=sender_pk, receiver=receiver, amount=amount, sign_txn=False)

        group_id = transaction.calculate_group_id(
            [app_call_txn, payment_call_txn])

        app_call_txn.group = group_id
        payment_call_txn.group = group_id

        app_call_txn_signed = app_call_txn.sign(sender_pk)
        payment_call_txn_signed = payment_call_txn.sign(sender_pk)

        signed_group = [app_call_txn_signed, payment_call_txn_signed]

        txn_id = self.algod_client.send_transactions(signed_group)

        self.wait_for_confirmation(txn_id, 60)

        print(f"Set up application call with transaction_id: {txn_id}")

        return txn_id

    def no_op_call(self, sender, sender_pk, app_id, on_complete, app_args=None, sign_txn=True, accounts=[], fee=0):
        suggested_params = self.algod_client.suggested_params()

        if fee != 0:
            suggested_params.fee = fee * ALGORAND_MIN_TX_FEE
            suggested_params.flat_fee = True

        txn = transaction.ApplicationCallTxn(
            sender=sender,
            sp=suggested_params,
            index=app_id,
            app_args=app_args,
            on_complete=on_complete,
            accounts=accounts
        )
        if sign_txn:
            txn = txn.sign(sender_pk)

        return txn

    def submit_call(self, app_id, sender, sender_pk, args):
        txn = self.no_op_call(
            sender=sender,
            app_id=app_id,
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=args,
            sign_txn=False,
            sender_pk=sender_pk
        )

        signed_txn = txn.sign(sender_pk)
        txn_id = signed_txn.transaction.get_txid()
        self.wait_for_confirmation(txn_id, 60)

        self.algod_client.send_transactions([signed_txn])
        txn_response = self.client.pending_transaction_info(txn_id)

        print(f"Application submit call with transaction resp: {txn_response}")

        return txn_id

    def accept_call(self, sender, sender_pk, app_id, args, accounts):
        txn = self.no_op_call(
            fee=2,
            sender=sender,
            app_id=app_id,
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=args,
            sign_txn=False,
            accounts=accounts,
            sender_pk=sender_pk

        )

        signed_txn = txn.sign(sender_pk)
        txn_id = signed_txn.transaction.get_txid()
        self.wait_for_confirmation(txn_id, 60)

        self.algod_client.send_transactions([signed_txn])
        txn_response = self.algod_client.pending_transaction_info(txn_id)

        print(f"Application accept call with transaction resp: {txn_response}")

        return txn_id

    def refund_call(self, sender, app_id, args, sender_pk):
        txn = self.no_op_call(
            sender=sender,
            app_id=app_id,
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=args,
            sign_txn=False,
            sender_pk=sender_pk
        )

        signed_txn = txn.sign(sender_pk)
        txn_id = signed_txn.transaction.get_txid()
        self.wait_for_confirmation(txn_id, 60)

        self.algod_client.send_transactions([signed_txn])

        txn_response = self.algod_client.pending_transaction_info(txn_id)

        print(f"Application refund call with transaction resp: {txn_response}")

        return txn_id

    def withdraw_call(self, app_id, sender, sender_pk, args, accounts=[]):
        txn = self.no_op_call(
            sender=sender,
            app_id=app_id,
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=args,
            sign_txn=False,
            accounts=accounts,
            sender_pk=sender_pk
        )

        signed_txn = txn.sign(sender_pk)
        txn_id = signed_txn.transaction.get_txid()
        self.wait_for_confirmation(txn_id, 60)

        self.algod_client.send_transactions([signed_txn])
        txn_response = self.algod_client.pending_transaction_info(txn_id)

        print(
            f"Application withdarw call with transaction resp: {txn_response}")

        return txn_id

    def decline_call(self, sender, sender_pk, app_id, args, accounts):
        txn = self.no_op_call(
            sender=sender,
            app_id=app_id,
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=args,
            sign_txn=False,
            accounts=accounts,
            sender_pk=sender_pk

        )

        signed_txn = txn.sign(sender_pk)
        txn_id = signed_txn.transaction.get_txid()
        self.wait_for_confirmation(txn_id, 60)

        self.algod_client.send_transactions([signed_txn])
        txn_response = self.algod_client.pending_transaction_info(txn_id)

        print(
            f"Application decline call with transaction resp: {txn_response}")

        return txn_id

    def delete_call(self, app_id: int) -> int:
        suggested_params = self.algod_client.suggested_params()
        suggested_params.fee = 2 * ALGORAND_MIN_TX_FEE
        suggested_params.flat_fee = True

        txn = transaction.ApplicationDeleteTxn(
            sender=self.deployer_address,
            index=app_id,
            sp=suggested_params
        )

        # here the deployer is deleting the application
        signed_txn = txn.sign(self.deployer_private_key)

        txn_id = signed_txn.transaction.get_txid()
        self.wait_for_confirmation(txn_id, 60)

        self.client.send_transactions([signed_txn])

        txn_response = self.client.pending_transaction_info(txn_id)

        print(f"Application Deleted with transaction resp: {txn_response}")

        return txn_id

    def payment_transaction(self, sender, sender_pk, receiver, amount, sign_txn=True):
        suggested_params = self.algod_client.suggested_params()

        txn = transaction.PaymentTxn(
            sender=sender,
            sp=suggested_params,
            receiver=receiver,
            amt=amount
        )

        if sign_txn:
            txn = txn.sign(sender_pk)

        return txn

    def __format_state(self, state):
        formatted = {}
        for item in state:
            key = item["key"]
            value = item["value"]
            formatted_key = base64.b64decode(key).decode("utf-8")

            if value["type"] == 1:
                if formatted_key == 'voted':
                    formatted_value = base64.b64decode(
                        value['bytes']).decode('utf-8')
                else:
                    formatted_value = value['bytes']
                formatted[formatted_key] = formatted_value
            else:
                formatted[formatted_key] = value['uint']

        return formatted

    def read_global_state(self, app_id: int):
        app = self.algod_client.application_info(app_id)
        global_state = app["params"]["global-state"] if "global-state" in app["params"] else []
        return self.__format_state(global_state)

transaction_instance = TransactionService()