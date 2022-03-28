from pyteal import *


def contract_events(
    initialize_contract=Reject(),
    delete_contract=Reject(),
    update_contract=Reject(),
    opt_in_contract=Reject(),
    close_out_contract=Reject(),
    no_op_contract=Reject(),
)-> Expr:

    """ Function Explanation

    Params:
        initialize_contract: This parameter handles the condition for the first call to the smart contract.
        delete_contract: This parameter handles the case of deletion of the smart contract.
        update_contract: This parameter handles the case of an update to the smart contract.
        opt_in_contract: This parameter handles the case of optin to the contract.
        close_out_contract: This parameter handles the case of closing out of the contract.
        no_op_contract: This parameter handles the case of a regular call to the smart contract.

    Returns:
        Array <> : The function returns an array of possible smart contract calls that can be made and handlers for each call. 
    """

    return Cond(
        [Txn.application_id() == Int(0), initialize_contract],
        [Txn.on_completion() == OnComplete.DeleteApplication, delete_contract],
        [Txn.on_completion() == OnComplete.UpdateApplication, update_contract],
        [Txn.on_completion() == OnComplete.OptIn, opt_in_contract],
        [Txn.on_completion() == OnComplete.CloseOut, close_out_contract],
        [Txn.on_completion() == OnComplete.NoOp, no_op_contract],
    )

def application(pyteal: Expr):
    # This function compiles all our pyteal code to the hightest version of teal

    # Mode.Application means we a calling the contract has an application and not a smart signature
    
    return compileTeal(pyteal, mode=Mode.Application, version=MAX_TEAL_VERSION)
