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
        self.address = [test_params.get(node).get('rpc') for node in test_params.keys()]
        self.instance = None


class OraclesCC(CCInstance):
    @staticmethod
    def new_oracle(proxy, schema=None, description="test oracle", o_type=None):
        name = randomstring(8)
        if not o_type:
            o_type = "s"
            res = proxy.oraclescreate(name, description, o_type)
        elif isinstance(o_type, str):
            res = proxy.oraclescreate(name, description, o_type)
        elif isinstance(o_type, list):
            for single_o_type in o_type:
                res = proxy.oraclescreate(name, description, single_o_type)
        else:
            raise TypeError("Invalid oracles format: ", o_type)
        if schema:
            validate_template(res, schema)
        assert res.get('result') == 'success'
        txid = proxy.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, proxy)
        oracle = {
            'format': txid,
            'name': name,
            'description': description,
            'oracle_id': txid
        }
        return oracle


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
