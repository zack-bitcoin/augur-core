"""This is the internal API for truthshell. These are the words that are used to interact with truthcoin.
"""
import copy, tools, blockchain, custom, random, transactions, sys, txs_tools, time, networking, txs_truthcoin
def easy_add_transaction(tx_orig, DB, privkey='default'):
    tx = copy.deepcopy(tx_orig)
    try:
        tx['count'] = tools.count(DB['address'], DB)
    except:
        tx['count'] = 1
    if privkey=='default':
        if 'privkey' in DB:
            privkey=DB['privkey']
        else:
            return('no private key is known, so the tx cannot be signed. Here is the tx: \n'+str(tools.package(tx_orig).encode('base64').replace('\n', '')))
    if 'pubkeys' not in tx:
        tx['pubkeys']=[tools.privtopub(privkey)]
    tx['signatures'] = [tools.sign(tools.det_hash(tx), privkey)]
    tools.log('collect winnings 3')
    return(blockchain.add_tx(tx, DB))
def help_(DB):      
    tell_about_command={
        'help':'type "./truthd.py help <cmd>" to learn about <cmd>. type "./truthd.py commands" to get a list of all truthshell commands',
        'commands':'returns a list of the truthshell commands',
        'new_address':'type "./truthd.py new_address <brain>" to make a new privkey, pubkey, and address using the brain wallet=<brain>. If you want to use this address, you need to copy/paste the pubkey into the file custom.py',
        'create_jury':'If you want to create a jury called "bitcoin", then type: ./truthd.py create_jury bitcoin.',
        'DB_print':'prints the database that is shared between threads',
        'info':'prints the contents of an entree in the hashtable. If you want to know what the first block was: info 0, if you want to know about a particular address <addr>: info <addr>, if you want to know about yourself: info my_address',
        'my_address':'tells you your own address',
        'spend':'spends money, in satoshis, to an address <addr>. Example: spend 1000 11j9csj9802hc982c2h09ds',
        'votecoin_spend':'spend votecoins from jury <jury>, to address <addr>. Example: votecoin_spend 1000 <jury> <addr>',
        'ask_decision': 'If you wanted to ask the jury <jury>, the question "what will the weather be tomorrow", with the unique identifier "weather_question_203", you would type: ./truthd.py ask_decision <jury> weather_question_203 what will the weather be tomorrow',
        'vote_on_decision':'If you want to vote in jury <jury>, and you want to vote on decision <decision>, and you want to vote "yes", for example: vote_on_decision <jury> <decision> yes',
        'reveal_vote':'If you want to reveal your vote for the decision with the unique identifier <decision> which was asked ofjury <jury>, then: reveal_vote <jury> <decision>',
        'SVD_consensus':'If you want to resolve decisions asked of jury <jury>, then: SVD_consensus <jury>',
        'make_PM':'example: ./truthd.py make_PM',
        'buy_shares':'example: ./truthd.py buy_shares"',
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
        'DB':'returns a database of information that is shared between threads',
        'pushtx':'publishes this transaction to the blockchain, will automatically sign the transaction if necessary: ./truthd.py pushtx tx privkey'
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
    return easy_add_transaction({'type': 'spend', 'amount': int(DB['args'][0]), 'to':DB['args'][1]}, DB)
def votecoin_spend(DB):
    if len(DB['args'])<3:
        return('not enough inputs')
    tx = {'type': 'spend', 'amount':int(DB['args'][0]), 'to': DB['args'][2], 'vote_id':DB['args'][1]}
    return easy_add_transaction(tx, DB)
def accumulate_words(l, out=''):
    if len(l)>0: return accumulate_words(l[1:], out+' '+l[0])
    return out
def ask_decision(DB):
    if len(DB['args'])<3:
        return('not enough inputs')
    #print('DB args: ' +str(DB['args']))
    tx={'type':'propose_decision', 'vote_id':DB['args'][0], 'decision_id':DB['args'][1], 'txt':accumulate_words(DB['args'][1:])[1:]}
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
def SVD_consensus(DB):
    if len(DB['args'])<1:
        return('unique id for that branch?')
    vote_id=DB['args'][0]
    jury=tools.db_get(vote_id, DB)
    k=txs_tools.decisions_keepers(vote_id, jury, DB)
    if k=='error':
        return('that jury does not exist yet')
    tx={'type':'SVD_consensus', 'vote_id':vote_id, 'decisions':k}
    return(easy_add_transaction(tx, DB))
def pushtx(DB):
    tx=tools.unpackage(DB['args'][0].decode('base64'))
    if len(DB['args'])==1:
        return easy_add_transaction(tx, DB)
    privkey=tools.det_hash(DB['args'][1])
    return easy_add_transaction(tx, DB, privkey)
def collect_winnings(DB):
    if len(DB['args'])<1:
        return ('not enough arguments')
    tools.log('collect_winnings 1')
    add=DB['address']
    acc=tools.db_get(add, DB)
    tx={'type':'collect_winnings', 'PM_id':DB['args'][0], 'address':add}
    tx['shares']=acc['shares'][tx['PM_id']]
    tools.log('collect_winnings 2')
    return easy_add_transaction(tx, DB)
def blockcount(DB): return(str(DB['length']))
def txs(DB):        return(str(DB['txs']))
def difficulty(DB): return(str(target.target(DB)))
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
    elif 'privkey' in DB: 
        DB['mine']=True
        return ('miner on. (use "./truthd.py mine off" to turn off)')
    else:
        return('there is no private key with which to sign blocks. If you want to mine, you need to uncomment the "brain_wallet" line in custom.py')
def pass_(DB): return ' '
def error_(DB): return error
Do={'SVD_consensus':SVD_consensus, 'reveal_vote':reveal_vote, 'vote_on_decision':vote_on_decision, 'ask_decision':ask_decision, 'create_jury':create_jury, 'spend':spend, 'votecoin_spend':votecoin_spend, 'make_PM':error_, 'buy_shares':error_, 'collect_winnings':collect_winnings, 'help':help_, 'blockcount':blockcount, 'txs':txs, 'balance':balance, 'my_balance':my_balance, 'b':my_balance, 'difficulty':difficulty, 'info':info, '':pass_, 'DB':DB_print, 'my_address':my_address, 'log':log, 'stop':stop_, 'commands':commands, 'pushtx':pushtx, 'mine':mine}
def main(DB, heart_queue):
    def responder(dic):
        command=dic['command']
        if command[0] in Do: 
            DB['args']=command[1:]
            try:
                out=Do[command[0]](DB)
            except:
                out='truthcoin api main failure : ' +str(sys.exc_info())
        else: 
            out=str(command[0]) + ' is not a command. use "./truthd.py commands" to get the list of truthshell commands. use "./truthd.py help help" to learn about the help tool.'
        return out
    try:
        return networking.serve_forever(custom.truthd_port, responder, heart_queue, DB)
    except:
        print('api error: ' +str(sys.exc_info()))
