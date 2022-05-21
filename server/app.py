from hashlib import sha512
import os
from flask import Flask, request
import json
import time
from Crypto.PublicKey import RSA
import helper
from User import User
from Package import Package

app = Flask(__name__)


pkgName2pkg = helper.convertJson2Pkg()
pkgJson = helper.getPkgJson()


# userName2userId = {}
userName2signMsg = {}
userName2publicKey = {}
userName2user = helper.convertJson2User()
usersJson = helper.getUserJson()
# print(users)
currentUserId = len(userName2publicKey)


@app.route('/')
def hello_world():
    return 'Welcome to SBAM'


# input:
# userName:"123"
# publicKey: {'e':123, 'n':123}
# output:
# {ifSuccess: 'True', msg: '1321312'}
@app.route('/registerUser', methods=['POST'])
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
        global currentUserId
        currentUserId += 1
        userName2user[userName] = User(
            currentUserId, userName, publicKey, socialMedia)
        # update the users json file
        usersJson[userName] = {"userId": currentUserId, "username": userName,
                               "publicKey": publicKey, "socialMedia": socialMedia}

        helper.updateUserJson(usersJson)

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
    if socialMedia == correctSocialMedia and pow(int(post), publicKey['e'], publicKey['n']) == int.from_bytes(
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
    pkgContent = request.files['f']
    metaInfo = request.files['meta']
    metaJson = json.load(metaInfo)
    metaInfo.seek(0)

    pkgName = metaJson["pkgName"]
    # pkgName = request.form['pkgName']
    # userName = request.form['userName']
    userName = metaJson["userName"]

    pkgPubKey = metaJson["pkgPubKey"]
    userSign = request.form['userSign']
    # print(int(userSign))
    if userName not in userName2publicKey:
        return json.dumps({'ifSuccess': False, 'message': "user not registered"})
    if pkgName in pkgName2pkg:
        return json.dumps({'ifSuccess': False, 'message': "this package is already registered"})

    userPubKey = userName2publicKey[userName]

    hash = sha512()

    chunk = 0
    while chunk != b'':
        chunk = pkgContent.read(1024)
        hash.update(chunk)
    chunk = 0
    while chunk != b'':
        chunk = metaInfo.read(1024)
        hash.update(chunk)
    hash = int.from_bytes(hash.digest(), byteorder='big')
    # print(pkgContent)
    if pow(int(userSign), userPubKey['e'], userPubKey['n']) == hash:
        pkgName2pkg[pkgName] = Package(
            pkgName, 0, userName, [userName2user[userName]], [pkgPubKey])
        print(pkgName)
        pkgJson[pkgName] = {"pkgName": pkgName, "version": 0, "ownername": userName, "colUsers": [
            userName2user[userName].username], "colPublicKey": [pkgPubKey]}
        # print(pkgJson)
        pkgPath = ("./storage/" + pkgName)
        os.mkdir(pkgPath)
        os.mkdir(pkgPath + "/Content")

        helper.updatePkgJson(pkgJson)

        #  read the content from start
        pkgContent.seek(0)
        metaInfo.seek(0)

        # write to storage
        with open(pkgPath + "/Content/" + pkgName, "wb") as output:
            for line in pkgContent:
                output.write(line)
        with open(pkgPath + "/pkgInfo.json", "wb") as output:
            for line in metaInfo:
                output.write(line)

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

    pkgObj = pkgName2pkg['pkgName']
    newUser = userName2user[colName]
    if pkgObj is None or newUser is None:
        return json.dumps({'ifSuccess': False})
    oriPkgKey = pkgObj.colPublicKey[0]
    if pow(int(sign), oriPkgKey['e'], oriPkgKey['n']) == \
            int.from_bytes(sha512(str.encode(pkgName+colName)).digest(), byteorder='big'):
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
    pkgContent = request.files['pkgContent']
    metaInfo = request.files['meta']
    metaJson = json.load(metaInfo)
    metaInfo.seek(0)
    pkgName = metaJson['pkgName']
    userName = metaJson['userName']
    version = metaJson['version']
    sign = request.form['sign']
    pkgObj = None
    if pkgName in pkgName2pkg:
        pkgObj = pkgName2pkg[pkgName]
    else:
        return json.dumps({'ifSuccess': False, 'message': 'this package is not registered'})

    if pkgObj.version != version:
        return json.dumps({'ifSuccess': False, 'message': 'current vesion is not connsistent with the previous version, please download the newest before update'})

    hash = sha512()
    chunk = 0
    while chunk != b'':
        chunk = pkgContent.read(1024)
        hash.update(chunk)

    chunk = 0
    while chunk != b'':
        chunk = metaInfo.read(1024)
        hash.update(chunk)

    metaInfo.seek(0)
    pkgContent.seek(0)

    # sign the file content
    hash = int.from_bytes(hash.digest(), byteorder='big')
    pkgPubKey = pkgObj.colPublicKey[pkgObj.colUsers.index(
        userName2user[userName])]

    # calculate the hash based on the package content and meta data
    if pow(int(sign), pkgPubKey['e'], pkgPubKey['n']) == hash:
        pkgObj.version += 1
        pkgJson[pkgName]['version'] += 1
        helper.updatePkgJson(pkgJson)
        
        pkgPath = ("./storage/" + pkgName)

        with open(pkgPath + "/Content/" + pkgName, "wb") as output:
            for line in pkgContent:
                output.write(line)
        with open(pkgPath + "/pkgInfo.json", "wb") as output:
            for line in metaInfo:
                output.write(line)
        # pkgObj.contents.append(pkgContent)
        return json.dumps({'ifSuccess': True})
    return json.dumps({'ifSuccess': False})


# input: pkgName
# output: string
@app.route('/downloadPkg', methods=['POST'])
def downloadPkg():
    pkgName = request.form['pkgName']
    pkgObj = pkgName2pkg[pkgName]
    # TODO
    return json.dumps({'content': 'str(pkgObj.contents[-1])'})


# input: pkgName, oldPkgPublicKey, newPkgPublicKey, sign(owner's user key, encrypt all para)
@app.route('/replacePkgKey', methods=['POST'])
def replacePkgKey():
    pkgName = request.form['pkgName']
    oldPkgPublicKey = json.loads(request.form['oldPkgPublicKey'])
    newPkgPublicKey = json.loads(request.form['newPkgPublicKey'])
    sign = request.form['sign']
    pkgObj = pkgName2pkg['pkgName']
    ownerKey = userName2publicKey[pkgObj.ownername]
    if pow(int(sign), ownerKey['e'], ownerKey['n']) == \
            int.from_bytes(sha512(str.encode(pkgName+str(oldPkgPublicKey)+str(newPkgPublicKey))).digest(), byteorder='big'):
        pkgObj.colPublicKey[pkgObj.colPublicKey.index(
            oldPkgPublicKey)] = newPkgPublicKey
        return json.dumps({'ifSuccess': True})
    return json.dumps({'ifSuccess': False})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
