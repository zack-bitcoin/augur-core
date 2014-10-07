"""This program starts all the threads going. When it hears a kill signal, it kills all the threads.
"""
import ht, miner, peer_recieve, time, threading, tools, custom, networking, sys, truthcoin_api, blockchain, peers_check, multiprocessing, database
def main(brainwallet, pubkey_flag=False):
    print('starting truthcoin')
    if not pubkey_flag:
        privkey=tools.det_hash(brainwallet)
        pubkey=tools.privtopub(privkey)
    else:
        pubkey=brainwallet
    DB = {
        'reward_peers_queue':multiprocessing.Queue(),
        'suggested_blocks': multiprocessing.Queue(),
        'suggested_txs': multiprocessing.Queue(),
        'heart_queue': multiprocessing.Queue(),
    }
    processes= [
        {'target': database.main,
         'args': (DB['heart_queue'],)},
        {'target': peers_check.main,
         'args': (custom.peers, DB)},
        {'target':tools.heart_monitor,
         'args':(DB['heart_queue'], )},
        {'target': blockchain.main,
         'args': (DB,)},
        {'target': truthcoin_api.main,
         'args': (DB, DB['heart_queue'])},
        {'target': miner.main,
         'args': (pubkey, DB)},
        #{'target': networking.serve_forever,
        # 'args': (lambda d: peer_recieve.main(d, DB), custom.port, DB['heart_queue'], True)}
    ]
    cmds=[]
    cmd=multiprocessing.Process(target=processes[0]['target'], args=processes[0]['args'])
    cmd.start()
    time.sleep(4)
    cmds.append(cmd)
    tools.db_put('test', 'TEST')
    tools.log(tools.db_get('test'))
    tools.log(tools.db_get('test'))
    tools.db_put('test', 'n')
    for process in processes[1:]:
        cmd=multiprocessing.Process(target=process['target'], args=process['args'])
        cmd.start()
        cmds.append(cmd)
    b=tools.db_existence(0)
    if not b:
        tools.db_put('length', -1)
        tools.db_put('memoized_votes', {})
        tools.db_put('txs', [])
        tools.db_put('peers_ranked', [])
        tools.db_put('targets', {})
        tools.db_put('times', {})
        tools.db_put('mine', False)
        tools.db_put('diffLength', '0')
    else:
        error()
    tools.db_put('stop', False)
    if not pubkey_flag:
        tools.db_put('privkey', privkey)
    else:
        tools.db_put('privkey', 'Default')
    tools.db_put('address', tools.make_address([pubkey], 1))
    while not tools.db_get('stop'):
        time.sleep(0.5)
    tools.log('about to stop threads')
    DB['heart_queue'].put('stop')
    for cmd in cmds:
        cmd.join()
        tools.log('stopped a thread')
    tools.log('all threads stopped')
    print('all threads stopped')
    sys.exit(1)

