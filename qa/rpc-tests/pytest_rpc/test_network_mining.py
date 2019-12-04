#!/usr/bin/env python3
# Copyright (c) 2019 SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import pytest
import time
from pytest_util import validate_template


@pytest.mark.usefixtures("proxy_connection")
class TestNetworkMining:

    def test_generate(self, test_params):  # generate, getgenerate, setgenerate calls
        rpc = test_params.get('node1').get('rpc')
        res = rpc.setgenerate(False, -1)
        assert not res
        res = rpc.getgenerate()
        assert not res.get('generate')
        assert res.get('numthreads') == -1
        res = rpc.setgenerate(True, 1)
        assert not res
        res = rpc.getgenerate()
        assert res.get('generate')
        assert res.get('numthreads') == 1
        # rpc.generate(2)  -- requires regtest mode

    def test_getmininginfo(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getinfo()
        blocks = res.get('blocks')
        rpc.setgenerate(True, 1)
        res = rpc.getmininginfo()
        assert res.get('blocks') == blocks
        assert res.get('generate') == True
        assert res.get('numthreads') == 1

    def test_getblocksubsidy(self, test_params):
        test_values = {
            'subsidy': 0.0001
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getblocksubsidy(131)
        assert res.get('miner') == test_values['subsidy']

    def test_getblocktemplate(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getblocktemplate()
        validate_template(res)

    def test_getlocalsolps(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getlocalsolps()
        assert isinstance(res, float) or isinstance(res, int)  # python can interpret number as either int or float

    #  getnetworkhashps call is deprecated

    def test_getnetworksolps(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getnetworksolps()
        assert isinstance(res, float) or isinstance(res, int)

    def test_prioritisetransaction(self, test_params):
        rpc = test_params.get('node1').get('rpc')
        res = rpc.prioritisetransaction("68ee9d23ba51e40112be3957dd15bc5c8fa9a751a411db63ad0c8205bec5e8a1", 0.0, 10000)
        assert res  # returns True on success

    def test_submitblock(self, test_params):
        test_values = {
            'duplicate_block': '0400000019e558e50502fe6b659a80654ea7347bd4df506f1388248b939ce3dd36550c020132592bc895a6efa41b08ef668a5414738e750a26f970c5325572d750ac4ed8fbc2f4300c01f0b7820d00e3347c8da4ee614674376cbc45359daa54f9b5493e5630d55d0f0f0f201000967fe09e1700a8b0a3f6181c3338cab3d350b689791f0b61db9180100000fd4005012649a902c3f5fc8919428a0dd7ed054fb2976ad70be7642550ab8221f153f4c71bf63822abc37c3c370b38b96205aeff29eee091c23cacf7ddcf29bf1860214e339e0b9047dd6b26b42dd1671339dcd493cc2c05bbc7dba7029723b51d4642d5db8e6f27a85de03f225a2bafe168c2e16975a36f39e28d52ee0199bcee25acb1a8d7de5e5da923e3cad0460d4fce9f1eb8dd3deb6a3792b8abf7eed043f34237adadf04bf33df503fa18ba1a8ca78774bb0755727091ce37937be43e1191c55f98867cf2c4b6f47f1428ea09264a2e5775162041c44127714f9b9ca2ffba477c2aa48319662c2d62e68fd38cc8873acc24f189b938c55ed26ff7b709d7d9fccb08c4626d3c0121acdcf5755e5fd98dcf23197a0b12ca73dbc382a57a166fd4edc7fb5e203b250b356f080b1b589941e42b4bc9600e3d5037074f3d9fdcafb417bf98e3fa34d6a42ffee94a1bb1ef15030e477a3930295197cd3172d83bbb5ca7c570556d066761814bcdcf96d26914ef217622a7a704fd7180030ef94a4309a4267c59f355dff66efb0d591baeb14260be70a39f5a3f848c97c18f65288388031df85a072c7466d6513700bbc885ae48f2c97a29543fc6111c819f21401e1b2dbc143565d8b60b7d992b8eec9709542862b317d6c9ccf05465434370559e37d8d78e110e13561d97120b9bfab7e842c11b2adc79fbdfd2084d0ea2a447a0d680f481bc3e98ce21a0437c7d57492b2f25a2960a990447a665146d55dde6a3b4b89c0a65ca4fc78fa8b3aaf8b12097aeff7858d7df98c30f23346d060f22b6ff8789f91a5ef31b06515df49e0fa1f6aeef32af3dd4451562fdadff9a333891bb1e1abc59a9dd1d1b9d59fa2389d4439d30f16b5079e025db3c4dbf72b0f3a99dc602ab6dcc8a1e87d7df84584b8b3a68b5ee27f1218751dd5464525f21b56c84015dcad6ba4ef63fe564e2b008f9dd28cc05ae536803f87e6220697b199803d518c748077ae2177ff41a0423b4ec5d570ca0cdefe48305d89f05afb6d3c3052132fd4514f08ac7c48a9877bbc735ea2e97ff87d6031563fcd9714181fbb32c4bfcf46f8b6e401c68e01908f54e16b68dd7bbbd17b665f3c99b0fc01dd4f10a35b5a22f434b0e33e8e253e230b7653a8ebb07913186bdf4f44fd00d52f8032898c28e51f98f7d63f004c9d50a45847fb7c99531bbfab3a7911d56d7797026eb4ad4405f76f8fc151770a07d8a6668545bcc6a0cb4435d93a53277f90d024f2c6b5104e6503542ea0fc296f3405628afef15f5e62d30f0f1f1127c90fe0f28823aef858c065be883dabaf8e0770e985d1e1c4221831a351548aee904e62c4e33c5d61228b7308a223c2af3bf1e1f2bd4eb63ddf8b868cd075e0f84c227e0e3b49ea9d5b552edc5b662d1e215d0ecfcfae803646840c3894a44f7f9e11e16a008e2c5fd78f70936c3bc2923142e34c9ef244c48c5a71ac9659ccf0a0a30cd4e31cb5cf2cd0c963da5b6720e7c6afe9e130ce6f4246e1c7ae50501d4e35b4a39ae54e19c72a2171adbe20b92659f761fe45757efa8a9331eda4b82172e6647e628604bbf44e3a92cb46ae2b674bc12201b9de7b36751c953ff30325b0a402649e9b0d9028326d55c212a113f06dd2664c6d9da282bcb9e1f3ed109309a942a89384eda30b4c300d91d9e8ea9deed930f5833c3dc4718ff32d47133fbc901a20110fd090d21a2a225120af6d1d385753182fcd249efffbceb7b5b99cfa8f099ad55034c97e96666bb4b84aabf96d30a70c917f489250e77aa947930c4735ab1b9ff855e3857142240e8f4dd73b69816c1ddf0e235e738898f230e4e9500324655b0ed0281115ed70f24a51a3de92a3fcf6d188c8512c89d964483e1559274bb170ed00101000000010000000000000000000000000000000000000000000000000000000000000000ffffffff035f0101ffffffff0100e876481700000023210285f68aec0e2f8b5e817d71a2a20a1fda74ea9943c752a13136a3a30fa49c0149ac5630d55d',
            'valid_block': '0400000029865a4962f43d6f95fdf9ccc89f82377a23d1fdc41eaf943c7881a5ca55c5018973d81f5ce7ab99f027b15c86ca88ec5e4b6f35ad4018bfc2058568bbe7f526000000000000000000000000000000000000000000000000000000000000000097954a5b9e830c1d1600ac305580abea34bda62eb503b02fc4b7872428cfa60bf5824a9b78fc0000fd400500c80d4a8c84cec781a5740d8d3fb18587a850b6380f073cd861c4ce7c4290460c533e0d4dd3b89fe0f0052ccdf9d450a1dfcd7263a39422000378da3eeb621078af689447a5ed0a7265a857463a36d72cdd35910d14de9816a25d631aeb0249ede829aca77f9cce1a2e4a84b75e4bd515845043d52f718638fb41e92d8b18bfe1f49e1c0d23223a285b2850e8469dfbb9782b20c8bebf2a61d7b7d8eea310c7c8d5bfa612bf94fd05562ec8876eacafa0c334a651ef70c941459161b60c20511087d63223878052d4fd1a92298789d7c57609fe3a247489674592e8e34a1728b28e2c2b3165f01d5fefa22e6384f7fe4e566de1741e264f057a0feb1b35d51694647ba52afd71c3bd375b924da95e2b413dbea256a2de9ccddcab88bd2e69cc3acc8a778b4d1db78b41df9fea6d69b071f570f628ad47537d081740a4f2c4fa6666dbb862a6d02ff07b5ae0a9fa24b003fa0355dbde0425d6c14452f0d357f2cfd97960c343ba73789a2d7ba580ea8834ef656a9e79c49fc0f61aa9452a644c8bc06afe31dce2a7ca5d6995adc8ce1f77165a075399e1d006e2bb57c09ffd6e21fcff440645faef599264a3b8c005cf60683371ba1af8847d1992c64e512f13d9d2d364969759233a27c65e1f2f1113cdb665e3e8f7baa2c398c4a2ee85a6ad1bdb095962fafaa01c3d85bc820653544b89b6e75a584d8d04bc77e5284a9ebbcd46c1a6732b841e46c876976805d932a90ac215bcc37801900d49cfb87fe5c809b30ebd8ece38669153c1f1a2438253a56a6507d556cc16b2990f0bd290fea59462d25eebdbfcb78eb403c8080e0c68e8e2ef8f67145121bce83b94dc8f9d0a742752323c5a4b42409ffcc37053c58596deff7981a20e3f412c07c839a341fdc177d5e28f7909696f90c90efff14048f440e7ea3181378f66d35b0697dc02c60154778f438cdd3dba5dc4c2763319498bbb3b8fae17508b073d07d83f5f1dc71bf2dc205f06245872620dfa341dbcdf9c574598c121120e91dd687dfd08451369ab29a11dc73f69d0722992a1c70cf1498ec9b9143fcb0abfd7b1e39189125e8567cb2cc3d71fcdb541a0776a5a665161f98385633153fc9702f079269a1dac0d2c708f5d94e346159858cfd50624ff5a0505358739b5f41adbe739bf75852eebb06eeccd79e030019a5227cd9a19e77b6821ba0794fe09cb074f40ce0b92c081c31cda2d4711d53889fc6f0579839fa74309768ef0a796fa1fa660e150d3ea5c0a369e1297d11177fc284524d6d5e40eb7ee4b400f6dfd6a10402904394e1694de300ddd565622e7ca7ed62970ff5add0b36a513b5d90d2194cf414ecc97e5dcc88698e06405dea09f49503c81cc61518f8aee882da6eeae09b4127a7fcc0c0829fca8fda3502ebf13ece0a90a8dfd05d8e514452247f79472c20683e2b1fde5ec14a2453bf00f9f1cd5a088d229a7fdfdfdc24f176fb9a8a409af70d894998957394d30a46668d71cd16907aa800ee9d96c2b9fc7fb5a7944a9b8d4f76609fc186e3c0a4d80fb9c8c236f76eb00bc24dd9abddef7d653740ece7141ac6175f7e9cab1cb0216e85adde43907b60c0581336b50ccd7682f28f00f7efd663df4d31701141657da989d236d16052c4b59fc46fb41657a26d7074fbc9dee602f7d03b86179e4c12bc0df253f815319dff12353a478d95febd5f902e363734e6e5ef4bf1865eb70750b9238be3382a51ded182569d112f37870d43465615ca9174d41f7f3b9eb780a28c7dba674075bbe04538ad669eef7716d1b7b252d49da3b00993f0c829860a1efafdcdc865d46f2f8aec9893b5bc607db33272e5b9f7cf134595e1ad5e8f34b1b7f93ca181c513afc4d8a531c36929e95cfbb4d268a9d94f80201000000010000000000000000000000000000000000000000000000000000000000000000ffffffff0603860f0e0101ffffffff0188b6e1110000000023210383d0b37f59f4ee5e3e98a47e461c861d49d0d90c80e9e16f7e63686a2dc071f3ac67954a5b01000000010b1561554a46ec535c4972a3a16652b270ee4af847ec3bbfcf6ba663ebcfefcb1a00000049483045022100b9cd7c1c56d69d9b05d695f9ac86c1233427ec26860774a0eb4e6052fe11ca8502207eca5a4eda1ccf92ccdb501ab7d61cf084d0f4431f059e27ee13ce11f9aa159b01ffffffff0188130000000000002321020e46e79a2a8d12b9b5d12c7a91adb4e454edfae43c0a0cb805427d2ac7613fd9ac00000000'
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.submitblock(test_values['valid_block'])
        assert not res  # None response on success
        res = rpc.submitblock(test_values['duplicate_block'])
        assert res == 'duplicate'

    def test_getnetworkinfo(self, test_params):
        test_values = {
            'connections': 1
        }
        rpc = test_params.get('node1').get('rpc')
        res = rpc.getnetworkinfo()
        assert res.get('connections') == test_values['connections']
        assert res.get('networks')[0]  # ipv4 info present
        assert res.get('networks')[1]  # ipv6 info present
        assert res.get('networks')[2]  # onion info present

    def test_getconnectioncount(self, test_params):
        test_values = {
            'connections': 1
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
        rpc = test_params.get('node2').get('rpc')
        cnode_ip = test_params.get('node1').get('rpc_ip')
        disconnect_node = (cnode_ip + ':' + str(test_params.get('node1').get('net_port')))
        rpc.addnode(disconnect_node, 'remove')  # remove node from addnode list to prevent reconnection
        res = rpc.disconnectnode(disconnect_node)  # has empty response
        assert not res
        time.sleep(5)  # time to stop node connection
        res = rpc.getpeerinfo()
        for peer in res:
            assert peer.get('addr') != disconnect_node

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
