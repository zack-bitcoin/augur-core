"""
When a peer talks to us, this is how we generate a response.
This is the external API.
"""
import networking
import custom
import tools
import blockchain
import time

def security_check(dic):
    if 'version' not in dic or dic['version'] != custom.version:
        return {'bool': False, 'error': 'version'}
    else:
        #we could add security features here.
        return {'bool': True, 'newdic': dic}

def blockCount(dic):
    length = tools.db_get('length')
    if length >= 0:
        return {'length': length,
                'diffLength': tools.db_get('diffLength')}
    else:
        return {'length': -1, 'diffLength': '0'}

def rangeRequest(dic):
    ran = dic['range']
    out = []
    counter = 0
    while (len(tools.package(out)) < custom.max_download
           and ran[0] + counter <= ran[1]):
        block = tools.db_get(ran[0] + counter)
        if 'length' in block:
            out.append(block)
        counter += 1
    return out

def txs(dic):
    return tools.db_get('txs')

def pushtx(dic, txs_queue):
    txs_queue.put(dic['tx'])
    return 'success'

def pushblock(dic, blocks_queue):
    length=tools.db_get('length')
    block = tools.db_get(length)    
    if 'peer' in dic: peer=dic['peer']
    else: peer=False
    if 'blocks' in dic:
        for i in range(20):
            if tools.fork_check(dic['blocks'], length, block):
                blockchain.delete_block()
        for block in dic['blocks']:
            blocks_queue.put([block, peer])
    else:
        blocks_queue.put([dic['block'], peer])
    return 'success'

def main(dic, blocks_queue, txs_queue):
    funcs = {'blockCount': blockCount, 'rangeRequest': rangeRequest,
             'txs': txs, 'pushtx': pushtx, 'pushblock': pushblock}
    if 'type' not in dic:
        return 'oops: ' +str(dic)
    if dic['type'] not in funcs:
        return ' '.join([dic['type'], 'is not in the api'])
    check = security_check(dic)
    if not check['bool']:
        return check
    try:
        if dic['type'] == 'pushtx':
            return pushtx(check['newdic'], txs_queue)
        elif dic['type'] == 'pushblock':
            return pushblock(check['newdic'], blocks_queue)
        else:
            return funcs[dic['type']](check['newdic'])
    except Exception as exc:
        tools.log(exc)
