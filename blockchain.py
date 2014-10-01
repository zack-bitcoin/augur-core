""" This file explains explains the rules for adding and removing blocks from the local chain.
"""
import time
import copy
import custom
import networking
import transactions
import sys
import tools
import target

def add_tx(tx, DB):
    # Attempt to add a new transaction into the pool.
    #print('top of add_tx')
    out=['']
    if type(tx) != type({'a':1}): 
        return False
    address = tools.make_address(tx['pubkeys'], len(tx['signatures']))
    def verify_count(tx, txs):
        return tx['count'] != tools.count(address, DB)
    def type_check(tx, txs):
        if not tools.E_check(tx, 'type', [str, unicode]):
            out[0]+='blockchain type'
            return False
        if tx['type'] == 'mint':
            return False
        if tx['type'] not in transactions.tx_check:
            out[0]+='bad type'
            return False
        return True
    def too_big_block(tx, txs):
        return len(tools.package(txs+[tx])) > networking.MAX_MESSAGE_SIZE - 5000
    def verify_tx(tx, txs, out):
        if not type_check(tx, txs):
            out[0]+='type error'
            return False
        if tx in txs:
            out[0]+='no duplicates'
            return False
        if verify_count(tx, txs):
            out[0]+='count error'
            return False
        if too_big_block(tx, txs):
            out[0]+='too many txs'
            return False
        tools.log('before tx check')
        if not transactions.tx_check[tx['type']](tx, txs, out, DB):
            out[0]+= 'tx: ' + str(tx)
            return False
        return True
    #tools.log('attempt to add tx: ' +str(tx))
    if verify_tx(tx, DB['txs'], out):
        DB['txs'].append(tx)
        return('added tx: ' +str(tx))
    else:
        return('failed to add tx because: '+out[0])
def recent_blockthings(key, DB, size, length=0):
    if key == 'time':
        storage = DB['times']
    if key == 'target':
        storage = DB['targets']
    def get_val(length):
        leng = str(length)
        if not leng in storage:
            storage[leng] = tools.db_get(leng, DB)[key]
        return storage[leng]
    if length == 0:
        length = DB['length']
    start = (length-size) if (length-size) >= 0 else 0
    return map(get_val, range(start, length))
def hexSum(a, b):
    # Sum of numbers expressed as hexidecimal strings
    return tools.buffer_(str(hex(int(a, 16)+int(b, 16)))[2: -1], 64)
def hexInvert(n):
    # Use double-size for division, to reduce information leakage.
    return tools.buffer_(str(hex(int('f' * 128, 16) / int(n, 16)))[2: -1], 64)
def add_block(block_pair, DB):
    """Attempts adding a new block to the blockchain.
     Median is good for weeding out liars, so long as the liars don't have 51%
     hashpower. """
    def median(mylist):
        if len(mylist) < 1:
            return 0
        return sorted(mylist)[len(mylist) / 2]

    def block_check(block, DB):
        def tx_check(txs):
            start = copy.deepcopy(txs)
            out = []
            start_copy = []
            while start != start_copy:
                if start == []:
                    return False  # Block passes this test
                start_copy = copy.deepcopy(start)
                if transactions.tx_check[start[-1]['type']](start[-1], out, [''], DB):
                    out.append(start.pop())
                else:
                    return True  # Block is invalid
            return True  # Block is invalid
        if not isinstance(block, dict): return False
        if 'error' in block: return False
        if not tools.E_check(block, 'length', [int]):
            return False
        length = DB['length']
        if int(block['length']) != int(length) + 1:
            return False
        if block['diffLength'] != hexSum(DB['diffLength'],
                                         hexInvert(block['target'])):
            return False
        if length >= 0:
            if tools.det_hash(tools.db_get(length, DB)) != block['prevHash']:
                return False
        a = copy.deepcopy(block)
        a.pop('nonce')
        if u'target' not in block.keys():
            return False
        half_way = {u'nonce': block['nonce'], u'halfHash': tools.det_hash(a)}
        if tools.det_hash(half_way) > block['target']:
            return False
        if block['target'] != target.target(DB, block['length']):
            return False
        earliest = median(recent_blockthings('time', DB, custom.mmm))
        if 'time' not in block:
            return False
        if block['time'] > time.time():
            return False
        if block['time'] < earliest:
            return False
        if tx_check(block['txs']):
            return False
        return True
    if type(block_pair)==type([1,2,3]):
        block=block_pair[0]
        peer=block_pair[1]
    else:
        block=block_pair
        peer=False
    #tools.log('attempt to add block: ' +str(block))
    if block_check(block, DB):
        #tools.log('add_block: ' + str(block))
        i=0
        j='empty'
        if peer != False:
            for p in DB['peers_ranked']:
                if p[0]==peer:
                    j=i
                i+=1
            if j!='empty':
                DB['peers_ranked'][j][1]*=0.1#listen more to people who give us good blocks.
            else:
                #maybe this peer should be added to our list of peers?
                pass
        tools.db_put(block['length'], block, DB)
        DB['length'] = block['length']
        DB['diffLength'] = block['diffLength']
        orphans = copy.deepcopy(DB['txs'])
        DB['txs'] = []
        for tx in block['txs']:
            DB['add_block']=True
            transactions.update[tx['type']](tx, DB)
        for tx in orphans:
            add_tx(tx, DB)
    else:
        i=0
        j='empty'
        if peer != False:
            for p in DB['peers_ranked']:
                if p[0]==peer:
                    j=i
                i+=1
            if j!='empty':
                DB['peers_ranked'][j][1]*=0.8#listen less to people who give us bad blocks.
                DB['peers_ranked'][j][1]+=0.2*60
            else:
                #maybe this peer should be added to our list of peers?
                pass


def delete_block(DB):
    """ Removes the most recent block from the blockchain. """
    if DB['length'] < 0:
        return
    try:
        DB['targets'].pop(str(DB['length']))
    except:
        pass
    try:
        DB['times'].pop(str(DB['length']))
    except:
        pass
    block = tools.db_get(DB['length'], DB)
    orphans = copy.deepcopy(DB['txs'])
    DB['txs'] = []
    for tx in block['txs']:
        orphans.append(tx)
        DB['add_block']=False
        transactions.update[tx['type']](tx, DB)
    tools.db_delete(DB['length'], DB)
    DB['length'] -= 1
    if DB['length'] == -1:
        DB['diffLength'] = '0'
    else:
        block = tools.db_get(DB['length'], DB)
        DB['diffLength'] = block['diffLength']
    for orphan in sorted(orphans, key=lambda x: x['count']):
        add_tx(orphan, DB)
def suggestions(DB, s, f, t, a):
    while True:
        DB['heart_queue'].put(s)
        for i in range(100):
            if i%t==0:
                time.sleep(a)
            if DB['stop']: return
            if not DB[s].empty():
                try:
                    f(DB[s].get(False), DB)
                except:
                    tools.log('suggestions ' + s + ' '+str(sys.exc_info()))
def suggestion_txs(DB): 
    try:
        return suggestions(DB, 'suggested_txs', add_tx, 1, 0.05)
    except:
        tools.log('suggestions txs error: ' +str(sys.exc_info()))
def suggestion_blocks(DB): 
    try:
        return suggestions(DB, 'suggested_blocks', add_block, 5, 0.01)
    except:
        tools.log('suggestions blocks error: ' +str(sys.exc_info()))
