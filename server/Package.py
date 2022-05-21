class Package:
    def __init__(self, pkgName, version, ownername, colUsers, colPublicKey):
        self.pkgName = pkgName
        self.version = version
        self.ownername = ownername
        self.colUsers = colUsers
        self.colPublicKey = colPublicKey
