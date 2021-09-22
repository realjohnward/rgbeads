import json
from web3 import Web3, middleware
from web3.exceptions import ContractLogicError
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import *
import os

from dotenv import load_dotenv
load_dotenv()

FROM_ADDRESS = os.getenv('FROM_ADDRESS')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
DESIRED_TXN_TIME = int(os.getenv('DESIRED_TXN_TIME'))
INFURA_KEY = os.getenv('INFURA_KEY')
ABI = json.load(open('abi.json'))
SAVE_PATH = "./data"

w3 = Web3(Web3.HTTPProvider(f'https://rinkeby.infura.io/v3/{INFURA_KEY}'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

strategy = construct_time_based_gas_price_strategy(DESIRED_TXN_TIME)
w3.eth.setGasPriceStrategy(strategy)

contract = w3.eth.contract(Web3.toChecksumAddress(CONTRACT_ADDRESS), abi=ABI)


def handle_transaction(fn_name, args, auto=False):
    checksum_addr = Web3.toChecksumAddress(FROM_ADDRESS)
    
    def calculate_nonce():
        return Web3.toHex(w3.eth.getTransactionCount(checksum_addr))
        
    data = contract.encodeABI(fn_name, args=args)
    
    while True:
        try:
            gas = getattr(contract.functions, fn_name)(*args).estimateGas({'from': checksum_addr})
            break 
        except ContractLogicError as e:
            print(f"A contract error occurred while calculating gas: {e}")
            print("S=skip, R=retry, Q=quit, L=Set gas estimate at latest block's gas limit")
            answer = input("> ")
            if "q" in answer.lower():
                quit()
            elif "s" in answer.lower():
                return
            elif "l" in answer.lower():
                gas = w3.eth.getBlock("latest").gasLimit
                break 
        except Exception as e:
            print(f"A misc. error occurred while calculating gas: {e}")
            print("Resolve bug. Quitting now.")
            quit()

    gasprice = w3.eth.generateGasPrice()

    txn_fee = gas * gasprice
    
    tr = {'to': contract.address, 
            'from': FROM_ADDRESS,
            'value': Web3.toHex(0), 
            'gasPrice': Web3.toHex(gasprice), 
            'nonce': calculate_nonce(),
            'data': data,
            'gas': gas,
            }

    print(f"Transaction:\n{tr}\n\nFunction: {fn_name}\nArguments:{args}\n\nEstimated Gas: {gas} * Gasprice: {gasprice} = {txn_fee} Txn Fee\n\nY=Yes I want to make the txn with calculated gasprice. <ANY #>=Yes I want to make the txn with a custom gasprice. N=No I'd like to skip this txn. Q=Quit")
    if auto is False:
        answer1 = input("> ")
    else:
        answer1 = "y"
    if "y" in answer1.lower():
        while True:
            try:
                signed = w3.eth.account.sign_transaction(tr, PRIVATE_KEY)
                tx = w3.eth.sendRawTransaction(signed.rawTransaction)    
                tx_receipt = w3.eth.waitForTransactionReceipt(tx)
                print("TXN RECEIPT: ", tx_receipt)
                break 
            except Exception as e:
                print(f"{fn_name} Error: ", e)
                print("\nC=continue, R=retry, Q=quit")
                answer = input("> ")
                if "q" in answer.lower():
                    quit()
                elif answer.lower() == 'c':
                    break
                else:
                    tr['nonce'] = calculate_nonce()

    elif "q" in answer1.lower():
        quit()

metadata_hashes = json.load(open(os.path.join(SAVE_PATH, "metadata_hashes.json")))

for i, metadata_hash in enumerate(metadata_hashes[:10]):
    token_uri = f'ipfs://{metadata_hash}'
    handle_transaction("createNFT", [token_uri], auto=False)