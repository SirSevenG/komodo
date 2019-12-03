#!/usr/bin/env python3
# Copyright (c) 2019 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
from pytest_util import validate_transaction


@pytest.mark.usefixtures("proxy_connection")
class TestBlockchainMethods:

    def test_coinsupply(self, test_params):
        test_values = {
            'height': '131',
            'supply': '10000130000.15801',
            'invalid_height': '200',
            'invalid_value': 'not_num'
        }
        rpc = test_params.get('node1').get('rpc')
        # fixed height
        res = rpc.coinsupply(test_values['height'])
        assert res.get('result') == 'success'
        assert res.get('height') == int(test_values['height'])
        assert res.get('supply') == float(test_values['supply'])
        # coinsupply without value should return max height
        res = rpc.coinsupply()
        assert res.get('result') == 'success'
        assert res.get('height') == int(test_values['height'])
        assert res.get('supply') == float(test_values['supply'])
        # invalid height
        res = rpc.coinsupply(test_values['invalid_height'])
        assert res.get('error') == "invalid height"
        # invalid value
        res = rpc.coinsupply(test_values['invalid_value'])
        assert res.get('error') == "couldnt calculate supply"

    def test_getbestblockhash(self, test_params):
        test_values = {
            'hexx': '01188f110a6cd6f04a621e394b21bad6441b9d0dd18167312329c0127f084757'
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getbestblockhash()
        assert res == test_values['hexx']

    def test_getblock(self, test_params):
        test_values = {
            'block15': '15',
            'hash15': '0c5c23bed58aa151c46f15f94ffd7a9ad65c87bc8c90082a94e2a68025a7621e',
            'size': '1586'
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
        test_values = {
            'chain': 'main',
            'blocks': 131,
            'headers': 131
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getblockchaininfo()
        assert res.get('chain') == test_values['chain']
        assert res.get('blocks') == test_values['blocks']
        assert res.get('headers') == test_values['headers']

    def test_getblockcount(self, test_params):
        test_values = {
            'height': 131
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getblockcount()
        assert res == test_values['height']

    def test_getblockhash(self, test_params):
        test_values = {
            'height': 123,
            'hexx': '009a0806606f3cbed90d01556735e878fac2451b7cd865c8193af7a85f1627ab'
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getblockhash(test_values['height'])
        assert res == test_values['hexx']

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
        res = rpc.getblockheader(test_values['blockhex'])
        assert res.get('hash') == test_values['blockhex']
        assert res.get('height') == test_values['height']
        # With 'true' optional param response should be same
        res = rpc.getblockheader(test_values['blockhex'], True)
        assert res.get('hash') == test_values['blockhex']
        assert res.get('height') == test_values['height']
        res = rpc.getblockheader(test_values['blockhex'], False)
        assert str(res) == test_values['expected_data']

    def test_getchaintips(self, test_params):
        test_values = {
            'height': 131,
            'status': 'active'
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getchaintips()
        assert res[0].get('height') == test_values['height']
        assert res[0].get('status') == test_values['status']

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
        test_values = {
            'difc': 8.8314332247557
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getdifficulty()
        assert res == test_values['difc']

    #
    # Only applies to -ac_staked Smart Chains
    #
    # def test_(self, test_params):
    #     test_values = {}

    def test_getmempoolinfo(self, test_params):  # we can only assert mempool call returns smth
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getmempoolinfo()  # atm mempool should be empty
        assert res.get('size') == 0
        assert res.get('bytes') == 0
        assert res.get('usage') == 0

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
        test_values = {
            'txlist': ['68ee9d23ba51e40112be3957dd15bc5c8fa9a751a411db63ad0c8205bec5e8a1'],
            'expected_data': '040000007a0e472a82a3022586bb40c545fc62b4d17361017aa295e8e074b0c27e9faf00a1e8c5be05820cad63db11a451a7a98f5cbc15dd5739be1201e451ba239dee68fbc2f4300c01f0b7820d00e3347c8da4ee614674376cbc45359daa54f9b5493ee135d55ddc9402200200b164f3198c9e0f83e8cdf42c3e4461f21b4c78b5f6ed8ea332bd16c40000fd400501c0f9a8c9440efed10e01c6f7fde36078995fc81a0dd1f6dbe631d0ffaaf2e2eaa4ab19c582dbf9004b02da2704d4e5e9d9c45bc0862a94b909ddbad02c5e0c02750131f9c13be41cb34d8fec0396cd395833a5103c72e0e79b802140662494324d5e29b4e55b5a3b18f6012b0d496b7891f043a488cc43b950c4bea46f10ed190e9bcfb09a7f5f5287dbb2c1a29b8e54fb0c19f6bea03c8ffc7cf12763a29faf63164a4d7e54050272caa01a8a64c69590c10aff35e59a1bb3b92ada05604ef9a0e1ede1e78b47c04cc451a2456c13aa5a0638acfd920c6b19158a3675b1701f62bce876f31b299327c04fefcb2fab1a3864424c9f9704eb7c248303618bf38b21c48521047a1e255286af1fca1f10ee22877a6a134a490c77051784e0e51f8ed7c55c323f05aa190213638be54211eb6a1f6a42ff38b47b55640ec7bfb7e60496697a85b1b38cf1e82ef17119fc1805c3c7130e417239336251597a40b8d1f0ae985cb612061db0864c848a7984635be8abfb8d39f569efa5127bf8dcccc680beb966d5bd225d395da0d778ff31161e81ac14cbd401aef1d49f2fbb826e842cbc19d0101dafa79649a371aa5c128752bcb231bf280e147311374efe95d5cbb7336c826ad1bf7778d2565795ed1f97dbe361ab66db6843b3713df964fd77a4320fa4372caee2a44e112b77b2e4287824c6c2ba81df0a5a068f6471aa1e8976f950f2ee9eb1bc7afcfef90f8fa98a9688e06c9fb3cdabebff26696147228efaad8109c00692f48a3e3b78bd14156341dd5e85853c495734f686538133c3e3fdd113d3ce482bc1c97691ddcf072464ba3fc7d25a58d6e2be373582f8cae6192beb1de9436c8f57db958123357619796e8b8cc75def7d0da5c97add9a89b90982c867f758574a3c4d7d6a5625231a46b7d1ce40b1b8c8984fe09c47a900bd7a4e0541f8bb689456c1bfe3d358236c758301601b36bc09724ad862a5eceb9d1996f73d719835f209190fcf074d85a3a20c8a96673af11d8a971de497bae81cb409321e6c6d58ee9ddeb3c2329f2b7ef211309e43161c2fc50b3f62655b9b8eb2944a7f2985f3d7ff2fc56fbb0556c1e4bbe1f9bf7874d6c884176cffbfb8b320c47d05e0e0d545c21a49e463e331874be91a760a34e7feaaf4d322fea1fe46f3055e79f9cc977571db062079eaff93e748e43d952784e4c101e6f191f07a06a7022a8e91d4b35fb5813524c20c7050ed305d080b65bfeaa2a83d3b6213b91d885a5c6a566ed53edb25ee3dd64fa1d64b853b37f53c51cbfe97a93a9df80a7d690e4e8d3547abe2d109c40f188d8bed9bbc461c9857449519156f45a056f8bafc2eadc14bb4207d202425e73da70e71641962886fe48df8ec57ab337a3a1dff92ce3128819af9b6ed41710cdb7d7bbed86505f2b6e97493a70ad92986b9b452444ede6a7f85a327d04ba827522dd6f5a472e6b6237f210b280c29541006d630b2a0540f6304d25b667093a98e4fd3074c13489ccb2e2254093708c1cb7e5c1e0877fe5e01bf06c5c123a7039b3bdbcc762d89d845d5f77e5b53b8230806bcafda477355a21416083cf706cf67ba2e7d2c88b4c1589b146161eff5f731c6927aaad0de3a636e6c3f5a6b3d2e95fea0a802e6ff8e4e9350b6694508de1aa7978a756f30fbb2ae5ef13a7d9559142ca8223ec52de5d0abc54b7e877af9cf352b2eadfca33d11feade67c2afda5698ba7cd2a6644320e139caf7c2a0e4bb2e55cb981f528647046fe7092b3e9db25d71257dff9cce8cd377325931de64ee66d18acfac0571b6f2ac37d58594f73b94579d9d031ca9fe4b700ca246f1c3e0c0fe86f7f9772639b330952077a91cfc04977534e00e0a21f157c88da4cd09886a64b56e5320100000001a1e8c5be05820cad63db11a451a7a98f5cbc15dd5739be1201e451ba239dee680101'
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.gettxoutproof(test_values['txlist'])
        assert str(res) == test_values['expected_data']

    def test_gettxoutsetinfo(self, test_params):
        test_values = {
            'height': 131,
            'bestblock': '01188f110a6cd6f04a621e394b21bad6441b9d0dd18167312329c0127f084757',
            'total_amount': 10000130000.15801
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.gettxoutsetinfo()
        assert res.get('height') == test_values['height']
        assert res.get('bestblock') == test_values['bestblock']
        assert res.get('total_amount') == test_values['total_amount']

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
        assert res.get('error') == test_values['error']  # with our test chain call should fail

    def test_verifychain(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.verifychain()
        assert res  # rpc returns True if chain was verified

    def test_verifytxoutproof(self, test_params):
        test_values = {
            'txid': ['68ee9d23ba51e40112be3957dd15bc5c8fa9a751a411db63ad0c8205bec5e8a1']
        }
        rpc = test_params.get('node1').get('rpc')
        txproof = rpc.gettxoutproof(test_values['txid'])
        res = rpc.verifytxoutproof(txproof)
        assert res[0] == test_values['txid'][0]  # gettxoutproof should be list, verify response - string

# TODO: add fixture to ensure bootstrap is fresh and mining is disabled at tests start \
#        or test_values data will not be valid
