from web3 import Web3, middleware
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import *
import os
import json
from dotenv import load_dotenv
load_dotenv()

FROM_ADDRESS = os.getenv('FROM_ADDRESS')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
DESIRED_TXN_TIME = int(os.getenv('DESIRED_TXN_TIME'))
INFURA_KEY = os.getenv('INFURA_KEY')

bytecode = json.load(open("bytecode.json"))['object']
abi = json.load(open('abi.json'))

w3 = Web3(Web3.HTTPProvider(f'https://rinkeby.infura.io/v3/{INFURA_KEY}'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

strategy = construct_time_based_gas_price_strategy(DESIRED_TXN_TIME)

w3.eth.setGasPriceStrategy(strategy)

RGBeads = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = Web3.toHex(w3.eth.getTransactionCount(FROM_ADDRESS))
gasprice = w3.eth.generateGasPrice()
print("gasprice: ", gasprice)

tr = {'to': None, 
        'from': FROM_ADDRESS,
        'value': Web3.toHex(0), 
        'gasPrice': Web3.toHex(gasprice), 
        'nonce': nonce,
        'data': "0x" + bytecode,
        'gas': 5000000,
        }

signed = w3.eth.account.sign_transaction(tr, PRIVATE_KEY)
tx = w3.eth.sendRawTransaction(signed.rawTransaction)    
tx_receipt = w3.eth.waitForTransactionReceipt(tx)

print("TXN RECEIPT: ", tx_receipt)
print("----")
print("CONTRACT ADDRESS: ", tx_receipt.contractAddress)
print("----")
print("Done.")