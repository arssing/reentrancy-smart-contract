from typing import TextIO
from tools import *
import socket
import json
from eth_abi import encode_single, is_encodable


GETH_PATH_TO_IPC = '/home/arss/8sem/kyrs/ethdata/geth.ipc'
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

        data = str(data).replace("'", '"')
        
        try:
            self.s.send(data.encode())
            response = json.loads(self.s.recv(1024).decode())
            return response['result']
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
    
    def listAccounts(self):
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
    
    def eth_call(self, to, frm=None, data=None, value=None, gas=None, gasPrice=None, default_block=DEFAULT_BLOCK):
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
        if gasPrice is not None:
            params['gasPrice'] = hex(gasPrice)
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
        receipt = self.getTransactionReceipt(tx)
        return receipt['contractAddress']

    def sha3(self, data):
        data = '0x'+(str(data).encode()).hex()
        return self._send('web3_sha3',[data])
    
    def get_selector_hash(self, name):
        return self.sha3(name)[:10]
    
    def coinbase(self):
        return self._send('eth_coinbase')

        


if __name__ == '__main__':
    #0x7182e366b09ec9ca1e4f4dbe9866c86b6a4ad1f8
    #a = decode_single('(bytes1,bytes1)', b'a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    #print(a)
    #connect = IpcConnect()
    #print(encode_abi('(uint,uint32[],bytes10,bytes)', (0x123, [0x456, 0x789], b'1234567890', b'Hello, world!')))
    #print(connect.listAccounts())
    #print(connect.listAccounts())
    '''
    addr = connect.get_contract_address("0x48397ffbfc53ab019c8b09397d10f5c5ae1d049db4e23c67d20b43b0bcb5cb83")
    sel = connect.get_selector('set(uint256)')
    newval = dec_to_uint256(445)
    print(connect.sendTransaction("0x7182e366b09ec9ca1e4f4dbe9866c86b6a4ad1f8", addr, data=sel+newval))
    sel2 = connect.get_selector('get()')
    ret = connect.eth_call(addr, data=sel2)
    print(ret)
    '''
    '''
    method = 'get()'
    print(connect.get_selector(method))
    ret = connect.eth_call(addr, data="0x6d4ce63c")
    print(ret)
    '''
    #connect.sendTransaction("0x7182e366b09ec9ca1e4f4dbe9866c86b6a4ad1f8", "0xe977a16b8dd1ba16b59c0d85735920ea7f458af8", eth_to_wei(2))
    #~/8sem/kyrs/src/contracts/SimpleStorage.sol
    '''
    txt = 'set(uint256)'
    text = Web3.sha3(text=txt)
    print(text.hex())
    '''
    bin, abi = get_bin_abi_by_code("~/8sem/kyrs/src/contracts/attack.sol")
    print(abi)
    #print(bin)
    abi = json.loads(abi)
    for fun in abi:
        print(fun)
    '''
    for fun in abi:
        print(fun)
        print(get_selector(fun))
    print(len(abi))
    '''
    #connect.create_contract("0x7182e366b09ec9ca1e4f4dbe9866c86b6a4ad1f8",bin)
    #print(abi)
    '''
0x608060405234801561001057600080fd5b5061012f806100206000396000f3fe6080604052348015600f57600080fd5b506004361060325760003560e01c806360fe47b11460375780636d4ce63c14604f575b600080fd5b604d600480360381019060499190608f565b6069565b005b60556073565b6040516060919060c2565b60405180910390f35b8060008190555050565b60008054905090565b60008135905060898160e5565b92915050565b60006020828403121560a057600080fd5b600060ac84828501607c565b91505092915050565b60bc8160db565b82525050565b600060208201905060d5600083018460b5565b92915050565b6000819050919050565b60ec8160db565b811460f657600080fd5b5056fea2646970667358221220179d8d51d54daf03f82a7cd963a015e6d9faf5a8b20413493551459163a41d6b64736f6c63430008040033
    '''
    '''
    [
        {
            "inputs":[],"name":"get","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"
        },
        {
            "inputs":[
                        {"internalType":"uint256","name":"x","type":"uint256"}
                    ],"name":"set","outputs":[],"stateMutability":"nonpayable","type":"function"
        }
    ]
    '''