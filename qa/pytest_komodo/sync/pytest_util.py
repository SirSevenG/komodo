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
    allowed_diff = round(1500 / blocktime)  # awerage blocks amount in 2,5 average BTC blocktime
    if notarized == 0:
        print("Waiting chain to get notarizations data")
        time.sleep(blocktime * 1.5)
        notarized = proxy.getinfo().get('notarized')
    if notarized >= longestchain - allowed_diff:
        return True
    else:
        return False
