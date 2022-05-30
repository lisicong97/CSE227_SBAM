from hashlib import sha512
from io import BytesIO
from logging import root
import os
import zipfile
from flask import Flask, request, send_file, send_from_directory, make_response
import json
import time
from Crypto.PublicKey import RSA
import helper
from User import User
from Package import Package

deployed_contract_address = '0x2E354F79F0e8D78afa0d5C086c7f203401C151ea'
app = Flask(__name__)


# pkgName2pkg = helper.convertJson2Pkg()
pkgJson = helper.getPkgJson()

userName2signMsg = {}
userName2publicKey = {}
userName2user = helper.convertJson2User()
usersJson = helper.getUserJson()
# print(users)
currentUserId = len(userName2publicKey)


@app.route('/')
def hello_world():
    print("1")
    return 'Welcome to SBAM'


# input:
# userName:"123"
# publicKey: {'e':123, 'n':123}
# output:
# {ifSuccess: 'True', msg: '1321312'}
@app.route('/registerUser', methods=['POST', 'GET'])
def registerUser():
    userName = request.form['userName']
    publicKey = json.loads(request.form['publicKey'])
    # print(userName2userId.keys)
    # print(userName2userId)
    if userName in userName2user:
        return json.dumps({'ifSuccess': False, 'message': 'user name already exist'})
    else:
        userName2signMsg[userName] = str(time.time_ns())
        userName2publicKey[userName] = publicKey
        return json.dumps({'ifSuccess': True, 'msg': userName2signMsg[userName]})


# input:
# userName:"123"
# signedMsg: "12312312312"
# socialMedia: "qwq"
# output:
# {ifSuccess: 'True'}
@app.route('/registerUserConfirm', methods=['POST'])
def confirmUser():
    userName = request.form['userName']
    signedMsg = request.form['signedMsg']
    publicKey = userName2publicKey[userName]
    socialMedia = request.form['socialMedia']

    # https://cryptobook.nakov.com/digital-signatures/rsa-sign-verify-examples
    msg = str.encode(userName2signMsg[userName])
    hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
    hashFromSignature = pow(int(signedMsg), publicKey['e'], publicKey['n'])
    if hash == hashFromSignature:
        try:
            pkstring = helper.exportPubKeyStr(publicKey['n'], publicKey['e'])
            message = helper.web3RegisterUser(deployed_contract_address,
                                              userName, pkstring, socialMedia)
        except:
            return json.dumps({'ifSuccess': False, 'message': 'register failed. Unable to register on blockchain'})

        global currentUserId
        currentUserId += 1
        userName2user[userName] = User(
            currentUserId, userName, publicKey, socialMedia)
        # update the users json file
        usersJson[userName] = {"userId": currentUserId, "username": userName,
                               "publicKey": publicKey, "socialMedia": socialMedia}

        # helper.updateUserJson(usersJson)

        return json.dumps({'ifSuccess': True, 'userId': currentUserId})
    else:
        return json.dumps({'ifSuccess': False, 'message': 'hash inconsistent'})


# if msg after sign is post, return true
# input:
# userName:"123"
# post: "12312312312"
# msg: "qwq"
# socialMedia: "@qwq"
# output:
# {ifProved: 'True'}
@app.route('/proveIdentity', methods=['POST'])
def proveIdentity():
    userName = request.form['userName']
    post = request.form['post']
    msg = request.form['msg']
    socialMedia = request.form['socialMedia']
    correctSocialMedia = userName2user[userName].socialMedia
    publicKey = userName2user[userName].publicKey

    hashFromPost = pow(int(post), publicKey['e'], publicKey['n'])
    if socialMedia == correctSocialMedia and hashFromPost == int.from_bytes(
            sha512(msg).digest(), byteorder='big'):
        return json.dumps({'ifProved': True})
    else:
        return json.dumps({'ifProved': False})


# input:
# pkgName "pkg1"
# pkgContent binary (https://blog.csdn.net/weixin_41712499/article/details/108463609)
# userName "123"
# pkgPublicKey {'n':asd, 'e':afd}
# userSign (plan to use user's signature of hash of file stream, check it)
# output:
# {ifSuccess: 'True'}
@app.route('/registerPkg', methods=['POST'])
def registerPkg():
    # print(request.form['pkgPublicKey'])
    pkgContent = request.files['pkgzip']
    metaInfo = request.files['meta']
    metaJson = json.load(metaInfo)
    metaInfo.seek(0)

    pkgName = metaJson["pkgName"]
    userName = metaJson["updater"]
    pkgPubKey = metaJson["colPublicKey"][0]
    userSign = request.form['userSign']
    # print(int(userSign))
    if userName not in userName2publicKey:
        return json.dumps({'ifSuccess': False, 'message': "user not registered"})
    if pkgName in pkgJson:
        return json.dumps({'ifSuccess': False, 'message': "this package is already registered"})

    # userPubKey = userName2publicKey[userName]

    hash = sha512()
    hash = helper.updateHash(pkgContent, hash)
    hash = helper.updateHash(metaInfo, hash)
    hash = int.from_bytes(hash.digest(), byteorder='big')

    if pow(int(userSign), pkgPubKey['e'], pkgPubKey['n']) == hash:

        try:
            pkstring = helper.exportPubKeyStr(pkgPubKey['n'], pkgPubKey['e'])
            helper.web3AddOwner(deployed_contract_address,
                                userName, pkstring, pkgName)
            helper.web3AddPkgwithVersion(
                deployed_contract_address, pkgName, '0', userName, userSign)
        except:
            return json.dumps({'ifSuccess': False, 'message': 'register failed. Unable to register on blockchain'})

        pkgContent.seek(0)
        helper.writeFile(pkgContent, pkgName + '.zip', 'wb')

        # print(pkgJson)
        pkgPath = ("./storage/" + pkgName)
        os.mkdir(pkgPath)
        os.mkdir(pkgPath + "/Content")

        #  read the content from start
        pkgContent.seek(0)
        metaInfo.seek(0)

        helper.uncompressFile(pkgContent.read(), './storage')

        # update global pkg info
        pkgJson[pkgName] = Package(
            pkgName, 0, userName, [userName2user[userName]], [pkgPubKey])

        # update the local pkg info
        pkgJson[pkgName] = {"pkgName": pkgName, "version": 0, "updater": userName, "colUsers": [
            userName], "colPublicKey": [pkgPubKey]}
        helper.updatePkgJson(pkgJson)

        return json.dumps({'ifSuccess': True})
    return json.dumps({'ifSuccess': False, 'message': 'identity not proved'})


# input:
# pkgName
# colName
# colPkgPublicKey
# sign by original pkgKey (pkgName + colName)
# output:
# {'ifSuccess': 'True'}
@app.route('/addCollaborator', methods=['POST'])
def addCollaborator():
    pkgName = request.form['pkgName']
    colName = request.form['colName']
    newPkgPubKey = json.loads(request.form['colPkgPublicKey'])
    sign = request.form['sign']
    if pkgName not in pkgJson:
        return json.dumps({'ifSuccess': False, 'message': 'package does not exist'})
    if colName not in userName2user:
        return json.dumps({'ifSuccess': False, 'message': 'collaborator not registered'})

    pkgObj = pkgJson[pkgName]
    newUser = userName2user[colName]
    oriPkgKey = pkgObj.colPublicKey[0]

    hashFromSignature = pow(int(sign), oriPkgKey['e'], oriPkgKey['n'])
    if hashFromSignature == int.from_bytes(sha512(str.encode(pkgName+colName)).digest(), byteorder='big'):
        pkgObj.colUsers.append(newUser)
        pkgObj.colPublicKey.append(newPkgPubKey)
        return json.dumps({'ifSuccess': True})
    return json.dumps({'ifSuccess': False})


# input:
# pkgName, version, userName, sign (use pkgKey to encrypt pkgName+version+pkgContent), pkgContent
# output:
# {'ifSuccess': 'True'}
@app.route('/updatePkg', methods=['POST'])
def updatePkg():
    print("received")
    pkgContent = request.files['pkg']
    metaInfo = request.files['meta']
    metaJson = json.load(metaInfo)
    metaInfo.seek(0)
    pkgName = metaJson['pkgName']
    userName = metaJson['updater']
    colUsers = metaJson['colUsers']
    colKeys = metaJson['colPublicKey']
    version = metaJson['version']
    # pkgName = request.form['pkgName']
    # userName = request.form['userName']
    sign = request.form['sign']
    pkgObj = None
    if pkgName in pkgJson:
        pkgObj = pkgJson[pkgName]
    else:
        return json.dumps({'ifSuccess': False, 'message': 'this package is not registered'})

    if pkgObj['version'] + 1 != version:
        return json.dumps({'ifSuccess': False, 'message': 'current vesion is not connsistent with the previous version, please download the newest before update'})

    hash = sha512()
    helper.updateHash(pkgContent, hash)
    helper.updateHash(metaInfo, hash)

    metaInfo.seek(0)
    pkgContent.seek(0)

    # sign the file content
    hash = int.from_bytes(hash.digest(), byteorder='big')
    index = pkgObj['colUsers'].index(userName)
    pkgPubKey = pkgObj['colPublicKey'][index]

    # calculate the hash based on the package content and meta data
    if pow(int(sign), pkgPubKey['e'], pkgPubKey['n']) == hash:
        try:
            # upload the metadata to the block chain
            # pkstring = helper.exportPubKeyStr(pkgPubKey['n'], pkgPubKey['e'])
            helper.web3AddPkgwithVersion(deployed_contract_address, pkgName, str(
                version), userName, sign)

        except:
            return json.dumps({'ifSuccess': False, 'message': 'update failed: unable to upload to blockchain'})

        helper.removeDir('./storage/' + pkgName)
        helper.uncompressFile(pkgContent.read(), './storage')
        pkgObj['version'] += 1
        pkgObj['updater'] = userName

        # update the global json file
        helper.updatePkgJson(pkgJson)

        # update the local json file inside pkg folder
        pkgPath = ("./storage/" + pkgName)
        helper.updateJson(pkgJson[pkgName], pkgPath + "/pkgInfo.json")

        return json.dumps({'ifSuccess': True})
    return json.dumps({'ifSuccess': False, 'message': 'hash inconsisent'})


# input: pkgName
# output: string
@app.route('/downloadPkg', methods=['POST'])
def downloadPkg():

    pkgName = request.form['pkgName']



    if pkgName not in pkgJson:
        response = make_response()
        response.headers['ifSuccess'] = False
        response.headers['message'] = "package not registered"
        # return json.dumps({'ifSuccess': False, 'message': "package not registered"})
    pkgPath = './storage/' + pkgName
  
    # helper.compressFile(pkgPath, pkgName + '.zip')

    response = make_response(send_file(pkgName + '.zip',
                                       mimetype='zip',
                                       attachment_filename=pkgName + '.zip',
                                       as_attachment=True))

    response.headers['ifSuccess'] = True
    response.headers['version'] = pkgJson[pkgName]['version']
    # os.remove(pkgName+'.zip')
    return response

    # return json.dumps({'meta': meta, 'f': fileContent})


# input: pkgName, oldPkgPublicKey, newPkgPublicKey, sign(owner's user key, encrypt all para)
@app.route('/replacePkgKey', methods=['POST'])
def replacePkgKey():
    pkgName = request.form['pkgName']
    oldPkgPublicKey = json.loads(request.form['oldPkgPublicKey'])
    newPkgPublicKey = json.loads(request.form['newPkgPublicKey'])
    sign = request.form['sign']
    pkgObj = pkgJson['pkgName']
    ownerKey = userName2publicKey[pkgObj.ownername]
    hashFromSignature = pow(int(sign), ownerKey['e'], ownerKey['n'])
    if hashFromSignature == int.from_bytes(sha512(str.encode(pkgName+str(oldPkgPublicKey)+str(newPkgPublicKey))).digest(), byteorder='big'):
        pkgObj.colPublicKey[pkgObj.colPublicKey.index(
            oldPkgPublicKey)] = newPkgPublicKey
        return json.dumps({'ifSuccess': True})
    return json.dumps({'ifSuccess': False})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
