""" 
This file mines blocks and talks to peers.
It maintains consensus of the blockchain.
"""
from Queue import Empty
import blockchain
import copy
import custom
import tools
import networking
import multiprocessing
import random
import time
import copy
import target

def make_mint(pubkey):
    address = tools.make_address([pubkey], 1)
    return {'type': 'mint',
            'pubkeys': [pubkey],
            'signatures': ['first_sig'],
            'count': tools.count(address)}

def genesis(pubkey):
    target_ = target.target()
    out = {'version': custom.version,
           'length': 0,
           'time': time.time(),
           'target': target_,
           'diffLength': blockchain.hexInvert(target_),
           'txs': [make_mint(pubkey)]}
    out = tools.unpackage(tools.package(out))
    return out

def make_block(prev_block, txs, pubkey):
    leng = int(prev_block['length']) + 1
    target_ = target.target(leng)
    diffLength = blockchain.hexSum(prev_block['diffLength'],
                                   blockchain.hexInvert(target_))
    out = {'version': custom.version,
           'txs': txs + [make_mint(pubkey)],
           'length': leng,
           'time': time.time(),
           'diffLength': diffLength,
           'target': target_,
           'prevHash': tools.det_hash(prev_block)}
    out = tools.unpackage(tools.package(out))
    return out

def POW(block, restart_signal):
    halfHash = tools.det_hash(block)
    block[u'nonce'] = random.randint(0, 10000000000000000000000000000000000000000)
    count = 0
    while tools.det_hash({u'nonce': block['nonce'],
                          u'halfHash': halfHash}) > block['target']:
        count += 1
        block[u'nonce'] += 1
        if restart_signal.is_set():
            restart_signal.clear()
            return {'solution_found': True}
    return block
def new_worker(solution_queue):
    in_queue=multiprocessing.Queue()
    restart=multiprocessing.Event()
    proc = multiprocessing.Process(target=miner, args=(restart, solution_queue, in_queue))
    proc.daemon=True
    proc.start()
    return({'in_queue':in_queue, 'restart':restart, 'solution_queue':solution_queue, 'proc':proc})
def dump_out(queue):
    while not queue.empty():
        try:
            queue.get(False)
        except:
            pass
def restart_workers(workers):
    for worker in workers:
        dump_out(worker['in_queue'])
        worker['restart'].set()
def main(pubkey, heart_queue, blocks_queue):
    num_cores = multiprocessing.cpu_count()
    solution_queue = multiprocessing.Queue()
    workers = [new_worker(solution_queue) for _ in range(num_cores)]
    try:
        while True:
            heart_queue.put('miner')
            if tools.db_get('stop'): 
                return
            elif tools.db_get('mine'):
                main_once(pubkey, blocks_queue, num_cores, solution_queue, workers)
            else:
                time.sleep(1)
    except Exception as exc:
        tools.log(exc)

def main_once(pubkey, blocks_queue, num_cores, solution_queue, workers):
    length=tools.db_get('length')
    if length==-1:
        candidate_block = genesis(pubkey)
    else:
        prev_block = tools.db_get(length)
        tools.log(prev_block)
        candidate_block = make_block(prev_block, tools.db_get('txs'), pubkey)
    work = candidate_block
    for worker in workers:
        worker['in_queue'].put(work)
        worker['in_queue'].put(work)
    start=time.time()
    while solution_queue.empty() and time.time()<start+5:#we might mine faster if the 5 was a 30.
        time.sleep(0.1)
    restart_workers(workers)
    while not solution_queue.empty():
        try:
            blocks_queue.put(solution_queue.get(False))
        except:
            continue

def miner(restart, solution_queue, in_queue):
    while True:
        try:
            candidate_block=in_queue.get(False)
        except:
            continue
        possible_block = POW(candidate_block, restart)
        if 'error' in possible_block: 
            continue
        elif 'solution_found' in possible_block: 
            continue
        else:
            solution_queue.put(possible_block)
