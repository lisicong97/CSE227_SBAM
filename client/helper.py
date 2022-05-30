from inspect import signature
import json
import shutil
import zipfile
import os
from io import BytesIO
from web3 import Web3, HTTPProvider
from hashlib import sha512
import hashlib
from Crypto.PublicKey import RSA

blockchain_address = 'http://127.0.0.1:9545'
web3 = Web3(HTTPProvider(blockchain_address))
web3.eth.defaultAccount = web3.eth.accounts[0]
compiled_contract_path = './../proj/build/contracts/Sbam.json'
with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json['abi']


def getweb3User(deployed_contract_address, userName):

    contract = web3.eth.contract(
        address=deployed_contract_address, abi=contract_abi)
    message = contract.functions.getUser(userName).call()
    return message

# pkgCols = ownerName, ownerPkgPubKey,string[10] collaboratorNames; string[10] pkgPubKeys; 
def getweb3PkgCol(deployed_contract_address, pkgName):
    contract = web3.eth.contract(
        address=deployed_contract_address, abi=contract_abi)
    message = contract.functions.getPkgInfo(pkgName).call()
    return message

# pkgInfo= (pkgName, version, updater, signature)
def getweb3Pkg(deployed_contract_address, pkgName, version):

    contract = web3.eth.contract(
        address=deployed_contract_address, abi=contract_abi)
    message = contract.functions.getPkg(pkgName, version).call()
    return message


def verifyPkg(deployed_contract_address, pkgName, version, pkgFile, metaFile):
    hash = hashlib.sha512()
    hash = updateHash(pkgFile, hash)
    # print("hash is   ", int.from_bytes(hash.digest(), byteorder='big'))
    hash = updateHash(metaFile, hash)
    hash = int.from_bytes(hash.digest(), byteorder='big')
    
    # pkgInfo= (pkgName, version, updater, signature)
    pkgInfo = getweb3Pkg(deployed_contract_address, pkgName, version)
    updater = pkgInfo[2]
    signature = pkgInfo[3]
    # print(int(signature))

    # pkgCols = ownerName, ownerPkgPubKey,string[10] collaboratorNames; string[10] pkgPubKeys;
    colInfo = getweb3PkgCol(deployed_contract_address,pkgName)
    try:
      colIndex = colInfo[2].index(updater)
    except ValueError:
      return False
    colpkstring = colInfo[3][colIndex]
    publicKey = RSA.importKey(colpkstring)
    # print(int(signature))
    # print("key is " , publicKey.e, publicKey.n)
    hashFromSignature = pow(int(signature), publicKey.e, publicKey.n)
    
    # print("first ", hash)
    # print("second ",hashFromSignature)
    if hash == hashFromSignature:
      return True
    else:
      return False


def updatePkgJson(pkgJson, pkgPath):
    with open(pkgPath + "/pkgInfo.json", "w") as jsonFile:
        json.dump(pkgJson, jsonFile, sort_keys=True, indent=4,
                  ensure_ascii=False)


def getPkgJson(pkgPath):
    package = {}
    try:
        with open(pkgPath + "/pkgInfo.json", "r") as pkgFile:
            package = json.load(pkgFile)
    except:
        pass
    return package


def updateHash(filePath, hash):
    if type(filePath) is str:
        with open(filePath, 'rb') as file:
            chunk = 0
            while chunk != b'':
                chunk = file.read(1024)
                hash.update(chunk)
        return hash
    else:
        chunk = 0
        while chunk != b'':
            chunk = filePath.read(1024)
            hash.update(chunk)
        return hash

def updateJson(pkgJson, filePath):
    with open(filePath, "w") as jsonFile:
        json.dump(pkgJson, jsonFile, sort_keys=True, indent=4,
                  ensure_ascii=False)

# def getPkgJson(filePath):
#     pkgs = {}
#     try:
#         with open(filePath, "r") as pkgFile:
#             pkgs = json.load(pkgFile)
#     except:
#         pass
#     return pkgs

def writeFile(srcFile, dstFile, mode):
    with open(dstFile, mode) as dst:
        for line in srcFile:
            dst.write(line)


def uncompressFile(srcZip, outputPath):
    filebytes = BytesIO(srcZip)
    myzipfile = zipfile.ZipFile(filebytes)
    for name in myzipfile.namelist():

        inputFile = myzipfile.open(name, 'r')
        # print(name)

        # relativePath = name.split('storage/')[1]
        os.makedirs(os.path.dirname(outputPath + '/' + name), exist_ok=True)
        # outputFile = open('./pkgStorage/' + name, 'w')
        writeFile(inputFile, outputPath + '/' + name, 'wb+')
    filebytes.seek(0)


def compressFile(folderPath, zipFileName):
    zipfolder = zipfile.ZipFile(
        zipFileName, 'w', compression=zipfile.ZIP_STORED)  # Compression type
    for path, dirs, files in os.walk(folderPath):
        for file in files:
            if not os.path.isdir(path):
                os.makedirs(path)
            zi = zipfile.ZipInfo.from_file(path + '/' + file)
            zi.date_time = (1980, 1,1,0,0,0)
            zipfolder.write(path + '/' + file, os.path.relpath(
                os.path.join(path, file), os.path.join(folderPath, '..')))
    zipfolder.close()


def removeDir(path):
    shutil.rmtree(path)
