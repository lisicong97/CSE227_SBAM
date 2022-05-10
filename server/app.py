from hashlib import sha512

from flask import Flask, request
import json
import time
from Crypto.PublicKey import RSA

import User

app = Flask(__name__)

userName2user = {}

userName2userId = {}
userName2signMsg = {}
userName2publicKey = {}
currentUserId = 0


@app.route('/')
def hello_world():
    return 'Welcome to SBAM'


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


@app.route('/registerUserConfirm', methods=['POST'])
def confirmUser():
    userName = request.form['userName']
    signedMsg = request.form['signedMsg']
    publicKey = userName2publicKey[userName]

    # https://cryptobook.nakov.com/digital-signatures/rsa-sign-verify-examples
    msg = str.encode(userName2signMsg[userName])
    hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
    hashFromSignature = pow(int(signedMsg), publicKey['e'], publicKey['n'])
    if hash == hashFromSignature:
        global currentUserId
        currentUserId += 1
        userName2user[userName] = User(currentUserId, userName, publicKey, None)
        return json.dumps({'ifSuccess': True})
    else:
        return json.dumps({'ifSuccess': False})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
