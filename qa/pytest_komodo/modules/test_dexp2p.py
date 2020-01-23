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
from basic.pytest_util import validate_template, randomstring, in_99_range, collect_orderids

# TODO: uncomment cancel id tests and add DEX_cancel [pubkey] check when fixed

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
                            'baseamount': {'type': 'string'},
                            'basesatoshis': {'type': 'integer'},
                            'relamount': {'type': 'string'},
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
        res = rpc1.DEX_broadcast(message, '4', 'BASE', 'REL', pubkey, '100', '1')
        id = str(res.get('id'))
        validate_template(res, schema_broadcast)
        # check orderbook
        res = rpc1.DEX_orderbook('', '0', 'BASE', 'REL')
        validate_template(res, schema_orderbook)
        # cancel order
        res = rpc1.DEX_cancel(id)
        assert res.get('tagA') == 'cancel'  # currently cancel has response similar to broadcast => subject to change


@pytest.mark.usefixtures("proxy_connection")
class TestDexP2Pe2e:

    def test_dex_broadcast(self, test_params):
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
        assert int(priority) <= int(res.get('priority'))

        res = rpc1.DEX_broadcast(message_static, priority, '', tagb_valid, pubkey, amounta, amountb)
        assert not res.get('tagA')
        assert res.get('tagB') == tagb_valid
        assert res.get('pubkey') == pubkey
        assert str(res.get('amountA')) == amounta
        assert str(res.get('amountB')) == amountb
        assert int(priority) <= int(res.get('priority'))

        res = rpc1.DEX_broadcast(message_static, priority, taga_valid, '', pubkey, amounta, amountb)
        assert not res.get('tagB')
        assert res.get('tagA') == taga_valid
        assert res.get('pubkey') == pubkey
        assert str(res.get('amountA')) == amounta
        assert str(res.get('amountB')) == amountb
        assert int(priority) <= int(res.get('priority'))

        res = rpc1.DEX_broadcast(message_static, priority, taga_valid, tagb_valid, '', amounta, amountb)
        assert res.get('tagA') == taga_valid
        assert res.get('tagB') == tagb_valid
        assert not res.get('pubkey')
        assert str(res.get('amountA')) == amounta
        assert str(res.get('amountB')) == amountb
        assert int(priority) <= int(res.get('priority'))

        res = rpc1.DEX_broadcast(message_static, priority, '', tagb_valid, '', amounta, amountb)
        assert not res.get('tagA')
        assert res.get('tagB') == tagb_valid
        assert not res.get('pubkey')
        assert str(res.get('amountA')) == amounta
        assert str(res.get('amountB')) == amountb
        assert int(priority) <= int(res.get('priority'))

        res = rpc1.DEX_broadcast(message_static, priority, taga_valid, '', '', amounta, amountb)
        assert not res.get('tagB')
        assert res.get('tagA') == taga_valid
        assert not res.get('pubkey')
        assert str(res.get('amountA')) == amounta
        assert str(res.get('amountB')) == amountb
        assert int(priority) <= int(res.get('priority'))

        res = rpc1.DEX_broadcast(message_static, priority, '', '', pubkey, amounta, amountb)
        assert not res.get('tagA')
        assert not res.get('tagB')
        assert res.get('pubkey') == pubkey
        assert str(res.get('amountA')) == amounta
        assert str(res.get('amountB')) == amountb
        assert int(priority) <= int(res.get('priority'))

        res = rpc1.DEX_broadcast(message_static, priority, '', '', '', '', '')
        assert res.get('tagA') == 'general'
        assert not res.get('tagB')
        assert not res.get('destpub')
        assert res.get('payload') == message_static
        assert int(priority) <= int(res.get('priority'))

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

    def test_dex_listing(self, test_params):
        rpc1 = test_params.get('node1').get('rpc')
        message_static = randomstring(22)
        taga = randomstring(15)
        tagb = randomstring(15)
        amounta = ['11.234', '1']
        amountb = ['12.0099', '4']
        stopat = ''
        minpriority = ['0', '9']
        priority = ['1', '9']
        pubkey = rpc1.DEX_stats().get('publishable_pubkey')

        num_broadcast = 100
        for num in range(num_broadcast):
            rpc1.DEX_broadcast((message_static + str(num)), priority[0], 'inbox', 'tag_test100', '', '', '')
        list1 = rpc1.DEX_list(stopat, minpriority[0], '', 'tag_test100', '')
        time.sleep(5)
        assert num_broadcast == list1.get('n')

        num_broadcast = 10000
        for num in range(num_broadcast):
            rpc1.DEX_broadcast((message_static + str(num)), minpriority[0], 'inbox', 'tag_test10k', '', '', '')
        list1 = rpc1.DEX_list(stopat, minpriority[0], '', 'tag_test10k', '')
        time.sleep(5)
        assert in_99_range(list1['n'], num_broadcast)

        # DEX_list stopat minpriority tagA tagB pubkey33 minA maxA minB maxB stophash
        # Broadcast orders to sort
        num_broadcast_orders = 3
        num_cycles = 2  # equal to amount[] entries above
        ids = []
        hashes = []
        for i in range(num_cycles):
            for num in range(num_broadcast_orders):
                rpc1.DEX_broadcast((message_static + str(num)), priority[i], taga, tagb, pubkey, amounta[i], amountb[i])
                rpc1.DEX_broadcast((message_static + str(num)), priority[i], taga, tagb, '', amounta[i], amountb[i])
                rpc1.DEX_broadcast((message_static + str(num)), priority[i], '', tagb, pubkey, amounta[i], amountb[i])
                rpc1.DEX_broadcast((message_static + str(num)), priority[i], taga, '', pubkey, amounta[i], amountb[i])
                rpc1.DEX_broadcast((message_static + str(num)), priority[i], '', tagb, '', amounta[i], amountb[i])
                rpc1.DEX_broadcast((message_static + str(num)), priority[i], taga, '', '', amounta[i], amountb[i])
                rpc1.DEX_broadcast((message_static + str(num)), priority[i], taga, tagb, '', amounta[i], amountb[i])
                rpc1.DEX_broadcast((message_static + str(num)), priority[i], '', '', pubkey, amounta[i], amountb[i])
            # get ids and hashes to use later
            res = rpc1.DEX_broadcast(message_static, priority[i], taga, tagb, pubkey, amounta[i], amountb[i])
            ids.append(res.get('id'))
            hashes.append(res.get('hash'))

        for i in range(num_cycles):
            res = rpc1.DEX_list(stopat, minpriority[i], taga, tagb, pubkey, '', '', '', '', '')
            print("\n\n----------", res.get('n'))
            res = rpc1.DEX_list(stopat, minpriority[i], '', tagb, pubkey, '', '', '', '', '')
            print("\n\n----------", res.get('n'))
            res = rpc1.DEX_list(stopat, minpriority[i], taga, '', pubkey, '', '', '', '', '')
            print("\n\n----------", res.get('n'))
            res = rpc1.DEX_list(stopat, minpriority[i], taga, tagb, '', '', '', '', '', '')
            print("\n\n----------", res.get('n'))
            res = rpc1.DEX_list(stopat, minpriority[i], '', '', pubkey, '', '', '', '', '')
            print("\n\n----------", res.get('n'))

    def test_dex_orderbooks(self, test_params):
        rpc1 = test_params.get('node1').get('rpc')
        message = randomstring(15)
        priority = '4'
        base = randomstring(6)
        rel = randomstring(6)
        amounta = '1000'
        amountb = '1'
        pubkey = rpc1.DEX_stats().get('publishable_pubkey')

        # broadcast orderbooks
        res = rpc1.DEX_broadcast(message, priority, base, rel, pubkey, amounta, amountb)
        assert res['tagA'] == base
        assert res['tagB'] == rel
        assert res['cancelled'] == 0
        order_pubkey_id = str(res['id'])
        res = rpc1.DEX_broadcast(message, priority, base, rel, '', amounta, amountb)
        order_nopub_id = str(res['id'])
        # swapping base - rel values, asks - bids should swap accordingly
        # this simple test works under assumption that random tags are unique
        res = rpc1.DEX_orderbook('', '0', base, rel, '')
        assert not res['bids']
        res = rpc1.DEX_orderbook('', '0', rel, base, '')
        assert not res['asks']

        # cancel order
        res = rpc1.DEX_cancel(order_pubkey_id)
        assert res.get('tagA') == 'cancel'
        # cancelled order should be excluded from list
        res = rpc1.DEX_orderbook('', '0', base, rel, '')
        for order in res.get('asks'):  # should return only asks here
            assert str(order.get('id')) != order_pubkey_id
        # order should have its cancellation timestamp in list response as cancelled property
        res = rpc1.DEX_list('', '', base, '', '')
        for blob in res.get('matches'):
            if str(blob.get('id')) == order_pubkey_id:
                assert blob.get('cancelled') > 0

        # orders broadcast without pubkey should not be cancelled
        res = rpc1.DEX_cancel(order_nopub_id)
        assert res.get('tagA') == 'cancel'
        res = rpc1.DEX_orderbook('', '0', base, rel, '')
        orders = collect_orderids(res, 'asks')
        assert order_nopub_id in orders
        res = rpc1.DEX_list('', '', base, '', '')
        blobs = collect_orderids(res, 'matches')
        assert order_nopub_id in blobs

    def test_dex_encryption(self, test_params):
        rpc1 = test_params.get('node1').get('rpc')
        message = randomstring(15)
        priority = '8'
        taga = randomstring(6)
        tagb = randomstring(6)
        pubkey1 = rpc1.DEX_stats().get('publishable_pubkey')

        # case1
        # blob sent without pubkey -- message should not be encrypted
        res = rpc1.DEX_broadcast(message, priority, taga, tagb, '', '', '')
        blob_bc_id = res.get('id')
        res = rpc1.DEX_list('', '', taga, tagb, '')
        message_res = ''
        pubkey_res = ''
        for blob in res.get('matches'):
            if blob.get('id') == blob_bc_id:
                message_res = blob.get('payload')
                pubkey_res = blob.get('pubkey')
        assert message_res == message
        assert not pubkey_res
        # case 2
        # blob with pubkey -- message should be encrypted and visible to key owner
        res = rpc1.DEX_broadcast(message, priority, taga, tagb, pubkey1, '', '')
        blob_bc_id = res.get('id')
        res = rpc1.DEX_list('', '', taga, tagb, '')
        message_res = ''
        decrypt_res = ''
        pubkey_res = ''
        for blob in res.get('matches'):
            if blob.get('id') == blob_bc_id:
                message_res = blob.get('payload')
                decrypt_res = blob.get('decrypted')
                pubkey_res = blob.get('pubkey')
        assert message_res != message
        assert decrypt_res == message
        assert pubkey_res == pubkey1
