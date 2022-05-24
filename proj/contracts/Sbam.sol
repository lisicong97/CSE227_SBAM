pragma solidity >=0.4.25;

contract Sbam {

    struct User {
    uint userId;
    string userName;
    bytes[] publicKey;
    string socialMedia;
    }

    struct VersionPackage {
        string pkgName;
        string version;
        string colName;
        bytes[] colPublicKey;
        bytes[] signature; // sign by uploader's pkg private key
    }

    mapping (string => User) userName2user;
    mapping (string => VersionPackage) pkgName2pkg; // pkgName_version

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
        return userName2user[userName]; // if value is empty, the return object will have default value ("", 0, "", 0)
    }

    // pkg content sign by private key of pkg
    function addPkgWithVersion(string memory pkgName, string memory version, string memory ownername, bytes[] memory pubKey, bytes[] memory sign) public returns(bool) {
        string memory key = string(abi.encodePacked(pkgName, "_", version));
        if (keccak256(abi.encodePacked(pkgName2pkg[key].pkgName)) 
            != keccak256(abi.encodePacked(""))) {
            emit printToConsole("This package name or version is occupied, please try another one.");
            return false;
        } else {
            VersionPackage memory pkg = VersionPackage(pkgName, version, ownername, pubKey, sign);
            pkgName2pkg[key] = pkg;
            return true;
        }
    }

    function getPkg(string memory pkgName, string memory version)  public view returns(VersionPackage memory) {
        string memory key = string(abi.encodePacked(pkgName, "_", version));
        return pkgName2pkg[key];
    }
}