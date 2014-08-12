import consensus
import listener
import time
import threading
import custom
import leveldb
import networking
import command_prompt_advanced
import sys
import truthcoin_api
import tools
import blockchain
import gui
from multiprocessing import Queue, Process

i_queue=Queue()
o_queue=Queue()
run_script=''
try:
    '''
    script_lines=file(sys.argv[1],'r').readlines()
    tools.log('script_lines: ' +str(script_lines))
    script=[]
    for line in script_lines:
        script
        i_queue.put(line[:-1].split(' '))
    '''
    script=file(sys.argv[1],'r').read()
except: pass
db = leveldb.LevelDB(custom.database_name)
DB = {'stop':False,
      'db': db,
      #'sigLength': -1,
      'txs': [],
      'suggested_blocks': [],
      'suggested_txs': [],
      'memoized_votes':{},
      'diffLength': '0'}
def len_f(i, DB):
    if not blockchain.db_existence(str(i), DB): return i-1
    return len_f(i+1, DB)
DB['length']=len_f(0, DB)
DB['diffLength']='0'
if DB['length']>-1:
    #print('DB: ' +str(DB))
    DB['diffLength']=blockchain.db_get(str(DB['length']), DB)['diffLength']
#cmd_prompt_func=truthcoin_api.main
#if custom.cmd_prompt_advanced:
#    cmd_prompt_func=command_prompt_advanced.main

worker_tasks = [
    # Keeps track of blockchain database, checks on peers for new blocks and
    # transactions.
    {'target': consensus.miner_controller,
     'args': (custom.pubkey, custom.peers, custom.hashes_per_check, DB),
     'daemon': False},
    {'target': consensus.mainloop,
     'args': (custom.peers, DB),
     'daemon': True},#it makes more threads, so it can't be a daemon.
    # Listens for peers. Peers might ask us for our blocks and our pool of
    # recent transactions, or peers could suggest blocks and transactions to us.
    {'target': listener.server,
     'args': (DB,),
     'daemon': True},
    #{'target': gui.main,
    # 'args': (custom.gui_port, custom.brainwallet, DB),
    # 'daemon': True},
    {'target': truthcoin_api.main,
     'args': (DB, i_queue, o_queue),
     'daemon':True}
]
networking.kill_processes_using_ports([str(custom.gui_port),
                                       str(custom.listen_port)])
cmd=Process(target=command_prompt_advanced.main, args=(i_queue, o_queue, script))
cmd.start()
def start_worker_proc(**kwargs):
    #print("Making worker thread.")
    is_daemon = kwargs.pop('daemon', True)
    proc = threading.Thread(**kwargs)
    proc.daemon = is_daemon
    proc.start()
    return proc

#print('tasks: ' + str(worker_tasks))
workers = [start_worker_proc(**task_info) for task_info in worker_tasks]
while not DB['stop']:
    #print('in loop')
    time.sleep(0.5)
tools.log('stopping all threads...')
cmd.join()
time.sleep(5)
sys.exit(1)

