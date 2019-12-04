#!/usr/bin/env python3
# Copyright (c) 2019 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
import time


@pytest.mark.usefixtures("proxy_connection")
class TestNetworkMining:

    def test_getnetworkinfo(self, test_params):
        test_values = {
            'connections': 1,
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getnetworkinfo()
        assert res.get('connections') == test_values['connections']
        assert res.get('networks')[0]  # ipv4 info present
        assert res.get('networks')[1]  # ipv6 info present
        assert res.get('networks')[2]  # onion info present

    def test_getconnectioncount(self, test_params):
        test_values = {
            'connections': 1,
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getconnectioncount()
        assert res == test_values['connections']

    def test_getpeerinfo(self, test_params):
        test_values = {
            'id': 1,
            'addr': '127.0.0.1'
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getpeerinfo()
        assert res[0].get('id') == test_values['id']
        assert test_values['addr'] in res[0].get('addr')

    def test_getnettotals(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getnettotals()
        assert isinstance(res.get('timemillis'), int)

    def test_ping(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.ping()
        assert not res  # ping call has empty response

    def test_getdeprecationinfo(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getdeprecationinfo()
        assert isinstance(res.get('version'), int)

    def test_addnode(self, test_params):
        rpc = test_params.get('node2').get('rpc')
        cnode_ip = test_params.get('node1').get('rpc_ip')
        connect_node = (cnode_ip + ':' + str(test_params.get('node1').get('net_port')))
        res = rpc.addnode(connect_node, 'remove')
        assert not res
        res = rpc.addnode(connect_node, 'onetry')
        assert not res
        res = rpc.addnode(connect_node, 'add')
        assert not res
        rpc.getpeerinfo()

    def test_disconnectnode(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getpeerinfo()
        addr = res[0].get('addr')
        rpc.disconnectnode(addr)  # has empty response
        time.sleep(5)  # time to stop node connection
        res = rpc.getpeerinfo()
        for peer in res:
            assert peer.get('addr') != addr

    def test_ban(self, test_params):  # setban, listbanned, clearbanned calls
        rpc = test_params.get('node1').get('rpc')
        ban_list = ['144.144.140.0/255.255.255.0', '144.144.140.12/255.255.255.255', '192.168.0.0/255.255.0.0']
        res = rpc.clearbanned()
        assert not res
        res = rpc.setban(ban_list[0], 'add', 64800)
        assert not res
        res = rpc.setban(ban_list[1], 'add', 64800)
        assert not res
        res = rpc.setban(ban_list[2], 'add', 64800)
        assert not res
        res = rpc.listbanned()
        for peer in res:
            node = peer.get('address')
            assert node in ban_list
        rpc.clearbanned()
        res = rpc.listbanned()
        assert not res
