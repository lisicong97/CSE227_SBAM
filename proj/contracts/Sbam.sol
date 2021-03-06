pragma solidity >=0.4.25;

contract Sbam {
    address authenticatedServerAddress = address(0x123);
    event MyEvent(string test);
    struct User {
        string userName;
        string publicKey;
        string socialMedia;
    }

    struct VersionPackage {
        string pkgName;
        string version;
        string colName;
        string signature; // sign by uploader's pkg private key
    }

    struct PkgCollaborator {
        string ownerName;
        string ownerPkgPubKey;
        string[10] collaboratorNames;
        string[10] pkgPubKeys;
    }

    mapping(string => User) userName2user;
    mapping(string => VersionPackage) pkgName2pkg; // key is pkgName_version
    mapping(string => PkgCollaborator) pkgName2Collaborators;

    event printToConsole(string message);

    // after register to server, register to block chain
    function registerUser(
        string memory userName,
        string memory publicKey,
        string memory socialMedia
    ) public returns (bool) {
        // if (msg.sender != authenticatedServerAddress) {
        //     emit printToConsole("Only authticated server address can write data to block chain!");
        //     return false;
        // }
        emit MyEvent("yes");
        if (
            keccak256(abi.encodePacked(userName2user[userName].userName)) !=
            keccak256(abi.encodePacked(""))
        ) {
            emit printToConsole(
                "This user name is occupied, please try another one."
            );
            return false;
        } else {
            User memory user = User(userName, publicKey, socialMedia);
            userName2user[userName] = user;
            return true;
        }
    }

    function getUser(string memory userName) public view returns (User memory) {
        return userName2user[userName]; // if value is empty, the return object will have default value ("", 0, "", 0)
    }

    // pkg content sign by private key of pkg
    function addPkgWithVersion(
        string memory pkgName,
        string memory version,
        string memory updater,
        string memory sign
        // , string memory userSignOf_pkgName_version_updater
    ) public returns (bool) {
        // if (msg.sender != authenticatedServerAddress) {
        //     emit printToConsole("Only authticated server address can write data to block chain!");
        //     return false;
        // }
        // if (!checkUserSign(userName2user[updater].publicKey, userSignOf_pkgName_version_updater, string(abi.encodePacked(pkgName, version, updater)))) {
        //     emit printToConsole("Only authticated user can write data to block chain!");
        //     return false;
        // }
        string memory key = string(abi.encodePacked(pkgName, "_", version));
        if (
            keccak256(abi.encodePacked(pkgName2pkg[key].pkgName)) !=
            keccak256(abi.encodePacked(""))
        ) {
            emit printToConsole(
                "This package name or version is occupied, please try another one."
            );
            return false;
        } else {
            VersionPackage memory pkg = VersionPackage(
                pkgName,
                version,
                updater,
                sign
            );
            pkgName2pkg[key] = pkg;
            return true;
        }
    }

    function getPkg(string memory pkgName, string memory version)
        public
        view
        returns (VersionPackage memory)
    {
        string memory key = string(abi.encodePacked(pkgName, "_", version));
        return pkgName2pkg[key];
    }

    function addPkgOwner(string memory ownerName, string memory pkgPubKey, string memory pkgName, string memory userSignOf_ownerName_pkgName)
        public
        returns (bool)
    {
        // if (msg.sender != authenticatedServerAddress) {
        //     emit printToConsole("Only authticated server address can write data to block chain!");
        //     return false;
        // }
        // if (!checkUserSign(userName2user[ownerName].publicKey, userSignOf_ownerName_pkgName, string(abi.encodePacked(ownerName, pkgName)))) {
        //     emit printToConsole("Only authticated user can write data to block chain!");
        //     return false;
        // }
        if (
            keccak256(
                abi.encodePacked(pkgName2Collaborators[pkgName].ownerName)
            ) != keccak256(abi.encodePacked(""))
        ) {
            emit printToConsole("This package already exists, can't renew it.");
            return false;
        } else {
            if (
                keccak256(
                    abi.encodePacked(userName2user[ownerName].userName)
                ) == keccak256(abi.encodePacked(""))
            ) {
                emit printToConsole("This user does not exist!");
                return false;
            }
            string[10] memory col = [ownerName, "", "", "", "", "", "", "", "", ""];
            string[10] memory key = [pkgPubKey, "", "", "", "", "", "", "", "", ""];
            PkgCollaborator memory pkgCol = PkgCollaborator(ownerName, pkgPubKey, col, key);
            pkgName2Collaborators[pkgName] = pkgCol;
            return true;
        }
    }

    function addPkgCollaborator(string memory colName, string memory pkgPubKey, string memory pkgName, string memory userSignOf_colName_pkgName)
        public
        returns (bool)
    {
        // if (msg.sender != authenticatedServerAddress) {
        //     emit printToConsole("Only authticated server address can write data to block chain!");
        //     return false;
        // }
        // if (!checkUserSign(userName2user[ownerName].publicKey, userSignOf_colName_pkgName, string(abi.encodePacked(colName, pkgName)))) {
        //     emit printToConsole("Only authticated user can write data to block chain!");
        //     return false;
        // }
        if (
            keccak256(
                abi.encodePacked(pkgName2Collaborators[pkgName].ownerName)
            ) == keccak256(abi.encodePacked(""))
        ) {
            emit printToConsole(
                "This package doesn't exist, check the package name!"
            );
            return false;
        } else {
            bool find = false;
            for (uint256 i = 1; i < 10; i++) {
                if (
                    keccak256(
                        abi.encodePacked(
                            pkgName2Collaborators[pkgName].collaboratorNames[i]
                        )
                    ) == keccak256(abi.encodePacked(""))
                ) {
                    pkgName2Collaborators[pkgName].collaboratorNames[i] = colName;
                    pkgName2Collaborators[pkgName].pkgPubKeys[i] = pkgPubKey;
                    find = true;
                    break;
                }
            }
            if (!find) {
                emit printToConsole(
                    "This capacity of collaborators is reach the limitation!"
                );
                return false;
            }
            return true;
        }
    }

    function getPkgInfo(string memory pkgName)
        public
        view
        returns (PkgCollaborator memory)
    {
        return pkgName2Collaborators[pkgName];
    }

    function checkUserSign(string memory pubKey, string memory sign, string memory para) public pure returns (bool) {
        return true;
    }
}
