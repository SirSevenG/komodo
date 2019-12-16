#!/usr/bin/env python3
# Copyright (c) 2019 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
import os
import time
from decimal import *
from pytest_util import validate_template, check_synced, mine_and_waitconfirms


@pytest.mark.usefixtures("proxy_connection")
class TestZcalls:

    def test_z_getnewaddress(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.z_getnewaddress()
        assert isinstance(res, str)

    def test_z_send(self, test_params):  # test sendmany, operationstatus and operationresult calls
        schema = {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                    'status': {'type': 'string'},
                    'creation_time': {'type': 'integer'},
                    'execution_secs': {'type': ['number', 'integer']},
                    'method': {'type': 'string'},
                    'error': {
                        'type': 'object',
                        'properties': {
                            'code': {'type': 'integer'},
                            'message': {'type': 'string'}
                        }
                    },
                    'result': {
                        'type': 'object',
                        'properties': {'txid': {'type': 'string'}}
                    },
                    'params': {
                        'type': 'object',
                        'properties': {
                            'fromaddress': {'type': 'string'},
                            'minconf': {'type': 'integer'},
                            'fee': {'type': ['number', 'integer']},
                            'amounts': {
                                'type': 'array',
                                'items': {
                                    'type': 'object',
                                    'properties': {
                                        'address': {'type': 'string'},
                                        'amount': {'type': ['integer', 'number']}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        rpc1 = test_params.get('node1').get('rpc')
        rpc2 = test_params.get('node2').get('rpc')
        transparent1 = rpc1.getnewaddress()
        shielded1 = rpc1.z_getnewaddress()
        transparent2 = rpc2.getnewaddress()
        shielded2 = rpc2.z_getnewaddress()
        amount = rpc1.getbalance() / 1000
        fee = 0.00005
        amount_full = rpc1.getbalance() - fee
        t_send = [{'address': transparent2, 'amount': amount}]
        z_send = [{'address': shielded2, 'amount': amount}]
        cases = [(transparent1, t_send), (transparent1, z_send), (shielded1, t_send), (shielded2, z_send)]
        # sendmany cannot use coinbase tx vouts
        txid = rpc1.sendtoaddress(transparent1, amount_full)
        mine_and_waitconfirms(txid, rpc1)

        if os.cpu_count() > 1:
            numthreads = (os.cpu_count() - 1)
        else:
            numthreads = 1
        rpc1.setgenerate(True, numthreads)
        assert check_synced(rpc1, rpc2)  # to perform z_sendmany nodes should be synced

        for case in cases:
            opid = rpc1.z_sendmany(case[0], case[1])
            assert isinstance(opid, str)
            attempts = 0
            while True:
                res = rpc1.z_getoperationstatus([opid])
                validate_template(res, schema)
                status = rpc1.z_getoperationstatus([opid])[0].get('status')
                if status == 'success':
                    print('Operation successfull\n')
                    res = rpc1.z_getoperationresult([opid])  # also clears op from memory
                    validate_template(res, schema)
                    break
                else:
                    attempts += 1
                    print('Waiting operation result\n')
                    time.sleep(10)
                if attempts >= 100:
                    print('operation timed out\n')
                    return False
        rpc1.setgenerate(False, numthreads)

    def test_z_getbalance(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        zaddr = rpc.z_getnewaddress()
        res = rpc.z_getbalance(zaddr, 1)
        assert isinstance(res, float) or isinstance(res, int) or isinstance(res, Decimal)

    def test_z_exportkey(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        zaddr = rpc.z_getnewaddress()
        res = rpc.z_exportkey(zaddr)
        assert isinstance(res, str)

    def test_z_importkey(self, test_params):
        rpc1 = test_params.get('node1').get('rpc')
        rpc2 = test_params.get('node2').get('rpc')
        zaddr = rpc2.z_getnewaddress()
        zkey = rpc2.z_exportkey(zaddr)
        res = rpc1.z_importkey(zkey)
        assert not res

    def test_z_listaddresses(self, test_params):
        schema = {
            'type': 'array',
            'items': {
                'type': 'string'
            }
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.z_listaddresses()
        validate_template(res, schema)

    def test_z_listopertaionsids(self, test_params):
        schema = {
            'type': 'array',
            'items': {
                'type': 'string'
            }
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.z_listoperationids()
        validate_template(res, schema)
        res = rpc.z_listoperationids('success')
        validate_template(res, schema)
