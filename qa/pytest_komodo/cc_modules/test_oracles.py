#!/usr/bin/env python3
# Copyright (c) 2021 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
from slickrpc.exc import RpcException as RPCError
from lib.pytest_util import validate_template, mine_and_waitconfirms, randomstring,\
                            randomhex, validate_raddr_pattern


@pytest.mark.usefixtures("proxy_connection", "test_params")
class TestOraclesCC:

    def test_oraclescreate_list_info(self, oracle_instance):
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

        # test oracle creation
        oracle_instance.new_oracle(oracle_instance.rpc2, schema=create_schema)

        res = oracle_instance.rpc1.oracleslist()
        validate_template(res, list_schema)

        res = oracle_instance.rpc1.oraclesinfo(oracle_instance.base_oracle.get('oracle_id'))
        validate_template(res, info_schema)

    def test_oraclesaddress(self, oracle_instance):

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

        res = oracle_instance.rpc1.oraclesaddress(oracle_instance.pubkey1)
        validate_template(res, oraclesaddress_schema)

        res = oracle_instance.rpc1.oraclesaddress(oracle_instance.pubkey1)
        for key in res.keys():
            if key.find('ddress') > 0:
                assert validate_raddr_pattern(res.get(key))

        res = oracle_instance.rpc1.oraclesaddress()
        for key in res.keys():
            if key.find('ddress') > 0:
                assert validate_raddr_pattern(res.get(key))

    def test_oracles_data_interactions(self, oracle_instance):
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

        amount = '10000000'
        sub_amount = '0.1'

        # Fund fresh oracle
        res = oracle_instance.rpc1.oraclesfund(oracle_instance.base_oracle.get('oracle_id'))
        validate_template(res, general_hex_schema)
        txid = oracle_instance.rpc1.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, oracle_instance.rpc1)

        # Register as publisher
        res = oracle_instance.rpc1.oraclesregister(oracle_instance.base_oracle.get('oracle_id'), amount)
        validate_template(res, general_hex_schema)
        txid = oracle_instance.rpc1.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, oracle_instance.rpc1)

        # Subscrive to new oracle
        oraclesinfo = oracle_instance.rpc1.oraclesinfo(oracle_instance.base_oracle.get('oracle_id'))
        publisher = oraclesinfo.get('registered')[0].get('publisher')
        res = oracle_instance.rpc1.oraclessubscribe(oracle_instance.base_oracle.get('oracle_id'), publisher, sub_amount)
        validate_template(res, general_hex_schema)
        txid = oracle_instance.rpc1.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, oracle_instance.rpc1)

        # Publish new data
        res = oracle_instance.rpc1.oraclesdata(oracle_instance.base_oracle.get('oracle_id'), '0a74657374737472696e67')  # teststring
        validate_template(res, general_hex_schema)
        txid = oracle_instance.rpc1.oracle(res.get('hex'))
        mine_and_waitconfirms(txid, oracle_instance.rpc1)

        # Check data
        oraclesinfo = oracle_instance.rpc1.oraclesinfo(oracle_instance.base_oracle.get('oracle_id'))
        baton = oraclesinfo.get('registered')[0].get('batontxid')
        res = oracle_instance.rpc1.oraclessample(oracle_instance.base_oracle.get('oracle_id'), baton)
        validate_template(res, sample_schema)
        assert res.get('txid') == baton

    def test_bad_calls(self, oracle_instance):
        oracle = oracle_instance
        # trying to register with negative datafee
        res = oracle.rpc1.oraclesregister(oracle.base_oracle.get('oracle_id'), "-100")
        assert res.get('error')

        # trying to register with zero datafee
        res = oracle.rpc1.oraclesregister(oracle.base_oracle.get('oracle_id'), "0")
        assert res.get('error')

        # trying to register with datafee less than txfee
        res = oracle.rpc1.oraclesregister(oracle.base_oracle.get('oracle_id'), "500")
        assert res.get('error')

        # trying to register valid (unfunded)
        res = oracle.rpc1.oraclesregister(oracle.base_oracle.get('oracle_id'), "1000000")
        assert res.get('error')

        # trying to register with invalid datafee
        res = oracle.rpc1.oraclesregister(oracle.base_oracle.get('oracle_id'), "asdasd")
        assert res.get('error')

        # looking up non-existent oracle should return error.
        res = oracle.rpc1.oraclesinfo("none")
        assert res.get('error')

        # attempt to create oracle with not valid data type should return error
        res = oracle.rpc1.oraclescreate("Test", "Test", "Test")
        assert res.get('error')

        # attempt to create oracle with name > 32 symbols should return error
        too_long_name = randomstring(33)
        res = oracle.rpc1.oraclescreate(too_long_name, "Test", "s")
        assert res.get('error')

        # attempt to create oracle with description > 4096 symbols should return error
        too_long_description = randomstring(4100)
        res = oracle.rpc1.oraclescreate("Test", too_long_description, "s")
        assert res.get('error')

#    def test_oracles_data(self):
#        oracles_data = {
#            's': '05416e746f6e',
#            'S': '000161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161',
#            'd': '0101',
#            'D': '010001',
#            'c': 'ff',
#            'C': 'ff',
#            't': 'ffff',
#            'T': 'ffff',
#            'i': 'ffffffff',
#            'I': 'ffffffff',
#            'l': '00000000ffffffff',
#            'L': '00000000ffffffff',
#            'h': 'ffffffff00000000ffffffff00000000ffffffff00000000ffffffff00000000',
#        }
#
#        oracles_response = {
#            's_un': 'Anton',
#            'S_un': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
#            'd_un': '01',
#            'D_un': '01',
#            'c_un': '-1',
#            'C_un': '255',
#            't_un': '-1',
#            'T_un': '65535',
#            'i_un': '-1',
#            'I_un': '4294967295',
#            'l_un': '-4294967296',
#            'L_un': '18446744069414584320',
#            'h_un': '00000000ffffffff00000000ffffffff00000000ffffffff00000000ffffffff'
#        }
#
#        oracles = (OraclesCC.new_oracle(OraclesCC.rpc1, o_type=o_type) for o_type in oracles_data.keys())
#
#        for oracle in oracles:
#            res = OraclesCC.rpc1.oraclesfund(oracle.get('oracle_id'))
#            txid = (OraclesCC.rpc1.sendrawtransaction(res.get('hex')))
#        mine_and_waitconfirms(txid, OraclesCC.rpc1)
#
#        for oracle in oracles:
#            res = OraclesCC.rpc1.oraclesregister(oracle.get('oracle_id'), '10000000')
#            txid = (OraclesCC.rpc1.sendrawtransaction(res.get('hex')))
#        mine_and_waitconfirms(txid, OraclesCC.rpc1)
#
#        for oracle in oracles:
#            oraclesinfo = OraclesCC.rpc1.oraclesinfo(oracle.get('oracle_id'))
#            publisher = oraclesinfo.get('registered')[0].get('publisher')
#            res = OraclesCC.rpc1.oraclessubscribe(oracle.get('oracle_id'), publisher, '0.1')
#            txid = (OraclesCC.rpc1.sendrawtransaction(res.get('hex')))
#        mine_and_waitconfirms(txid, OraclesCC.rpc1)
#
#        for oracle, o_type in zip(oracles, oracles_data.keys()):
#            res = OraclesCC.rpc1.oraclesdata(oracle.get('oracle_id'), oracles_data.get(o_type))
#            assert res.get('result') == 'success'
#            o_data = OraclesCC.rpc1.sendrawtransaction(res.get("hex"))
#        mine_and_waitconfirms(o_data, OraclesCC.rpc1)
#
#        for oracle, o_type in zip(oracles, oracles_data.keys()):
#            oraclesinfo = OraclesCC.rpc1.oraclesinfo(oracle.get('oracle_id'))
#            baton = oraclesinfo.get('registered')[0].get('batontxid')
#
#            res = OraclesCC.rpc1.oraclessample(oracle.get('oracle_id'), baton)
#            assert (res.get('data')[0] == oracles_response.get(str(o_type) + '_un'))
