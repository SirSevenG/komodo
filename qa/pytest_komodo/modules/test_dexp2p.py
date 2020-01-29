#!/usr/bin/env python3
# Copyright (c) 2020 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://www.opensource.org/licenses/mit-license.php.

import pytest
import time
# from decimal import *
import os
import sys

sys.path.append('../')
from basic.pytest_util import validate_template, randomstring, in_99_range, collect_orderids,\
                              randomhex, get_size, write_file


@pytest.mark.usefixtures("proxy_connection")
class TestDexP2Prpc:

    def test_dexrpc(self, test_params):
        rpc1 = test_params.get('node1').get('rpc')
        schema_stats = {
            'type': 'object',
            'properties': {
                'publishable_pubkey': {'type': 'string'},
                'perfstats': {'type': 'string'}
            }
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
                'amountA': {'type': ['string']},
                'amountB': {'type': ['string']},
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
                            'amountA': {'type': ['string']},
                            'amountB': {'type': ['string']},
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
        schema_setpub = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'publishable_pubkey': {'type': 'string'},
                'perfstats': {'type': 'string'},
            }
        }
        schema_publish_subscribe = {
            'type': 'object',
            'properties': {
                'fname': {'type': 'string'},
                'result': {'type': 'string'},
                'id': {'type': 'integer'},
                'senderpub': {'type': 'string'},
                'filesize': {'type': 'integer'},
                'fragments': {'type': 'integer'},
                'numlocators': {'type': 'integer'},
                'filehash': {'type': 'string'}
            }
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
        order_id = str(res.get('id'))
        validate_template(res, schema_broadcast)

        # check get id
        res = rpc1.DEX_get(order_id)
        validate_template(res, schema_broadcast)  # same response to broadcast

        # check orderbook
        res = rpc1.DEX_orderbook('', '0', 'BASE', 'REL')
        validate_template(res, schema_orderbook)

        # cancel order
        res = rpc1.DEX_cancel(order_id)
        validate_template(res, schema_broadcast)
        # currently cancel has response similar to broadcast => subject to change
        assert res.get('tagA') == 'cancel'

        # publish file
        file = 'to_publish.txt'
        write_file(file)
        res = rpc1.DEX_publish(file, '0')
        validate_template(res, schema_publish_subscribe)
        print(res)
        assert res.get('result') == 'success'

        # subscribe to published file
        res = rpc1.DEX_subscribe(file, '0', '0', pubkey)
        validate_template(res, schema_publish_subscribe)
        assert res.get('result') == 'success'

        # check setpubkey with random pubkey-like string
        res = rpc1.DEX_setpubkey('01' + randomhex())
        validate_template(res, schema_setpub)
        assert res.get('result') == 'success'


@pytest.mark.usefixtures("proxy_connection")
class TestDexP2Pe2e:

    def test_dex_broadcast_get(self, test_params):
        rpc1 = test_params.get('node1').get('rpc')
        message_static = randomstring(22)
        taga_valid = 'inbox'
        tagb_valid = randomstring(15)
        taga_invalid = randomstring(16)
        tagb_invalid = randomstring(16)
        amounta = '11'
        amountb = '12'
        priority = '1'
        pubkey = rpc1.DEX_stats().get('publishable_pubkey')

        # broadacast messages
        res = rpc1.DEX_broadcast(message_static, priority, taga_valid, tagb_valid, pubkey, amounta, amountb)
        assert res.get('tagA') == taga_valid
        assert res.get('tagB') == tagb_valid
        assert res.get('pubkey') == pubkey
        assert float(res.get('amountA')) == float(amounta)
        assert float(res.get('amountB')) == float(amountb)
        assert int(priority) <= int(res.get('priority'))

        # DEX_get should return exact same blob as broadcast above
        get_order = rpc1.DEX_get(str(res.get('id')))
        assert res == get_order

        res = rpc1.DEX_broadcast(message_static, priority, '', tagb_valid, pubkey, amounta, amountb)
        assert not res.get('tagA')
        assert res.get('tagB') == tagb_valid
        assert res.get('pubkey') == pubkey
        assert float(res.get('amountA')) == float(amounta)
        assert float(res.get('amountB')) == float(amountb)
        assert int(priority) <= int(res.get('priority'))

        res = rpc1.DEX_broadcast(message_static, priority, taga_valid, '', pubkey, amounta, amountb)
        assert not res.get('tagB')
        assert res.get('tagA') == taga_valid
        assert res.get('pubkey') == pubkey
        assert float(res.get('amountA')) == float(amounta)
        assert float(res.get('amountB')) == float(amountb)
        assert int(priority) <= int(res.get('priority'))

        res = rpc1.DEX_broadcast(message_static, priority, taga_valid, tagb_valid, '', amounta, amountb)
        assert res.get('tagA') == taga_valid
        assert res.get('tagB') == tagb_valid
        assert not res.get('pubkey')
        assert float(res.get('amountA')) == float(amounta)
        assert float(res.get('amountB')) == float(amountb)
        assert int(priority) <= int(res.get('priority'))

        res = rpc1.DEX_broadcast(message_static, priority, '', tagb_valid, '', amounta, amountb)
        assert not res.get('tagA')
        assert res.get('tagB') == tagb_valid
        assert not res.get('pubkey')
        assert float(res.get('amountA')) == float(amounta)
        assert float(res.get('amountB')) == float(amountb)
        assert int(priority) <= int(res.get('priority'))

        res = rpc1.DEX_broadcast(message_static, priority, taga_valid, '', '', amounta, amountb)
        assert not res.get('tagB')
        assert res.get('tagA') == taga_valid
        assert not res.get('pubkey')
        assert float(res.get('amountA')) == float(amounta)
        assert float(res.get('amountB')) == float(amountb)
        assert int(priority) <= int(res.get('priority'))

        res = rpc1.DEX_broadcast(message_static, priority, '', '', pubkey, amounta, amountb)
        assert not res.get('tagA')
        assert not res.get('tagB')
        assert res.get('pubkey') == pubkey
        assert float(res.get('amountA')) == float(amounta)
        assert float(res.get('amountB')) == float(amountb)
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
        rpc2 = test_params.get('node2').get('rpc')
        message_static = randomstring(22)
        minpriority = ['0', '9']
        priority = ['1', '9']
        taga = randomstring(15)
        tagb = randomstring(15)
        amounta = ['11.234', '1']
        amountb = ['12.0099', '4']
        stopat = ''
        pubkey = rpc1.DEX_stats().get('publishable_pubkey')

        num_broadcast = 100
        for num in range(num_broadcast):
            rpc1.DEX_broadcast((message_static + str(num)), '4', 'inbox', 'tag_test100', '', '', '')
        list1 = rpc1.DEX_list(stopat, minpriority[0], '', 'tag_test100', '')
        list2 = rpc2.DEX_list(stopat, minpriority[0], '', 'tag_test100', '')
        time.sleep(5)  # time to sync broadcasts for both nodes
        assert num_broadcast == list1.get('n')

        num_broadcast = 10000
        for num in range(num_broadcast):
            rpc1.DEX_broadcast((message_static + str(num)), minpriority[0], 'inbox', 'tag_test10k', '', '', '')
        list1 = rpc1.DEX_list(stopat, minpriority[0], '', 'tag_test10k', '')
        time.sleep(5)
        assert in_99_range(list1['n'], num_broadcast)

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
            res = rpc1.DEX_broadcast((message_static + str(num_broadcast_orders + i)), priority[i], taga, tagb,
                                     pubkey, amounta[i], amountb[i])
            ids.append(res.get('id'))
            hashes.append(res.get('hash'))
        time.sleep(10)
        # DEX_list stopat minpriority taga tagb pubkey mina maxa minb maxb stophash
        res_min0 = rpc1.DEX_list(stopat, minpriority[0], taga, '', '')
        assert int(res_min0.get('n')) == 32
        # Should have less broadcasts with high priority
        # Can't operate set numbers here
        res_min1 = rpc1.DEX_list(stopat, minpriority[1], taga, '', '')
        assert int(res_min1.get('n')) < int(res_min0.get('n'))
        # base listing check
        res = rpc1.DEX_list(stopat, minpriority[0], '', tagb, '')
        assert int(res.get('n')) == 32
        res = rpc1.DEX_list(stopat, minpriority[0], '', '', pubkey)
        assert int(res.get('n')) >= 26  # including previous broadcasts with same pubkey, might be more than 26
        # in case when tests are run together
        res = rpc1.DEX_list(stopat, minpriority[0], taga, tagb, pubkey)
        assert int(res.get('n')) == 8
        res = rpc1.DEX_list(stopat, minpriority[0], taga, '', pubkey)
        assert int(res.get('n')) == 14
        res = rpc1.DEX_list(stopat, minpriority[0], '', tagb, pubkey)
        assert int(res.get('n')) == 14
        res = rpc1.DEX_list(stopat, minpriority[0], taga, tagb, '')
        assert int(res.get('n')) == 20

        # check amounts
        res = rpc1.DEX_list(stopat, minpriority[0], taga, tagb, '', amounta[1], amounta[0], amountb[1], amountb[0])
        assert int(res.get('n')) == 20
        res = rpc1.DEX_list(stopat, minpriority[0], taga, tagb, '', '', '', amountb[1], amountb[0])
        assert int(res.get('n')) == 20
        res = rpc1.DEX_list(stopat, minpriority[0], taga, tagb, '', '', amounta[0], amountb[1], '')
        assert int(res.get('n')) == 20
        res = rpc1.DEX_list(stopat, minpriority[0], taga, tagb, '', amounta[0], '', '', '')
        assert int(res.get('n')) == 10

        # check stopat
        res = rpc1.DEX_list(str(ids[1]), minpriority[0], taga, '', '')
        assert int(res.get('n')) == 0  # ids[1] is last id
        res = rpc1.DEX_list(str(ids[0]), minpriority[0], taga, '', '')
        assert int(res.get('n')) == 16

        # check stophash
        res = rpc1.DEX_list(stopat, minpriority[0], taga, '', '', '', '', '', '', hashes[1])
        assert int(res.get('n')) == 0  # hashes[1] is the last orders' hash
        res = rpc1.DEX_list(stopat, minpriority[0], taga, '', '', '', '', '', '', hashes[0])
        assert int(res.get('n')) == 16

    def test_dex_orderbooks_cancel(self, test_params):
        rpc1 = test_params.get('node1').get('rpc')
        message = randomstring(15)
        priority = '4'
        base = randomstring(6)
        rel = randomstring(6)
        amounta = '81.44'
        amountb = '0.7771'
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
        price_calc = float(amountb) / float(amounta)
        price_res = float(res.get('asks')[0].get('price'))
        assert round(price_calc, 6) == round(price_res, 6)  # rounding due to possible diff in 8th decimal
        res = rpc1.DEX_orderbook('', '0', rel, base, '')
        assert not res['asks']
        price_calc = float(amounta) / float(amountb)
        price_res = float(res.get('bids')[0].get('price'))
        assert round(price_calc, 6) == round(price_res, 6)

        # cancel order by id
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

        # broadcast more orders with different tags to cancel
        unique_pairs = 2
        base_list = []
        rel_list = []
        for i in range(unique_pairs):
            base_list.append(randomstring(6))
            rel_list.append(randomstring(6))
        message = randomstring(15)
        amounta = '0.7777'
        amountb = '0.66'
        for i in range(unique_pairs):
            for num in range(5):
                rpc1.DEX_broadcast((message + str(num)), priority, base_list[i], rel_list[i], pubkey, amounta, amountb)
                rpc1.DEX_broadcast((message + str(num)), priority, rel_list[i], base_list[i], pubkey, amounta, amountb)
        time.sleep(15)  # orders should be old enough to be cancelled by tag/pubkey

        # cancel by tags
        blobs1 = collect_orderids(rpc1.DEX_list('', '', base_list[0], rel_list[0], pubkey), 'matches')
        blobs2 = collect_orderids(rpc1.DEX_list('', '', base_list[1], rel_list[1], pubkey), 'matches')
        res = rpc1.DEX_cancel('', '', base_list[0], rel_list[0])  # cancel all orders with pubkey by tags pair
        cancel = res.get('timestamp')
        for blob in blobs1:
            res = rpc1.DEX_get(blob)
            assert res.get('cancelled') == cancel
        for blob in blobs2:  # other pairs must be unaffected
            res = rpc1.DEX_get(blob)
            assert res.get('cancelled') == 0

        # cancel by pubkey
        res = rpc1.DEX_cancel('', pubkey)
        cancel = res.get('timestamp')
        for blob in blobs2:
            res = rpc1.DEX_get(blob)
            assert res.get('cancelled') == cancel

    # not yet ready
    #def test_file_publish(self, test_params):
        #rpc1 = test_params.get('node1').get('rpc')
        #rpc2 = test_params.get('node2').get('rpc')
        #pubkey = rpc1.DEX_stats().get('publishable_pubkey')
        #filename1 = 'file_' + randomstring(5)
        #write_file(filename1)
        #filename2 = 'file_' + randomstring(5)
        #write_file(filename2)
        #size1 = get_size(filename1)
        #size2 = get_size(filename2)
#
        ## publish both files on 1st node
        #res = rpc1.DEX_publish(filename1, '0')
        #assert not res  # empty response on success => subject to change
        #res = rpc1.DEX_publish(filename2, '0')
        #assert not res
#
        ## Both nodes should be able locate file by files tag and locators tag
        ## os.path.getsize(file_path)
        #res = rpc1.DEX_list('0', '0', 'files')
        #print(res)
        #res = rpc2.DEX_list('0', '0', 'files')
        #print(res)
        #res = rpc1.DEX_list('0', '0', filename1, 'locators')
        #print(res)
        #res = rpc1.DEX_list('0', '0', filename2, 'locators')
        #print(res)
        #res = rpc2.DEX_list('0', '0', filename1, 'locators')
        #print(res)
        #res = rpc2.DEX_list('0', '0', filename2, 'locators')
        #print(res)


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
