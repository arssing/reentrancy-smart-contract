from tools import *
from config import GETH_PATH_TO_IPC
import socket
import json
import re
from eth_abi import encode_single, is_encodable
from exceptions import TransactionZeroStatus

DEFAULT_BLOCK = 'latest'

class IpcConnect(object):

    def __init__(self, path=GETH_PATH_TO_IPC):
        self.s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.s.connect(GETH_PATH_TO_IPC)

    def __del__(self):
        self.s.close()
    
    def _send(self, method, params=[], _id=1):
        data = {
            'jsonrpc':'2.0', 
            'method':method, 
            'params':params, 
            'id': _id
        }

        data = json.dumps(data)
        try:
            self.s.send(data.encode())
            response = json.loads(self.s.recv(2048).decode())
            return response['result']
        except KeyError:
            return response
        except Exception as e:
            raise e
    
    def newAccount(self, passphrase):
        method = 'personal_newAccount'
        new_account = self._send(method, [passphrase])
        return new_account

    def getBalance(self, address, tag_block=DEFAULT_BLOCK):
        method = 'eth_getBalance'
        balance = self._send(method, [address, tag_block])
        return hex_to_dec(balance)

    def get_balance(self, address, tag_block=DEFAULT_BLOCK):
        method = 'eth_getBalance'
        balance = self._send(method, [address, tag_block])
        return hex_to_dec(balance)
    
    def list_accounts(self):
        method = 'personal_listAccounts'
        list_acc = self._send(method, [])
        return list_acc
    
    def sendTransaction(self, frm, to=None, value=None, data=None, gas=None, gas_price=None):
        method = 'eth_sendTransaction'
        params = {'from':frm}
        if to is not None:
            params['to'] = to
        if value is not None:
            params['value'] = hex(value)
        if data is not None:
            params['data'] = data
        if gas is not None:
            params['gas'] = hex(gas)
        if gas_price is not None:
            params['gasPrice'] = hex(gas_price)
        tx_hash = self._send(method, [params])
        return tx_hash
    
    def eth_call(self, to, frm=None, data=None, value=None, gas=None, gas_price=None, default_block=DEFAULT_BLOCK):
        method = 'eth_call'
        params = {'to': to}
        if frm is not None:
            params['from'] = frm
        if data is not None:
            params['data'] = data
        if value is not None:
            params['value'] = hex(value)
        if gas is not None:
            params['gas'] = hex(gas)
        if gas_price is not None:
            params['gasPrice'] = hex(gas_price)
        return self._send(method, [params, default_block])

    def create_contract(self, frm, code, types=None, args=None):
        if types is not None and args is not None:
            code += encode_abi(types, args)
        return self.sendTransaction(frm, data=code)

    def getTransactionReceipt(self, tx_hash):
        method = 'eth_getTransactionReceipt'
        info_tx = self._send(method, [tx_hash])
        return info_tx

    def get_contract_address(self, tx):
        self.wait_tx(tx)
        receipt = self.getTransactionReceipt(tx)
        return receipt['contractAddress']

    def sha3(self, data):
        data = '0x'+(str(data).encode()).hex()
        return self._send('web3_sha3',[data])
    
    def get_selector_hash(self, name):
        return self.sha3(name)[:10]
    
    def coinbase(self):
        return self._send('eth_coinbase')

    def wait_tx(self, tx_hash):
        receipt = None
        while receipt == None:
            receipt = self.getTransactionReceipt(tx_hash)
        if receipt["status"] == "0x0":
            raise TransactionZeroStatus
        return receipt

    def get_call_data(self, func: str, data_to_call=[]):
        selector = self.get_selector_hash(func)
        if data_to_call == []:
            return selector
        payload = re.findall(r"\(.*\)", func)[0]
        calldata = encode_abi(payload, data_to_call)
        return selector+calldata
    
    def send_ether(self, to, value, gas=None, gas_price=None):
        tx = self.sendTransaction(
            self.coinbase(), 
            to=to, 
            value=eth_to_wei(value),
            gas=gas,
            gas_price=gas_price
        )
        tx_info = self.wait_tx(tx)
        return tx_info['blockHash']