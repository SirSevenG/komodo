#!/usr/bin/env python3
# Copyright (c) 2021 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
from slickrpc.exc import RpcException as RPCError
from basic.pytest_util import validate_template, mine_and_waitconfirms, randomstring, randomhex, validate_raddr_pattern


@pytest.mark.usefixtures("proxy_connection")
class TestOraclesCCcalls:

    @staticmethod
    def new_oracle(proxy, schema=None, description="test oracle", o_type=None):
        name = randomstring(8)
        if not o_type:
            o_type = "s"
        res = proxy.oraclescreate(name, description, o_type)
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

    def test_oraclescreate_list_info(self, test_params):
        create_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'hex': {'type': 'string'},
                'error': {'type': 'string'}
            },
            'required': ['result']
        }

        list_schema = {
            'type': 'array',
            'items': {'type': 'string'}
        }

        info_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'txid': {'type': 'string'},
                'description': {'type': 'string'},
                'name': {'type': 'string'},
                'format': {'type': 'string'},
                'marker': {'type': 'string'},
                'registered': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'publisher': {'type': 'string'},
                            'baton': {'type': 'string'},
                            'batontxid': {'type': 'string'},
                            'lifetime': {'type': 'string'},
                            'funds': {'type': 'string'},
                            'datafee': {'type': 'string'}
                        }
                    }
                }
            },
            'required': ['result']
        }

        rpc = test_params.get('node1').get('rpc')
        oracle = self.new_oracle(rpc, schema=create_schema)

        res = rpc.oracleslist()
        validate_template(res, list_schema)

        res = rpc.oraclesinfo(oracle.get('oracle_id'))
        validate_template(res, info_schema)

    def test_oraclesaddress(self, test_params):

        oraclesaddress_schema = {
            'type': 'object',
            'properties': {
                "result": {'type': 'string'},
                "OraclesCCAddress": {'type': 'string'},
                "OraclesCCBalance": {'type': 'number'},
                "OraclesNormalAddress": {'type': 'string'},
                "OraclesNormalBalance": {'type': 'number'},
                "OraclesCCTokensAddress": {'type': 'string'},
                "PubkeyCCaddress(Oracles)": {'type': 'string'},
                "PubkeyCCbalance(Oracles)": {'type': 'number'},
                "myCCAddress(Oracles)": {'type': 'string'},
                "myCCbalance(Oracles)": {'type': 'number'},
                "myaddress": {'type': 'string'},
                "mybalance": {'type': 'number'}
            },
            'required': ['result']
        }

        rpc = test_params.get('node1').get('rpc')
        pubkey = test_params.get('node1').get('pubkey')

        res = rpc.oraclesaddress(pubkey)
        validate_template(res, oraclesaddress_schema)

    def test_oracles_data_interactions(self, test_params):
        general_hex_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'hex': {'type': 'string'},
                'error': {'type': 'string'}
            },
            'required': ['result']
        }

        sample_schema = {
            'type': 'object',
            'properties': {
                'samples': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'txid': {'type': 'string'},
                            'data': {'type': 'string'}
                        }
                    }
                }
            }
        }

        rpc = test_params.get('node1').get('rpc')
        oracle = self.new_oracle(rpc)
        amount = '10000000'
        sub_amount = '0.1'

        # Fund fresh oracle
        res = rpc.oraclesfund(oracle.get('oracle_id'))
        validate_template(res, general_hex_schema)
        txid = rpc.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, rpc)

        # Register as publisher
        res = rpc.oraclesregister(oracle.get('oracle_id'), amount)
        validate_template(res, general_hex_schema)
        txid = rpc.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, rpc)

        # Subscrive to new oracle
        oraclesinfo = rpc.oraclesinfo(oracle.get('oracle_id'))
        publisher = oraclesinfo.get('registered')[0].get('publisher')
        print('\noraclesinfo\n', oraclesinfo, '\n\n')
        print('\npublisher\n', publisher, '\n\n')
        print('\nexpected_id\n', oracle.get('oracle_id'), '\n\n')
        res = rpc.oraclessubscribe(oracle.get('oracle_id'), publisher, sub_amount)
        validate_template(res, general_hex_schema)
        print('\n\n', res, '\n\n')
        txid = rpc.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, rpc)

        # Publish new data
        res = rpc.oraclesdata(oracle.get('oracle_id'), '0a74657374737472696e67')  # teststring
        validate_template(res, general_hex_schema)
        txid = rpc.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, rpc)

        # Check data
        oraclesinfo = rpc.oraclesinfo(oracle.get('oracle_id'))
        baton = oraclesinfo.get('registered')[0].get('batontxid')
        print('\noraclesinfo\n', oraclesinfo, '\n\n')
        print('\nbatontxid\n', baton, '\n\n')
        print('\nexpected_id\n', oracle.get('oracle_id'), '\n\n')
        res = rpc.oraclessample(oracle.get('oracle_id'), baton)
        print(res)
        validate_template(res, sample_schema)
        assert res.get('txid') == baton


@pytest.mark.usefixtures("proxy_connection")
class TestOraclesCC:

    def test_oraclesaddress(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        pubkey = test_params.get('node1').get('pubkey')

        res = rpc.oraclesaddress(pubkey)
        for key in res.keys():
            if key.find('ddress') > 0:
                assert validate_raddr_pattern(res.get(key))

        res = rpc.oraclesaddress()
        for key in res.keys():
            if key.find('ddress') > 0:
                assert validate_raddr_pattern(res.get(key))

#    @staticmethod
#    def bad_calls(proxy, token, pubkey):
#
#    def test_bad_calls(self, test_params):
#        rpc = test_params.get('node1').get('rpc')
#        pubkey = test_params.get('node1').get('pubkey')
#         oracle = self.new_oracle(rpc)
#        self.bad_calls(rpc, token, pubkey)
