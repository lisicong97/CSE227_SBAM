import json
import shutil
import zipfile
import os
from io import BytesIO
from web3 import Web3, HTTPProvider

blockchain_address = 'http://127.0.0.1:9545'
web3 = Web3(HTTPProvider(blockchain_address))
web3.eth.defaultAccount = web3.eth.accounts[0]
compiled_contract_path = './../proj/build/contracts/Sbam.json'
with open(compiled_contract_path) as file:
      contract_json = json.load(file)
      contract_abi = contract_json['abi']

def getweb3User(deployed_contract_address, userName):
  

  contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
  message = contract.functions.getUser(userName).call()
  return message
  
def getweb3PkgCol(deployed_contract_address, pkgName):
  contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
  message = contract.functions.getPkgInfo(pkgName).call()
  return message


def getweb3Pkg(deployed_contract_address, pkgName, version):

  contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
  message = contract.functions.getPkg(pkgName, version).call()
  return message


def verifyPkg(deployed_contract_address, pkgName, version):
  pkgInfo = getweb3Pkg(deployed_contract_address, pkgName, version)



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
  with open(filePath, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            hash.update(chunk)
  return hash


def writeFile(srcFile, dstFile, mode):
  with open(dstFile, mode) as dst:
    for line in srcFile:
        dst.write(line)

def uncompressFile(srcZip,outputPath):
  filebytes = BytesIO(srcZip)
  myzipfile = zipfile.ZipFile(filebytes)
  for name in myzipfile.namelist():

    inputFile = myzipfile.open(name, 'r')
    # print(name)

    # relativePath = name.split('storage/')[1]
    os.makedirs(os.path.dirname(outputPath + '/' + name), exist_ok=True)
    # outputFile = open('./pkgStorage/' + name, 'w')
    writeFile( inputFile, outputPath + '/' + name, 'wb+')
  myzipfile.close()

def compressFile(folderPath, zipFileName):
  zipfolder = zipfile.ZipFile(zipFileName,'w', compression = zipfile.ZIP_STORED) # Compression type 
  for path, dirs, files in os.walk(folderPath):
      for file in files:
          if not os.path.isdir(path):
            os.makedirs(path)
          zipfolder.write(path + '/' + file, os.path.relpath(os.path.join(path, file), os.path.join(folderPath, '..')) )
  zipfolder.close()



def removeDir(path):
  shutil.rmtree(path)