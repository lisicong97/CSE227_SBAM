# CSE227_SBAM

**a Secure Package Manager based in block-chain based on SPAM**

Use geth to run block chain locally,  and rewrite configuration in proj/truffle-config.js to run Sbam smart contract. Below is an example:

```
geth --port 3000 --networkid 58343 --nodiscover --datadir=./blkchain --maxpeers=0  --rpc --rpcport 8543 --rpcaddr 127.0.0.1 --rpccorsdomain "*" --rpcapi "eth,net,web3,personal,miner"
geth attach http://127.0.0.1:8543
cd proj
truffle migrate
```



To start the server, using command below:

```
python server/app.py
```

To interact with server, using command below:

```
python sbam.py {paras}
```

Here is a list of commands and parameters needed for clients:

 Commands      |  Parameters    |     Description 
 -------- | :-----------:  | :-----------
new-user     | userName, socialMedia     | register new user with customized user name and the social media account name which used to prove user's identify later
prove-identity     | userName, socialMedia, post, message     | prove the identity of given userName and its associate social media account with encrypted post and normal message
new-pkg     | userName, pkgName, pathToFile | register new package with user name, customized package name and the path to the package
add-collaborator  | pkgName, collaborator name | add collaborator to the package 
update-pkg  | pkgName, userName, pathToUpdatedPkg | update corresponding package with pkgName, userName and the path to the updated package
download-pkg  | pkgName | download package with pkgName
replace-package-key  | pkgName | replace the key of the package


Update 4.24

* Check data_struct_design.txt(deprecated) to see the data structure and function design

Update 4.27

* Initialize truffle project

Update 5.3
* detailed data structure with a media server : https://docs.google.com/document/d/1VIIydXgGLpFnEszDSsNnV_eoqZvfjcJ71c_RChGVGCg/edit

Update 5.12
* finished server-client structure according to above doc

Update 5.17

* finished ethereum coding, smart constract is in Sbam.sol
