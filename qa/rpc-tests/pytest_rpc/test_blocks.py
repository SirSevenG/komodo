#!/usr/bin/env python3
# Copyright (c) 2019 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
from pytest_util import validate_transaction
from pytest_util import validate_template


@pytest.mark.usefixtures("proxy_connection")
class TestBlockchainMethods:

    def test_coinsupply(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getinfo()
        height = res.get('blocks')
        # fixed height
        res = rpc.coinsupply(str(height))
        assert res.get('result') == 'success'
        assert isinstance(res.get('height'), int)
        # coinsupply without value should return max height
        res = rpc.coinsupply()
        assert res.get('result') == 'success'
        assert isinstance(res.get('height'), int)
        # invalid height
        res = rpc.coinsupply("-1")
        assert res.get('error') == "invalid height"
        # invalid value
        res = rpc.coinsupply("aaa")
        assert res.get('error') == "couldnt calculate supply"

    def test_getbestblockhash(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getbestblockhash()
        assert isinstance(res, str)

    def test_getblock(self, test_params):
        test_values = {
            'block15': '15'
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getblock(test_values['block15'])
        assert res.get('height') == int(test_values['block15'])
        assert res.get('hash') == test_values['hash15']
        assert res.get('size') == int(test_values['size'])
        res = rpc.getblock(test_values['hash15'])
        assert res.get('height') == int(test_values['block15'])
        assert res.get('hash') == test_values['hash15']
        assert res.get('size') == int(test_values['size'])

    def test_getblockchaininfo(self, test_params):
        schema = {
            'type': 'object',
            'required': ['chain', 'blocks', 'synced', 'headers', 'bestblockhash', 'upgrades', 'consensus',
                         'difficulty', 'verificationprogress', 'chainwork', 'pruned', 'commitments'],
            'properties': {
                'chain': {'type': 'string'},
                'blocks': {'type': 'integer'},
                'synced': {'type': 'boolean'},
                'headers': {'type': 'integer'},
                'bestblockhash': {'type': 'string'},
                'difficulty': {'type': ['integer', 'number']},
                'verificationprogress': {'type': 'integer'},
                'chainwork': {'type': 'string'},
                'pruned': {'type': 'boolean'},
                'commitments': {'type': ['integer', 'number']},
                'valuePools': {'type': 'array',
                               'items': {'type': 'object'}},
                'upgrades': {'type': 'object'},
                'consensus': {'type': 'object'}
            }
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getblockchaininfo()
        validate_template(res, schema)

    def test_getblockcount(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getinfo()
        height = res.get('blocks')
        res = rpc.getblockcount()
        assert res == height

    def test_getblockhash(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getinfo()
        height = res.get('blocks')
        res = rpc.getblockhash(height)
        assert isinstance(res, str)

    #
    #  timestampindex -- required param
    #
    # def test_getblockhashes(self, test_params):
    #     test_values = {
    #         'high': 101,
    #         'low': 99,
    #         'options': '{"noOrphans":false, "logicalTimes":true}'
    #     }
    #     rpc = test_params.get('node1').get('rpc')
    #     res = rpc.getblockhashes(test_values['high'], test_values['low'], test_values['options'])

    def test_getblockheader(self, test_params):
        test_values = {
            'blockhex': '009a0806606f3cbed90d01556735e878fac2451b7cd865c8193af7a85f1627ab',
            'height': 123,
            'expected_data': '04000000ca16739f4dab6be5f1265eb5b08281081cc130758b2c0249303f74fc7ccd6c01fb0666044a364de8ec32b22143f577278d6ed6988d4a3e809570021f15e5b564fbc2f4300c01f0b7820d00e3347c8da4ee614674376cbc45359daa54f9b5493eee37d55d39ea012006000a0ca215d728e337fa145f3fa2168667a980c7674156f744b3422cbe0000fd400500a051ac20904ff178ec44500caa4d8718e31aeca90364ac0a42154f30c5e4f24061f204e6723053e5712287f9b219734cb1c97352621563cc2534f0adab5f377ba9c6f2520066a7db48a698d103dafb02be066900cc36d48f4ff02f5d0bc0e2a3beb5b276a75b8c800780f05ca19821955cab60edd877ca2e1533f81ca2064e0d581c265a355fb5b1a3045ba2028fe23a37390b41bd2829e4af3b7905550f395058db472efb971601046f6f7902dbfaaf53f2632af562b165bb9671533dc2e40041db9f3cf379a407aa209c95ce4738a86e100c4d61a46e3bf9e712355ebdbe97f37a4dbdf54b6f826e64eb5ee6633186e7173478d2e35c3f5f76040b5b1c06352d25b79077357c52e23c85e4db1832903e2cbe99afe3db23feeff4a44a61035965b1ef27310f4dc6069ee8dfed9b2181ebaeecf3255d8f12db7f1888a47430df2a5f4a432697e84df3c2df2e5a00b4047a9abe4045e60fc98ad63f3b4eb656a93595f9e904874443c645d83ff27b231cde3088fad4485d251519454178ebdfcdcd124921ad47d656847dc6797cf51f2b16fcb7ae15717d27f24792162df5855f6e663e06022ca77112e5f6f311a70f9dc3e8ddd818da3d673ba06dfd1e91244ce4edd460513942cdc92754f51d1e3db567218c4c77f75f62eab0394020cfe0886c931f6ad9d16f9abc00e0f633881c21c2550fc12be0bc067a67029452bb278094f5f420d65ebe4f031eb96b0ba4b25831de1279a0d62210e02d0fc9af751df7150d7d157dac1ad79b245413112f24e169005529680a29f8920d5cedbff1777e339ee1a7e71b6e085ec1d5085b7b48874584baaff4234c19b882bb2780bb63e05629bba2979c5315e69f758152527ee175a217d2bf2043f55904a9d619921ae3f3e4f83b9248e71656677ab21d83ad6839c5a21a0c6c4b7a727f51071ca72e00d6f2fb114460a27c55b0f9d5ec106d2c3bbf5b772d0233cc94e1a23b2b24748648e865b754239d417c0d43551a43466aa3115301792f12d348cae47a5e2b143d2e99d3a08b6d189d9201641d0ef1a0e58f29b603030630b809ae505cceb0712fd083e03f7b3abc4e10b962a7a9191e33efcd6768da525c5aad58dffa720a695dc39fa0e0f3b3d85227adf7e34d9bda18252e249b32aea41cc74dcc1b64258059b5ad72882cd8b301ce2e5802cc733cd09e30f3ddafbe7d9538ae3fdc21471ec73370c74f8d1862dc6bd3f81627ce720c290bf9f6ef9c494eafe35bd16bf26a736a263e9979c11bd9d1ee424a0ce158dee1fe0a1d65450b9bf3c08106fc6d0b9504d8173b20a084888c8fec6435ad5b5b204bb43b8bcdc084ab83321ed7b583ddb15e7a285d215b4a0e41f896fbe0fac2556a992b28fb8c147ce43c3452e74e54c0b37240bdca71fb81f77f7e5ed76700f765baf7029f88f58f40bbea0af34abe1c3e09d818d9d5a5dc09242c702e58b09dc5e022df833860d911634be0fe15d222fe1be91b8c5d2aef80c31e47fe1df91fee1de1b03b964bb2cdfcd42c11894ed714141b051c45b25773e9280815d29dea4b566260777a8c2135151dc5213135b85c156cd6ff06060ddb3d24cf1b81f74a90a1c3172b5cf497adc5db3bab9dddb0ab39b7e2cc37a14d15e874c42358a912312cc08e4f0d057a011f6e56434f4f75d24e4cc5f10a3dafde151a549a55deec682197fcad15daed4ccc51b27cf030c90762b197b4597fe32898e20a927a64167e52fc62574460a4e595dfa0cdf199e5de84ce3e9b3f7dbb8abc08534c9e4d5ca345b683f2385aee6018a419b7cf7b27485b126ae5d9cfc5b038af4148edc7336b5cbcca118c26e4aa89be5bc0ed417ed722f1f1448c5647ef24682ab656612babbd41f42993cba2fddcc0974878'
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getinfo()
        block = res.get('blocks')
        res = rpc.getblockheader(test_values['blockhex'])
        assert res.get('hash') == test_values['blockhex']
        assert res.get('height') == test_values['height']
        # With 'true' optional param response should be same
        res = rpc.getblockheader(test_values['blockhex'], True)
        assert res.get('hash') == test_values['blockhex']
        assert res.get('height') == test_values['height']
        res = rpc.getblockheader(test_values['blockhex'], False)
        assert isinstance(res, str)

    def test_getchaintips(self, test_params):
        schema = {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['height', 'hash', 'branchlen', 'status'],
                'properties': {
                    'height': {'type': 'integer'},
                    'hash': {'type': 'string'},
                    'branchlen': {'type': 'integer'},
                    'status': {'type': 'string'}
                }
            }
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getchaintips()
        validate_template(res, schema)

    def test_getchaintxstats(self, test_params):
        test_values = {
            'full_txcount': 132,
            'full_blockcount': 130,
            'full_win_fblock': '01188f110a6cd6f04a621e394b21bad6441b9d0dd18167312329c0127f084757',
            'num': 30,
            'num_txcount': 132,
            'num_blockcount':  30,
            'num_win_fblock': '01188f110a6cd6f04a621e394b21bad6441b9d0dd18167312329c0127f084757',
            'hash': '01188f110a6cd6f04a621e394b21bad6441b9d0dd18167312329c0127f084757',
            'hs_num': 21,
            'num_hash_win_txcount': 21,
            'num_hash_fblock': '01188f110a6cd6f04a621e394b21bad6441b9d0dd18167312329c0127f084757',
            'num_hash_blockcount': 21
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getchaintxstats()
        assert res.get('txcount') == test_values['full_txcount']
        assert res.get('window_final_block_hash') == test_values['full_win_fblock']
        assert res.get('window_block_count') == test_values['full_blockcount']
        res = rpc.getchaintxstats(test_values['num'])
        assert res.get('txcount') == test_values['num_txcount']
        assert res.get('window_final_block_hash') == test_values['num_win_fblock']
        assert res.get('window_block_count') == test_values['num_blockcount']
        res = rpc.getchaintxstats(test_values['hs_num'], test_values['hash'])
        assert res.get('window_tx_count') == test_values['num_hash_win_txcount']
        assert res.get('window_final_block_hash') == test_values['num_hash_fblock']
        assert res.get('window_block_count') == test_values['num_hash_blockcount']

    def test_getdifficulty(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getdifficulty()
        assert isinstance(res, float) or isinstance(res, int)

    #
    # Only applies to -ac_staked Smart Chains
    #
    # def test_(self, test_params):
    #     test_values = {}

    def test_getmempoolinfo(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getmempoolinfo()
        assert isinstance(res.get('size'), int)
        assert isinstance(res.get('bytes'), int)
        assert isinstance(res.get('usage'), int)

    #
    # The method requires spentindex to be enabled.
    # txid 68ee9d23ba51e40112be3957dd15bc5c8fa9a751a411db63ad0c8205bec5e8a1
    #
    # def test_getspentinfo(self, test_params):
    #     pass

    def test_gettxout(self, test_params):
        test_values = {
            'tx': '68ee9d23ba51e40112be3957dd15bc5c8fa9a751a411db63ad0c8205bec5e8a1',
            'vout0': 0,
            'voutN': 1,
            'bestblock': '01188f110a6cd6f04a621e394b21bad6441b9d0dd18167312329c0127f084757',
            'coins_value': 1000.0
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.gettxout(test_values['tx'], test_values['vout0'])
        assert res.get('bestblock') == test_values['bestblock']
        assert res.get('value') == test_values['coins_value']
        res = rpc.gettxout(test_values['tx'], test_values['voutN'])
        assert not res  # gettxout retuns None when vout does not exist

    def test_gettxoutproof(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.listunspent()
        txid = res[0].get('txid')
        res = rpc.gettxoutproof([txid])
        assert isinstance(res, str)

    def test_gettxoutsetinfo(self, test_params):
        schema = {
            'type': 'object',
            'required': ['height', 'bestblock', 'transactions', 'txouts', 'bytes_serialized',
                         'hash_serialized', 'total_amount'],
            'properties': {
                'height': {'type': 'integer'},
                'bestblock': {'type': 'string'},
                'transactions': {'type': 'integer'},
                'txouts': {'type': 'integer'},
                'bytes_serialized': {'type': 'integer'},
                'hash_serialized': {'type': 'string'},
                'total_amount': {'type': ['integer', 'number']}
            }
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.gettxoutsetinfo()
        validate_template(res, schema)

    def test_kvupdate(self, test_params):
        test_values = {
            'v_key': 'valid_key',
            'value': 'test+value',
            'days': '2',
            'pass': 'secret',
            'n_key': 'invalid_key',
            'keylen': 9
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.kvupdate(test_values['v_key'], test_values['value'], test_values['days'], test_values['pass'])
        assert res.get('key') == test_values['v_key']
        assert res.get('keylen') == test_values['keylen']
        assert res.get('value') == test_values['value']

    def test_getrawmempool(self, test_params):
        test_values = {
            'key': 'mempool_key',
            'value': 'key_value',
            'days': '1',
            'pass': 'secret'
        }  # to get info into mempool, we need to create tx, kvupdate call creates one for us
        rpc = test_params.get('node1').get('rpc')
        res = rpc.kvupdate(test_values['key'], test_values['value'], test_values['days'], test_values['pass'])
        txid = res.get('txid')
        kvheight = res.get('height')
        res = rpc.getrawmempool()
        assert txid in res
        res = rpc.getrawmempool(False)  # False is default value, res should be same as in call above
        assert txid in res
        res = rpc.getrawmempool(True)
        assert res.get(txid).get('height') == kvheight

    def test_kvsearch(self, test_params):
        test_values = {
            'key': 'search_key',
            'value': 'search_value',
            'days': '1',
            'pass': 'secret'
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.kvupdate(test_values['key'], test_values['value'], test_values['days'], test_values['pass'])
        txid = res.get('txid')
        keylen = res.get('keylen')
        rpc.setgenerate(True, 1)  # enable mining
        validate_transaction(rpc, txid, 1)  # wait for block
        res = rpc.kvsearch(test_values['key'])
        assert res.get('key') == test_values['key']
        assert res.get('keylen') == keylen
        assert res.get('value') == test_values['value']

    def test_notaries(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.notaries('1')
        assert res.get('notaries')  # call should return list of notary nodes disregarding blocknum

    def test_minerids(self, test_params):
        test_values = {
            'error': "couldnt extract minerids"
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.minerids('1')
        assert res.get('error') == test_values['error'] or isinstance(res.get('mined'), list)
        # likely to fail on bootstrap test chains

    def test_verifychain(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.verifychain()
        assert res  # rpc returns True if chain was verified

    def test_verifytxoutproof(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.listunspent()
        txid = res[0].get('txid')
        txproof = rpc.gettxoutproof([txid])
        res = rpc.verifytxoutproof(txproof)
        assert res[0] == txid
