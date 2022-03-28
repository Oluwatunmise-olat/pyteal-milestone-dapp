from pyteal import *
from contract_helpers import contract_events

def approval_program():

    # App Global States

    def initialize_app():
        pass

    def delete_app():
        pass

    return contract_events(
        delete_contract=delete_app(),
        initialize_contract=initialize_app(),
        no_op_contract=Seq([

        ])
    )

def clear_program():
    pass