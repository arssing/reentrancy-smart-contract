#based on https://github.com/ConsenSys/ethjsonrpc/blob/master/ethjsonrpc/client.py

import requests
import json
from tools import hex_to_dec

GETH_RPC_PORT = 8545
GETH_RPC_HOST = 'localhost'
CONTENT_TYPE = 'application/json'

class JsonRpc(object):

    def __init__(self, host=GETH_RPC_HOST, port=GETH_RPC_PORT):
        self.url = 'http://{}:{}'.format(host, port)
        self.headers = {'Content-type': CONTENT_TYPE}

    def _send(self, method, params, _id=1):
        data = {
            'jsonrpc':'2.0', 
            'method':method, 
            'params':params, 
            'id': _id
        }
        try:
            r = requests.post(self.url, headers=self.headers, data=json.dumps(data))
            response = r.json()
            return response['result']
        except Exception as e:
            raise e

    def getBalance(self, address, tag_block):
        method = 'eth_getBalance'
        params = [address, tag_block]
        balance = hex_to_dec(self._send(method, params))
        return hex_to_dec(self._send(method, params))

if __name__ == '__main__':
    address = '0x7182E366b09ec9CA1E4F4dBe9866C86B6A4Ad1F8'
    tag_block = 'latest'
    connect = JsonRpc()
    print(connect.getBalance(address, tag_block))
    