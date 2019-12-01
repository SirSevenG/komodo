#!/usr/bin/env python3
# Copyright (c) 2019 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
import json


def test_getinfo(proxy_connection):
    with open('nodesconfig.json', 'r') as f:
        params_dict = json.load(f)

    node1_params = params_dict["node1"]
    node2_params = params_dict["node2"]
    rpc = proxy_connection(node1_params)
    rpc1 = proxy_connection(node2_params)
    pubkey = node1_params["pubkey"]
    pubkey1 = node2_params["pubkey"]

    res = rpc.getinfo()
    assert res.get('result')
    res = rpc1.getinfo()
    assert res.get('result')
