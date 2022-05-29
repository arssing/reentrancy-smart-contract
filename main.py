import os
import json
from subprocess import call
import time
import logging
import re
from IpcClient import *
from tools import *
from IpcClient import *

ATTACKER_CONTRACT = "attackerContract/attacker.sol"
ic = IpcConnect()
logging.basicConfig(level="INFO")
logging.getLogger('urllib3').setLevel('CRITICAL')
logging.getLogger('requests').setLevel('CRITICAL')
logging.getLogger('solcx').setLevel('CRITICAL')
logger = logging.getLogger()

def get_calldata(func_name, address=None):
    args = []
    if "()" not in func_name:
        argss = re.findall(r"\(.*\)",func_name)[0]
        argss = argss[1:-1]
        try:
            argss = argss.split(",")
        except:
            argss = [argss]
            pass
        for arg in argss:
            if arg == "address":

                if address == None:
                    args.append(ic.coinbase())
                else:
                    args.append(address)

            elif arg == "uint256":
                args.append(eth_to_wei(1))
            else:
                return -1

    called_func = bytes.fromhex(ic.get_call_data(func_name, args)[2:])
    return called_func

def get_info_from_attacker(address):
    calledData_selector = ic.get_call_data("calledData()")
    calledContract_selector = ic.get_call_data("calledContract()")
    count_selector = ic.get_call_data("count()")
    call_data = ic.eth_call(address, data=calledData_selector)
    contract_addr = ic.eth_call(address, data=calledContract_selector)
    count_amount = ic.eth_call(address, data=count_selector)
    return (contract_addr, call_data, count_amount)

def main():
    attacker_bytecode, abi = compile_sol_get_data(ATTACKER_CONTRACT)
    call_with_msg_val = ic.get_call_data("callWithMsgValue()")
    call_without_msg_val = ic.get_call_data("callWithoutMsgValue()")
    count_selector = ic.get_call_data("count()")

    #развертывание контракта злоумышленника
    attacker_address = ic.wait_tx(
        ic.create_contract(
            ic.coinbase(),
            "0x"+attacker_bytecode
        )
    )["contractAddress"]
    logger.info(f"Контракт Attacker развернут по адресу:{attacker_address}")
    
    contracts = {}
    contracts_list = get_files_by_folder("contracts",".sol")

    for contract in contracts_list:
        try:
            bytecode, abi = compile_sol_get_data(f"contracts/{contract}")
        except Exception:
            logger.critical(f"не удалось скомпилировать: contracts/{contract}")
            return
        funcs = get_target_function(abi, ['view','nonpayable','payable'])
        contracts[f"contracts/{contract}"] = {"abi": abi, "functions": funcs, "bytecode":bytecode}
    logger.info(f"Все контраты скомпилированы:{list(contracts.keys())}")
        
    for contract in contracts.keys():

        start = time.time()
        tx = ic.wait_tx(
            ic.create_contract(
                ic.coinbase(),
                "0x"+contracts[contract]["bytecode"]
            )
        )

        address = tx["contractAddress"]
        logger.info(f"{contract} развернут по адресу: {address}")
        logger.info(f"Взаимодействуем с контрактом {contract}:")

        for payable in contracts[contract]["functions"]["payable"]:
            
            called_func = get_calldata(payable, attacker_address)
            if called_func == -1:
                logger.info(f"Не можем обработать nonpayable функцию:{payable}")
                continue
            set_data = ic.get_call_data("setData(address,bytes)",[address,called_func])

            #устанавливаем данные для взаимодействия с payable функцией
            ret = ic.wait_tx(
                ic.sendTransaction(
                    frm=ic.coinbase(), 
                    to=attacker_address, 
                    data=set_data
                )
            )

            try:
                if "address" in payable:
                    payable_selector = ic.get_call_data(payable, [ic.coinbase()])
                else:
                    payable_selector = ic.get_call_data(payable)
                #взаимодействуем с payable функцией через аккаунт пользователя
                ret = ic.wait_tx(
                    ic.sendTransaction(
                        frm=ic.coinbase(), 
                        to=address, 
                        value=eth_to_wei(2),
                        data=payable_selector,
                        gas=470000,
                        gas_price=5000000
                    )
                )
                logger.info(f"Отправлено 2 eth через функцию {payable}")
                #взаимодействуем с payable функцией через контракт злоумышленника
                ret = ic.wait_tx(
                    ic.sendTransaction(
                        frm=ic.coinbase(), 
                        to=attacker_address, 
                        value=eth_to_wei(1),
                        data=call_with_msg_val,
                        gas=470000,
                        gas_price=5000000
                    )
                )
                logger.info(f"Отправлен 1 eth через функцию {payable} со смарт-контракта Attacker")
            
            except TransactionZeroStatus:
                logger.warning(f"Транзакция вернулась с 0 статусом")
                logger.warning(f"Не удалось определить повзаимодействовать с {payable}")
                continue

            for nonpayable in contracts[contract]["functions"]["nonpayable"]:

                try:
                    called_func = get_calldata(nonpayable, attacker_address)
                    if called_func == -1:
                        logger.info(f"Не можем обработать nonpayable функцию:{nonpayable}")
                        break
                    set_data = ic.get_call_data("setData(address,bytes)",[address,called_func])

                    ret = ic.wait_tx(
                        ic.sendTransaction(
                            ic.coinbase(), 
                            attacker_address, 
                            data=set_data,
                            gas=300000,
                            gas_price=5000000
                        )
                    )
                    count_before = ic.eth_call(attacker_address, data=count_selector)
                    balance_before = wei_to_eth(ic.get_balance(address))

                    #взаимодействуем с nonpayable функцией
                    logger.info(f"Взаимодействие с {nonpayable} функцией через контракт Attacker")
                    
                    ret = ic.wait_tx(
                        ic.sendTransaction(
                            frm=ic.coinbase(), 
                            to=attacker_address, 
                            data=call_without_msg_val,
                            gas=4700000,
                            gas_price=5000000
                        )
                    )

                    count_after = ic.eth_call(attacker_address, data=count_selector)
                    balance_after = wei_to_eth(ic.get_balance(address))

                    if count_before != count_after:
                        logger.warning(f"Найдена реентерабельная функция {nonpayable} в контракте {contract}:")
                        logger.info(f"Баланс: до={balance_before}; после={balance_after}")
                        logger.info(f"Count: \nдо={count_before};\nпосле={count_after}")
                    else:
                        logger.info("Реентерабельная функция не найдена")
                        logger.info(f"Баланс: до={balance_before}; после={balance_after}")
                        logger.info(f"Count: \nдо={count_before};\nпосле={count_after}")
                except TransactionZeroStatus:
                    logger.warning(f"Транзакция вернулась с 0 статусом")
                    logger.warning(f"Не удалось определить, уязвима ли функция {nonpayable}")
                    continue
        print(f"Время выполнения:{time.time()-start}")
if __name__ == "__main__":
    main()