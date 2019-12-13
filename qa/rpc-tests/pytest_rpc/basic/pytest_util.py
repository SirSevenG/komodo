import time
import jsonschema
import os
if os.name == 'posix':
    from slickrpc import Proxy
else:
    from bitcoinrpc.authproxy import AuthServiceProxy as Proxy


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


def mine_and_waitconfirms(txid, proxy):  # should be used after tx is send
    if os.cpu_count() > 1:
        numthreads = (os.cpu_count() - 1)
    else:
        numthreads = 1
    proxy.setgenerate(True, numthreads)
    # we need the tx above to be confirmed in the next block
    attempts = 0
    while True:
        try:
            confirmations_amount = proxy.getrawtransaction(txid, 1)['confirmations']
            break
        except Exception as e:
            print("\ntx is in mempool still probably, let's wait a little bit more\nError: ", e)
            time.sleep(5)
            attempts += 1
            if attempts < 100:
                pass
            else:
                print("\nwaited too long - probably tx stuck by some reason")
                proxy.setgenerate(False, numthreads)
                return False
    if confirmations_amount < 2:
        print("\ntx is not confirmed yet! Let's wait a little more")
        time.sleep(5)
        proxy.setgenerate(False, numthreads)
        return True
    else:
        print("\ntx confirmed")
        proxy.setgenerate(False, numthreads)
        return True


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


def validate_template(blocktemplate, schema=''):  # BIP 0022
    blockschema = {
        'type': 'object',
        'required': ['bits', 'curtime', 'height', 'previousblockhash', 'version', 'coinbasetxn'],
        'properties': {
            'capabilities': {'type': 'array',
                             'items': {'type': 'string'}},
            'version': {'type': ['integer', 'number']},
            'previousblockhash': {'type': 'string'},
            'finalsaplingroothash': {'type': 'string'},
            'transactions': {'type': 'array',
                             'items': {'type': 'object'}},
            'coinbasetxn': {'type': 'object',
                            'required': ['data', 'hash', 'depends', 'fee', 'required', 'sigops'],
                            'properties': {
                                'data': {'type': 'string'},
                                'hash': {'type': 'string'},
                                'depends': {'type': 'array'},
                                'fee': {'type': ['integer', 'number']},
                                'sigops': {'type': ['integer', 'number']},
                                'coinbasevalue': {'type': ['integer', 'number']},
                                'required': {'type': 'boolean'}
                            }
                            },
            'longpollid': {'type': 'string'},
            'target': {'type': 'string'},
            'mintime': {'type': ['integer', 'number']},
            'mutable': {'type': 'array',
                        'items': {'type': 'string'}},
            'noncerange': {'type': 'string'},
            'sigoplimit': {'type': ['integer', 'number']},
            'sizelimit': {'type': ['integer', 'number']},
            'curtime': {'type': ['integer', 'number']},
            'bits': {'type': 'string'},
            'height': {'type': ['integer', 'number']}
        }
    }
    if not schema:
        schema = blockschema
    jsonschema.validate(instance=blocktemplate, schema=schema)
