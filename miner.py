""" This file mines blocks and talks to peers. It maintains consensus of the
    blockchain.
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
import sys

def make_mint(pubkey, DB):
    address = tools.make_address([pubkey], 1)
    return {'type': 'mint',
            'pubkeys': [pubkey],
            'signatures': ['first_sig'],
            'count': blockchain.count(address, DB)}

def genesis(pubkey, DB):
    target = blockchain.target(DB)
    out = {'version': custom.version,
           'length': 0,
           'time': time.time(),
           'target': target,
           'diffLength': blockchain.hexInvert(target),
           'txs': [make_mint(pubkey, DB)]}
    out = tools.unpackage(tools.package(out))
    return out

def make_block(prev_block, txs, pubkey, DB):
    #print('DB: ' +str(DB))
    #print('prev: ' +str(prev_block))
    leng = int(prev_block['length']) + 1
    target = blockchain.target(DB, leng)
    diffLength = blockchain.hexSum(prev_block['diffLength'],
                                   blockchain.hexInvert(target))
    out = {'version': custom.version,
           'txs': txs + [make_mint(pubkey, DB)],
           'length': leng,
           'time': time.time(),
           'diffLength': diffLength,
           'target': target,
           'prevHash': tools.det_hash(prev_block)}
    out = tools.unpackage(tools.package(out))
    return out
def POW(block, hashes, restart_signal):
    halfHash = tools.det_hash(block)
    block[u'nonce'] = random.randint(0, 10000000000000000000000000000000000000000)
    count = 0
    while tools.det_hash({u'nonce': block['nonce'],
                          u'halfHash': halfHash}) > block['target']:
        count += 1
        block[u'nonce'] += 1
        if count > hashes:
            return {'error': False}
        if restart_signal.is_set():
            restart_signal.clear()
            return {'solution_found': True}
    return block
def miner(block_submit_queue, get_work_queue, restart_signal):
    block_header = None
    need_new_work = False
    while True:
        # Either get the current block header, or restart because a block has
        # been solved by another worker.
        try:
            if need_new_work or block_header is None:
                block_header, hashes_till_check = get_work_queue.get(True, 1)
                need_new_work = False
        # Try to optimistically get the most up-to-date work.
        except Empty:
            need_new_work = False
            continue

        possible_block = POW(block_header, hashes_till_check, restart_signal)
        if 'error' in possible_block:  # We hit the hash ceiling.
            continue
        # Another worker found the block.
        elif 'solution_found' in possible_block:
            # Empty out the signal queue.
            need_new_work = True
        # We've found a block!
        else:
            block_submit_queue.put(block_header)
            need_new_work = True


def restart_workers(worker_mailboxes):
    #print("Possible solution found, restarting mining workers.")
    for worker_mailbox in worker_mailboxes:
        worker_mailbox['restart'].set()

def spawn_worker(submitted_blocks):
    #print("Spawning worker")
    restart_signal = multiprocessing.Event()
    work_queue = multiprocessing.Queue()
    worker_proc = multiprocessing.Process(target=miner,
                                          args=(submitted_blocks, work_queue,
                                                restart_signal))
    worker_proc.daemon = True
    worker_proc.start()
    return {'restart': restart_signal, 'worker': worker_proc,
            'work_queue': work_queue}

def main(pubkey, hashes_till_check, DB):
    """ Spawns worker CPU mining processes and coordinates the effort."""
    submitted_blocks = multiprocessing.Queue()
    num_cores = multiprocessing.cpu_count()
    tools.log("Creating %d mining workers." % num_cores)
    worker_mailboxes = [spawn_worker(submitted_blocks) for _ in range(num_cores)]
    candidate_block = None
    length = None
    while True:
        time.sleep(2)
        DB['heart_queue'].put('miner')
        length = DB['length']
        if length == -1:
            candidate_block = genesis(pubkey, DB)
            txs = []
        else:
            prev_block = blockchain.db_get(length, DB)
            candidate_block = make_block(prev_block, DB['txs'], pubkey, DB)

        work = (candidate_block, hashes_till_check)

        for worker_mailbox in worker_mailboxes:
            worker_mailbox['work_queue'].put(copy.copy(work))

        # When block found, add to suggested blocks.
        solved_block = submitted_blocks.get()  # TODO(roasbeef): size=1?
        if solved_block['length'] != length + 1:
            continue
        #tools.log('potential block: ' +str(solved_block))
        DB['suggested_blocks'].put(solved_block)
        restart_workers(worker_mailboxes)
        if DB['stop']:
            sys.exit(1)

