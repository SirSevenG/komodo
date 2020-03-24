#!/usr/bin/env python3
# Copyright (c) 2019 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
import json
from basic.pytest_util import validate_template, mine_and_waitconfirms, \
                              randomstring, check_synced, wait_blocks
from util import assert_success, assert_error, mine_and_waitconfirms, send_and_mine,\
    rpc_connect, wait_some_blocks, generate_random_string, komodo_teardown


@pytest.mark.usefixtures("proxy_connection")
class TestRewards:

    @staticmethod
    def new_rewardsplan(proxy, schema=None):
        name = randomstring(4)
        amount = '250'
        apr = '25'
        mindays = '0'
        maxdays = '10'
        mindeposit = '10'
        res = proxy.rewardscreatefunding(name, amount, apr, mindays, maxdays, mindeposit)
        if schema:
            validate_template(res, schema)
        assert res.get('result') == 'success'
        txid = proxy.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, proxy)
        rewardsplan = {
            'fundingtxid': txid,
            'name': name
        }
        return rewardsplan

    def test_rewardscreatefunding(self, test_params):
        createfunding_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'hex': {'type': 'string'},
                'error': {'type': 'string'}
            },
            'required': ['result']
        }

        rpc = test_params.get('node1').get('rpc')
        self.new_rewardsplan(rpc, schema=createfunding_schema)

    def test_reardsaddress(self, test_params):
        rewardsaddress_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'error': {'type': 'string'},
                'RewardsCCAddress': {'type': 'string'},
                'RewardsCCBalance': {'type': 'number'},
                'RewardsNormalAddress': {'type': 'string'},
                'RewardsNormalBalance': {'type': 'number'},
                'RewardsCCTokensAddress': {'type': 'string'},
                'PubkeyCCaddress(Rewards)': {'type': 'string'},
                'PubkeyCCbalance(Rewards)': {'type': 'number'},
                'myCCAddress(Rewards)': {'type': 'string'},
                'myCCbalance(Rewards)': {'type': 'number'},
                'myaddress': {'type': 'string'},
                'mybalance': {'type': 'number'}
            },
            'required': ['result']
        }

        rpc = test_params.get('node1').get('rpc')
        res = rpc.rewardsaddress()
        validate_template(res, rewardsaddress_schema)
        assert res.get('result') == 'success'

    def test_rewarsdlist(self, test_params):
        rewadslist_schema = {
            'type': 'array',
            'items': {'type': 'string'}
        }

        rpc1 = test_params.get('node1').get('rpc')
        res = rpc1.rewardslist()
        validate_template(res, rewadslist_schema)

    @staticmethod
    def rewardsinfo_maincheck(proxy, fundtxid, schema):
        res = proxy.rewardsinfo(fundtxid)
        validate_template(res, schema)
        assert res.get('result') == 'success'

    def test_rewardsinfo(self, test_params):
        rewardsinfo_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'error': {'type': 'string'},
                'fundingtxid': {'type': 'string'},
                'name': {'type': 'string'},
                'sbits': {'type': 'integer'},
                'APR': {'type': 'string'},
                'minseconds': {'type': 'integer'},
                'maxseconds': {'type': 'integer'},
                'mindeposit': {'type': 'string'},
                'funding': {'type': 'string'},
                'locked': {'type': 'string'}
            },
            'required': ['result']
        }

        rpc1 = test_params.get('node1').get('rpc')
        try:
            fundtxid = rpc1.rewardslist()[0]
            self.rewardsinfo_maincheck(rpc1, fundtxid, rewardsinfo_schema)
        except IndexError:
            print('\nNo Rewards CC available on chain')
            fundtxid = self.new_rewardsplan(rpc1).get('fundingtxid')
            self.rewardsinfo_maincheck(rpc1, fundtxid, rewardsinfo_schema)

    @staticmethod
    def rewardsaddfunding_maincheck(proxy, fundtxid, schema):
        name = proxy.rewardsinfo(fundtxid).get('name')
        amount = proxy.rewardsinfo(fundtxid).get('mindeposit')  # not related to mindeposit here, just to get amount
        res = proxy.rewardsaddfunding(name, fundtxid, amount)
        validate_template(res, schema)
        assert res.get('result') == 'success'
        txid = proxy.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, proxy)

    def test_rewardsaddfunding(self, test_params):
        addfunding_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'hex': {'type': 'string'},
                'error': {'type': 'string'}
            },
            'required': ['result']
        }

        rpc1 = test_params.get('node1').get('rpc')
        try:
            fundtxid = rpc1.rewardslist()[0]
            self.rewardsaddfunding_maincheck(rpc1, fundtxid, addfunding_schema)
        except IndexError:
            print('\nNo Rewards CC available on chain')
            fundtxid = self.new_rewardsplan(rpc1).get('fundingtxid')
            self.rewardsaddfunding_maincheck(rpc1, fundtxid, addfunding_schema)

    @staticmethod
    def un_lock_maincheck(proxy, fundtxid, schema):
        name = proxy.rewardsinfo(fundtxid).get('name')
        amount = proxy.rewardsinfo(fundtxid).get('mindeposit')
        res = proxy.rewardslock(name, fundtxid, amount)
        validate_template(res, schema)
        assert res.get('result') == 'success'
        locktxid = proxy.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(locktxid, proxy)
        res = proxy.rewardsunlock(name, fundtxid, locktxid)
        validate_template(res, schema)
        assert res.get('result') == 'success'
        unlocktxid = proxy.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(unlocktxid, proxy)

    def test_lock_unlock(self, test_params):
        lock_unlock_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'hex': {'type': 'string'},
                'error': {'type': 'string'}
            },
            'required': ['result']
        }

        rpc1 = test_params.get('node1').get('rpc')
        try:
            fundtxid = rpc1.rewardslist()[0]
            self.un_lock_maincheck(rpc1, fundtxid, lock_unlock_schema)
        except IndexError:
            print('\nNo Rewards CC available on chain')
            fundtxid = self.new_rewardsplan(rpc1).get('fundingtxid')
            self.un_lock_maincheck(rpc1, fundtxid, lock_unlock_schema)


@pytest.mark.usefixtures("proxy_connection")
def test_rewards(test_params):

    # test params inits
    rpc = test_params.get('node1').get('rpc')
    rpc1 = test_params.get('node2').get('rpc')

    pubkey = test_params.get('node1').get('pubkey')
    pubkey1 = test_params.get('node2').get('pubkey')

    is_fresh_chain = test_params.get("is_fresh_chain")

    result = rpc.rewardsaddress()
    for x in result.keys():
        if x.find('ddress') > 0:
            assert result[x][0] == 'R'

    result = rpc.rewardsaddress(pubkey)
    for x in result.keys():
        if x.find('ddress') > 0:
            assert result[x][0] == 'R'

    # no rewards yet
    if is_fresh_chain:
        result = rpc.rewardslist()
        assert result == []

    # looking up non-existent reward should return error
    result = rpc.rewardsinfo("none")
    assert_error(result)

    # creating rewards plan with name > 8 chars, should return error
    result = rpc.rewardscreatefunding("STUFFSTUFF", "7777", "25", "0", "10", "10")
    assert_error(result)

    # creating rewards plan with 0 funding
    result = rpc.rewardscreatefunding("STUFF", "0", "25", "0", "10", "10")
    assert_error(result)

    # creating rewards plan with 0 maxdays
    result = rpc.rewardscreatefunding("STUFF", "7777", "25", "0", "10", "0")
    assert_error(result)

    # creating rewards plan with > 25% APR
    result = rpc.rewardscreatefunding("STUFF", "7777", "30", "0", "10", "10")
    assert_error(result)

    # creating valid rewards plan
    plan_name = generate_random_string(6)
    result = rpc.rewardscreatefunding(plan_name, "7777", "25", "0", "10", "10")
    assert result['hex'], 'got raw xtn'
    fundingtxid = send_and_mine(result['hex'], rpc)
    assert fundingtxid, 'got txid'
    result = rpc.rewardsinfo(fundingtxid)
    assert_success(result)
    assert result['name'] == plan_name
    assert result['APR'] == "25.00000000"
    assert result['minseconds'] == 0
    assert result['maxseconds'] == 864000
    assert result['funding'] == "7777.00000000"
    assert result['mindeposit'] == "10.00000000"
    assert result['fundingtxid'] == fundingtxid

    # checking if new plan in rewardslist
    result = rpc.rewardslist()
    assert fundingtxid in result

    # creating reward plan with already existing name, should return error
    result = rpc.rewardscreatefunding(plan_name, "7777", "25", "0", "10", "10")
    assert_error(result)

    # add funding amount must be positive
    result = rpc.rewardsaddfunding(plan_name, fundingtxid, "-1")
    assert_error(result)

    # add funding amount must be positive
    result = rpc.rewardsaddfunding(plan_name, fundingtxid, "0")
    assert_error(result)

    # adding valid funding
    result = rpc.rewardsaddfunding(plan_name, fundingtxid, "555")
    addfundingtxid = send_and_mine(result['hex'], rpc)
    assert addfundingtxid, 'got funding txid'

    # checking if funding added to rewardsplan
    result = rpc.rewardsinfo(fundingtxid)
    assert result['funding'] == "8332.00000000"

    # trying to lock funds, locking funds amount must be positive
    result = rpc.rewardslock(plan_name, fundingtxid, "-5")
    assert_error(result)

    # trying to lock funds, locking funds amount must be positive
    result = rpc.rewardslock(plan_name, fundingtxid, "0")
    assert_error(result)

    # trying to lock less than the min amount is an error
    result = rpc.rewardslock(plan_name, fundingtxid, "7")
    assert_error(result)

    # locking funds in rewards plan
    result = rpc.rewardslock(plan_name, fundingtxid, "10")
    assert_success(result)
    locktxid = result['hex']
    assert locktxid, "got lock txid"

    # locktxid has not been broadcast yet
    result = rpc.rewardsunlock(plan_name, fundingtxid, locktxid)
    assert_error(result)

    # broadcast xtn
    txid = rpc.sendrawtransaction(locktxid)
    assert txid, 'got txid from sendrawtransaction'

    # confirm the xtn above
    wait_some_blocks(rpc, 1)

    # will not unlock since reward amount is less than tx fee
    result = rpc.rewardsunlock(plan_name, fundingtxid, locktxid)
    assert_error(result)
