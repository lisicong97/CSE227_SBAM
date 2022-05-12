from hashlib import sha512

from flask import Flask, request
import json
import time
from Crypto.PublicKey import RSA

from User import User
from Package import  Package

app = Flask(__name__)

userName2user = {}
pkgName2pkg = {}

userName2userId = {}
userName2signMsg = {}
userName2publicKey = {}
currentUserId = 0


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
    if userName2userId[userName] is not None:
        return json.dumps({'ifSuccess': False})
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
        userName2user[userName] = User(currentUserId, userName, publicKey, socialMedia)
        return json.dumps({'ifSuccess': True})
    else:
        return json.dumps({'ifSuccess': False})


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
    pkgContent = request.files['pkgContent']
    pkgName = request.form['pkgName']
    userName = request.form['userName']
    pkgPubKey = json.loads(request.form['pkgPublicKey'])
    userSign = request.form['userSign']
    userPubKey = userName2publicKey[userName]
    if userPubKey is None:
        return json.dumps({'ifSuccess': False})
    if pow(int(userSign), userPubKey['e'], userPubKey['n']) == \
            int.from_bytes(sha512(pkgContent.stream).digest(), byteorder='big') and \
            pkgName not in pkgName2pkg:
        pkgName2pkg[pkgName] = Package(pkgName, 0, [pkgContent], userName, [userName2user[userName]], [pkgPubKey])
        return json.dumps({'ifSuccess': True})
    return json.dumps({'ifSuccess': False})


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
    pkgContent = request.files['pkgContent']
    pkgName = request.form['pkgName']
    userName = request.form['userName']
    version = request.form['version']
    sign = request.form['sign']
    pkgObj = pkgName2pkg[pkgName]
    pkgPubKey = pkgObj.colPublicKey[pkgObj.colUsers.index(userName2user[userName])]
    if pow(int(sign), pkgPubKey['e'], pkgPubKey['n']) == \
            int.from_bytes(sha512(str.encode(pkgName+version+pkgContent)).digest(), byteorder='big') and \
            pkgObj.version + 1 == version:
        pkgObj.version += 1
        pkgObj.contents.append(pkgContent)
        return json.dumps({'ifSuccess': True})
    return json.dumps({'ifSuccess': False})


# input: pkgName
# output: string
@app.route('/downloadPkg', methods=['POST'])
def downloadPkg():
    pkgName = request.form['pkgName']
    pkgObj = pkgName2pkg[pkgName]
    return str(pkgObj.contents[-1])


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
        pkgObj.colPublicKey[pkgObj.colPublicKey.index(oldPkgPublicKey)] = newPkgPublicKey
        return json.dumps({'ifSuccess': True})
    return json.dumps({'ifSuccess': False})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
