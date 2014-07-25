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
    easy_add_transaction({'type': 'create_jury', 'vote_id': DB['args'][0]}, DB)
def DB_print(DB):
    return(str(DB))
def info(DB): 
    if DB['args']<1:
        print('here')
        error()
        #'unique id for that info?: '), DB)))
    if len(DB['args'])<1:
        return ('whos info? example: info 0')
    return(str(blockchain.db_get(DB['args'][0], DB)))   
def spend(DB): easy_add_transaction({'type': 'spend', 'amount': int(raw_input('how much to send (in satoshis)? ' )), 'to': raw_input('who to send to? ' )}, DB)
def votecoin_spend(DB):
    amount = int(raw_input('how much to send (in satoshis)? ' ))
    vote_id=raw_input('unique id for that branch? ' )
    to = raw_input('who to send to? ' )
    tx = {'type': 'spend', 'amount': amount, 'to': to, 'vote_id':vote_id}
    easy_add_transaction(tx, DB)

def ask_decision(DB):
    vote_id=raw_input('unique id for that branch? ' )
    decision_id=raw_input('unique id for that decision? ')
    txt=raw_input('txt of decision? ')
    tx={'type':'propose_decision', 'vote_id':vote_id, 'decision_id':decision_id, 'txt':txt}
    return easy_add_transaction(tx, DB)

def vote_on_decision(DB):
    vote_id=raw_input('unique id for that branch? ')
    decision_id=raw_input('unique id for that decision? ')
    acc=blockchain.db_get(custom.address, DB)
    answer=raw_input('answer "yes" or "no": ')
    value=[answer, str(random.random())+str(random.random())]
    answer_hash=tools.det_hash(value)
    DB['memoized_votes'][answer_hash]=value
    old_vote='unsure'
    if decision_id in acc['votes']: #this is always False...
        old_vote=acc['votes'][decision_id]
    tx={'type':'jury_vote', 'vote_id':vote_id, 'decision_id':decision_id, 'old_vote':old_vote, 'new_vote':answer_hash}
    return easy_add_transaction(tx, DB)

def reveal_vote(DB):
    vote_id=raw_input('unique id for that branch? ')
    decision_id=raw_input('unique id for that decision? ')
    acc=blockchain.db_get(custom.address, DB)
    decision_id=raw_input('unique id for that decision? ')
    if decision_id in acc['votes']:
        answer_hash=acc['votes'][decision_id]
        a=DB['memoized_votes'][answer_hash]
        tx={'type':'reveal_jury_vote', 'vote_id':vote_id, 'decision_id':decision_id, 'old_vote':answer_hash, 'new_vote':a[0], 'secret':a[1]}
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
    vote_id=raw_input('unique id for that branch? ')
    jury=blockchain.db_get(vote_id, DB)
    tx={'type':'SVD_consensus', 'vote_id':vote_id, 'decisions':decisions_keepers(jury, DB)}
    return(easy_add_transaction(tx, DB))

def make_PM(DB):
    tx={'type':'prediction_market', 'PM_id':'weather', 'fees':0, 'B':10, 'states':['0 0 0', '1 0 0', '1 1 0', 'default'], 'states_combinatory':[[0,0,0],[1,0,0],[1,1,0]], 'shares_purchased':[0,0,0,0],'decisions':["unique title for decision","unique title for decision2","unique title for decision3"], 'owner':custom.address}
    #print('pm in make: ' +str(tx))
    return easy_add_transaction(tx, DB)

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
    blockchain.add_tx(tx, DB)
    return('CREATED TX: ' + str(tx))


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
def balance(DB): 
    return(str(my_balance(DB, raw_input('address'))))
Do={'SVD_consensus':SVD_consensus, 'reveal_vote':reveal_vote, 'vote_on_decision':vote_on_decision, 'ask_decision':ask_decision, 'create_jury':create_jury, 'spend':spend, 'votecoin_spend':votecoin_spend, 'make_PM':make_PM, 'buy_shares':buy_shares, 'collect_winnings':collect_winnings, 'h':help_, 'help':help_, '?':help_, 'blockcount':blockcount, 'txs':txs, 'balance':balance, 'my_balance':my_balance, 'b':my_balance, 'difficulty':difficulty, 'info':info, 'me':me, 'wait_till_block':wait_till_block, '':(lambda DB: 42), 'DB':DB_print}
def Do_func(DB): return Do.get(DB['command'], lambda DB: str(DB['command']) + ' is not a command. use "?" for a list of commands')(DB)
def main(DB, script):
    command_prompt_advanced.run_script(DB, script)
    while True:
        DB['command']=raw_input('>>> ')
        #if command in Do: Do[command](DB)
        out=Do_func(DB)
        print(out)
        #else: print(str(command) + ' is not a command. use "?" for a list of commands')

