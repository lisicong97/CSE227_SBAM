import json


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
