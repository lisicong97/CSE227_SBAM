import json
import shutil
import zipfile
import os
from io import BytesIO

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