// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EtherStore {
    mapping(address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(address addr) public {
        uint bal = balances[msg.sender];
        require(bal > 0);
    
        (bool sent, ) = addr.call{value: bal}("");
        require(sent, "Failed to send Ether");
        balances[msg.sender] -= bal;

    }
}