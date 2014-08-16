import time, networking, tools, blockchain, custom
def cmd(peer, x):
    return networking.send_command(peer, x)
def fork_check(newblocks, DB):
    block = blockchain.db_get(DB['length'], DB)
    recent_hash = tools.det_hash(block)
    their_hashes = map(tools.det_hash, newblocks)
    return recent_hash not in their_hashes
def bounds(length, peers_block_count):
    if peers_block_count['length'] - length > custom.download_many:
        end = length + custom.download_many - 1
    else:
        end = peers_block_count['length']
    return [max(length - 2, 0), end]
def download_blocks(peer, DB, peers_block_count, length):
    blocks = cmd(peer, {'type': 'rangeRequest',
                        'range': bounds(length, peers_block_count)})
    if not isinstance(blocks, list):
        return []
    for i in range(2):  # Only delete a max of 2 blocks, otherwise a
        # peer might trick us into deleting everything over and over.
        if fork_check(blocks, DB):
            blockchain.delete_block(DB)
    for block in blocks:
        DB['suggested_blocks'].put(block)
    return
def ask_for_txs(peer, DB):
    txs = cmd(peer, {'type': 'txs'})
    for tx in txs:
        DB['suggested_txs'].put(tx)
    pushers = [x for x in DB['txs'] if x not in txs]
    for push in pushers:
        cmd(peer, {'type': 'pushtx', 'tx': push})
    return []
def give_block(peer, DB, block_count):
    cmd(peer, {'type': 'pushblock',
               'block': blockchain.db_get(block_count['length'] + 1,
                                          DB)})
    return []
def peer_check(peer, DB):
    block_count = cmd(peer, {'type': 'blockCount'})
    #tools.log('block count: ' +str(block_count))
    if not isinstance(block_count, dict):
        return
    if 'error' in block_count.keys():
        return
    length = DB['length']
    size = max(len(DB['diffLength']), len(block_count['diffLength']))
    us = tools.buffer_(DB['diffLength'], size)
    them = tools.buffer_(block_count['diffLength'], size)
    if them < us:
        return give_block(peer, DB, block_count)
    if us == them:
        return ask_for_txs(peer, DB)
    return download_blocks(peer, DB, block_count, length)
def main(peers, DB):
    # Check on the peers to see if they know about more blocks than we do.
    while True:
        time.sleep(10)
        for peer in peers:
            peer_check(peer, DB)
