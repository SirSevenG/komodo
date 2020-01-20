#!/usr/bin/env python3
# Copyright (c) 2020 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
import time
# from decimal import *
# import os
import sys

sys.path.append('../')
from basic.pytest_util import validate_template, randomstring, in_99_range


@pytest.mark.usefixtures("proxy_connection")
class TestDexP2Prpc:

    def test_dexrpc(self, test_params):
        rpc1 = test_params.get('node1').get('rpc')
        schema_stats = {
            'type': 'object',
            'properties': {
                'publishable_pubkey': {'type': 'string'},
                'perfstats': {'type': 'string'}
            },
            'required': ['publishable_pubkey']
        }
        schema_broadcast = {
            'type': 'object',
            'properties': {
                'timestamp': {'type': 'integer'},
                'recvtime': {'type': 'integer'},
                'id': {'type': 'integer'},
                'tagA': {'type': 'string'},
                'tagB': {'type': 'string'},
                'senderpub': {'type': 'string'},
                'destpub': {'type': 'string'},
                'payload': {'type': 'string'},
                'hex': {'type': 'integer'},
                'amountA': {'type': ['integer', 'number']},
                'amountB': {'type': ['integer', 'number']},
                'priority': {'type': 'integer'},
                'error': {'type': 'string'},
                'cancelled': {'type': 'integer'}
            },
            'required': ['timestamp', 'id', 'tagA', 'tagB', 'payload']
        }
        schema_list = {
            'type': 'object',
            'properties': {
                'tagA': {'type': 'string'},
                'tagB': {'type': 'string'},
                'destpub': {'type': 'string'},
                'n': {'type': 'integer'},
                'matches': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'timestamp': {'type': 'integer'},
                            'id': {'type': 'integer'},
                            'hex': {'type': 'integer'},
                            'priority': {'type': 'integer'},
                            'amountA': {'type': ['integer', 'number']},
                            'amountB': {'type': ['integer', 'number']},
                            'tagA': {'type': 'string'},
                            'tagB': {'type': 'string'},
                            'destpub': {'type': 'string'},
                            'payload': {'type': 'string'},
                            'decrypted': {'type': 'string'},
                            'decryptedhex': {'type': 'integer'},
                            'senderpub': {'type': 'string'},
                            'recvtime': {'type': 'integer'},
                            'error': {'type': 'string'},
                            'cancelled': {'type': 'integer'}
                        }
                    }
                }
            },
            'required': ['tagA', 'tagB', 'n']
        }
        schema_orderbook = {
            'type': 'object',
            'properties': {
                'asks': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'price': {'type': 'string'},
                            'price15': {'type': 'string'},
                            'baseamount': {'type': 'integer'},
                            'basesatoshis': {'type': 'integer'},
                            'relamount': {'type': 'integer'},
                            'relsatoshis': {'type': 'integer'},
                            'priority': {'type': 'integer'},
                            'timestamp': {'type': 'integer'},
                            'id': {'type': 'integer'},
                            'pubkey': {'type': 'string'},
                            'hash': {'type': 'string'}
                        }
                    }
                },
                'bids': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'price': {'type': 'string'},
                            'price15': {'type': 'string'},
                            'baseamount': {'type': 'integer'},
                            'basesatoshis': {'type': 'integer'},
                            'relamount': {'type': 'integer'},
                            'relsatoshis': {'type': 'integer'},
                            'priority': {'type': 'integer'},
                            'timestamp': {'type': 'integer'},
                            'id': {'type': 'integer'},
                            'pubkey': {'type': 'string'},
                            'hash': {'type': 'string'}
                        }
                    }
                }
            },
            'required': ['asks', 'bids']
        }
        res = rpc1.DEX_stats()
        validate_template(res, schema_stats)
        pubkey = res.get('publishable_pubkey')
        # inbox message broadcast
        message = 'testmessage'
        res = rpc1.DEX_broadcast(message, '4', 'inbox', '', pubkey, '', '')
        validate_template(res, schema_broadcast)
        # check dexlist
        res = rpc1.DEX_list('', '4', '', '', pubkey)
        validate_template(res, schema_list)
        # orderbook broadcast
        res = rpc1.DEX_broadcast(message, '4', 'BASE', 'REL', '', '100', '1')
        validate_template(res, schema_broadcast)
        # check orderbook
        res = rpc1.DEX_orderbook('', '0', 'BASE', 'REL')
        validate_template(res, schema_orderbook)
        # DEX_cancel is not included atm


@pytest.mark.usefixtures("proxy_connection")
class TestDexP2Pe2e:

    def test_dex_broadcast_and_listing(self, test_params):
        rpc1 = test_params.get('node1').get('rpc')
        message_static = randomstring(22)
        taga_valid = 'inbox'
        tagb_valid = randomstring(15)
        taga_invalid = randomstring(16)
        tagb_invalid = randomstring(16)
        amounta = '11'
        amountb = '12'
        stopat = ''
        minpriority = '0'
        priority = '1'
        pubkey = rpc1.DEX_stats().get('publishable_pubkey')

        # broadacast messages
        res = rpc1.DEX_broadcast(message_static, priority, taga_valid, tagb_valid, pubkey, amounta, amountb)
        assert res.get('tagA') == taga_valid
        assert res.get('tagB') == tagb_valid
        assert res.get('pubkey') == pubkey
        assert str(res.get('amountA')) == amounta
        assert str(res.get('amountB')) == amountb

        res = rpc1.DEX_broadcast(message_static, priority, '', '', pubkey, amounta, amountb)
        assert not res.get('tagA')
        assert not res.get('tagB')
        assert res.get('pubkey') == pubkey
        assert str(res.get('amountA')) == amounta
        assert str(res.get('amountB')) == amountb

        res = rpc1.DEX_broadcast(message_static, priority, '', '', '', '', '')
        assert res.get('tagA') == 'general'
        assert not res.get('tagB')
        assert not res.get('destpub')
        assert res.get('payload') == message_static

        # tags are restricted to 15 characters, rpc should fail or return -1
        try:
            res = rpc1.DEX_broadcast(message_static, priority, taga_invalid, '', '', '', '')
            if res != -1:
                raise Exception("Should have failed")
        except Exception as e:
            print(e)
        try:
            res = rpc1.DEX_broadcast(message_static, priority, '', tagb_invalid, '', '', '')
            if res != -1:
                raise Exception("Should have failed")
        except Exception as e:
            print(e)

        # test listing
        num_broadcast = 100
        for num in range(num_broadcast):
            rpc1.DEX_broadcast((message_static + str(num)), priority, 'inbox', 'tag_test100', '', '', '')
        list1 = rpc1.DEX_list(stopat, minpriority, '', 'tag_test100', '')
        time.sleep(5)
        assert num_broadcast == list1.get('n')

        num_broadcast = 10000
        for num in range(num_broadcast):
            rpc1.DEX_broadcast((message_static + str(num)), minpriority, 'inbox', 'tag_test10k', '', '', '')
        list1 = rpc1.DEX_list(stopat, minpriority, '', 'tag_test10k', '')
        time.sleep(5)
        assert in_99_range(list1['n'], num_broadcast)

    def test_dex_orderbooks(self, test_params):
        rpc1 = test_params.get('node1').get('rpc')
        message = randomstring(15)
        priority = '4'
        base = randomstring(6)
        rel = randomstring(6)
        amounta = '1000'
        amountb = '1'

        # broadcast orderbooks

        res = rpc1.DEX_broadcast(message, priority, base, rel, '', amounta, amountb)
        assert res['tagA'] == base
        assert res['tagB'] == rel
        assert res['cancelled'] == 0
        id = res['id']
        res = rpc1.DEX_orderbook('', '0', base, rel, '')
        # supposing tags are not real coins, swapping base - rel values, asks - bids should swap accordingly
        assert not res['bids']
        res = rpc1.DEX_orderbook('', '0', rel, base, '')
        assert not res['asks']
        # DEX_cancel is not working properly atm
        # TODO: add DEX_cancel test here for orders
