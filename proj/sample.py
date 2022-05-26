import json
from web3 import Web3, HTTPProvider

deployed_contract_address = '0x4f428DeB3841cE0bE976abb782Bd8fFD774867FB'

blockchain_address = 'http://127.0.0.1:9545'
web3 = Web3(HTTPProvider(blockchain_address))
compiled_contract_path = './build/contracts/Sbam.json'

with open(compiled_contract_path) as file:
    contract_json = json.load(file)
    contract_abi = contract_json['abi']

contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)


message = contract.functions.registerUser("Stephen", "123", "sumo").call()
print(message)
message = contract.functions.getUser("Stephen").call()
print(message)