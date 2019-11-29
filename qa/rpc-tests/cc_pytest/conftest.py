import pytest
import json
from slickrpc import Proxy


@pytest.fixture
def proxy_connection(scope="session"):
    proxy_connections = []

    def _proxy_connection(node_params_dictionary):
        try:
            proxy = Proxy("http://%s:%s@%s:%d" % (node_params_dictionary["rpc_user"],
                                                  node_params_dictionary["rpc_password"],
                                                  node_params_dictionary["rpc_ip"],
                                                  node_params_dictionary["rpc_port"]))
            proxy_connections.append(proxy)
        except Exception as e:
            raise Exception("Connection error! Probably no daemon on selected port. Error: ", e)
        return proxy

    yield _proxy_connection

    for each in proxy_connections:
        print("\nStopping created proxies...")
        each.stop()
