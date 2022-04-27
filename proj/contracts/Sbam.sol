pragma solidity >=0.4.25;

struct User {
    uint userId;
    string userName;
    bytes[] publicKey;
}

struct Package {
	uint packageId;
	string packageName;
	bytes[][] publicKey; // may have different collaborators
    uint version;
	bytes[][] content;
}

contract Sbam {
    mapping (string => uint) userName2userId;
    mapping (uint => User) userId2user;

    mapping(string => uint) pkgName2pkgId;
	mapping(uint => Package) pkgId2pkg;

    uint nextUserId;

    constructor() {
        nextUserId = 1;
    }

    event printToConsole(string message);

    function registerUser(string memory userName) public returns(bool) {
        // already has user name
        if (userName2userId[userName] != 0) {
            emit printToConsole("This user name is occupied, please try another one.");
            return false;
        } else {
            userName2userId[userName] = nextUserId;
            nextUserId++;
            // TODO: generate key pair
            emit printToConsole("IMPORTANT: your private key is 111");
            return true;
        }
    }

    function getUserIdByName(string memory userName) public view returns(uint) {
        return userName2userId[userName];
    }
}