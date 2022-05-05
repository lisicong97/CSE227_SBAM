import rsa
import sys

# sbam message_name option1 option2...
if len(sys.argv) == 1:
	print 'Please type your command'

message = sys.argv[1]

# sbam new-user userName
if message == 'new-user':
	(pk, sk) = rsa.newkeys(2048)
	# save the public key
	publicKey = pk.save_pkcs1()
	pubFile = open('public_key.key', 'wb')
	pubFile.write(publicKey)
	pubFile.close()

	# save the private key 
	privateKey = sk.save_pkcs1()
	priFile = open('private_key.key', 'wb')
	priFile.write(privateKey)
	priFile.close()

# sbam new-pkg userName pkgName
if message == 'new-pkg':


# sbam update-pkg userName pkgName curVersion 
if message == 'update-pkg':


# sbam add-collaborator colName pkgName
if message == 'add-collaborator'：


# sbam download-pkg pkgName
if message == 'download-pkg':
