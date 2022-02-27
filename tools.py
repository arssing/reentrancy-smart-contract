import subprocess
from eth_abi import encode_single, is_encodable

def hex_to_dec(num):
    return int(num,16)
def wei_to_eth(wai):
    return 1.0 * wai / 10**18
def eth_to_wei(eth):
    return eth * 10**18
def get_bin_abi_by_code(path_to_sol):
    try:
        result = subprocess.Popen("solc --bin --abi "+ path_to_sol, shell=True, stdout=subprocess.PIPE)
    except Exception as e:
        raise e
    out = (result.stdout.read()).decode()
    sp = out.split('\n')
    return '0x'+sp[3], sp[5]
def ast_in_file(path_to_sol, path_to_file):
    try:
        result = subprocess.Popen("solc --ast-json "+ path_to_sol, shell=True, stdout=subprocess.PIPE)
    except Exception as e:
        raise e
    out = (result.stdout.read()).decode()
    with open("ast_out.json", "w") as f:
        f.write(out)
def dec_to_uint256(num):
    num = str(hex(num))[2:]
    num_iter = 64-len(num)
    for i in range(num_iter):
        num = "0" + num
    return num
def encode_abi(types, args):
    '''
    ex: encode_abi('(uint,uint32[],bytes10,bytes)', (0x123, [0x456, 0x789], b'1234567890', b'Hello, world!'))
    '''
    if is_encodable(types, args):
        return encode_single(types, args).hex()
    raise Exception("encode_abi: error")

def get_comp(dic):
    out = ""
    try:
        for c in dic['components']:
            out += get_components(c)
        return out
    except:
        return dic['type']+','
def get_components(dic):
    out = get_comp(dic)
    return out
def get_selector(abi_fun):
    '''
    return name func(type)
    ex: {'inputs': [{'internalType': 'uint32', 'name': 'x', 'type': 'uint32'}, {'internalType': 'bool', 'name': 'y', 'type': 'bool'}], 'name': 'baz', 'outputs': [{'internalType': 'bool', 'name': 'r', 'type': 'bool'}], 'stateMutability': 'pure', 'type': 'function'}
    return: baz(uint32,bool)
    ex: {'inputs': [{'components': [{'internalType': 'uint256', 'name': 'a', 'type': 'uint256'}, {'internalType': 'uint256[]', 'name': 'b', 'type': 'uint256[]'}, {'components': [{'internalType': 'uint256', 'name': 'x', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'y', 'type': 'uint256'}], 'internalType': 'struct Test.T[]', 'name': 'c', 'type': 'tuple[]'}], 'internalType': 'struct Test.S', 'name': '', 'type': 'tuple'}, {'components': [{'internalType': 'uint256', 'name': 'x', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'y', 'type': 'uint256'}], 'internalType': 'struct Test.T', 'name': '', 'type': 'tuple'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'name': 'f', 'outputs': [], 'stateMutability': 'pure', 'type': 'function'}
    return: f(uint256,uint256[],uint256,uint256,uint256,uint256,uint256)
    '''
    if abi_fun['inputs'] == [] or abi_fun['type'] != 'function':
        return None
    out = abi_fun['name']+'('
    for a in abi_fun['inputs']:
        if a['type'] == 'tuple':
            out += get_components(a)
        else:    
            out += a['type']+','
    return out[:-1]+')'