#!/usr/bin/env python3
# Copyright (c) 2019 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
from pytest_util import validate_template


@pytest.mark.usefixtures("proxy_connection")
class TestRawtransactions:

    def test_rawtransactions(self, test_params):  # create, fund, sign, send calls
        fund_schema = {
            'type': 'object',
            'properties': {
                'hex': {'type': 'string'},
                'fee': {'type': ['integer', 'number']},
                'changepos': {'type': ['integer', 'number']}
            }
        }
        sign_schema = {
            'type': 'object',
            'properties': {
                'hex': {'type': 'string'},
                'complete': {'type': 'boolean'}
            }
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.listunspent()
        txid = res[0].get('txid')
        vout = res[0].get('vout')
        amount = res[0].get('amount') * 0.9
        address = rpc.getnewaddress()
        ins = [{'txid': txid, 'vout': vout}]
        outs = {address: amount}

        rawtx = rpc.createrawtransaction(ins, outs)
        assert isinstance(rawtx, str)

        fundtx = rpc.fundrawtransaction(rawtx)
        validate_template(fundtx, fund_schema)

        signtx = rpc.signrawtransaction(fundtx.get('hex'))
        validate_template(signtx, sign_schema)
        assert signtx['complete']

        sendtx = rpc.sendrawtransaction(signtx.get('hex'))
        assert isinstance(sendtx, str)

    def test_getrawtransaction(self, test_params):  # decode, get methods
        rpc = test_params.get('node1').get('rpc')
