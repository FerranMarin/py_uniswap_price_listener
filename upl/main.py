import logging

from web3 import Web3

from upl.abis import UNISWAP_FACOTRY_ABI, PAIR_ABI, SYMBOL_ABI
from upl.app import sio

W3 = Web3(Web3.WebsocketProvider("wss://mainnet.infura.io/ws/v3/b6744db53a18407799db22924e0725db"))


class Pair:
    def __init__(self, symbol, decimals, address, price):
        self.symbol = symbol
        self.decimals = decimals
        self.address = address
        self.price = price
        self.web3 = W3
        self.contract = self.web3.eth.contract(
            address=Web3.toChecksumAddress(self.address),
            abi=PAIR_ABI
        )

    def get_pair_price(self):
        reserves = self.contract.functions.getReserves.call()
        return reserves[0] / reserves[1]   


class UniswapPriceListener:
    def __init__(self):
        self.uniswap_factory = Web3.toChecksumAddress("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")
        self.web3 = W3
        self.factory_contract = self.web3.eth.contract(
            address=self.uniswap_factory,
            abi=UNISWAP_FACOTRY_ABI
        )
        self.pairs = []
    
    def get_total_pairs(self):
        return self.factory_contract.functions.allPairsLength().call()
    
    def get_pair_info(self, pair_id):
        pair_address = self.factory_contract.functions.allPairs(pair_id).call()
        pair_contract = self.web3.eth.contract(
            address=Web3.toChecksumAddress(pair_address),
            abi=PAIR_ABI
        )
        token0 = pair_contract.functions.token0().call()
        token0_contract = self.web3.eth.contract(
            address=Web3.toChecksumAddress(token0),
            abi=SYMBOL_ABI
        )
        token0symbol = token0_contract.functions.symbol().call()
        token1 = pair_contract.functions.token1().call()
        token1_contract = self.web3.eth.contract(
            address=Web3.toChecksumAddress(token1),
            abi=SYMBOL_ABI
        )
        token1symbol = token1_contract.functions.symbol().call()
        reserves = pair_contract.functions.getReserves().call()
        decimals = pair_contract.functions.decimals().call()
        return Pair(
            symbol=f"{token0symbol}/{token1symbol} - {pair_contract.functions.symbol().call()}",
            decimals=decimals,
            address=pair_address,
            price=reserves[0] / reserves[1]
        )

    def load_pairs(self):
        logging.info("Loading pairs")
        for n in range(self.get_total_pairs()+1):
            pair_info = self.get_pair_info(n)
            msg = f"Added pair {pair_info}"
            sio.emit(msg)
            logging.info(msg)
            self.pairs.append(pair_info)      
