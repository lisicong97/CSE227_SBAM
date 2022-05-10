class Package:
    def __init__(self, pkgName, version, contents, ownername, colUsers, colPublicKey):
        self.pkgName = pkgName
        self.version = version
        self.contents = contents
        self.ownername = ownername
        self.colUsers = colUsers
        self.colPublicKey = colPublicKey
