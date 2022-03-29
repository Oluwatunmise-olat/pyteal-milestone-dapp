import sys
import time
from pyteal import TealCompileError, TealInputError, TealTypeError, TealInternalError
from utils.services import WebService, AccountService, TransactionService


class Interface:

    @staticmethod
    def create_call():
        pass

    @staticmethod
    def set_up_call():
        pass

    @staticmethod
    def refund_call():
        pass

    @staticmethod
    def submit_call():
        pass

    @staticmethod
    def accept_call():
        pass

    @staticmethod
    def withdraw_call():
        pass

    @staticmethod
    def decline_call():
        pass


def main():
    try:
        print("======================")
        print("making deployment call ...")
        print("======================")

        # deploy the smart contract
        application_id = Interface.create_call()

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

        set_up_response = Interface.set_up_call()

        print(f"Smart Contract SetUp response {set_up_response}")

        # wait for some time
        time.sleep(15)

        # submit milestone
        print("======================")
        print("making submit call ...")
        print("======================")

        submit_response = Interface.submit_call()
        print(f"Smart Contract Submit response {submit_response}")

        time.sleep(15)

        # accept call
        print("======================")
        print("making accept call ...")
        print("======================")

        accept_response = Interface.accept_call()
        print(f"Smart Contract Accept response {accept_response}")



    except Exception as e:
        exc_type, value, traceback = sys.exc_info()
        # assert exc_type.__name__ == 'NameError'
        print(e.__class__.__name__, exc_type, value, traceback)

def delete_app():
    print("======================")
    print("making delete call ...")
    print("======================")


    del_response = Interface.delete_app()
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