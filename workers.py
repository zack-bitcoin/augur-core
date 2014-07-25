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

run_script=''
try:
    script_lines=file(sys.argv[1],'r').readlines()
    for line in script_lines:
        run_script+=line
except: pass

db = leveldb.LevelDB(custom.database_name)
DB = {'db': db,
      'recentHash': 0,
      'length': -1,
      'sigLength': -1,
      'txs': [],
      'suggested_blocks': [],
      'suggested_txs': [],
      'memoized_votes':{},
      'diffLength': '0'}

cmd_prompt_func=truthcoin_api.main
if custom.cmd_prompt_advanced:
    cmd_prompt_func=command_prompt_advanced.main

worker_tasks = [
    # Keeps track of blockchain database, checks on peers for new blocks and
    # transactions.
    {'target': consensus.miner_controller,
     'args': (custom.pubkey, custom.peers, custom.hashes_per_check, DB),
     'daemon': True},
    {'target': consensus.mainloop,
     'args': (custom.peers, DB),
     'daemon': True},
    # Listens for peers. Peers might ask us for our blocks and our pool of
    # recent transactions, or peers could suggest blocks and transactions to us.
    {'target': listener.server,
     'args': (DB,),
     'daemon': True},
#    {'target': gui.main,
#     'args': (custom.gui_port, custom.brainwallet, DB),
#     'daemon': True},
    {'target': cmd_prompt_func,
     'args': (DB,run_script),
     'daemon': True},
]
networking.kill_processes_using_ports([str(custom.gui_port),
                                       str(custom.listen_port)])


def start_worker_proc(**kwargs):
    print("Making worker thread.")
    is_daemon = kwargs.pop('daemon', True)
    proc = threading.Thread(**kwargs)
    proc.daemon = is_daemon
    proc.start()
    return proc

#print('tasks: ' + str(worker_tasks))
workers = [start_worker_proc(**task_info) for task_info in worker_tasks]
try:
    while True:
        time.sleep(100)
except:
    print("Exiting.")
    sys.exit(1)
