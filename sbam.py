import hashlib
from urllib import request
from Crypto.PublicKey import RSA
import sys
import requests
from hashlib import sha512
import json
SERVER_IP = "http://127.0.0.1:5000/"

# sbam message_name option1 option2...
if len(sys.argv) == 1:
	print("Please type your command")

message = sys.argv[1]

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

# sbam new-user userName socalMedia
if message == 'new-user':
	if len(sys.argv) < 3:
		print("Please type in your user name and social media account name")

	userName = sys.argv[2]
	socialMedia = sys.argv[3]
	keyPair = RSA.generate(bits=1024)

	# save the public key
	publicKey = keyPair.publickey().exportKey()
	pubFile = open("publicKey.pem", "wb")
	pubFile.write(publicKey)
	pubFile.close()

	# save the private key 
	privateKey = keyPair.exportKey()
	priFile = open("privateKey.pem", "wb")
	priFile.write(privateKey)
	priFile.close()

	# send userName to request sign message from server
	userInfo = {'userName': userName, 'publicKey': json.dumps({'e': keyPair.e, 'n': keyPair.n})}
	response1 = requests.post(SERVER_IP + "/registerUser", data=userInfo)
	r1 = response1.json()
    # deal with the message from the server
	if r1['ifSuccess'] == False:
		print("User Name Has Been Taken!")
	else:
		msg = r1['msg']
		hash = int.from_bytes(sha512(str.encode(msg)).digest(), byteorder='big')
		signature = pow(hash, keyPair.d, keyPair.n)
		signInfo = {'userName': userName, 'signedMsg': signature, 'socialMedia': socialMedia}
		#data = json.dumps(signInfo)
		response2 = requests.post(SERVER_IP + "/registerUserConfirm", data=signInfo)
		r2 = response2.json()
		if r2['ifSuccess'] == False:
			print("Register Failed!")
		else:
			print("Register Succeed!")

# sbam prove-identity userName socialMedia post msg 
if message == 'prove-identity':
	userName = sys.argv[2]
	socialMedia = sys.argv[3]
	post = sys.argv[4]
	msg = sys.argv[5]
	userInfo = {'userName': userName, 'socialMedia': socialMedia, 'post': post, 'msg': msg}
	response = requests.post(SERVER_IP + "/proveIdentity", data=userInfo)
	r = response.json()
	if r['ifProved']:
		print("User Identity Confirmed Successfully!")
	else:
		print("User Identity confirmed Failed!")


# sbam new-pkg userName pkgName pathToFile 
if message == 'new-pkg':
	userName = sys.argv[2]
	pkgName = sys.argv[3]
	pkgPath = sys.argv[4]
	pkgContent = open(pkgPath, 'rb')

	# generate the pkg key pair
	pkgKeyPair = RSA.generate(bits=1024)

	# save the public key
	pkgPubKey = pkgKeyPair.publickey().exportKey()
	pkgPubFile = open(pkgName+"pkgPubKey.pem", "wb")
	pkgPubFile.write(pkgPubKey)
	pkgPubFile.close()

	# save the private key 
	pkgPriKey = pkgKeyPair.exportKey()
	pkgPriFile = open(pkgName+"pkgPriKey.pem", "wb")
	pkgPriFile.write(pkgPriKey)
	pkgPriFile.close()

	# get the user private key
	f = open('privateKey.pem', 'r')
	priKey = RSA.importKey(f.read())

	# create hash of file stream: https://howtodoinjava.com/modules/python-find-file-hash/
	hash = hashlib.sha512()
	with open(pkgPath, 'rb') as file:
		chunk = 0
		while chunk != b'':
			chuck = file.read(1024)
			hash.update(chuck)

	# sign the file content 
	hash = int.from_bytes(hash.digest(), byteorder='big')
	signature = pow(hash, priKey.d, priKey.n)
	pkgInfo = {'userName': userName, 'pkgName': pkgName, 'pkgContent': pkgContent, 'userSign': signature, 'pkgPublicKey': {'e': pkgKeyPair.e, 'n': pkgKeyPair.n}}
	
	response = requests.post(SERVER_IP + "/registerPkg", data=pkgInfo)

	r = response.json()
	if r['ifSuccess']:
		# Write to the package meta file
		metaContent[pkgName] = 0
		print("Package register Succeed!")
	else:
		print("Package register Failed!")
	

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
	hash = int.from_bytes(sha512(str.encode(pkgName+colName)).digest(), byteorder='big')
	signature = pow(hash, priPkgKey.d, priPkgKey.n)
	colInfo = {'pkgName': pkgName, 'colName': colName, 'colPkgPublicKey':colPubKey, 'sign': signature}
	response = requests.post(SERVER_IP + "/addCollaborator", data=colInfo)
	r = response.json()
	if r['ifSuccess']:
		print("Add Collaborator Succeed!")
	else:
		print("Add collaborator Failed!")



# sbam update-pkg pkgName userName updatedPkgPath	
if message == 'update-pkg':
	pkgName = sys.argv[2]
	userName = sys.argv[3]
	updatedPkgPath = sys.argv[4]
	version = metaContent[pkgName] if pkgName in metaContent  else 0

	updatedPkgContent = open(updatedPkgPath, 'rb')

	# get the corresponding pkg private key
	f = open(pkgName+'pkgPriKey.pem', 'r')
	priPkgKey = RSA.importKey(f.read())

	#sign
	hash = int.from_bytes(sha512(str.encode(pkgName+version+str(updatedPkgContent.read()))).digest(), byteorder='big')
	signature = pow(hash, priPkgKey.d, priPkgKey.n)

	file = {'pkgContent': updatedPkgContent}
	data = {'pkgName':pkgName, 'userName': userName, 'version': version+1, 'sign': signature}
	response = requests.post(SERVER_IP + "/updatePkg", files=file, data=data)
	print(response.content)
	r = json.loads(response.content)
	if r['ifSuccess']:
		# update the pkg version after update package successfully
		metaContent[pkgName] = version + 1
		print("Update Package Succeed!")
	else:
		print("Update Package Failed")


# sbam download-pkg pkgName
if message == 'download-pkg':
	pkgName = sys.argv[2]
	response = requests.post(SERVER_IP + "/downloadPkg", data={'pkgName': pkgName})
	with open (pkgName, 'w') as f:
		f.write(json.loads(response.content)['content'])
	print('file saved')


# sbam replace-package-key pkgName
if message == 'replace-package-key':
	pkgName = sys.argv[2]

	# get the old public and private key
	f = open(pkgName+'pkgPubKey.pem', 'r')
	oldPubPkgKey = RSA.importKey(f.read())

	f = open(pkgName+'pkgPriKey.pem', 'r')
	oldPriPkgKey = RSA.importKey(f.read())

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
	hash = int.from_bytes(sha512(str.encode(pkgName+str(oldPubPkgKey)+str(newPkgPubKey))).digest(), byteorder='big')
	signature = pow(hash, priKey.d, priKey.n)

	replaceInfo = {'pkgName': pkgName, 'oldPkgPublicKey': oldPubPkgKey, 'newPkgPublicKey': newPkgPubKey, 'sign': signature}
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
