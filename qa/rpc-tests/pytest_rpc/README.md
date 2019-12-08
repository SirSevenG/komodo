Updated RPC unit-tests infrastructure for Antara smart-chain custom modules 

Using pytest as testing framework and slickrpc as rpc proxy. No more python2 support.

To start just set test nodes RPC credentials in `nodesconfig.json`.
I thought such config usage might be useful as in some manual testing plays as well as in some CI configuration tests integration.

`is_fresh_chain=False` param allows to run tests on existing chains (it skips some tests which expecting first CC usage on chain)

So yes - you can run these tests on existing chains, just RPC creds (and wallets with some balance) needed.

# Dependencies

`pip3 install setuptools wheel slick-bitcoinrpc pytest wget jsonschema`

# Usage

In `~/komodo/qa/rpc-tests/pytest_rpc` directory:

`python3 -m pytest basic -s` - starts all basic tests
`python3 -m pytest cc_modules/test_dice.py -s` - starts specific test, dice in this case

`-s` flag is optional, just displaying python prints which might be helpful in debugging

`ci_test.sh cc_modules` script will start a all CCs full test suite from bootstrapped chain - best way to start the tests
You still can run specific test via script `ci_test.sh basic/test_utils.py`

The `start_chains.py` script can spin needed amount of nodes and start the test chain.
You can find an example of this script usage in `ci_setup.sh`. Don't forget to change `test_config.json` accordingly to the chain params.

On Windows machines use `start_ci.bat` instead of `ci_setup.sh`

Also there is bootstrap downloading functionality in `start_chains.py` what should be quite useful for automated testing setups
