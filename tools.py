import subprocess
import requests
import re
import json
from exceptions import *
from eth_abi import encode_single, is_encodable
import solcx
import os

def hex_to_dec(num):
    return int(num,16)

def wei_to_eth(wai):
    return 1.0 * wai / 10**18

def eth_to_wei(eth):
    return int(eth * 10**18)

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

def get_all_version():
    supports_from = [0, 4, 11] #0.4.11
    all_text = requests.get("https://github.com/ethereum/solc-bin/blob/gh-pages/bin/list.txt").text
    all_v = re.findall(r'v\d\.\d{1,2}\.\d{1,2}', all_text)
    all_v = list(dict.fromkeys(all_v))

    out_ver = []
    for ver in all_v:
        current_ver = ver.split(".")
        if int(current_ver[0][1:]) > supports_from[0]:
            out_ver.append(ver[1:])
        elif int(current_ver[0][1:]) == supports_from[0] and \
             int(current_ver[1]) > supports_from[1]:
             out_ver.append(ver[1:])
        elif int(current_ver[0][1:]) == supports_from[0] and \
             int(current_ver[1]) == supports_from[1] and \
             int(current_ver[2]) >= supports_from[2]:
             out_ver.append(ver[1:])
    return out_ver

def get_solidity_version(code):
    supports_version = get_all_version()
    try:
        pragma_sol = re.findall(r"pragma solidity (?:\^|>|>=|=)\d\.\d\.\d{1,2}(?:;|)", code)[0]
        sol_ver = re.search(r"\d\.\d{1,2}\.\d{1,2}", pragma_sol)[0]
        if sol_ver in supports_version:
            if ">=" in pragma_sol or "=" in pragma_sol or "^" in pragma_sol:
                return sol_ver
            elif ">" in pragma_sol:
                index = supports_version.index(sol_ver)-1
                if index >= 0:
                    return supports_version[supports_version.index(sol_ver)-1]
        raise UnsupportedSolidityVersion
    except: 
        raise UnsupportedSolidityVersion

def solidity_compile(path_to_file, out_file):
    with open(path_to_file, "r") as file:
        code = file.read()
    _solc_ver = get_solidity_version(code)
    solcx.install_solc(_solc_ver)
    compiled_sol = solcx.compile_standard(
    {
        "language": "Solidity",
        "sources": {"out.sol": {"content": code}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        },
    },
    solc_version = _solc_ver
    )
    with open(f"{out_file}", "w") as file:
        json.dump(compiled_sol, file)

def compile_sol_get_data(path_to_file):
    with open(path_to_file, "r") as f:
        code = f.read()
    _solc_ver = get_solidity_version(code)
    solcx.install_solc(_solc_ver)
    
    compiled_sol = solcx.compile_source(
        code,
        output_values=['abi','bin'],
        solc_version=_solc_ver
    )

    contract_id, contract_interface = compiled_sol.popitem()
    bytecode = contract_interface['bin']
    abi = contract_interface['abi']
    return (bytecode, abi)

def get_target_function(abi, target_funcs=["nonpayable"]):
    result = {}
    
    for type_func in target_funcs:
        result[type_func] = []

    for func in abi:
        
        if func["stateMutability"] not in target_funcs:
            continue
        try:
            name = func["name"]
        except:
            continue
        inputs = ""
        for inpts in func["inputs"]:
            inputs += f"{inpts['type']},"
        
        list_func = result[func["stateMutability"]]
        list_func.append(f"{name}({inputs[:-1]})")
        result[func["stateMutability"]] = list_func
    return result

def read_json(path_to_file, bytecode=False, abi=False):
    keys = []

    with open(path_to_file,"r") as f:
        all_json = json.loads(f.read())
        all_contracts = all_json["contracts"]["out.sol"]
        for contract_name in all_contracts:
            keys.append(contract_name)
    contracts_functions = {}
    #get data about contract
    for key in keys:
        abi = all_contracts[key]["abi"]
        func_bytecode = get_target_function(abi, ["view","payable","nonpayable"])
        func_bytecode["file_path"] = path_to_file
        
        if bytecode:
            func_bytecode["bytecode"] = all_contracts[key]["evm"]["bytecode"]["object"]
        if abi:
            func_bytecode["abi"] = all_contracts[key]["abi"]
        contracts_functions[key] = func_bytecode
    return contracts_functions


def get_files_by_folder(folder, extension):
    res = []
    # Iterate directory
    for file in os.listdir(f"{os.getcwd()}/{folder}/"):
        # check only text files
        if file.endswith(extension):
            res.append(file)
    return res