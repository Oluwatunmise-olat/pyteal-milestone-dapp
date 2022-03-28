from pyteal import *
from contract_helpers import contract_events

def approval_program():

    # App Global States

    op_set_state = Bytes("set_state")
    op_accept = Bytes("accept")
    op_decline = Bytes("decline")
    op_submit = Bytes("submit")
    op_withdraw = Bytes("withdraw")
    op_refund = Bytes("refund")

    def initialize_app():
        pass

    def delete_app():
        pass

    @Subroutine(TealType.none)
    def set_state():
        pass

    @Subroutine(TealType.none)
    def accept():
        pass

    @Subroutine(TealType.none)
    def submit():
        pass

    @Subroutine()
    def decline():
        pass

    @Subroutine(TealType.none)
    def refund():
        pass

    @Subroutine(TealType.none)
    def withdraw():
        pass

    return contract_events(
        delete_contract=delete_app(),
        initialize_contract=initialize_app(),
        no_op_contract=Seq([
            Cond(
                [Txn.application_args[0] == op_set_state, set_state()],
                [Txn.application_args[0] == op_accept, accept()],
                [Txn.application_args[0] == op_submit, submit()],
                [Txn.application_args[0] == op_decline, decline()],
                [Txn.application_args[0] == op_refund, refund()]
                [Txn.application_args[0] == op_withdraw, withdraw()],
            ),
            Reject()
        ])
    )

def clear_program():
    pass