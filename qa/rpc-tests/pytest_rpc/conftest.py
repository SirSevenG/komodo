import pytest
import json
import os
# Using different proxy to bypass libcurl issues on Windows
if os.name == 'posix':
    from slickrpc import Proxy
else:
    from bitcoinrpc.authproxy import AuthServiceProxy as Proxy


@pytest.fixture(scope='session')
def proxy_connection():
    proxy_connected = []

    def _proxy_connection(node_params_dictionary):
        try:
            proxy = Proxy("http://%s:%s@%s:%d" % (node_params_dictionary["rpc_user"],
                                                  node_params_dictionary["rpc_password"],
                                                  node_params_dictionary["rpc_ip"],
                                                  node_params_dictionary["rpc_port"]))
            proxy_connected.append(proxy)
        except Exception as e:
            raise Exception("Connection error! Probably no daemon on selected port. Error: ", e)
        return proxy

    yield _proxy_connection

    for each in proxy_connected:
        print("\nStopping created proxies...")
        each.stop()


@pytest.fixture(scope='session')
def test_params(proxy_connection):
    with open('nodesconfig.json', 'r') as f:
        params_dict = json.load(f)
    node1_params = params_dict['node1']
    node2_params = params_dict['node2']
    rpc1 = proxy_connection(node1_params)
    rpc2 = proxy_connection(node2_params)
    test_params = {'node1': node1_params, 'node2': node2_params}
    test_params['node1'].update({'rpc': rpc1})
    test_params['node2'].update({'rpc': rpc2})
    return test_params
