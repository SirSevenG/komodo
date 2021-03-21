#!/usr/bin/env python3
# Copyright (c) 2021 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
from slickrpc.exc import RpcException as RPCError
from basic.pytest_util import validate_template, mine_and_waitconfirms, randomstring, randomhex, validate_raddr_pattern


@pytest.mark.usefixtures("proxy_connection")
class TestTokenCCcalls:

    @staticmethod
    def new_token(proxy, schema=None):
        name = randomstring(8)
        amount = '0.10000000'
        res = proxy.tokencreate(name, amount, "test token 1")
        if schema:
            validate_template(res, schema)
        assert res.get('result') == 'success'
        txid = proxy.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, proxy)
        token = {
            'tokenid': txid,
            'name': name
        }
        return token

    def test_tokencreate_list_info(self, test_params):
        create_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'hex': {'type': 'string'},
                'error': {'type': 'string'}
            },
            'required': ['result']
        }

        list_schema = {
            'type': 'array',
            'items': {'type': 'string'}
        }

        info_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'tokenid': {'type': 'string'},
                'owner': {'type': 'string'},
                'name': {'type': 'string'},
                'supply': {'type': 'integer'},
                'description': {'type': 'string'},
                'version':  {'type': 'integer'},
                'IsMixed': {'type': 'string'}
            },
            'required': ['result']
        }

        rpc = test_params.get('node1').get('rpc')
        token = self.new_token(rpc, schema=create_schema)

        res = rpc.tokenlist()
        validate_template(res, list_schema)

        res = rpc.tokeninfo(token.get('tokenid'))
        validate_template(res, info_schema)

    def test_tokenaddress(self, test_params):
        assetaddress_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                "GlobalPk Assets CC Address": {'type': 'string'},
                "GlobalPk Assets CC Balance": {'type': 'number'},
                "GlobalPk Assets Normal Address": {'type': 'string'},
                "GlobalPk Assets Normal Balance": {'type': 'number'},
                "GlobalPk Assets/Tokens CC Address": {'type': 'string'},
                "pubkey Assets CC Address": {'type': 'string'},
                "pubkey Assets CC Balance": {'type': 'number'},
                "mypk Assets CC Address": {'type': 'string'},
                "mypk Assets CC Balance": {'type': 'number'},
                "mypk Normal Address": {'type': 'string'},
                "mypk Normal Balance": {'type': 'number'}
            },
            'required': ['result']
        }

        tokenaddress_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                "GlobalPk Tokens CC Address": {'type': 'string'},
                "GlobalPk Tokens CC Balance": {'type': 'number'},
                "GlobalPk Tokens Normal Address": {'type': 'string'},
                "GlobalPk Tokens Normal Balance": {'type': 'number'},
                "pubkey Tokens CC Address": {'type': 'string'},
                "pubkey Tokens CC Balance": {'type': 'number'},
                "mypk Tokens CC Address": {'type': 'string'},
                "mypk Tokens CC Balance": {'type': 'number'},
                "mypk Normal Address": {'type': 'string'},
                "mypk Normal Balance": {'type': 'number'}
            },
            'required': ['result']
        }

        rpc = test_params.get('node1').get('rpc')
        pubkey = test_params.get('node1').get('pubkey')

        res = rpc.assetsaddress(pubkey)
        validate_template(res, assetaddress_schema)

        res = rpc.tokenaddress(pubkey)
        validate_template(res, tokenaddress_schema)

    def test_tokentransfer_balance(self, test_params):
        transfer_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'hex': {'type': 'string'}
            },
            'required': ['result']
        }

        balance_schema = {
            'type': 'object',
            'properties': {
                'result': {'type': 'string'},
                'CCaddress': {'type': 'string'},
                'tokenid': {'type': 'string'},
                'balance': {'type': 'integer'}
            },
            'required': ['result']
        }

        rpc1 = test_params.get('node1').get('rpc')
        rpc2 = test_params.get('node2').get('rpc')
        pubkey2 = test_params.get('node2').get('pubkey')

        token1 = self.new_token(rpc1)

        amount = 150
        res = rpc1.tokentransfer(token1.get('tokenid'), pubkey2, str(amount))
        validate_template(res, transfer_schema)
        txid = rpc1.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, rpc1)

        res = rpc2.tokenbalance(token1.get('tokenid'), pubkey2)
        validate_template(res, balance_schema)
        assert amount == res.get('balance')
        assert token1.get('tokenid') == res.get('tokenid')

    def test_tokenask_bid_orders(self, test_params):
        askbid_schema = {
            'type': 'object',
            'properties': {
                'hex': {'type': 'string'}
            },
            'required': ['hex']
        }

        orders_schema = {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'funcid': {'type': 'string'},
                    'txid': {'type': 'string'},
                    'vout':  {'type': 'integer'},
                    'amount': {'type': 'string'},
                    'askamount': {'type': 'string'},
                    'origaddress': {'type': 'string'},
                    'origtokenaddress': {'type': 'string'},
                    'tokenid': {'type': 'string'},
                    'totalrequired': {'type': ['string', 'integer']},
                    'price': {'type': 'string'}
                }
            }
        }

        rpc1 = test_params.get('node1').get('rpc')
        rpc2 = test_params.get('node2').get('rpc')
        pubkey2 = test_params.get('node2').get('pubkey')

        token1 = self.new_token(rpc1)
        amount1 = 150
        amount2 = 100
        price = 0.1

        res = rpc1.tokenask(str(amount1), token1.get('tokenid'), str(price))
        validate_template(res, askbid_schema)
        asktxid = rpc1.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(asktxid, rpc1)

        res = rpc1.tokenbid(str(amount2), token1.get('tokenid'), str(price))
        validate_template(res, askbid_schema)
        bidtxid = rpc1.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(bidtxid, rpc1)

        # Check orders and myorders call
        orders1 = rpc2.tokenorders(token1.get('tokenid'))
        print(orders1)
        validate_template(orders1, orders_schema)
        orders2 = rpc1.mytokenorders(token1.get('tokenid'))
        print(orders2)
        validate_template(orders2, orders_schema)
        # assert orders1 == orders2

        # Check fills and cancel calls
        res = rpc2.tokenfillask(token1.get('tokenid'), asktxid, str(int(amount1 * 0.5)))
        validate_template(res, askbid_schema)
        asktxid2 = rpc2.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(asktxid2, rpc2)

        res = rpc2.tokenfillbid(token1.get('tokenid'), bidtxid, str(int(amount2 * 0.5)))
        validate_template(res, askbid_schema)
        bidtxid2 = rpc2.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(bidtxid2, rpc2)

        res = rpc1.tokencancelask(token1.get('tokenid'), asktxid2)
        validate_template(res, askbid_schema)
        txid = rpc1.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, rpc1)

        res = rpc1.tokencancelbid(token1.get('tokenid'), bidtxid2)
        validate_template(res, askbid_schema)
        txid = rpc1.sendrawtransaction(res.get('hex'))
        mine_and_waitconfirms(txid, rpc1)

        # There should be no orders left after cancelling
        orders = rpc1.mytokenorders(token1.get('tokenid'))
        validate_template(orders, orders_schema)
        assert len(orders) == 0


@pytest.mark.usefixtures("proxy_connection")
class TestTokenCC:

    def test_rewardsaddress(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        pubkey = test_params.get('node1').get('pubkey')

        res = rpc.assetsaddress(pubkey)
        for key in res.keys():
            if key.find('ddress') > 0:
                assert validate_raddr_pattern(res.get(key))

        res = rpc.tokenaddress(pubkey)
        for key in res.keys():
            if key.find('ddress') > 0:
                assert validate_raddr_pattern(res.get(key))

    @staticmethod
    def bad_calls(proxy, token, pubkey):
        name = token.get('name')
        tokenid = token.get('tokenid')
        # trying to create token with negative supply
        # with pytest.raises(RPCError):
        res = proxy.tokencreate("NUKE", "-1987420", "no bueno supply")
        assert res.get('error')
        # creating token with name more than 32 chars
        res = proxy.tokencreate("NUKE123456789012345678901234567890", "1987420", "name too long")
        assert res.get('error')
        # getting token balance for non existing tokenid
        res = proxy.tokenbalance("", pubkey)
        assert res.get('error')
        # no info for invalid tokenid
        res = proxy.tokeninfo(pubkey)
        assert res.get('error')
        # invalid token transfer amount
        randompubkey = randomhex()
        res = proxy.tokentransfer(tokenid, randompubkey, "0")
        assert res.get('error')
        # invalid token transfer amount
        res = proxy.tokentransfer(tokenid, randompubkey, "-1")
        assert res.get('error')
        # invalid numtokens bid
        res = proxy.tokenbid("-1", tokenid, "1")
        assert res.get('error')
        # invalid numtokens bid
        res = proxy.tokenbid("0", tokenid, "1")
        assert res.get('error')
        # invalid price bid
        # with pytest.raises(RPCError):
        res = proxy.tokenbid("1", tokenid, "-1")
        assert res.get('error')
        # invalid price bid
        res = proxy.tokenbid("1", tokenid, "0")
        assert res.get('error')
        # invalid tokenid bid
        res = proxy.tokenbid("100", "deadbeef", "1")
        assert res.get('error')
        # invalid numtokens ask
        res = proxy.tokenask("-1", tokenid, "1")
        assert res.get('error')
        # invalid numtokens ask
        res = proxy.tokenask("0", tokenid, "1")
        assert res.get('error')
        # invalid price ask
        # with pytest.raises(RPCError):
        res = proxy.tokenask("1", tokenid, "-1")
        assert res.get('error')
        # invalid price ask
        res = proxy.tokenask("1", tokenid, "0")
        assert res.get('error')
        # invalid tokenid ask
        res = proxy.tokenask("100", "deadbeef", "1")
        assert res.get('error')

    def test_bad_calls(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        pubkey = test_params.get('node1').get('pubkey')
        token = TestTokenCCcalls.new_token(rpc)
        self.bad_calls(rpc, token, pubkey)
