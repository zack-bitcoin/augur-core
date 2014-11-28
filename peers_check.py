"""We regularly check on peers to see if they have mined new blocks.
This file explains how we initiate interactions with our peers.
"""
import time, networking, tools, blockchain, custom, random, sys
def cmd(peer, x): return networking.send_command(peer, x)
def download_blocks(peer, DB, peers_block_count, length):
    b=[max(0, length-10), min(peers_block_count['length']+1, length+custom.download_many)]
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
def peer_check(i, peers, DB):
    peer=peers[i][0]
    #tools.log('before block count')
    block_count = cmd(peer, {'type': 'blockCount'})
    #tools.log('block count: ' +str(block_count))
    if not isinstance(block_count, dict):
        return
    if 'error' in block_count.keys():
        return
    peers[i][2]=block_count['diffLength']
    peers[i][3]=block_count['length']
    tools.db_put('peers_ranked', peers)
    my_peers=tools.db_get('peers_ranked')
    their_peers=cmd(peer, {'type':'peers'})
    if type(their_peers)==list:
        for p in their_peers:
            if p not in my_peers:
                F=True
                tools.add_peer(p)
                #my_peers.append(p)
        for p in my_peers:
            if p not in their_peers:
                cmd(peer, {'type':'recieve_peer', 'peer':p})
    length = tools.db_get('length')
    diffLength= tools.db_get('diffLength')
    size = max(len(diffLength), len(block_count['diffLength']))
    us = tools.buffer_(diffLength, size)
    them = tools.buffer_(block_count['diffLength'], size)
    if them < us:
        return give_block(peer, DB, block_count['length'])
    elif us == them:
        try:
            return ask_for_txs(peer, DB)
        except Exception as exc:
            tools.log('ask for tx error')
            tools.log(exc)
    else:
        return download_blocks(peer, DB, block_count, length)
def exponential_random(r, i=0):
    if random.random()<r: return i
    return exponential_random(r, i+1)
def main(peers, DB):
    # Check on the peers to see if they know about more blocks than we do.
    #DB['peers_ranked']=[]
    p=tools.db_get('peers_ranked')
    if type(p)!=list:
        time.sleep(3)
        return main(peers, DB)
    for peer in peers:
        tools.add_peer(peer, p)
    try:
        while True:
            time.sleep(0.01)
            if tools.db_get('stop'): return
            if len(peers)>0:
                main_once(DB)
    except Exception as exc:
        tools.log(exc)
def main_once(DB):
    pr=tools.db_get('peers_ranked')
    pr=sorted(pr, key=lambda r: r[2])
    pr.reverse()
    time.sleep(0.05)
    #if DB['suggested_blocks'].empty() and tools.db_get('length')>3:
    #    time.sleep(0)
    i=0
    while not DB['suggested_blocks'].empty():
        i+=1
        time.sleep(0.1)
    i=exponential_random(2.0/4)%len(pr)
    blacklist=tools.db_get('blacklist')
    p=tools.package(pr[i][0])
    while p in blacklist and blacklist[p]>500:
        i=exponential_random(2.0/4)%len(pr)
        p=tools.package(pr[i][0])
        pr[i][1]=100
    t1=time.time()
    r=peer_check(i, pr, DB)
    t2=time.time()
    p=pr[i][0]
    pr=tools.db_get('peers_ranked')
    a=0.5
    for peer in pr:
        if peer[0]==p:
            pr[i][1]*=(1-a)
            if r==0:
                pr[i][1]+=a*(t2-t1)
            else:
                pr[i][1]+=a*60
    tools.db_put('peers_ranked', pr)



