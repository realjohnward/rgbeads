import json
from web3 import Web3, middleware
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import *
import os

FROM_ADDRESS = os.getenv('FROM_ADDRESS')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
DESIRED_TXN_TIME = int(os.getenv('DESIRED_TXN_TIME'))
INFURA_KEY = os.getenv('INFURA_KEY')

w3 = Web3(Web3.HTTPProvider(f'https://rinkeby.infura.io/v3/{INFURA_KEY}'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

strategy = construct_time_based_gas_price_strategy(DESIRED_TXN_TIME)
w3.eth.setGasPriceStrategy(strategy)

ABI = json.load(open('abi.json'))

w3.eth.setGasPriceStrategy(strategy)
BYTECODE = json.load(open("bytecode.json"))['object']
CONTRACT_ADDR = None


def deploy_contract():
    RGBeads = w3.eth.contract(abi=ABI, bytecode=BYTECODE)

    nonce = Web3.toHex(w3.eth.getTransactionCount(addr))
    gasprice = w3.eth.generateGasPrice()
    print("gasprice: ", gasprice)

    tr = {'to': None, 
            'from': addr,
            'value': Web3.toHex(0), 
            'gasPrice': Web3.toHex(gasprice), 
            'nonce': nonce,
            'data': "0x" + bytecode,
            'gas': 5000000,
            }

    signed = w3.eth.account.sign_transaction(tr, PRIVATE_KEY)
    tx = w3.eth.sendRawTransaction(signed.rawTransaction)    
    tx_receipt = w3.eth.waitForTransactionReceipt(tx)

    print("TX RECEIPT: ", tx_receipt)
    print("----")
    print("Done.")    
    

