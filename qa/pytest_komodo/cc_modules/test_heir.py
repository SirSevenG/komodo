#!/usr/bin/env python3
# Copyright (c) 2019 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
import time
import jsonschema
import warnings
import sys
sys.path.append('../')
from basic.pytest_util import validate_template, mine_and_waitconfirms, randomstring
from util import assert_success, assert_error, send_and_mine, \
    rpc_connect, wait_some_blocks, komodo_teardown


@pytest.mark.usefixtures("proxy_connection")
class TestHeirCCcalls:

    def test_heirfund(self, test_params):
        heirfund_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'hex': {'type': 'string'},
                'error': {'type': 'string'}
            },
            'required': ['result']
        }

        rpc1 = test_params.get('node1').get('rpc')
        pubkey1 = test_params.get('node1').get('pubkey')
        amount = '100'
        name = 'heir' + randomstring(5)
        inactivitytime = '20'
        res = rpc1.heirfund(amount, name, pubkey1, inactivitytime, 'testMemo')
        validate_template(res, heirfund_schema)
        txid = rpc1.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, rpc1)

    def test_heiraddress(self, test_params):
        heiraddress_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'HeirCCAddress': {'type': 'string'},
                'CCbalance': {'type': 'number'},
                'HeirNormalAddress': {'type': 'string'},
                'HeirCC`1of2`Address': {'type': 'string'},
                'HeirCC`1of2`TokensAddress': {'type': 'string'},
                'myAddress': {'type': 'string'},
                'myCCAddress(Heir)': {'type': 'string'},
                'PubkeyCCAddress(Heir)': {'type': 'string'},
                'myCCaddress': {'type': 'string'},
                'myCCbalance': {'type': 'number'},
                'myaddress': {'type': 'string'},
                'mybakance': {'type': 'number'},
                'error': {'type': 'string'}
            },
            'required': ['result']
        }

        rpc1 = test_params.get('node1').get('rpc')
        pubkey1 = test_params.get('node1').get('pubkey')
        res = rpc1.heiraddress(pubkey1)
        validate_template(res, heiraddress_schema)
        assert res.get('result') == 'success'

    def test_heirlist(self, test_params):
        heirlist_schema = {
            'type': 'array',
            'items': {
                'type': 'string'
            }
        }

        rpc1 = test_params.get('node1').get('rpc')
        res = rpc1.heirlist()
        validate_template(res, heirlist_schema)

    def test_heiradd(self, test_params):
        hieradd_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'hex': {'type': 'string'},
                'error': {'type': 'string'}
            },
            'required': ['result']
        }

        rpc1 = test_params.get('node1').get('rpc')
        amount = '100'
        try:
            fundid = rpc1.heirlist()[0]
            res = rpc1.heiradd(amount, fundid)
            validate_template(res, hieradd_schema)
            assert res.get('result') == 'success'
            txid = rpc1.sendrawtransaction(res.get('hex'))
            mine_and_waitconfirms(txid, rpc1)
        except IndexError:
            print('\nNo heirplan on chain, creating one\n')
            pubkey1 = test_params.get('node1').get('pubkey')
            amount = '100'
            name = 'heir' + randomstring(5)
            inactivitytime = '20'
            res = rpc1.heirfund(amount, name, pubkey1, inactivitytime, 'testMemoHeirInfo')
            txid = rpc1.sendrawtransaction(res.get('hex'))
            mine_and_waitconfirms(txid, rpc1)
            fundid = rpc1.heirlist()[0]
            res = rpc1.heiradd(amount, fundid)
            validate_template(res, hieradd_schema)
            assert res.get('result') == 'success'
            txid = rpc1.sendrawtransaction(res.get('hex'))
            mine_and_waitconfirms(txid, rpc1)

    def test_heirinfo(self, test_params):
        heirinfo_schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'fundingtxid': {'type': 'string'},
                'owner': {'type': 'string'},
                'heir': {'type': 'string'},
                'type': {'type': 'string'},
                'lifetime': {'type': 'string'},
                'available': {'type': 'string'},
                'InactivityTimeSetting': {'type': 'string'},
                'IsHeirSpendingAllowed': {'type': 'string'},
                'memo': {'type': 'string'},
                'result': {'type': 'string'},
                'error': {'type': 'string'}
            },
            'required': ['result']
        }

        rpc1 = test_params.get('node1').get('rpc')
        try:
            fundid = rpc1.heirlist()[0]
            res = rpc1.heirinfo(fundid)
            validate_template(res, heirinfo_schema)
            assert res.get('result') == 'success'
        except IndexError:
            print('\nNo heirplan on chain, creating one\n')
            pubkey1 = test_params.get('node1').get('pubkey')
            amount = '100'
            name = 'heir' + randomstring(5)
            inactivitytime = '20'
            res = rpc1.heirfund(amount, name, pubkey1, inactivitytime, 'testMemoHeirInfo')
            txid = rpc1.sendrawtransaction(res.get('hex'))
            mine_and_waitconfirms(txid, rpc1)
            fundid = rpc1.heirlist()[0]
            res = rpc1.heirinfo(fundid)
            validate_template(res, heirinfo_schema)
            assert res.get('result') == 'success'

    def test_heirclaim(self, test_params):
        heirclaim_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'hex': {'type': 'string'},
                'error': {'type': 'string'}
            },
            'required': ['result']
        }

        rpc1 = test_params.get('node1').get('rpc')
        # create heir plan to claim
        pubkey1 = test_params.get('node2').get('pubkey')
        amount = '100'
        name = 'heir' + randomstring(5)
        inactivitytime = '120'
        res = rpc1.heirfund(amount, name, pubkey1, inactivitytime, 'testMemo')
        fundtxid = rpc1.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(fundtxid, rpc1)

        # Wait inactivitytime and claim funds
        time.sleep(int(inactivitytime))
        res = rpc1.heirclaim(amount, fundtxid)
        print(res)
        validate_template(res, heirclaim_schema)
        claimtxid = rpc1.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(claimtxid, rpc1)


#@pytest.mark.usefixtures("proxy_connection")
#def test_heir(test_params):
#
#    # test params inits
#    rpc = test_params.get('node1').get('rpc')
#    rpc1 = test_params.get('node2').get('rpc')
#
#    pubkey = test_params.get('node1').get('pubkey')
#    pubkey1 = test_params.get('node2').get('pubkey')
#
#    is_fresh_chain = test_params.get("is_fresh_chain")
#
#    result = rpc.heiraddress('')
#    assert_success(result)
#
#    # verify all keys look like valid AC addrs, could be better
#    for x in result.keys():
#        if x.find('ddress') > 0:
#            assert result[x][0] == 'R'
#
#    result = rpc.heiraddress(pubkey)
#    assert_success(result)
#
#    # test that additional CCaddress key is returned
#    for x in result.keys():
#        if x.find('ddress') > 0:
#            assert result[x][0] == 'R'
#
#    # getting empty heir list
#    if is_fresh_chain:
#        result = rpc.heirlist()
#        assert result == []
#
#    # valid heirfund case with coins
#    result = rpc.heirfund("1000", "UNITHEIR", pubkey1, "10", "TESTMEMO")
#    assert_success(result)
#    heir_fund_txid = send_and_mine(result["hex"], rpc)
#    assert heir_fund_txid, "got heir funding txid"
#
#    # heir fund txid should be in heirlist now
#    result = rpc.heirlist()
#    assert heir_fund_txid in result
#
#    # checking heirinfo
#    result = rpc.heirinfo(heir_fund_txid)
#    assert_success(result)
#    assert result["fundingtxid"] == heir_fund_txid
#    assert result["name"] == "UNITHEIR"
#    assert result["owner"] == pubkey
#    assert result["heir"] == pubkey1
#    assert result["memo"] == "TESTMEMO"
#    assert result["lifetime"] == "1000.00000000"
#    assert result["type"] == "coins"
#    assert result["InactivityTimeSetting"] == "10"
#    # TODO: we have non insta blocks now so should set inactivity time more than blocktime to proper test it
#    # assert result["IsHeirSpendingAllowed"] == "false"
#
#    # waiting for 11 seconds to be sure that needed time passed for heir claiming
#    time.sleep(11)
#    wait_some_blocks(rpc, 1)
#    result = rpc.heirinfo(heir_fund_txid)
#    assert result["lifetime"] == "1000.00000000"
#    assert result["IsHeirSpendingAllowed"] == "true"
#
#    # have to check that second node have coins to cover txfee at least
#    second_node_balance = rpc1.getbalance()
#    if second_node_balance < 0.1:
#        rpc.sendtoaddress(rpc1.getnewaddress(), 1)
#        time.sleep(10)  # to ensure transactions are in different blocks
#        rpc.sendtoaddress(rpc1.getnewaddress(), 1)
#        wait_some_blocks(rpc, 2)
#    assert second_node_balance > 0.1
#
#    # let's claim whole heir sum from second node
#    result = rpc1.heirclaim("1000", heir_fund_txid)
#    assert_success(result)
#    heir_claim_txid = send_and_mine(result["hex"], rpc1)
#    assert heir_claim_txid, "got claim txid"
#
#    # balance of second node after heirclaim should increase for 1000 coins - txfees
#    # + get one block reward when broadcasted heir_claim_txid
#    # TODO: very bad test with non-clearly hardcoded blockreward - needs to be changed
#    # result = round(rpc1.getbalance()) - round(second_node_balance)
#    # assert result > 100999
#
#    # no more funds should be available for claiming
#    result = rpc.heirinfo(heir_fund_txid)
#    assert result["lifetime"] == "1000.00000000"
#    assert result["available"] == "0.00000000"
#
#    # creating tokens which we put to heir contract
#    token_hex = rpc.tokencreate("TEST", "1", "TESTING")
#    token_txid = send_and_mine(token_hex["hex"], rpc)
#    assert token_txid, "got token txid"
#
#    # checking possesion over the tokens and balance
#    result = rpc.tokenbalance(token_txid, pubkey)["balance"]
#    assert result == 100000000
#
#    # valid heir case with tokens
#    token_heir_hex = rpc.heirfund("100000000", "UNITHEIR", pubkey1, "10", "TESTMEMO", token_txid)
#    token_heir_txid = send_and_mine(token_heir_hex["hex"], rpc)
#    assert token_heir_txid, "got txid of heirfund with tokens"
#
#    # checking heirinfo
#    result = rpc.heirinfo(token_heir_txid)
#    assert_success(result)
#    assert result["fundingtxid"] == token_heir_txid
#    assert result["name"] == "UNITHEIR"
#    assert result["owner"] == pubkey
#    assert result["heir"] == pubkey1
#    assert result["lifetime"] == "100000000"
#    assert result["type"] == "tokens"
#    assert result["InactivityTimeSetting"] == "10"
#    # TODO: we have non insta blocks now so should set inactivity time more than blocktime to proper test it
#    # assert result["IsHeirSpendingAllowed"] == "false"
#
#    # waiting for 11 seconds to be sure that needed time passed for heir claiming
#    time.sleep(11)
#    wait_some_blocks(rpc, 2)
#    result = rpc.heirinfo(token_heir_txid)
#    assert result["lifetime"] == "100000000"
#    assert result["IsHeirSpendingAllowed"] == "true"
#
#    # let's claim whole heir sum from second node
#    result = rpc1.heirclaim("100000000", token_heir_txid)
#    assert_success(result)
#
#    heir_tokens_claim_txid = send_and_mine(result["hex"], rpc1)
#    assert heir_tokens_claim_txid, "got claim txid"
#
#    # claiming node should have correct token balance now
#    result = rpc1.tokenbalance(token_txid, pubkey1)["balance"]
#    assert result == 100000000
#
#    # no more funds should be available for claiming
#    result = rpc.heirinfo(token_heir_txid)
#    assert result["lifetime"] == "100000000"
#    assert result["available"] == "0"
