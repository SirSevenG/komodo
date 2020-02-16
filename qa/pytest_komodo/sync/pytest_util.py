import time
import os


def env_get(var, default):
    try:
        res = os.environ[var]
    except KeyError:
        res = default
    return res


def get_chainstate(proxy):
    vals = {}
    res = proxy.getinfo()
    vals.update({'synced': res.get('synced')})
    vals.update({'notarized': res.get('notarized')})
    vals.update({'blocks': res.get('blocks')})
    vals.update({'longestchain': res.get('longestchain')})
    return vals


def check_notarized(notarized, longestchain, proxy, blocktime=60):
    # Assuming chain should get notarization in 2 BTC blocks
    allowed_diff = round(1500 / blocktime)  # COIN rough blocks amount in 2,5 average BTC blocktime
    if os.environ['IS_BOOTSTRAP_NEEDED']:  # Bootstraped node may appear 'in sync' without any peers connected
        peers_connected = 0
        ltime = time.time()
        timeout = time.time() + 5 * blocktime
        while peers_connected < 4 and ltime < timeout:
            ltime = time.time()
            peers_connected = len(proxy.getpeerinfo())
            proxy.ping()
            print(proxy.getpeerinfo())
            print("Waiting more peers to connect")
            time.sleep(10)
    if notarized == 0:
        print("Waiting chain to get notarizations data")
        ltime = time.time()
        timeout = time.time() + 1500
        while notarized == 0 and ltime <= timeout:
            time.sleep(blocktime * 1.5)
            notarized = proxy.getinfo().get('notarized')
            ltime = time.time()
            print("Waiting notarization")
            print(notarized)
    if notarized >= longestchain - allowed_diff:
        return True
    else:
        return False
