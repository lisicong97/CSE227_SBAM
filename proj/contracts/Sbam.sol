pragma solidity >=0.4.25;

contract Sbam {

    struct User {
    uint userId;
    string userName;
    bytes[] publicKey;
    string socialMedia;
    }

    struct Package {
        string pkgName;
        string owner;
        bytes[] signature; // sign by uploader's pkg private key
    }

    mapping (string => User) userName2user;
    mapping (string => Package) pkgName2pkg;

    event printToConsole(string message);

    // after register to server, register to block chain
    function registerUser(uint id, string memory userName, bytes[] memory publicKey, 
        string memory socialMedia) public returns(bool) {
        if (keccak256(abi.encodePacked(userName2user[userName].userName)) 
            != keccak256(abi.encodePacked(""))) {
            emit printToConsole("This user name is occupied, please try another one.");
            return false;
        } else {
            User memory user = User(id, userName, publicKey, socialMedia);
            userName2user[userName] = user;
            return true;
        }
    }

    function getUser(string memory userName) public view returns(User memory) {
        return userName2user[userName]; // if value is empty, the return object will have default value ("", 0, balabala)
    }

    // pkg content sign by private key of pkg
    function registerPkg(string memory pkgName, string memory ownername, bytes[] memory sign) public returns(bool) {
        if (keccak256(abi.encodePacked(pkgName2pkg[pkgName].pkgName)) 
            != keccak256(abi.encodePacked(""))) {
            emit printToConsole("This pkg name is occupied, please try another one.");
            return false;
        } else {
            Package memory pkg = Package(pkgName, ownername, sign);
            pkgName2pkg[pkgName] = pkg;
            return true;
        }
    }

    function updatePkg(string memory pkgName, bytes[] memory sign) public returns(bool) {
        pkgName2pkg[pkgName].signature = sign;
        return true;
    }

    function getPkg(string memory pkgName)  public view returns(Package memory) {
        return pkgName2pkg[pkgName];
    }
}