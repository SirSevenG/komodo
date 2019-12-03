from slickrpc import Proxy
import time


def create_proxy(node_params_dictionary):
    try:
        proxy = Proxy("http://%s:%s@%s:%d" % (node_params_dictionary.get('rpc_user'),
                                              node_params_dictionary.get('rpc_password'),
                                              node_params_dictionary.get('rpc_ip'),
                                              node_params_dictionary.get('rpc_port')))
    except Exception as e:
        raise Exception("Connection error! Probably no daemon on selected port. Error: ", e)
    return proxy


def validate_proxy(env_params_dictionary, proxy, node=0):
    while True:  # base connection check
        try:
            getinfo_output = proxy.getinfo()
            print(getinfo_output)
            break
        except Exception as e:
            print(e)
            time.sleep(2)
    print("IMPORTING PRIVKEYS")
    res = proxy.importprivkey(env_params_dictionary.get('test_wif')[node], '', True)
    print(res)
    assert proxy.validateaddress(env_params_dictionary.get('test_address')[node])['ismine']
    assert proxy.getinfo()['pubkey'] == env_params_dictionary.get('test_pubkey')[node]
    assert proxy.getbalance() > 777


def validate_transaction(proxy, txid, conf_req):
    try:
        isinstance(proxy, Proxy)
    except Exception as e:
        raise TypeError("Not a Proxy object, error: " + str(e))
    conf = 0
    while conf < conf_req:
        print("\nWaiting confirmations...")
        resp = proxy.gettransaction(txid)
        conf = resp.get('confirmations')
        time.sleep(2)
