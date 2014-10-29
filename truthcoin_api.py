"""This is the internal API for truthshell. These are the words that are used to interact with truthcoin.
"""
import copy, tools, blockchain, custom, random, transactions, sys, txs_tools, time, networking, txs_truthcoin, target
def easy_add_transaction(tx_orig, DB, privkey='default'):
    tx = copy.deepcopy(tx_orig)
    if privkey in ['default', 'Default']:
        if tools.db_existence('privkey'):
            privkey=tools.db_get('privkey')
        else:
            return('no private key is known, so the tx cannot be signed. Here is the tx: \n'+str(tools.package(tx_orig).encode('base64').replace('\n', '')))
    pubkey=tools.privtopub(privkey)
    address=tools.make_address([pubkey], 1)
    if 'count' not in tx:
        try:
            tx['count'] = tools.count(address, {})
        except:
            tx['count'] = 1
    if 'pubkeys' not in tx:
        tx['pubkeys']=[pubkey]
    if 'signatures' not in tx:
        tx['signatures'] = [tools.sign(tools.det_hash(tx), privkey)]
    return(blockchain.add_tx(tx, DB))
def help_(DB, args):      
    tell_about_command={
        'help':'type "./truth_cli.py help <cmd>" to learn about <cmd>. type "./truth_cli.py commands" to get a list of all truthshell commands',
        'commands':'returns a list of the truthshell commands',
        'start':'type "./truth_cli.py start" to start truthcoin node',
        'new_address':'type "./truth_cli.py new_address <brain>" to make a new privkey, pubkey, and address using the brain wallet=<brain>. If you want to use this address, you need to copy/paste the pubkey into the file custom.py',
        'create_jury':'If you want to create a jury called "bitcoin", then type: ./truth_cli.py create_jury bitcoin.',
        'DB_print':'prints the database that is shared between threads',
        'info':'prints the contents of an entree in the hashtable. If you want to know what the first block was: info 0, if you want to know about a particular address <addr>: info <addr>, if you want to know about yourself: info my_address',
        'my_address':'tells you your own address',
        'spend':'spends money, in satoshis, to an address <addr>. Example: spend 1000 11j9csj9802hc982c2h09ds',
        'votecoin_spend':'spend votecoins from jury <jury>, to address <addr>. Example: votecoin_spend 1000 <jury> <addr>',
        'ask_decision': 'If you wanted to ask the jury <jury>, the question "what will the weather be tomorrow", with the unique identifier "weather_question_203", you would type: ./truth_cli.py ask_decision <jury> weather_question_203 what will the weather be tomorrow',
        'vote_on_decision':'If you want to vote in jury <jury>, and you want to vote on decision <decision>, and you want to vote "yes", for example: vote_on_decision <jury> <decision> yes',
        'reveal_vote':'If you want to reveal your vote for the decision with the unique identifier <decision> which was asked ofjury <jury>, then: reveal_vote <jury> <decision>',
        'SVD_consensus':'If you want to resolve decisions asked of jury <jury>, then: SVD_consensus <jury>',
        'make_PM':'example: ./truth_cli.py make_PM',
        'buy_shares':'example: ./truth_cli.py buy_shares"',
        'collect_winnings':'To transform your winning shares from prediction market <PM> into truthcoin: collect_winnings <PM>',
        'blockcount':'returns the number of blocks since the genesis block',
        'txs':'returns a list of the zeroth confirmation transactions that are expected to be included in the next block',
        'difficulty':'returns current difficulty',
        'my_balance':'the amount of truthcoin that you own',
        'balance':'if you want to know the balance for address <addr>, type: ./truth_cli.py balance <addr>',
        'log':'records the following words into the file "log.py"',
        'stop':'This is the correct way to stop truthcoin. If you turn off in any other way, then you are likely to corrupt your database, and you have to redownload all the blocks again.',
        'mine':'turn the miner on/off. Example to turn on: "./truth_cli.py mine on", example to turn off: "./truth_cli.py mine off"',
        'DB':'returns a database of information that is shared between threads',
        'pushtx':'publishes this transaction to the blockchain, will automatically sign the transaction if necessary: ./truth_cli.py pushtx tx privkey',
        'peers':'tells you your list of peers'
    }
    if len(args)==0:
        return("needs 2 words. example: 'help help'")
    try:
        return tell_about_command[args[0]]    
    except:
        return(str(args[0])+' is not yet documented')
def create_jury(DB, args): 
    if len(args)<1:
        return('not enough inputs')
    return easy_add_transaction({'type': 'create_jury', 'vote_id': args[0]}, DB)
def peers(DB, args):
    return(tools.db_get('peers_ranked'))
def DB_print(DB, args):
    return(DB)
def info(DB, args): 
    if len(args)<1:
        return ('not enough inputs')
    if args[0]=='my_address':
        address=tools.db_get('address')
    else:
        address=args[0]
    return(tools.db_get(address, DB))
def my_address(DB, args):
    return(tools.db_get('address'))
def spend(DB, args): 
    if len(args)<2:
        return('not enough inputs')
    return easy_add_transaction({'type': 'spend', 'amount': int(args[0]), 'to':args[1]}, DB)
def votecoin_spend(DB, args):
    if len(args)<3:
        return('not enough inputs')
    tx = {'type': 'spend', 'amount':int(args[0]), 'to': args[2], 'vote_id':args[1]}
    return easy_add_transaction(tx, DB)
def accumulate_words(l, out=''):
    if len(l)>0: return accumulate_words(l[1:], out+' '+l[0])
    return out
def ask_decision(DB, args):
    if len(args)<3:
        return('not enough inputs')
    #print('DB args: ' +str(args))
    tx={'type':'propose_decision', 'vote_id':args[0], 'decision_id':args[1], 'txt':accumulate_words(args[1:])[1:]}
    return easy_add_transaction(tx, DB)
def vote_on_decision(DB, args):
    if len(args)<3:
        return('not enough inputs')
    decision_id=args[1]
    answer=args[2]
    acc=tools.db_get(tools.db_get('address'), DB)
    value=[answer, str(random.random())+str(random.random())]
    answer_hash=tools.det_hash(value)
    m=tools.db_get('memoized_votes')
    m[answer_hash]=value
    tools.db_put('memoized_votes', m)
    #DB['memoized_votes'][answer_hash]=value
    old_vote='unsure'
    if decision_id in acc['votes']: #this is always False...
        old_vote=acc['votes'][decision_id]
    tx={'type':'jury_vote', 'vote_id':args[0], 'decision_id':decision_id, 'old_vote':old_vote, 'new_vote':answer_hash}
    return easy_add_transaction(tx, DB)
def reveal_vote(DB, args):
    if len(args)<2:
        return('not enough inputs')
    acc=tools.db_get(tools.db_get('address'), DB)
    decision_id=args[1]
    if decision_id in acc['votes']:
        answer_hash=acc['votes'][decision_id]
        m=tools.db_get('memoized_votes')
        if answer_hash not in m:
            return('reveal vote error')
        a=m[answer_hash]
        tx={'type':'reveal_jury_vote', 'vote_id':args[0], 'decision_id':decision_id, 'old_vote':answer_hash, 'new_vote':a[0], 'secret':a[1]}
        return easy_add_transaction(tx, DB)
    else:
        return('you do not have any encrypted vote to decrypt')
def SVD_consensus(DB, args):
    if len(args)<1:
        return('unique id for that branch?')
    vote_id=args[0]
    jury=tools.db_get(vote_id, DB)
    k=txs_tools.decisions_keepers(vote_id, jury, DB)
    if k=='error':
        return('that jury does not exist yet')
    tx={'type':'SVD_consensus', 'vote_id':vote_id, 'decisions':k}
    return(easy_add_transaction(tx, DB))
def pushtx(DB, args):
    tx=tools.unpackage(args[0].decode('base64'))
    if len(args)==1:
        return easy_add_transaction(tx, DB)
    privkey=tools.det_hash(args[1])
    return easy_add_transaction(tx, DB, privkey)
def collect_winnings(DB, args):
    if len(args)<1:
        return ('not enough arguments')
    tools.log('collect_winnings 1')
    add=tools.db_get('address')
    acc=tools.db_get(add, DB)
    tx={'type':'collect_winnings', 'PM_id':args[0], 'address':add}
    tx['shares']=acc['shares'][tx['PM_id']]
    tools.log('collect_winnings 2')
    return easy_add_transaction(tx, DB)
def blockcount(DB, args): return(tools.db_get('length'))
def txs(DB, args):        return(tools.db_get('txs'))
def difficulty(DB, args): return(target.target(DB))
def my_balance(DB, args, address='default'): 
    if address=='default':
        address=tools.db_get('address')
    return(tools.db_get(address, DB)['amount']-txs_tools.cost_0(tools.db_get('txs'), address)['truthcoin_cost'])
def balance(DB, args): 
    if len(args)<1:
        return('what address do you want the balance for?')
    return(my_balance(DB, args, args[0]))
def log(DB, args): tools.log(accumulate_words(args)[1:])
def stop_(DB, args): 
    tools.db_put('stop', True)
    return('turning off all threads')
def commands(DB, args): return sorted(Do.keys()+['start', 'new_address', 'make_PM', 'buy_shares'])
def mine(DB, args):
    if len(args)>0:
        if args[0]=='off': 
            tools.db_put('mine', False)
            return('miner is now turned off')
        elif args[0]=='on':
            if tools.db_existence('privkey'):
                tools.db_put('mine', True)
                return ('miner on. (use "./truth_cli.py mine off" to turn off)')
            else:
                return('there is no private key with which to sign blocks. If you want to mine, you need to uncomment the "brain_wallet" line in custom.py')
    else:
        m=tools.db_get('mine')
        if m: 
            m='on'
        else: 
            m='off'
        return('miner is currently: ' +m)
def pass_(DB, args): return ' '
def error_(DB, args): return error
Do={'SVD_consensus':SVD_consensus, 'reveal_vote':reveal_vote, 'vote_on_decision':vote_on_decision, 'ask_decision':ask_decision, 'create_jury':create_jury, 'spend':spend, 'votecoin_spend':votecoin_spend, 'collect_winnings':collect_winnings, 'help':help_, 'blockcount':blockcount, 'txs':txs, 'balance':balance, 'my_balance':my_balance, 'b':my_balance, 'difficulty':difficulty, 'info':info, '':pass_, 'DB':DB_print, 'my_address':my_address, 'log':log, 'stop':stop_, 'commands':commands, 'pushtx':pushtx, 'mine':mine, 'peers':peers}
def main(DB, heart_queue):
    def responder(dic):
        command=dic['command']
        if command[0] in Do: 
            args=command[1:]
            try:
                out=Do[command[0]](DB, args)
            except Exception as exc:
                tools.log(exc)
                out='truthcoin api main failure : ' +str(sys.exc_info())
        else: 
            out=str(command[0]) + ' is not a command. use "./truth_cli.py commands" to get the list of truthshell commands. use "./truth_cli.py help help" to learn about the help tool.'
        return out
    try:
        return networking.serve_forever(responder, custom.api_port, heart_queue)
    except exc as Exception:
        tools.log('api error')
        tools.log(exc)
