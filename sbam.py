from Crypto.PublicKey import RSA
import sys
import requests
from hashlib import sha512
import json

# sbam message_name option1 option2...
if len(sys.argv) == 1:
	print("Please type your command")

message = sys.argv[1]

# sbam new-user userName
if message == 'new-user':
	if len(sys.argv) < 3:
		print("Please type in your user name")

	userName = sys.argv[2]
	keyPair = RSA.generate(bits=1024)

	# save the public key
	publicKey = keyPair.publickey().export_key()
	pubFile = open("publicKey.pem", "wb")
	pubFile.write(publicKey)
	pubFile.close()

	# save the private key 
	privateKey = keyPair.export_key()
	priFile = open("privateKey.pem", "wb")
	priFile.write(privateKey)
	priFile.close()

	# send userName to request sign message from server
	userInfo = {'userName': userName, 'publicKey': {'e': keyPair.e, 'n': keyPair.n}}
	data = json.dumps(userInfo)
	response1 = requests.post("/registerUser", data=data)

    # deal with the message from the server
	if response1['ifSuccess'] == False:
		print("User Name Has Been Taken!")
	else:
		msg = response1.text['msg']
		hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
		signature = pow(hash, keyPair.d, keyPair.n)
		signInfo = {'userName': userName, 'signedMsg': signature}
		data = json.dumps(signInfo)
		response2 = requests.post("/registerUserConfirm", data=data)
		if response2['ifSuccess'] == False:
			print("Register Failed!")
		else:
			print("Register Success!")


# sbam new-pkg userName pkgName
if message == 'new-pkg':


# sbam update-pkg userName pkgName curVersion 
if message == 'update-pkg':


# sbam add-collaborator colName pkgName
if message == 'add-collaborator'：


# sbam download-pkg pkgName
if message == 'download-pkg':
