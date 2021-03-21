import pytest
import json
import os
import time
from lib.pytest_util import randomstring, validate_template, mine_and_waitconfirms
# Using different proxy to bypass libcurl issues on Windows
try:
    from slickrpc import Proxy
except ImportError:
    from bitcoinrpc.authproxy import AuthServiceProxy as Proxy


class CCInstance:
    def __init__(self, test_params: dict):
        """Base CC Instance class to wrap test_params data"""
        self.rpc = [test_params.get(node).get('rpc') for node in test_params.keys()]
        self.pubkey = [test_params.get(node).get('pubkey') for node in test_params.keys()]
        self.address = [test_params.get(node).get('address') for node in test_params.keys()]
        self.instance = None


class OraclesCC(CCInstance):
    def __init__(self, test_params: dict):

        super().__init__(test_params)
        self.base_oracle = None

    def new_oracle(self, proxy, schema=None, description="test oracle", o_type=None):
        name = randomstring(8)
        if not o_type:
            o_type = "s"
            res = proxy.oraclescreate(name, description, o_type)
        elif isinstance(o_type, str):
            res = proxy.oraclescreate(name, description, o_type)
        elif isinstance(o_type, list):
            txid = ""
            oracles = []
            for single_o_type in o_type:
                res = proxy.oraclescreate(name, description, single_o_type)
                txid = proxy.sendrawtransaction(res.get('hex'))
                oracles.append({
                                'format': single_o_type,
                                'name': name,
                                'description': description,
                                'oracle_id': txid
                               })
            mine_and_waitconfirms(txid, proxy)
            return oracles
        else:
            raise TypeError("Invalid oracles format: ", o_type)
        if schema:
            validate_template(res, schema)
        assert res.get('result') == 'success'
        txid = proxy.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, proxy)
        oracle = {
            'format': o_type,
            'name': name,
            'description': description,
            'oracle_id': txid
        }
        if not self.base_oracle:
            self.base_oracle = oracle
        return oracle


class TokenCC(CCInstance):
    def __init__(self, test_params: dict):
        super().__init__(test_params)
        self.base_token = None

    def new_token(self, proxy, schema=None):
        name = randomstring(8)
        amount = '0.10000000'
        res = proxy.tokencreate(name, amount, "test token 1")
        if schema:
            validate_template(res, schema)
        assert res.get('result') == 'success'
        txid = proxy.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, proxy)
        token = {
            'tokenid': txid,
            'name': name
        }
        if not self.base_token:
            self.base_token = token
        return token


class DiceCC(CCInstance):
    def __init__(self, test_params: dict):
        super().__init__(test_params)
        self.open_casino = None

    def new_casino(self, proxy, schema=None):
        rpc1 = proxy
        name = randomstring(4)
        funds = '777'
        minbet = '1'
        maxbet = '77'
        maxodds = '10'
        timeoutblocks = '5'
        res = rpc1.dicefund(name, funds, minbet, maxbet, maxodds, timeoutblocks)
        if schema:
            validate_template(res, schema)
        assert res.get('result') == 'success'
        txid = rpc1.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, rpc1)
        casino = {
            'fundingtxid': txid,
            'name': name,
            'minbet': minbet,
            'maxbet': maxbet,
            'maxodds': maxodds
        }
        if not self.open_casino:
            self.open_casino = casino
        return casino

    @staticmethod
    def diceinfo_maincheck(proxy, fundtxid, schema):
        res = proxy.diceinfo(fundtxid)
        validate_template(res, schema)
        assert res.get('result') == 'success'

    @staticmethod
    def diceaddfunds_maincheck(proxy, amount, fundtxid, schema):
        name = proxy.diceinfo(fundtxid).get('name')
        res = proxy.diceaddfunds(name, fundtxid, amount)
        validate_template(res, schema)
        assert res.get('result') == 'success'
        addtxid = proxy.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(addtxid, proxy)

    @staticmethod
    def dicebet_maincheck(proxy, casino, schema):
        res = proxy.dicebet(casino.get('name'), casino.get('fundingtxid'), casino.get('minbet'), casino.get('maxodds'))
        validate_template(res, schema)
        assert res.get('result') == 'success'
        bettxid = proxy.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(bettxid, proxy)
        return bettxid

    @staticmethod
    def dicestatus_maincheck(proxy, casino, bettx, schema):
        res = proxy.dicestatus(casino.get('name'), casino.get('fundingtxid'), bettx)
        validate_template(res, schema)
        assert res.get('result') == 'success'

    @staticmethod
    def dicefinsish_maincheck(proxy, casino, bettx, schema):
        res = proxy.dicefinish(casino.get('name'), casino.get('fundingtxid'), bettx)
        validate_template(res, schema)
        assert res.get('result') == 'success'

    @staticmethod
    def create_entropy(proxy, casino):
        amount = '1'
        for i in range(100):
            res = proxy.diceaddfunds(casino.get('name'), casino.get('fundingtxid'), amount)
            fhex = res.get('hex')
            proxy.sendrawtransaction(fhex)
        checkhex = proxy.diceaddfunds(casino.get('name'), casino.get('fundingtxid'), amount).get('hex')
        tx = proxy.sendrawtransaction(checkhex)
        mine_and_waitconfirms(tx, proxy)


@pytest.fixture(scope='session')
def proxy_connection():
    proxy_connected = []

    def _proxy_connection(node_params_dictionary):
        try:
            proxy = Proxy("http://%s:%s@%s:%d" % (node_params_dictionary["rpc_user"],
                                                  node_params_dictionary["rpc_password"],
                                                  node_params_dictionary["rpc_ip"],
                                                  node_params_dictionary["rpc_port"]), timeout=360)
            proxy_connected.append(proxy)
        except ConnectionAbortedError as e:
            raise Exception("Connection error! Probably no daemon on selected port. Error: ", e)
        return proxy

    yield _proxy_connection

    for each in proxy_connected:
        print("\nStopping created proxies...")
        time.sleep(10)  # time wait for tests to finish correctly before stopping daemon
        try:  # while using AuthServiceProxy, stop method results in connection aborted error
            each.stop()
        except ConnectionAbortedError as e:
            print(e)


@pytest.fixture(scope='session')
def test_params(proxy_connection):
    with open('nodesconfig.json', 'r') as f:
        params_dict = json.load(f)
    nodelist_raw = list(params_dict.keys())
    nodelist = []
    if os.environ['CLIENTS']:
        numclients = int(os.environ['CLIENTS'])
        for i in range(numclients):
            nodelist.append(nodelist_raw[i])
    else:
        nodelist_raw.pop()  # escape extra param in dict -- is_fresh_chain
        nodelist = nodelist_raw
    test_params = {}
    for node in nodelist:
        node_params = params_dict[node]
        rpc = proxy_connection(node_params)
        test_params.update({node: node_params})
        test_params[node].update({'rpc': rpc})
    return test_params


@pytest.fixture(scope='session')
def oracle_instance(test_params):
    oracle = OraclesCC(test_params)
    return oracle


@pytest.fixture(scope='session')
def token_instance(test_params):
    token = TokenCC(test_params)
    return token


@pytest.fixture(scope='session')
def dice_casino(test_params):
    dice = DiceCC(test_params)
    return dice
