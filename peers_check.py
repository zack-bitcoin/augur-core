"""
We regularly check on peers to see if they have mined new blocks.
This file explains how we initiate interactions with our peers.
"""
import time
import networking
import tools
import blockchain
import custom
import random
import sys

def cmd(peer, x):
    return networking.send_command(peer, x)

def download_blocks(peer, blocks_queue, peers_block_count, length):
    b=[max(0, length-10), min(peers_block_count['length'], length+custom.download_many)]
    blocks = cmd(peer, {'type': 'rangeRequest', 'range': b})
    if type(blocks)!=list: return -1
    if not isinstance(blocks, list): return []
    length=tools.db_get('length')
    block=tools.db_get(length)
    for i in range(20):  # Only delete a max of 20 blocks, otherwise a
        # peer might trick us into deleting everything over and over.
        if tools.fork_check(blocks, length, block):
            blockchain.delete_block()
    for block in blocks:
        blocks_queue.put([block, peer])
    return 0

def ask_for_txs(peer, txs_queue):
    txs = cmd(peer, {'type': 'txs'})
    if not isinstance(txs, list):
        return -1
    for tx in txs:
        txs_queue.put(tx)
    T=tools.db_get('txs')
    pushers = [x for x in T if x not in txs]
    for push in pushers:
        cmd(peer, {'type': 'pushtx', 'tx': push})
    return 0

def give_block(peer, block_count_peer):
    blocks=[]
    b=[max(block_count_peer+1, 0), min(tools.db_get('length'), block_count_peer+custom.download_many)]
    for i in range(b[0], b[1]+1):
        blocks.append(tools.db_get(i))
    cmd(peer, {'type': 'pushblock',
               'blocks': blocks})
    return 0

def peer_check(i, peers, blocks_queue, txs_queue):
    peer=peers[i][0]
    block_count = cmd(peer, {'type': 'blockCount'})
    if not isinstance(block_count, dict):
        return
    if 'error' in block_count.keys():
        return
    peers[i][2]=block_count['diffLength']
    peers[i][3]=block_count['length']
    length = tools.db_get('length')
    diffLength= tools.db_get('diffLength')
    size = max(len(diffLength), len(block_count['diffLength']))
    us = tools.buffer_(diffLength, size)
    them = tools.buffer_(block_count['diffLength'], size)
    if them < us:
        return give_block(peer, block_count['length'])
    if us == them:
        try:
            return ask_for_txs(peer, txs_queue)
        except:
            tools.log('ask for tx error')
    #try:
    return download_blocks(peer, blocks_queue, block_count, length)
    #except:
    #    tools.log('could not download blocks')

def exponential_random(r, i=0):
    if random.random()<r: return i
    return exponential_random(r, i+1)

def main(peers, heart_queue, blocks_queue, txs_queue):
    # Check on the peers to see if they know about more blocks than we do.
    #DB['peers_ranked']=[]
    p=tools.db_get('peers_ranked')
    if type(p)!=list:
        time.sleep(3)
        return main(peers, heart_queue, blocks_queue, txs_queue)
    for peer in peers:
        tools.log('add peer')
        p.append([peer, 5, '0', 0])
    tools.db_put('peers_ranked', p)
    try:
        while True:
            if tools.db_get('stop')==True: return
            if len(peers)>0:
                main_once(heart_queue, blocks_queue, txs_queue)
    except:
        tools.log('main peers check: ' +str(sys.exc_info()))

def main_once(heart_queue, blocks_queue, txs_queue):
    heart_queue.put('peers check')
    pr=tools.db_get('peers_ranked')
    pr=sorted(pr, key=lambda r: r[2])
    pr.reverse()
    if blocks_queue.empty() and tools.db_get('length')>3:
        time.sleep(10)
    i=0
    while not blocks_queue.empty():
        i+=1
        time.sleep(0.1)
        if i%100==0: 
            heart_queue.put('peers check')
    heart_queue.put('peers check')
    i=exponential_random(3.0/4)%len(pr)
    t1=time.time()
    r=peer_check(i, pr, blocks_queue, txs_queue)
    t2=time.time()
    pr[i][1]*=0.8
    if r==0:
        pr[i][1]+=0.2*(t2-t1)
    else:
        pr[i][1]+=0.2*30
    tools.db_put('peers_ranked', pr)
    heart_queue.put('peers check')



