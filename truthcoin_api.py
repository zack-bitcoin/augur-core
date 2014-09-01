"""This is the internal API for truthshell. These are the words that are used to interact with truthcoin.
"""
import copy, tools, blockchain, custom, random, transactions, sys, txs_tools, time, networking
def easy_add_transaction(tx_orig, DB):
    tx = copy.deepcopy(tx_orig)
    if 'pubkeys' not in tx:
        tx['pubkeys']=[DB['pubkey']]
    try:
        tx['count'] = tools.count(DB['address'], DB)
    except:
        tx['count'] = 1
    tx['signatures'] = [tools.sign(tools.det_hash(tx), DB['privkey'])]
    return(blockchain.add_tx(tx, DB))
def help_(DB):      
    tell_about_command={
        'help':'type "./truthd.py help <cmd>" to learn about <cmd>. type "./truthd.py commands" to get a list of all truthshell commands',
        'commands':'returns a list of the truthshell commands',
        'create_jury':'If you want to create a jury called "bitcoin", then type: ./truthd.py create_jury bitcoin.',
        'DB_print':'prints the database that is shared between threads',
        'info':'prints the contents of an entree in the hashtable. If you want to know what the first block was: info 0, if you want to know about a particular address <addr>: info <addr>, if you want to know about yourself: info my_address',
        'my_address':'tells you your own address',
        'spend':'spends money, in satoshis, to an address <addr>. Example: spend 1000 11j9csj9802hc982c2h09ds',
        'votecoin_spend':'spend votecoins from jury <jury>, to address <addr>. Example: votecoin_spend 1000 <jury> <addr>',
        'ask_decision': 'If you wanted to ask the jury <jury>, the question "what will the weather be tomorrow", with the unique identifier "weather_question_203", you would type: ./truthd.py ask_decision weather_question_203 what will the weather be tomorrow',
        'vote_on_decision':'If you want to vote in jury <jury>, and you want to vote on decision <decision>, and you want to vote "yes", for example: vote_on_decision <jury> <decision> yes',
        'reveal_vote':'If you want to reveal your vote for the decision with the unique identifier <decision> which was asked ofjury <jury>, then: reveal_vote <jury> <decision>',
        'SVD_consensus':'If you want to resolve decisions asked of jury <jury>, then: SVD_consensus <jury>',
        'make_PM':'The inputs for make_PM are very complicated. For now, you have to: (1) use "./truthd.py stop" to kill the program. (2) edit the function "make_PM" in the file "truthcoin_api.py".(3) restart the program with "python threads.py"',
        'buy_shares':'The inputs for buy_shares are very complicated. For now, you have to: (1) use "./truthd.py stop" to kill the program. (2) edit the function "make_PM" in the file "truthcoin_api.py".(3) restart the program with "python threads.py"',
        'collect_winnings':'To transform your winning shares from prediction market <PM> into truthcoin: collect_winnings <PM>',
        'blockcount':'returns the number of blocks since the genesis block',
        'txs':'returns a list of the zeroth confirmation transactions that are expected to be included in the next block',
        'difficulty':'returns current difficulty',
        'my_balance':'the amount of truthcoin that you own',
        #'wait_till_block':'to stop the truthshell until block 100 has passed, type: "./truthd.py wait_till_block 100". Any additional words that you type are saved until block 100, and they are executed at that time.',
        'balance':'if you want to know the balance for address <addr>, type: ./truthd.py balance <addr>',
        'log':'records the following words into the file "log.py"',
        'stop':'This is the correct way to stop truthcoin. If you turn off in any other way, then you are likely to corrupt your database, and you have to redownload all the blocks again.',
        'mine':'turn the miner on/off. Example to turn on: "./truthd.py mine on", example to turn off: "./truthd.py mine off"',
        'DB':'returns a database of information that is shared between threads'
    }
    if len(DB['args'])==0:
        return("needs 2 words. example: 'help help'")
    try:
        return tell_about_command[DB['args'][0]]    
    except:
        return(str(DB['args'][0])+' is not yet documented')
def create_jury(DB): 
    if len(DB['args'])<1:
        return('not enough inputs')
    return easy_add_transaction({'type': 'create_jury', 'vote_id': DB['args'][0]}, DB)
def DB_print(DB):
    return(str(DB))
def info(DB): 
    if len(DB['args'])<1:
        return ('not enough inputs')
    if DB['args'][0]=='my_address':
        address=DB['address']
    else:
        address=DB['args'][0]
    return(str(tools.db_get(address, DB)))   
def my_address(DB):
    return(str(DB['address']))
def spend(DB): 
    if len(DB['args'])<2:
        return('not enough inputs')
    easy_add_transaction({'type': 'spend', 'amount': int(DB['args'][0]), 'to':DB['args'][1]}, DB)
def votecoin_spend(DB):
    tx = {'type': 'spend', 'amount':int(DB['args'][0]), 'to': DB['args'][2], 'vote_id':DB['args'][1]}
    return easy_add_transaction(tx, DB)
def accumulate_words(l, out=''):
    if len(l)>0: return accumulate_words(l[1:], out+' '+l[0])
    return out
def ask_decision(DB):
    if len(DB['args'])<3:
        return('not enough inputs')
    tx={'type':'propose_decision', 'vote_id':DB['args'][0], 'decision_id':DB['args'][1], 'txt':accumulate_words(DB['args'][2:])[1:]}
    return easy_add_transaction(tx, DB)
def vote_on_decision(DB):
    if len(DB['args'])<3:
        return('not enough inputs')
    decision_id=DB['args'][1]
    answer=DB['args'][2]
    acc=tools.db_get(DB['address'], DB)
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
        return('not enough inputs')
    acc=tools.db_get(DB['address'], DB)
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
    jury=tools.db_get(vote_id, DB)
    tx={'type':'SVD_consensus', 'vote_id':vote_id, 'decisions':decisions_keepers(jury, DB)}
    return(easy_add_transaction(tx, DB))
def make_PM(DB):
    #contains an example prediction market. which is compatible with the example buy_shares on this same page.
    #to make_PM other than the example, you need to edit the following line of code, and restart truthcoin.
    tx={'type':'prediction_market', 'PM_id':'weather', 'fees':0, 'B':10, 'states':['0 0 0', '1 0 0', '1 1 0', 'default'], 'states_combinatory':[[0,0,0],[1,0,0],[1,1,0]], 'shares_purchased':[0,0,0,0],'decisions':["decision_1","decision_2","decision_3"], 'owner':DB['address']}
    return(easy_add_transaction(tx, DB))
def buy_shares(DB):
    #to buy shares other than the example, you need to edit the following line of code, and restart truthcoin.
    tx={'type':'buy_shares', 'buy':[5,4,3,0], 'PM_id':'weather'}
    return(easy_add_transaction(tx, DB))
def collect_winnings(DB):
    add=DB['address']
    acc=tools.db_get(add, DB)
    tx={'type':'collect_winnings', 'PM_id':DB['args'][1], 'shares':acc['shares'][tx['PM_id']], 'address':add}
    return easy_add_transaction(tx, DB)
def blockcount(DB): return(str(DB['length']))
def txs(DB):        return(str(DB['txs']))
def difficulty(DB): return(str(blockchain.target(DB)))
def my_balance(DB, address='default'): 
    if address=='default':
        address=DB['address']
    return(str(tools.db_get(address, DB)['amount']-txs_tools.cost_0(DB['txs'], DB)['truthcoin_cost']))
def balance(DB): 
    if len(DB['args'])<1:
        return('what address do you want the balance for?')
    return(str(my_balance(DB, DB['args'][0])))
def log(DB): tools.log(accumulate_words(DB['args'])[1:])
def stop_(DB): 
    DB['stop']=True
    return('turning off all threads')
def commands(DB): return str(Do.keys())
def mine(DB):
    if len(DB['args'])>0 and DB['args'][0]=='off': 
        DB['mine']=False
        return('miner is now turned off')
    else: 
        DB['mine']=True
        return ('miner on. (use "./truthd.py mine off" to turn off)')
Do={'SVD_consensus':SVD_consensus, 'reveal_vote':reveal_vote, 'vote_on_decision':vote_on_decision, 'ask_decision':ask_decision, 'create_jury':create_jury, 'spend':spend, 'votecoin_spend':votecoin_spend, 'make_PM':make_PM, 'buy_shares':buy_shares, 'collect_winnings':collect_winnings, 'help':help_, 'blockcount':blockcount, 'txs':txs, 'balance':balance, 'my_balance':my_balance, 'b':my_balance, 'difficulty':difficulty, 'info':info, '':(lambda DB: ' '), 'DB':DB_print, 'my_address':my_address, 'log':log, 'stop':stop_, 'commands':commands, 'mine':mine}
def main(DB, heart_queue):
    def responder(dic):
        command=dic['command']
        if command[0] in Do: 
            DB['args']=command[1:]
            out=Do[command[0]](DB)
        else: 
            out=str(command[0]) + ' is not a command. use "./truthd.py commands" to get the list of truthshell commands. use "./truthd.py help help" to learn about the help tool.'
        return out
    try:
        return networking.serve_forever(custom.truthd_port, responder, heart_queue, DB)
    except:
        print('api error: ' +str(sys.exc_info()))
