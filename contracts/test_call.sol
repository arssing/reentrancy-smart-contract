// SPDX-License-Identifier: GPL-3.0
pragma solidity >0.7.4 <0.9.0;

contract Deployed {
    uint public a = 1;
    
    function setA(uint _a) external returns (uint) {
        a = _a;
        return a;
    }
    
}
