from email.header import decode_header
from algosdk.v2client.algod import AlgodClient
from algosdk import mnemonic, encoding, account
from algosdk.logic import get_application_address
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

    @staticmethod
    def format_data(data):
        formatted = {}
        for item in data:
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
