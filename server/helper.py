import json
from User import User
from Package import  Package
import zipfile
import os
from io import BytesIO
import shutil

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


def getUserJson():
  users = {}
  try:
    with open("./User.json", "r") as userFile:
      users =  json.load(userFile)
  except:
    pass
  return users

def convertJson2User():
  users = {}
  try:
    with open("./User.json", "r") as userFile:
      j =  json.load(userFile)
      for i in j:
        newUser = User(j[i]['userId'], j[i]['username'], j[i]['publicKey'], j[i]['socialMedia'])
        users[i] = newUser
  except:
    pass
  return users


def getPkgJson():
  pkgs = {}
  try:
    with open("./Package.json", "r") as pkgFile:
      pkgs =  json.load(pkgFile)
  except:
    pass
  return pkgs


def convertJson2Pkg():
  pkgs = {}
  try:
    with open("./Package.json", "r") as pkgFile:
      j =  json.load(pkgFile)
      for i in j:
        newUser = User(j[i]['pkgName'], j[i]['version'], j[i]['ownername'], j[i]['colUsers'], j[i]['colPublicKey'])
        pkgs[i] = newUser
  except:
    pass
  return pkgs

def updateUserJson(userJson):
  with open("User.json", "w") as jsonFile:
              json.dump(userJson, jsonFile, sort_keys=True, indent=4,
                        ensure_ascii=False)

def updatePkgJson(pkgJson):
  with open("Package.json", "w") as jsonFile:
          json.dump(pkgJson, jsonFile, sort_keys=True, indent=4,
                    ensure_ascii=False)

def updateJson(pkgJson, filePath):
  with open(filePath, "w") as jsonFile:
          json.dump(pkgJson, jsonFile, sort_keys=True, indent=4,
                    ensure_ascii=False)

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
