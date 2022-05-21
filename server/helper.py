import json
from User import User
from Package import  Package

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