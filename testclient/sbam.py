import hashlib
from urllib import request
from Crypto.PublicKey import RSA
import sys
import requests
from hashlib import sha512
import json
import helper
import zipfile
import os

from io import BytesIO

SERVER_IP = "http://127.0.0.1:5000"
deployed_contract_address = '0x2E354F79F0e8D78afa0d5C086c7f203401C151ea'

# sbam message_name option1 option2...
if len(sys.argv) == 1:
    raise ValueError('no argument given argument number')

message = ""
try:
    message = sys.argv[1]
except:
    print("message not specified")

# create the pkg file if non exist
pkgFile = open("pkgVersion.txt", 'a')
# load the meta content of packages to memeory
metaContent = {}
try:
    for line in pkgFile:
        l = line.split(" ")
        metaContent[l[0]] = int(l[1])
except:
    pass
pkgFile.close()


"""
Message: new-user

Description: sbam new-user userName socalMedia

argv[2]: User Name
argv[3]: social Media
"""
if message == 'new-user':
    if len(sys.argv) != 4:
        print("Please type in your user name and social media account name")
        sys.exit()

    userName = sys.argv[2]
    socialMedia = sys.argv[3]
    keyPair = RSA.generate(bits=1024)
    userKeyPath = "./UserKeys/" + userName

    # save the public key
    publicKey = keyPair.publickey().exportKey()
    os.makedirs(os.path.dirname(userKeyPath + "/publicKey.pem"), exist_ok=True)
    pubFile = open(userKeyPath + "/publicKey.pem", "wb")
    pubFile.write(publicKey)
    pubFile.close()

    # save the private key
    privateKey = keyPair.exportKey()
    priFile = open(userKeyPath + "/privateKey.pem", "wb")
    priFile.write(privateKey)
    priFile.close()

    # send userName to request sign message from server
    userInfo = {'userName': userName, 'publicKey': json.dumps(
        {'e': keyPair.e, 'n': keyPair.n})}
    response1 = requests.post(SERVER_IP + "/registerUser", data=userInfo)
    print(response1)
    r1 = response1.json()
    # deal with the message from the server
    if r1['ifSuccess'] == False:
        print("User Name Has Been Taken!")
    else:
        msg = r1['msg']
        hash = int.from_bytes(
            sha512(str.encode(msg)).digest(), byteorder='big')
        signature = pow(hash, keyPair.d, keyPair.n)
        signInfo = {'userName': userName,
                    'signedMsg': signature, 'socialMedia': socialMedia}
        response2 = requests.post(
            SERVER_IP + "/registerUserConfirm", data=signInfo)
        r2 = response2.json()
        if r2['ifSuccess'] == False:
            print("Register Failed!")
        else:
            print("Register Succeed!")

"""
Message: prove identity

Description: prove the idenity of client

argv[2]: User Name
argv[3]: social Media
argv[4]: the social media post
argv[5]: msg
"""
if message == 'prove-identity':
    userName = sys.argv[2]
    socialMedia = sys.argv[3]
    post = sys.argv[4]
    msg = sys.argv[5]
    userInfo = {'userName': userName,
                'socialMedia': socialMedia, 'post': post, 'msg': msg}
    response = requests.post(SERVER_IP + "/proveIdentity", data=userInfo)
    r = response.json()
    if r['ifProved']:
        print("User Identity Confirmed Successfully!")
    else:
        print("User Identity confirmed Failed!")

"""
Message: new-pkg

Description: publish new package to server and blockchain

argv[2]: User Name
argv[3]: Package Name
argv[4]: The local package path
"""
if message == 'new-pkg':
    userName = sys.argv[2]
    pkgName = sys.argv[3]
    pkgPath = sys.argv[4]
    # pkgContent = open(pkgPath + "/Content/pkgcontent", 'rb')
    pkgKeyPath = "./UserKeys/" + userName + "/pkgKeys/" + pkgName
    userKeyPath = "./UserKeys/" + userName
    # generate the pkg key pair
    pkgKeyPair = RSA.generate(bits=1024)

    # save the public key
    pkgPubKey = pkgKeyPair.publickey().exportKey()
    os.makedirs(os.path.dirname(pkgKeyPath + "/pkgPubKey.pem"), exist_ok=True)
    pkgPubFile = open(pkgKeyPath + "/pkgPubKey.pem", "wb")
    pkgPubFile.write(pkgPubKey)
    pkgPubFile.close()

    # save the private key
    pkgPriKey = pkgKeyPair.exportKey()
    pkgPriFile = open(pkgKeyPath + "/pkgPriKey.pem", "wb")
    pkgPriFile.write(pkgPriKey)
    pkgPriFile.close()

    # get the user private key

    
    # ------  not used currently ------ #
    # f = open(userKeyPath + '/privateKey.pem', 'rb')
    # priKey = RSA.importKey(f.read())
    # ------  not used currently ------ #
    # print("key is ", pkgPriKey)
    # print(priKey)
    
    # put the pkg info into json file
    meta = {"pkgName": pkgName, "version": 0, "updater": userName}
    helper.updatePkgJson(meta, pkgPath)
 
    # compress the whole package directory
    helper.compressFile(pkgPath, pkgName + '.zip')

    # create hash of file stream: https://howtodoinjava.com/modules/python-find-file-hash/
    hash = hashlib.sha512()
    hash = helper.updateHash(pkgName + '.zip', hash)
    hash = helper.updateHash(pkgPath + '/pkgInfo.json', hash)
    # hash = helper.updateHash(pkgKeyPath + "/pkgPubKey.pem", hash)

    # sign the file content
    hash = int.from_bytes(hash.digest(), byteorder='big')
    signature = pow(hash, pkgKeyPair.d , pkgKeyPair.n)
    # print(hash)

    pkgInfo = {'userName': userName, 'pkgName': pkgName,
               'userSign': signature, 'pkgPublicKey': pkgPubKey}

    response = requests.post(SERVER_IP + "/registerPkg", data=pkgInfo, files={
                             "pkgzip": open(pkgName + '.zip', 'rb'), 'meta': open(pkgPath + '/pkgInfo.json', 'rb'), 'pkgPubkey': open(pkgKeyPath + "/pkgPubKey.pem", 'rb')})
    os.remove(pkgName + '.zip')

    r = response.json()
    print(pkgPath + '/pkgInfo.json')
    print(open(pkgPath + '/pkgInfo.json', 'rb').read())
    if r['ifSuccess']:
        # # Write to the package meta file
        # metaContent[pkgName] = 0
        print("Package register Succeed!")
    else:
        print(r['message'])

"""
Message: add-collaborator

Description: add collaborator to the certain package

argv[2]: package name
argv[3]: collaborator user name
"""
# sbam add-collaborator pkgName colName
if message == 'add-collaborator':
    pkgName = sys.argv[2]
    colName = sys.argv[3]

    # generate key pair for the collaborate
    colKeyPair = RSA.generate(bits=1024)
    # save the public key
    colPubKey = keyPair.publickey().exportKey()
    colPubFile = open(colName+"publicKey.pem", "wb")
    colPubFile.write(colPubKey)
    colPubFile.close()
    # save the private key
    colPriKey = keyPair.exportKey()
    colPriFile = open(colName+"privateKey.pem", "wb")
    colPriFile.write(colPriKey)
    colPriFile.close()

    # get the package original private key
    f = open(pkgName+'pkgPriKey.pem', 'r')
    priPkgKey = RSA.importKey(f.read())

    # sign the pkgName + colName
    hash = int.from_bytes(
        sha512(str.encode(pkgName+colName)).digest(), byteorder='big')

    signature = pow(hash, priPkgKey.d, priPkgKey.n)
    colInfo = {'pkgName': pkgName, 'colName': colName,
               'colPkgPublicKey': colPubKey, 'sign': signature}
    response = requests.post(SERVER_IP + "/addCollaborator", data=colInfo)
    r = response.json()
    if r['ifSuccess']:
        print("Add Collaborator Succeed!")
    else:
        print("Add collaborator Failed!")


"""
Message: update-pkg

Description: update the information of certain package

argv[2]: package name
argv[3]: owner/collaborator user name
argv[4]: the path of updated package
"""
# sbam update-pkg pkgName userName updatedPkgPath
if message == 'update-pkg':
    try:
        pkgName = sys.argv[2]
        userName = sys.argv[3]
        updatedPkgPath = sys.argv[4]
    except:
        print("Update Package Error: incorrect number of args")

    pkgKeyPath = "./UserKeys/" + userName + "/pkgKeys/" + pkgName
    # get the corresponding pkg private key
    key = open(pkgKeyPath + '/pkgPriKey.pem', 'r')
    priPkgKey = RSA.importKey(key.read())

    
    #update the meta info file
    pkgJson = helper.getPkgJson(updatedPkgPath)
    pkgJson['version'] += 1
    pkgJson['updater'] = userName
    helper.updatePkgJson(pkgJson, updatedPkgPath)
    

    # helper.updatePkgJson(pkgJson,updatedPkgPath)



    # compress the whole package directory
    helper.compressFile(updatedPkgPath, pkgName + '.zip')

    # sign the file content

    hash = hashlib.sha512()

    hash = helper.updateHash(pkgName + '.zip', hash)
    hash = helper.updateHash(updatedPkgPath + '/pkgInfo.json', hash)

    hash = int.from_bytes(hash.digest(), byteorder='big')
    signature = pow(hash, priPkgKey.d, priPkgKey.n)

    updatedPkg = open(pkgName + '.zip', 'rb')
    metaFile = open(updatedPkgPath + '/pkgInfo.json', 'rb')
    file = {'pkg': updatedPkg, 'meta': metaFile}
    data = {'pkgName': pkgName, 'userName': userName,
            'sign': signature}
    response = requests.post(SERVER_IP + "/updatePkg", files=file, data=data)
    os.remove(pkgName + '.zip')

    # print(response.content)
    r = json.loads(response.content)
    if r['ifSuccess']:
        # update the pkg version after update package successfully
        # metaContent[pkgName] = version + 1
        # metaJson = helper.getPkgJson(updatedPkgPath)
        # metaJson['version'] += 1
        # helper.updatePkgJson(metaJson, updatedPkgPath)
        print("Update Package Succeed!")
    else:
        print(r["message"])


"""
Message: download-pkg

Description: download certain package

argv[2]: package name
argv[3]: the local path to download pkg
argv[4]: the version, default is latest
"""
if message == 'download-pkg':
    pkgName = sys.argv[2]
    downloadPath = sys.argv[3]
    version = sys.argv[4]
    response = requests.post(SERVER_IP + "/downloadPkg",
                             data={'pkgName': pkgName, 'version' : version})

    r = response.headers

    if not r['ifSuccess']:

        print(r['message'])
    else:
        version = r['version']
        helper.removeDir(downloadPath + "/" + pkgName)
        helper.uncompressFile(response.content, downloadPath)
        # col = helper.getweb3PkgCol(deployed_contract_address, pkgName)

        # pkgInfo= (pkgName, version, updater, signature)
        # pkgInfo = helper.getweb3Pkg(deployed_contract_address, pkgName, '0')

        # print(col)
        # print(pkgInfo)
        metaFile = open(downloadPath + "/" + pkgName + '/pkgInfo.json', "rb")

        filebytes = BytesIO(response.content)
        # print(filebytes.read())
        # myzipfile = zipfile.ZipFile(filebytes)
        # with open('./myPkg.zip', 'wb') as dst:
        #   t = myzipfile.getvalue()
        #   dst.write(t)
        helper.writeFile(filebytes, pkgName + '.zip' , 'wb')
        f = open(pkgName + '.zip', 'rb')
        # helper.wr

        ret = helper.verifyPkg(deployed_contract_address, pkgName, version,f, metaFile)
        os.remove(pkgName + '.zip')
        if ret:
          print('file saved')
        else:
          print('unable to verify')

"""
Message: replace package key

Description: revoke the package key and set it to a new one

argv[2]: package name
"""
if message == 'replace-package-key':
    pkgName = sys.argv[2]

    # get the old public and private key
    f = open(pkgName+'pkgPubKey.pem', 'r')
    oldPubPkgKey = RSA.importKey(f.read())

    # generate new key pair for the pkg
    newPkgKeyPair = RSA.generate(bits=1024)
    # save the public key
    newPkgPubKey = newPkgKeyPair.publickey().exportKey()
    newPkgPubFile = open(pkgName+"publicKey.pem", "wb")
    newPkgPubFile.write(newPkgPubKey)
    newPkgPubFile.close()
    # save the private key
    newPkgPriKey = newPkgKeyPair.exportKey()
    newPkgPriFile = open(pkgName+"privateKey.pem", "wb")
    newPkgPriFile.write(newPkgPriKey)
    newPkgPriFile.close()

    # get the user key
    f = open('privateKey.pem', 'r')
    priKey = RSA.importKey(f.read())

    # sign pkgName oldPkgPublicKey newPkgPublicKey
    hash = int.from_bytes(sha512(str.encode(
        pkgName+str(oldPubPkgKey)+str(newPkgPubKey))).digest(), byteorder='big')
    signature = pow(hash, priKey.d, priKey.n)

    replaceInfo = {'pkgName': pkgName, 'oldPkgPublicKey': oldPubPkgKey,
                   'newPkgPublicKey': newPkgPubKey, 'sign': signature}
    #data = json.dumps(replaceInfo)

    response = requests.post(SERVER_IP + "/replacePkgKey", data=replaceInfo)
    r = json.loads(response)
    if r['ifSuccess']:
        print("Replace Key Succeed!")
    else:
        print("Replace Key Failed!")

# write the pkg meta content to the file
pkgFile = open("pkgVersion.txt", 'w')
if len(metaContent) != 0:
    for key, value in metaContent.items():
        pkgFile.write(key + " " + str(value) + "\n")
pkgFile.close()
