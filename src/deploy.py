import sys
import time
from pyteal import TealCompileError, TealInputError, TealTypeError, TealInternalError
from utils.services import WebService, AccountService, transaction_instance
from utils.time import get_current_timestamp, get_future_timestamp_in_days, get_future_timestamp_in_secs
from contract import approval_program, clear_program
from deploy_helpers import contract_schema, compile_to_bytes

# Addresses

client_address = WebService.get_address_from_pk(
    AccountService.get_client_private_key())
freelancer_address = WebService.get_address_from_pk(
    AccountService.get_freelancer_private_key())

# Private Keys
client_pk = AccountService.get_client_private_key()
freelancer_pk = AccountService.get_freelancer_private_key()


class Interface:

    @staticmethod
    def create_call():
        # The spce that should be reserved for storage local (if using local storage) and globally
        global_schema = contract_schema(6, 5)
        local_schema = contract_schema(0, 0)

        algod_client = WebService.algod_client()

        compiled_approval_program = compile_to_bytes(
            client=algod_client, code=approval_program())

        compiled_clear_program = compile_to_bytes(
            client=algod_client, code=clear_program())

        # arguments
        args = [
            WebService.address_to_bytes(client_address),
            WebService.address_to_bytes(freelancer_address),
            1_500_000,  # (15 algo)
        ]

        app_id = transaction_instance.create_contract(
            approval_program=compiled_approval_program,
            clear_program=compiled_clear_program,
            global_schema=global_schema,
            local_schema=local_schema,
            args=args
        )

        # Read global state of contract

        global_state = transaction_instance.read_global_state(app_id)

        print("================================")
        print(" Samrt Contract Global State ...")
        print("=================================")

        print(global_state)

        return app_id

    @staticmethod
    def set_up_call(app_id, sender, sender_pk, receiver, amount):
        args = [
            "set_state",
            int(get_current_timestamp()),  # start milestone timestamp
            # end milestone timestamp (14 days)
            int(get_future_timestamp_in_days(days=14))
        ]

        return transaction_instance.set_up_call(app_id=app_id, app_args=args, receiver=receiver, sender=sender, amount=amount, sender_pk=sender_pk)

    @staticmethod
    def refund_call(sender_pk, sender, app_id, args):
        return transaction_instance.refund_call(sender_pk=sender_pk, sender=sender, app_id=app_id, args=args)

    @staticmethod
    def submit_call(app_id, sender_pk, sender):
        args = [
            "submit",
            "True",
            # timestamp for altimatum (7 days from submission)
            int(get_future_timestamp_in_days(days=7))
        ]
        return transaction_instance.submit_call(app_id=app_id, sender_pk=sender_pk, sender=sender, args=args)

    @staticmethod
    def accept_call(app_id, sender_pk, sender, accounts: list):
        args = ["accept"]
        return transaction_instance.accept_call(app_id=app_id, sender_pk=sender_pk, sender=sender, accounts=accounts, args=args)

    @staticmethod
    def withdraw_call(app_id, sender_pk, sender):
        args = ["withdraw"]
        return transaction_instance. withdraw_call(app_id=app_id, sender=sender, sender_pk=sender_pk, args=args)

    @staticmethod
    def decline_call():
        pass

    @staticmethod
    def delete_call(app_id, accounts):
        return transaction_instance.delete_call(app_id=app_id, accounts=accounts)


def main():
    try:
        print("======================")
        print("making deployment call ...")
        print("======================")

        # deploy the smart contract
        application_id = Interface.create_call()

        print(f"Application id: {application_id}")

        # get the smart contract algorand address
        print("======================")
        print("get smart contract address ...")
        print("======================")

        smart_contract_address = WebService.get_smart_contract_address(
            application_id)

        print(f"Smart Contract Address {smart_contract_address}")

        # set up smart contract
        print("======================")
        print("making set up call ...")
        print("======================")

        set_up_response = Interface.set_up_call(
            receiver=smart_contract_address, app_id=application_id, amount=1_500_000, sender=client_address, sender_pk=client_pk)

        print(f"Smart Contract SetUp response {set_up_response}")

        # wait for some time
        time.sleep(15)

        # submit milestone
        print("======================")
        print("making submit call ...")
        print("======================")

        submit_response = Interface.submit_call(
            app_id=application_id, sender_pk=freelancer_pk, sender=freelancer_address)
        print(f"Smart Contract Submit response {submit_response}")

        time.sleep(15)

        # accept call
        print("======================")
        print("making accept call ...")
        print("======================")

        accept_response = Interface.accept_call(
            app_id=application_id, sender_pk=client_pk, sender=client_address, accounts=[freelancer_address])
        print(f"Smart Contract Accept response {accept_response}")

    except Exception as e:
        print(e)
        exc_type, value, traceback = sys.exc_info()
        # assert exc_type.__name__ == 'NameError'
        print(e.__class__.__name__, exc_type, value, traceback)


def delete_app(app_id, accounts):
    print("======================")
    print("making delete call ...")
    print("======================")

    del_response = Interface.delete_call(app_id, accounts)
    return del_response


""" Error Types
    1. TealInternalError
    2. TealTypeError
    3. TealInputError
    4. TealCompileError
"""

# compile pyteal code to teal
# withdraw case
# refund case
# decline case

if __name__ == '__main__':
    main()

    # delete_app(39, accounts=[client_address])

