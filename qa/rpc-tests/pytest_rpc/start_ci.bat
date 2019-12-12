set CLIENTS=2
set CHAIN=TONYCI
set TEST_ADDY=RPWhA4f4ZTZxNi5K36bcwsWdVjSVDSjUnd
set TEST_WIF0=UpcQympViQpLmv1WzMwszKPrmKUa28zsv8pdLCMgNMXDFBBBKxCN
set TEST_PUBKEY0=02f0ec2d3da51b09e4fc8d9ba334c275b02b3ab6f22ce7be0ea5059cbccbd1b8c7
set TEST_ADDY1=RHoTHYiHD8TU4k9rbY4Aoj3ztxUARMJikH
set TEST_WIF1=UwmmwgfXwZ673brawUarPzbtiqjsCPWnG311ZRAL4iUCZLBLYeDu
set TEST_PUBKEY1=0285f68aec0e2f8b5e817d71a2a20a1fda74ea9943c752a13136a3a30fa49c0149
set CHAIN_MODE=REGULAR
set IS_BOOTSTRAP_NEEDED=True
set BOOTSTRAP_URL=http://159.69.45.70/bootstrap.tar.gz

whoami
python.exe --version
python.exe -m pip freeze

python.exe chainstart.py

python.exe -m pytest %* -s -vv
