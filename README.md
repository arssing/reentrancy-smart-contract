## How to use
### Install

```shell
 sudo add-apt-repository -y ppa:ethereum/ethereum
 sudo apt-get update
 sudo apt-get install ethereum
 mkdir data
 geth --datadir data init genesis.json
```
Create new account with password and start geth:
```shell
geth --datadir data account new
geth --datadir data --unlock "<address>" console
```
Stop it (ctrl+C), change GETH_PATH_TO_IPC in config.py to your IPC url.
Start script:
```shell
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python main.py
```
### Example output
```shell
INFO:root:contracts/PrivateBank.sol развернут по адресу: 0xdda608f4e5626a48a7de3b3223793c49f66780c8
INFO:root:Взаимодействуем с контрактом contracts/PrivateBank.sol:
INFO:root:Отправлено 2 eth через функцию Deposit()
INFO:root:Отправлен 1 eth через функцию Deposit() со смарт-контракта Attacker
INFO:root:Взаимодействие с CashOut(uint256) функцией через контракт Attacker
WARNING:root:Найдена реентерабельная функция CashOut(uint256) в контракте contracts/PrivateBank.sol:
INFO:root:Баланс: до=3.0; после=1.0
```
