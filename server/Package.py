class Package:
    def __init__(self, pkgName, version, updater, colUsers, colPublicKey):
        self.pkgName = pkgName
        self.version = version
        self.updater = updater
        self.colUsers = colUsers
        self.colPublicKey = colPublicKey
