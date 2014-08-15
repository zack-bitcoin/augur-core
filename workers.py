import miner
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
peers_queue=Queue()
peers_queue_2=Queue()
try:
    script=file(sys.argv[1],'r').read()
except: script=''
db = leveldb.LevelDB(custom.database_name)
DB = {'stop':False,
      'db': db,
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
    DB['diffLength']=blockchain.db_get(str(DB['length']), DB)['diffLength']
#cmd_prompt_func=truthcoin_api.main
#if custom.cmd_prompt_advanced:
#    cmd_prompt_func=command_prompt_advanced.main

worker_tasks = [
    # Keeps track of blockchain database, checks on peers for new blocks and
    # transactions.
    #all these workers share memory DB
    #if any one gets blocked, then they are all blocked.
    {'target': miner.main,
     'args': (custom.pubkey, custom.hashes_per_check, DB),
     'daemon': False},#it makes more threads, so it can't be a daemon.
    {'target': blockchain.suggestion_blocks,
     'args': (DB),
     'daemon': True},
    {'target': blockchain.suggestion_txs,
     'args': (DB),
     'daemon': True},
    {'target': peers_check.main,
     'args': (custom.peers, DB),
     'daemon': True},
    {'target': listener.sender,
     'args': (DB, peers_queue_2),
     'daemon': True},
    {'target': truthcoin_api.main,
     'args': (DB, i_queue, o_queue),
     'daemon':True}
]
networking.kill_processes_using_ports([str(custom.gui_port),
                                       str(custom.listen_port)])
processes= [#these do NOT share memory with the rest.
    {'target':command_prompt_advanced.main, 
     'args':(i_queue, o_queue, script)},
    {'target':networking.serve_forever, 
     'args':(peers_queue, custom.listen_port)},
    {'target':listener.reciever, 
     'args':(peers_queue, peers_queue_2)}
]
cmds=[]
for process in processes:
    cmd=Process(target=process['target'], args=process['args'])
    cmd.start()
    cmds.append(cmd)
def start_worker_proc(**kwargs):
    #print("Making worker thread.")
    proc = threading.Thread(**kwargs)
    proc.daemon = kwargs.pop('daemon', True)
    proc.start()
    return proc

#print('tasks: ' + str(worker_tasks))
workers = [start_worker_proc(**task_info) for task_info in worker_tasks]
while not DB['stop']:
    #print('in loop')
    time.sleep(0.5)
tools.log('stopping all threads...')
for cmd in cmds:
    cmd.join()
time.sleep(5)
sys.exit(1)

