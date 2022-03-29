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

    # App Global Schemas (byteslice | uint64)
    # byteslice [the deployer of the contract address]
    global_creator = Bytes("global_creator")
    # unint64 [time the milestone is to start]
    global_start_date = Bytes("start_date")
    # unint64 [time the milestone is to end]
    global_end_date = Bytes("end_date")
    # unint64 [amont to be paid in algo for milestone]
    global_amount = Bytes("amount")
    # unint64 [time the client has to review submission and accept or decline after freelancer submission]
    global_altimatum = Bytes("altimatum")

    global_client = Bytes("client")  # byteslice
    global_freelancer = Bytes("freelancer")  # byteslice

    # unit64 [when the freelancer submitted the work for review]
    global_submission_date = Bytes("submission_date")
    global_submitted = Bytes("submit")  # byteslice
    global_sent = Bytes("sent")  # byteslice [status of payment]

    def initialize_app():
        # This fucntion sets the initialize contract states.
        # It handles the deployment phase of the contract.

        return Seq([
            # making sure we are sending 3 argumnets with the cntract call
            Assert(Txn.application_args.length() == Int(3)),

            # set the states
            # we set the global contract deploer to the sender of the transaction
            App.globalPut(global_creator, Txn.sender()),
            # we set the client address
            App.globalPut(global_client, Txn.application_args[0]),
            # we set the freelancers address
            App.globalPut(global_freelancer, Txn.application_args[1]),
            # we set the milestone amount in algo
            App.globalPut(global_amount, Txn.amount,
                          Btoi(Txn.application_args[2])),
            App.globalPut(global_altimatum, Int(0)),  # set the altimatum to 0
            # the paymnet hasn't been made
            App.globalPut(global_sent, Bytes("False")),
            # No submission date has been set
            App.globalPut(global_submission_date, Int(0)),
            # milestone hasn't been submitted yet.
            App.globalPut(global_submitted, Bytes("False")),
            # set the start date to Int(0)
            App.globalPut(global_start_date, Int(0)),
            # set the end date to Int(0)
            App.globalPut(global_end_date, Int(0)),
            Approve()
        ])

    def delete_app():
        # can only be called by client and creator of contract
        # the client can only delete the app if the milestone has not stared or it has ended
        # send all algo the client address
        # set all global variables to initial state
        pass

    @Subroutine(TealType.none)
    def set_state():
        # This fucntion sets the parameters to get the contract started
        # It is a grouped transaction with the second being a payment transaction to the smart contract escrow address.

        return Seq([
            # Run some checks
            Assert(
                And(
                    # assert it a group transaction with a group size of 2
                    Global.group_size() == Int(2),
                    Txn.group_index() == Int(0),
                    # assert it is the client making this call
                    Txn.sender() == App.globalGet(global_client),
                    # assert the length of the argumnets passed is 3
                    Txn.application_args.length() == Int(3),

                    # assert the second transaction in the group is a payment transaction
                    Gtxn[1].type_enum() == TxnType.Payment,
                    # assert the right amount is sent
                    Gtxn[1].amount() == App.globalGet(global_amount),
                    # assert the payment is to the smart contract escrow address
                    Gtxn[1].receiver() == Global.current_application_address(),
                    Gtxn[1].close_to_receiver() == Global.zero_address(),
                    App.globalGet(global_start_date) == App.globalGet(
                        global_end_date) == Int(0),  # assert the contract hasn't started
                )
            ),

            #  set the start and end dates
            App.globalPut(global_start_date, Btoi(Txn.application_args[1])),
            App.globalPut(global_end_date, Btoi(Txn.application_args[2])),
            Approve()
        ])

    @Subroutine(TealType.none)
    def submit():
        return Seq([
            Assert(
                And(
                    # the transaction sender must be the freelancer associated with the contract
                    Txn.sender() == App.globalGet(global_freelancer),
                    # assert that the milestone has started and been set
                    App.globalGet(global_start_date) != Int(0),
                    App.globalGet(global_end_date) != Int(0),
                    # assert that the submission has not beem previously made
                    App.globalGet(global_submitted) == Bytes("False"),
                    # assert that the payment hasn't beem made
                    App.globalGet(global_sent) == Bytes("False"),
                    # assert that the second argumnet equals True to set submission status
                    Txn.application_args[1] == Bytes("True"),
                    Txn.application_args.length() == Int(2),

                    # assert the start date is less than current date time
                    App.globalGet(global_start_date <
                                  Global.latest_timestamp()),
                    # assert that the enddate is greater than the current date time
                    App.globalGet(global_end_date >=
                                  Global.latest_timestamp()),

                )
            ),
            # we set the submission status to true
            App.globalPut(global_submitted, Txn.application_args[1]),
            # we set the submission date
            App.globalPut(global_submission_date, Global.latest_timestamp()),
            # check here -->
            # we set the altimatum date (7 days)
            App.globalPut(global_altimatum,
                          Global.latest_timestamp() + Int(7)),
            Approve()
        ])

    @Subroutine(TealType.none)
    def accept():
        # case of client accpeting the milestone
        return Seq([
            Assert(
                And(
                    App.globalGet(global_submitted) == Bytes(
                        "True"),  # the freelancer must have submitted
                    # assert the call is made by the client
                    Txn.sender() == App.globalGet(global_client),
                    # assert that the payment hasn't been previously made
                    App.globalGet(global_sent) == Bytes("False"),
                    Txn.application_args.length() == Int(1),
                    Txn.group_index() == Int(0),
                    Txn.accounts[1] == App.globalGet(global_client),
                )
            ),

            Assert(
                # two because the first call to this handler and the second call which is a paymant call
                Txn.fee() >= Global.min_txn_fee() * Int(2)
            ),

            sendPayment(Txn.accounts[1], App.globalGet(
                global_amount), Txn.accounts[1]),  # send payments to freelancer
            # we set the status of payment to true
            App.globalPut(global_sent, Bytes("True")),
            Approve()
        ])

    @Subroutine(TealType.none)
    def decline():
        # work must have been submitted
        # payment should not have been made
        # 60% of amount is sent to client
        # 40% of amount is sent to freelancer
        pass

    @Subroutine(TealType.none)
    def refund():
        # client request for refund when
        # 1. work has not began
        # 2. work has eneded and freelancer didn't submit

        return Seq([
            Assert(
                And(
                    Txn.sender() == App.globalGet(global_client),
                    Txn.application_args.length() == Int(1),
                    App.globalGet(global_sent) == Bytes("False"),
                )
            ),
            Assert(
                Or(
                    App.globalGet(
                        global_start_date) > Global.latest_timestamp(),
                    And(
                        App.globalGet(
                            global_end_date) < Global.latest_timestamp(),
                        App.globalGet(global_submitted) == Bytes("False")
                    )
                )
            ),
            Assert(
                # two because the first call to this handler and the second call which is a paymant call
                Txn.fee() >= Global.min_txn_fee() * Int(2)

            ),
            sendPayment(Txn.sender(), App.globalGet(
                global_amount), Txn.sender()),
            App.globalPut(global_sent, Bytes("True")),
            Approve()
        ])

    @Subroutine(TealType.none)
    def withdraw():
        # case client hasn't accepted or declined submission
        # altimatum time must have beem exceeded
        # freelancer must have submitted work
        # payment hasn't been made by client
        return Seq([
            Assert(
                And(
                    Txn.sender() == App.globalGet(global_freelancer),
                    App.globalGet(global_submitted) == Bytes("True"),
                    # assert that the payment hasn't be made
                    App.globalGet(global_sent) == Bytes("False"),
                    Txn.application_args.length() == Int(1),
                    Txn.group_index() == Int(0),
                    App.globalGet(global_altimatum) != Int(0),
                    Global.latest_timestamp() >= App.globalGet(global_altimatum)
                )
            ),
            Assert(
                # two because the first call to this handler and the second call which is a paymant call
                Txn.fee() >= Global.min_txn_fee() * Int(2)

            ),
            sendPayment(Txn.sender(), App.globalGet(
                global_amount), Txn.sender()),
            App.globalPut(global_sent, Bytes("True")),
            Approve()
        ])

    @Subroutine(TealType.none)
    # This demonstrates just a basic use case of inner transactions.
    # Accounts on algorand must maintain a minimum balace of 100,000 microAlgos
    def sendPayment(receiver, amount_in_algo, close_to_receiver):
        return Seq([
            InnerTxnBuilder.Begin(),
            InnerTxnBuilder.SetFields({
                # specifies the type of transacion been made (paymnet, application_call, etc)
                TxnField.type_enum: TxnType.Payment,
                # we subtract the cost for making the call (gas fee) and the minimum amount of algo that must be in an algorand account
                TxnField.amount: amount_in_algo - (Global.min_txn_fee() + Global.min_balance()),
                # The sender of this payment is the smart contract escrow address
                TxnField.sender: Global.current_application_address(),
                TxnField.receiver: receiver,  # Funds receiver
                # address to send the remaining algo in the escrow account to,
                TxnField.close_remainder_to: close_to_receiver,
                TxnField.fee: Int(0)
            }),
            InnerTxnBuilder.Submit()
        ])

    return contract_events(
        delete_contract=delete_app(),
        initialize_contract=initialize_app(),
        no_op_contract=Seq([
            Cond(
                [Txn.application_args[0] == op_set_state, set_state()],
                [Txn.application_args[0] == op_submit, submit()],
                [Txn.application_args[0] == op_accept, accept()],
                [Txn.application_args[0] == op_decline, decline()],
                [Txn.application_args[0] == op_refund, refund()]
                [Txn.application_args[0] == op_withdraw, withdraw()],
            ),
            Reject()
        ])
    )


def clear_program():
    return Approve()
