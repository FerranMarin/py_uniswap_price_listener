from unittest.mock import patch, call

from web3 import Web3

from upl.main import Pair, UniswapPriceListener


class MockedSio:
    def emit(msg, other_arg):
        print(msg)
        print(other_arg)
        pass


@patch("web3.eth.Eth.contract")
@patch("web3.Web3.toChecksumAddress", return_value="addrs")
def test_pair_init(mocked_checksum, _):
    p = Pair("symbol", 123, "0xabc123", 345)
    mocked_checksum.assert_called_with("0xabc123")
    assert p.symbol == "symbol"
    assert p.decimals == 123
    assert p.address == "0xabc123"
    assert p.price == 345
    

def test_pair_get_pair_price():
    p = Pair("symbol", 123, "0x3139Ffc91B99aa94DA8A2dc13f1fC36F9BDc98eE", 345)
    reserves = p.contract.functions.getReserves().call()
    new_price = p.get_pair_price()
    assert type(new_price) == float
    assert new_price == reserves[0] / reserves[1]


def test_uniswappricelistener_init():
    upl = UniswapPriceListener()
    assert upl.pairs == []
    assert upl.uniswap_factory == Web3.toChecksumAddress("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")


def test_uniswappricelistener_get_total_pairs():
    upl = UniswapPriceListener()
    pairs = upl.get_total_pairs()
    assert type(pairs) == int


def test_uniswappricelistener_get_pair_info():
    upl = UniswapPriceListener()
    info = upl.get_pair_info(0)
    assert info.symbol == "USDC/WETH - UNI-V2"
    assert info.decimals == 18
    assert info.address == "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
    assert type(info.price) == float
    

@patch("upl.main.UniswapPriceListener.get_total_pairs", return_value=1)
@patch("upl.main.UniswapPriceListener.get_pair_info",
       return_value=Pair("symbol", 123, "0x3139Ffc91B99aa94DA8A2dc13f1fC36F9BDc98eE", 345))
def test_uniswappricelistener_load_pairs(mocked_info, mocked_pairs):
    sio = MockedSio()
    upl = UniswapPriceListener()
    upl.load_pairs(sio)
    mocked_pairs.assert_called_once()
    mocked_info.assert_has_calls(calls=[call(0), call(1)])
