"""We regularly check on peers to see if they have mined new blocks.
This file explains how we initiate interactions with our peers.
"""
import time, networking, tools, blockchain, custom, random, sys
def cmd(peer, x): 
    if type(peer)!=list:
        peer=tools.peer_split(peer)
    return networking.send_command(peer, x)
def download_blocks(peer, DB, peers_block_count, length):
    b=[max(0, length-10), min(peers_block_count, length+custom.download_many)]
    blocks = cmd(peer, {'type': 'rangeRequest', 'range': b})
    if type(blocks)!=list: return -1
    if not isinstance(blocks, list): return []
    length=tools.db_get('length')
    block=tools.db_get(length)
    for i in range(10):#this part should be re-written so badly
        if tools.fork_check(blocks, DB, length, block):
            blockchain.delete_block(DB)
            length-=1
    for block in blocks:
        DB['suggested_blocks'].put([block, peer])
    return 0
def ask_for_txs(peer, DB):
    txs = cmd(peer, {'type': 'txs'})
    if not isinstance(txs, list):
        return -1
    for tx in txs:
        DB['suggested_txs'].put(tx)
    T=tools.db_get('txs')
    pushers = filter(lambda t: t not in txs, T)
    for push in pushers:
        cmd(peer, {'type': 'pushtx', 'tx': push})
    return 0
def give_block(peer, DB, block_count_peer):
    blocks=[]
    b=[max(block_count_peer-5, 0), min(tools.db_get('length'), block_count_peer+custom.download_many)]
    for i in range(b[0], b[1]+1):
        blocks.append(tools.db_get(i, DB))
    cmd(peer, {'type': 'pushblock',
               'blocks': blocks})
    return 0
def ask_for_count(peer):
    peers=tools.db_get('peers')
    block_count = cmd(peer, {'type': 'blockCount'})
    if not isinstance(block_count, dict):
        return
    if 'error' in block_count.keys():
        return
    peers[peer]['diffLength']=block_count['diffLength']
    peers[peer]['length']=block_count['length']
    tools.db_put('peers', peers)
def trade_peers(peer):
    peers=tools.db_get('peers')
    peer_length=peers[peer]['length']
    peer_diffLength=peers[peer]['diffLength']
    their_peers=cmd(peer, {'type':'peers'})
    if type(their_peers)==list:#compatibility so that I can download from old-fashioned nodes
        out={}
        for p in their_peers:
            out[p[0][0]]=tools.empty_peer()
            out[p[0][0]]['port']=p[0][1]
        their_peers=out#end of compatibility patch.
    #tools.log('their_peers: ' +str(their_peers))
    if 'error' in their_peers.keys(): return {'error':'cannot connect'}
    def minus(a, b): 
        return filter(lambda p: p not in b, a)
    to_them=minus(peers.keys(), their_peers.keys())
    to_me=minus(their_peers.keys(), peers.keys())
    for p in to_me:
        if not ':' in p:#these two lines wont be necessary after the networking node finishes downloading the blockchain.
            p=p+':'+str(their_peers[p]['port'])
        #tools.log('peer: ' +str(p))
        tools.add_peer(p)
    cmd(peer, {'type':'recieve_peer', 'peers':to_them})
def peer_check(peer, DB):
    peers=tools.db_get('peers')
    if peers[peer]['length']==0 or random.random()<0.1:
        ask_for_count(peer)
        out=trade_peers(peer)
        if type(out)==dict and 'error' in out:
            return 1
    peers=tools.db_get('peers')
    length = tools.db_get('length')
    diffLength= tools.db_get('diffLength')
    size = max(len(diffLength), len(peers[peer]['diffLength']))
    us = tools.buffer_(diffLength, size)
    them = tools.buffer_(peers[peer]['diffLength'], size)
    if them < us:
        return give_block(peer, DB, peers[peer]['length'])
    elif us == them:
        try:
            ask_for_count(peer)
            trade_peers(peer)
            return ask_for_txs(peer, DB)
        except Exception as exc:
            tools.log('ask for tx error')
            tools.log(exc)
    else:
        return download_blocks(peer, DB, peers[peer]['length'], length)
def exponential_random(r, i=0):
    if random.random()<r: return i
    return exponential_random(r, i+1)
def main(peers, DB):
    # Check on the peers to see if they know about more blocks than we do.
    map(tools.add_peer, peers)
    try:
        while True:
            time.sleep(0.01)
            if tools.db_get('stop'): return
            main_once(DB)
    except Exception as exc:
        tools.log(exc)
def main_once(DB):
    pr=tools.db_get('peers')
    keys=filter(lambda x: pr[x]['blacklist']<500 , pr.keys())
    keys=sorted(keys, key=lambda r: pr[r]['lag'])
    if len(keys)<1:
        time.sleep(0.5)
        return
    time.sleep(0.05)
    while not DB['suggested_blocks'].empty():
        time.sleep(0.1)
        if tools.db_get('stop'): return 0
    i=exponential_random(9.0/10)%len(keys)
    t1=time.time()
    r=peer_check(keys[i], DB)
    t2=time.time()
    a=0.5
    pr=tools.db_get('peers')#this has been changed, we need to reload.
    pr[keys[i]]['lag']*=(1-a)
    if r==0: a*=(t2-t1)
    else: 
        a*=60
    pr[keys[i]]['lag']+=a
    tools.db_put('peers', pr)



