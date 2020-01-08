#!/usr/bin/env python3
# Copyright (c) 2020 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
import os
import time
from decimal import *
from pytest_util import validate_template


@pytest.mark.usefixtures("proxy_connection")
class TestDexP2P:

    def test_DEXbase(self, test_params):
        rpc1 = test_params.get('node1').get('rpc')
        schema_stats = {
            'type': 'object',
            'properties': {
                'publishable_pubkey': {'type': 'string'},
            },
            'required': ['publishable_pubkey']
        }
        schema_broadcast = {
            'type': 'object',
            'properties': {
                'timestamp': {'type': 'integer'},
                'id': {'type': 'integer'},
                'tagA': {'type': 'string'},
                'tagB': {'type': 'string'},
                'destpub': {'type': 'string'},
                'payload': {'type': 'string'},
                'hex': {'type': 'integer'},
                'amountA': {'type': ['integer', 'number']},
                'amountB': {'type': ['integer', 'number']},
                'priority': {'type': 'integer'},
            },
            'required': ['timestamp', 'id', 'tagA', 'tagB', 'destpub', 'payload', ]
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
                            'decryptedhex': {'type': 'integer'}
                        }
                    }
                }
            },
            'required': ['tagA', 'tagB', 'destpub', 'n']
        }
        res = rpc1.DEX_stats()
        validate_template(res, schema_stats)
        pubkey = res.get('publishable_pubkey')
        priority = '4'
        taga = ""
        tagb = ""
        amounta = ""
        amountb = ""
        stopat = ""
        minpriority = ""
        message = 'testmessage'
        res = rpc1.DEX_broadcast(message, priority, taga, tagb, pubkey, amounta, amountb)
        validate_template(res, schema_broadcast)
        res = rpc1.DEX_list(stopat, minpriority, taga, tagb, pubkey)
        validate_template(res, schema_list)
