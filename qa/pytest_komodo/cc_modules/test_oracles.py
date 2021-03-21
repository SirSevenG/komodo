#!/usr/bin/env python3
# Copyright (c) 2021 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
from slickrpc.exc import RpcException as RPCError
from lib.pytest_util import validate_template, mine_and_waitconfirms, randomstring, randomhex, validate_raddr_pattern


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
        res = rpc.oraclessubscribe(oracle.get('oracle_id'), publisher, sub_amount)
        validate_template(res, general_hex_schema)
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
        res = rpc.oraclessample(oracle.get('oracle_id'), baton)
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

    @staticmethod
    def bad_calls(proxy, oracle):
        valid_formats = ["s", "S", "d", "D", "c", "C", "t", "T", "i", "I", "l", "L", "h"]

        for vformat in valid_formats:
            # trying to register with negative datafee
            res = proxy.oraclesregister(oracle.get('oracle_id'), "-100")
            assert res.get('error')

            # trying to register with zero datafee
            res = proxy.oraclesregister(oracle.get('oracle_id'), "0")
            assert res.get('error')

            # trying to register with datafee less than txfee
            res = proxy.oraclesregister(oracle.get('oracle_id'), "500")
            assert res.get('error')

            # trying to register valid (unfunded)
            res = proxy.oraclesregister(oracle.get('oracle_id'), "1000000")
            assert res.get('error')

            # trying to register with invalid datafee
            res = proxy.oraclesregister(oracle.get('oracle_id'), "asdasd")
            assert res.get('error')

        # looking up non-existent oracle should return error.
        res = proxy.oraclesinfo("none")
        assert res.get('error')

        # attempt to create oracle with not valid data type should return error
        res = proxy.oraclescreate("Test", "Test", "Test")
        assert res.get('error')

        # attempt to create oracle with name > 32 symbols should return error
        too_long_name = randomstring(33)
        res = proxy.oraclescreate(too_long_name, "Test", "s")
        assert res.get('error')

        # attempt to create oracle with description > 4096 symbols should return error
        too_long_description = randomstring(4100)
        res = proxy.oraclescreate("Test", too_long_description, "s")
        assert res.get('error')

    def test_bad_calls(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        oracle = TestOraclesCCcalls.new_oracle(rpc)
        self.bad_calls(rpc, oracle)

    def test_oracles_data(self, test_params):
        oracles_data = {
            's': '05416e746f6e',
            'S': '000161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161',
            'd': '0101',
            'D': '010001',
            'c': 'ff',
            'C': 'ff',
            't': 'ffff',
            'T': 'ffff',
            'i': 'ffffffff',
            'I': 'ffffffff',
            'l': '00000000ffffffff',
            'L': '00000000ffffffff',
            'h': 'ffffffff00000000ffffffff00000000ffffffff00000000ffffffff00000000',
        }

        oracles_response = {
            's_un': 'Anton',
            'S_un': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'd_un': '01',
            'D_un': '01',
            'c_un': '-1',
            'C_un': '255',
            't_un': '-1',
            'T_un': '65535',
            'i_un': '-1',
            'I_un': '4294967295',
            'l_un': '-4294967296',
            'L_un': '18446744069414584320',
            'h_un': '00000000ffffffff00000000ffffffff00000000ffffffff00000000ffffffff'
        }

        rpc = test_params.get('node1').get('rpc')

        for o_type in oracles_data.keys():
            oracle = TestOraclesCCcalls.new_oracle(rpc, o_type=o_type)

            res = rpc.oraclesfund(oracle.get('oracle_id'))
            txid = rpc.sendrawtransaction(res.get('hex'))
            mine_and_waitconfirms(txid, rpc)

            res = rpc.oraclesregister(oracle.get('oracle_id'), '10000000')
            txid = rpc.sendrawtransaction(res.get('hex'))
            mine_and_waitconfirms(txid, rpc)

            oraclesinfo = rpc.oraclesinfo(oracle.get('oracle_id'))
            publisher = oraclesinfo.get('registered')[0].get('publisher')
            res = rpc.oraclessubscribe(oracle.get('oracle_id'), publisher, '0.1')
            txid = rpc.sendrawtransaction(res.get('hex'))
            mine_and_waitconfirms(txid, rpc)

            res = rpc.oraclesdata(oracle.get('oracle_id'), oracles_data.get(o_type))
            assert res.get('result') == 'success'
            o_data = rpc.sendrawtransaction(res.get("hex"))
            mine_and_waitconfirms(o_data, rpc)

            oraclesinfo = rpc.oraclesinfo(oracle.get('oracle_id'))
            baton = oraclesinfo.get('registered')[0].get('batontxid')

            res = rpc.oraclessample(oracle.get('oracle_id'), baton)
            assert (res.get('data')[0] == oracles_response.get(str(o_type) + '_un'))
