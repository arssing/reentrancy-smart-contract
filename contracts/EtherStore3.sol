// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EtherStore {
    mapping(address => uint) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(address addr, uint amount) public {
        uint bal = balances[msg.sender];
        require(bal >= amount);
    
        (bool sent, ) = addr.call{value: amount}("");
        require(sent, "Failed to send Ether");
        balances[msg.sender] -= amount;

    }
}