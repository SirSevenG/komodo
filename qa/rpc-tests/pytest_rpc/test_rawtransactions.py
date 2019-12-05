#!/usr/bin/env python3
# Copyright (c) 2019 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
from pytest_util import validate_template


@pytest.mark.usefixtures("proxy_connection")
class TestRawtransactions:

    def test_createrawtransaction(self, test_params):
        test_values = {
            'txid': test_params['txid'],
            'vout': '0',
            'address': test_params['address'],
            'amount': '1'
        }
        rpc = test_params.get('node1').get('rpc')
        # [[{"txid":"9f44dc664882198b14e9a8c466d466efcdd070ccb6f57be8e2884aa11e7b2a30","vout":0}],
        # {"RHCXHfXCZQpbUbihNHh5gTwfr7NXmJXmHi":0.01} ]
        res = rpc.createrawtransaction([{test_values['txid'], test_values['vout']},
                                        {test_values['address']: test_values['amount']}])
        assert isinstance(res, str)
