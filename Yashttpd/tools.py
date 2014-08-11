import pt
import hashlib
from json import dumps as package, loads as unpackage
from collections import OrderedDict
def addr(tx): return make_address(tx['pubkeys'], len(tx['signatures']))
def sign(msg, privkey): return pt.ecdsa_sign(msg, privkey)
def verify(msg, sig, pubkey): return pt.ecdsa_verify(msg, sig, pubkey)
def privtopub(privkey): return pt.privtopub(privkey)
def hash_(x): return hashlib.sha256(x).hexdigest()
def det_hash(x):
    """Deterministically takes sha256 of dict, list, int, or string."""
    def det_list(l): return '[%s]' % ','.join(map(det, sorted(l)))
    def det_dict(x):
        list_=map(lambda p: det(p[0]) + ':' + det(p[1]), sorted(x.items()))
        return '{%s}' % ','.join(list_)
    def det(x): return {list: det_list, dict: det_dict}.get(type(x), str)(x)
    return hash_(det(unpackage(package(x))))
def base58_encode(num):
    num = int(num, 16)
    alphabet = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
    base_count = len(alphabet)
    encode = ''
    if num < 0:
        return ''
    while (num >= base_count):
        mod = num % base_count
        encode = alphabet[mod] + encode
        num = num / base_count
    if num:
        encode = alphabet[num] + encode
    return encode
def make_address(pubkeys, n):
    """n is the number of pubkeys required to spend from this address."""
    return (str(len(pubkeys)) + str(n) +
            base58_encode(det_hash({str(n): pubkeys}))[0:29])
def buffer_(str_to_pad, size):
    return str_to_pad.rjust(size, '0')
def E_check(dic, key, type_):
    if not isinstance(type_, list): type_=[type_]
    if len(type_)==0: return False#to end the recursion.
    if not key in dic: return False
    if isinstance(type_[0], type):
        if not isinstance(dic[key], type_[0]): return E_check(dic, key, type_[1:])
    else:
        if not dic[key] == type_[0]: return E_check(dic, key, type_[1:])
    return True
def reveal_time_p(DB, n=10):
    return DB['length']%20>=(20-n)
def is_number(s):
    try:
        int(s)
        return True
    except:
        return False
