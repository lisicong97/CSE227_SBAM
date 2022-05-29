import json
from mailbox import Message
from web3 import Web3, HTTPProvider

deployed_contract_address = '0x2E354F79F0e8D78afa0d5C086c7f203401C151ea'

blockchain_address = 'http://127.0.0.1:9545'
web3 = Web3(HTTPProvider(blockchain_address))
web3.eth.defaultAccount = web3.eth.accounts[0]
compiled_contract_path = './build/contracts/Sbam.json'

with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json['abi']

contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

# l = [0x12, 0x11]
message = contract.functions.registerUser("Stephen", "234", "sumo").transact()
print(message)
message = contract.functions.getUser("Stephen").call()
print(message)
message = contract.functions.addPkgWithVersion("some", "1", "gary", "123", "123").transact()
print(message)
message = contract.functions.getPkg("some", "1").call()
print(message)