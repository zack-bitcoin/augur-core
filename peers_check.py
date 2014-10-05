"""We regularly check on peers to see if they have mined new blocks.
This file explains how we initiate interactions with our peers.
"""
import time, networking, tools, blockchain, custom, random, sys
def cmd(peer, x): return networking.send_command(peer, x)
def download_blocks(peer, DB, peers_block_count, length):
    b=[max(0, length-10), min(peers_block_count['length'], length+custom.download_many)]
    blocks = cmd(peer, {'type': 'rangeRequest', 'range': b})
    if type(blocks)!=list: return -1
    if not isinstance(blocks, list): return []
    for i in range(20):  # Only delete a max of 20 blocks, otherwise a
        # peer might trick us into deleting everything over and over.
        if tools.fork_check(blocks, DB):
            blockchain.delete_block(DB)
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
    pushers = [x for x in T if x not in txs]
    for push in pushers:
        cmd(peer, {'type': 'pushtx', 'tx': push})
    return 0
def give_block(peer, DB, block_count_peer):
    blocks=[]
    b=[max(block_count_peer+1, 0), min(DB['length'], block_count_peer+custom.download_many)]
    for i in range(b[0], b[1]+1):
        blocks.append(tools.db_get(i, DB))
    cmd(peer, {'type': 'pushblock',
               'blocks': blocks})
    return 0
def peer_check(peer, DB):
    block_count = cmd(peer, {'type': 'blockCount'})
    if not isinstance(block_count, dict):
        return
    if 'error' in block_count.keys():
        return
    length = DB['length']
    diffLength= tools.db_get('diffLength')
    size = max(len(diffLength), len(block_count['diffLength']))
    us = tools.buffer_(diffLength, size)
    them = tools.buffer_(block_count['diffLength'], size)
    if them < us:
        return give_block(peer, DB, block_count['length'])
    if us == them:
        try:
            return ask_for_txs(peer, DB)
        except:
            tools.log('ask for tx error')
    try:
        return download_blocks(peer, DB, block_count, length)
    except:
        tools.log('could not download blocks')
def exponential_random(weights):
    def grab(r, weights, counter=0):
        if len(weights)==0: return counter
        if r<weights[0]: return counter
        else: return grab(r-weights[0], weights[1:], counter+1)
    weights=map(lambda x: 1.0/x, weights)
    tot=sum(weights)
    r=random.random()*tot
    return grab(r, weights)
def main(peers, DB):
    # Check on the peers to see if they know about more blocks than we do.
    #DB['peers_ranked']=[]
    p=tools.db_get('peers_ranked')
    for peer in peers:
        p.append([peer, 5])
    tools.db_put('peers_ranked', p)
    try:
        while True:
            if tools.db_get('stop'): return
            if len(peers)>0:
                main_once(peers, DB)
            while not DB['reward_peers_queue'].empty():
                q=DB['reward_peers_queue'].get()
                p=q['peer']
                d=q['do']
                pr=tools.db_get('peers_ranked')
                i=0
                j='empty'
                for p in pr:
                    if p[0]==peer:
                        j=i
                    i+=1
                if j!='empty':
                    if d=='reward':
                        #listen more to people who give us good blocks.
                        pr[j][1]*=0.1
                    elif d=='punish':
                        #listen less to people who give us bad blocks.
                        pr[j][1]*=0.8
                        pr[j][1]+=0.2*60
                    tools.db_put('peers_ranked', pr)
                else:
                    #maybe this peer should be added to our list of peers?
                    pass
    except:
        tools.log('main peers check: ' +str(sys.exc_info()))
def main_once(peers, DB):
    #DB['peers_ranked']=sorted(DB['peers_ranked'], key=lambda r: r[1])
    DB['heart_queue'].put('peers check')
    pr=tools.db_get('peers_ranked')
    pr=sorted(pr, key=lambda r: r[1])
    if DB['suggested_blocks'].empty():
        time.sleep(10)
    i=0
    while not DB['suggested_blocks'].empty():
        i+=1
        time.sleep(0.1)
        if i%100==0: 
            DB['heart_queue'].put('peers check')
    #tools.log('suggested_blocks emptied at : ' +str(time.time()))
    DB['heart_queue'].put('peers check')
    i=exponential_random(map(lambda x: x[1], pr))
    t1=time.time()
    r=peer_check(pr[i][0], DB)
    t2=time.time()
    pr[i][1]*=0.8
    if r==0:
        pr[i][1]+=0.2*(t2-t1)
    else:
        pr[i][1]+=0.2*30
    tools.db_put('peers_ranked', pr)
    DB['heart_queue'].put('peers check')
