"""This does the same thing as gui.py but without graphics"""

import copy
import tools
import blockchain
import custom
import http
import random
import transactions
import sys
import txs_tools
import time
import command_prompt_advanced

def create_jury(DB): 
    return easy_add_transaction({'type': 'create_jury', 'vote_id': DB['args'][0]}, DB)
def DB_print(DB):
    return(str(DB))
def info(DB): 
    '''    if DB['args']<1:
        print('here')
        error()
        #'unique id for that info?: '), DB)))
    '''
    if len(DB['args'])<1:
        return ('whos info? example: info 0')
    return(str(blockchain.db_get(DB['args'][0], DB)))   
def my_address(DB):
    return(str(custom.address))
def spend(DB): easy_add_transaction({'type': 'spend', 'amount': int(raw_input('how much to send (in satoshis)? ' )), 'to': raw_input('who to send to? ' )}, DB)
def votecoin_spend(DB):
    tx = {'type': 'spend', 'amount':int(DB['args'][0]), 'to': DB['args'][2], 'vote_id':DB['args'][1]}
    return easy_add_transaction(tx, DB)

def ask_decision(DB):
    if len(DB['args'])<3:
        return('unique id for that branch? unique id for that decision? txt of decision? ')
    tx={'type':'propose_decision', 'vote_id':DB['args'][0], 'decision_id':DB['args'][1], 'txt':accumulate_words(DB['args'][2:])[1:]}
    return easy_add_transaction(tx, DB)

def vote_on_decision(DB):
    if len(DB['args'])<3:
        return('unique id for that branch? unique id for that decision? answer "yes" or "no": ')
    decision_id=DB['args'][1]
    answer=DB['args'][2]
    acc=blockchain.db_get(custom.address, DB)
    value=[answer, str(random.random())+str(random.random())]
    answer_hash=tools.det_hash(value)
    DB['memoized_votes'][answer_hash]=value
    old_vote='unsure'
    if decision_id in acc['votes']: #this is always False...
        old_vote=acc['votes'][decision_id]
    tx={'type':'jury_vote', 'vote_id':DB['args'][0], 'decision_id':decision_id, 'old_vote':old_vote, 'new_vote':answer_hash}
    return easy_add_transaction(tx, DB)

def reveal_vote(DB):
    if len(DB['args'])<2:
        return('unique id for that branch? unique id for that decision?')
    acc=blockchain.db_get(custom.address, DB)
    decision_id=DB['args'][1]
    if decision_id in acc['votes']:
        answer_hash=acc['votes'][decision_id]
        if answer_hash not in DB['memoized_votes']:
            return('reveal vote error')
        a=DB['memoized_votes'][answer_hash]
        tx={'type':'reveal_jury_vote', 'vote_id':DB['args'][0], 'decision_id':decision_id, 'old_vote':answer_hash, 'new_vote':a[0], 'secret':a[1]}
        return easy_add_transaction(tx, DB)
    else:
        return('you do not have any encrypted vote to decrypt')

def decisions_keepers(jury, DB):
    matrix=transactions.decision_matrix(jury, jury['decisions'], DB)
    #exclude decisions with insufficient participation*certainty
    pc=transactions.part_cert(matrix)
    decisions=[]
    for i in range(len(pc)):
        if pc[i]>0.6:
            decisions.append(jury['decisions'][i])
    return decisions

def SVD_consensus(DB):
    if len(DB['args'])<1:
        return('unique id for that branch?')
    vote_id=DB['args'][0]
    jury=blockchain.db_get(vote_id, DB)
    tx={'type':'SVD_consensus', 'vote_id':vote_id, 'decisions':decisions_keepers(jury, DB)}
    return(easy_add_transaction(tx, DB))

def make_PM(DB):
    tx={'type':'prediction_market', 'PM_id':'weather', 'fees':0, 'B':10, 'states':['0 0 0', '1 0 0', '1 1 0', 'default'], 'states_combinatory':[[0,0,0],[1,0,0],[1,1,0]], 'shares_purchased':[0,0,0,0],'decisions':["decision_1","decision_2","decision_3"], 'owner':custom.address}
    #print('pm in make: ' +str(tx))
    return(easy_add_transaction(tx, DB))

def buy_shares(DB):
    tx={'type':'buy_shares', 'buy':[5,4,3,0], 'PM_id':'weather'}
    return(easy_add_transaction(tx, DB))

def collect_winnings(DB):
    add=custom.address
    acc=blockchain.db_get(add, DB)
    tx={'type':'collect_winnings', 'PM_id':'weather', 'shares':acc['shares'][tx['PM_id']], 'address':add}
    return easy_add_transaction(tx, DB)

def easy_add_transaction(tx_orig, DB):
    tx = copy.deepcopy(tx_orig)
    if 'pubkeys' not in tx:
        tx['pubkeys']=[custom.pubkey]
    try:
        tx['count'] = blockchain.count(custom.address, DB)
    except:
        tx['count'] = 1
    tx['signatures'] = [tools.sign(tools.det_hash(tx), custom.privkey)]
    return(blockchain.add_tx(tx, DB))


def help_(DB):      return(str('available commands: '+str(Do.keys())))
def blockcount(DB): return(str(DB['length']))
def txs(DB):        return(str(DB['txs']))
def difficulty(DB): return(str(blockchain.target(DB)))
def me(DB):         
    a=str(blockchain.db_get(custom.address, DB))
    return(a)
def my_balance(DB, address=custom.address): 
    return(str(blockchain.db_get(address, DB)['amount']-txs_tools.cost_0(DB['txs'], DB)['truthcoin_cost']))
def wait_till_block(DB):
    while True:
        time.sleep(1)
        b=blockcount(DB)
        if int(b)>=int(DB['args'][0]):
            return str(b)
def balance(DB): return(str(my_balance(DB, raw_input('address'))))
def log(DB): tools.log(accumulate_words(DB['args'])[1:])
def stop_(DB): DB['stop']=True
Do={'SVD_consensus':SVD_consensus, 'reveal_vote':reveal_vote, 'vote_on_decision':vote_on_decision, 'ask_decision':ask_decision, 'create_jury':create_jury, 'spend':spend, 'votecoin_spend':votecoin_spend, 'make_PM':make_PM, 'buy_shares':buy_shares, 'collect_winnings':collect_winnings, 'h':help_, 'help':help_, '?':help_, 'blockcount':blockcount, 'txs':txs, 'balance':balance, 'my_balance':my_balance, 'b':my_balance, 'difficulty':difficulty, 'info':info, 'me':me, 'wait_till_block':wait_till_block, '':(lambda DB: 42), 'DB':DB_print, 'my_address':my_address, 'log':log, 'stop':stop_}
#def Do_func(DB): return Do.get(DB['command'], lambda DB: str(DB['command']) + ' is not a command. use "?" for a list of commands')(DB)
def accumulate_words(l, out=''):
    if len(l)>0: return accumulate_words(l[1:], out+' '+l[0])
    return out
def main(DB, i_queue, o_queue):
    #command_prompt_advanced.run_script(DB, script)
    while True:
        time.sleep(0.4)
        if not(i_queue.empty()):
            command=i_queue.get()
            if command[0] in Do: 
                DB['args']=command[1:]
                out=Do[command[0]](DB)
            else: 
                out=str(command[0]) + ' is not a command. use "?" for a list of commands'
            #tools.log('tryint to print: ' +str(out))
            o_queue.put(out)
        #DB['command']=raw_input('>>> ')
        #if command in Do: Do[command](DB)
        #out=Do_func(DB)
        #print(out)
        #tools.log(out)
        #else: print(str(command) + ' is not a command. use "?" for a list of commands')




