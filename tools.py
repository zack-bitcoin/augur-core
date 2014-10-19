"""A bunch of functions that are used by multiple threads.
"""
import pt, hashlib, re, subprocess, time, copy, ht, networking, custom
from json import dumps as package, loads as unpackage
#from collections import OrderedDict

def heart_monitor(queue):
    beats={}
    while True:
        time.sleep(0.5)
        t=time.time()
        for beat in beats:
            if t-beats[beat]>30:
                beats[beat]=t
                log('thread has an error: ' +str(beat))
        while not(queue.empty()):
            time.sleep(0.01)
            beat=queue.get(False)
            #log('heart monitor: ' +str(beat))
            if beat=='stop': return
            if beat not in beats:
                log('adding thread: ' +str(beat))
            beats[beat]=t

def log(tx):
    with open("log.py", "a") as myfile:
        myfile.write(tx+'\n')

def can_unpack(o):
    try:
        unpackage(o)
        return True
    except:
        return False

def addr(tx):
    return make_address(tx['pubkeys'], len(tx['signatures']))

def sign(msg, privkey):
    return pt.ecdsa_sign(msg, privkey)

def verify(msg, sig, pubkey):
    return pt.ecdsa_verify(msg, sig, pubkey)

def privtopub(privkey):
    return pt.privtopub(privkey)

def hash_(x):
    return hashlib.sha384(x).hexdigest()[0:64]

def det_hash(x):
    return hash_(package(x, sort_keys=True))

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
    return ''.join([
        str(len(pubkeys)),
        str(n),
        base58_encode(det_hash({str(n): pubkeys}))[0:29]])

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

def reveal_time_p(n=10):
    return db_get('length')%20>=(20-n)

def is_number(s):
    try:
        int(s)
        return True
    except:
        return False

def kill_processes_using_ports(ports):
    popen = subprocess.Popen(['netstat', '-lpn'],
                             shell=False,
                             stdout=subprocess.PIPE)
    (data, err) = popen.communicate()
    pattern = "^tcp.*((?:{0})).* (?P<pid>[0-9]*)/.*$"
    pattern = pattern.format(')|(?:'.join(ports))
    prog = re.compile(pattern)
    for line in data.split('\n'):
        match = re.match(prog, line)
        if match:
            pid = match.group('pid')
            subprocess.Popen(['kill', '-9', pid])

def s_to_db(c): 
    response=networking.send_command(['localhost', custom.database_port], c)
    if (type(response)==dict and 'error' in response):
        time.sleep(1)
        log('response was: ' +str(response))
        log('command was: ' +str(c))
        #error()
        return s_to_db(c)
    else:
        return response

default_entry={'count': 0, 'amount': 0, 'votecoin':{}, 'votes':{}, 'shares':{}}

def db_get(n):
    out=ht.get(n)
    if out=='undefined':
        return copy.deepcopy(default_entry)
    return out

def db_put(key, dic): 
    return s_to_db({'type':'put', 'args':[key, dic]})

def db_delete(key):
    return db_put(key, 'n')

def db_existence(key):
    n=str(key)
    out=ht.get(n)
    return not out=='undefined'

def count(address):
    # Returns the number of transactions that pubkey has broadcast.
    def zeroth_confirmation_txs(address):
        def is_zero_conf(t):
            other_address=make_address(t['pubkeys'], len(t['signatures']))
            return address == other_address
        return len(filter(is_zero_conf, db_get('txs')))
    current = db_get(address)['count']
    zeroth=zeroth_confirmation_txs(address)
    return current+zeroth

def fork_check(newblocks, length, block):
    recent_hash = det_hash(block)
    their_hashes = map(lambda x: x['prevHash'] if x['length']>0 else 0, newblocks)
    return (recent_hash not in their_hashes) and length>=newblocks[0]['length']-1
