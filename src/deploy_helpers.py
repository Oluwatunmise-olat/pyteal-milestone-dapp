from algosdk.future import transaction
from algosdk.v2client.algod import AlgodClient
import base64
from pyteal import *


def contract_schema(byteslice, uint):
    # This fuction is used to set the global and local contract schemas to be allocated
    return transaction.StateSchema(uint, byteslice)

def compile_to_bytes(client: AlgodClient, code):
    # This function helps convert our teal code to bytes
    compile_response = client.compile(code)
    return base64.b64encode(compile_response['result'])
