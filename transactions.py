"""This file explains how we tell if a transaction is valid or not, it explains
how we update the system when new transactions are added to the blockchain."""
import pprint
import blockchain
import custom
import copy
import tools
import ConsensusMechanism
import math

def addr(tx):
    return tools.make_address(tx['pubkeys'], len(tx['signatures']))

E_check=tools.E_check

def cost_0(txs, DB):
    #cost of the zeroth confirmation transactions
    total_cost = []
    votecoin_cost = {}
    for Tx in filter(lambda t: custom.address == addr(t), txs):
        def spend_():
            global total_cost
            global votecoin_cost
            total_cost.append(custom.fee)
            if 'vote_id' not in tx:
                total_cost += Tx['amount']
            else:
                if Tx['vote_id'] not in votecoin_cost: 
                    votecoin_cost[Tx['vote_id']]=0
                votecoin_cost[Tx['vote_id']]+=Tx['amount']
        def buy_shares_():
            global total_cost
            cost = cost_to_buy_shares(Tx, DB)
            total_cost.append(custom.buy_shares_fee)
            total_cost.append(cost)
            total_cost.append(int(abs(cost*0.01))))
            
        Do={'spend':spend_,
            'mint':(lambda: total_cost.append(-custom.block_reward)), 
            'create_jury':(lambda: total_cost.append(custom.create_jury_fee)), 
            'propose_decision':(lambda: total_cost.append(custom.propose_decision_fee)), 
            'jury_vote':(lambda: total_cost.append(custom.jury_vote_fee)),
            'reveal_jury_vote':(lambda: total_cost.append(custom.reveal_jury_vote_fee)),
            'SVD_consensus':(lambda: total_cost.append(custom.SVD_consensus_fee)),
            'collect_winnings':(lambda: total_cost.append(-custom.collect_winnings_reward)),
            'buy_shares':buy_shares_,
            'prediction_market':(lambda: total_cost.append(Tx['B']*math.log(len(Tx['states']))))}
        Do[Tx['type']]()
        '''
        if Tx['type'] == 'mint':
            total_cost -= custom.block_reward
        if Tx['type'] == 'create_jury':
            total_cost += custom.create_jury_fee
        if Tx['type'] == 'propose_decision':
            total_cost += custom.propose_decision_fee
        if Tx['type'] == 'buy_shares':
            cost = cost_to_buy_shares(Tx, DB)
            total_cost += cost
            total_cost += int(abs(cost*0.01))
        if Tx['type'] == 'prediction_market':
            total_cost += Tx['B']*math.log(len(Tx['states']))
        '''
    return {'truthcoin_cost':sum(total_cost), 'votecoin_cost':votecoin_cost}
    

def fee_check(tx, txs, DB):
    address = addr(tx)
    cost_=cost_0(txs, DB)
    truthcoin_cost = cost_['truthcoin_cost']
    votecoin_cost = cost_['votecoin_cost']
    acc=blockchain.db_get(address, DB)
    if int(acc['amount']) < truthcoin_cost: 
        print('insufficient truthcoin')
        return False
    for v_id in votecoin_cost:
        if v_id not in acc['votecoin']: 
            print('0 votecoin: ' +str(v_id))
            return False
        if acc['votecoin'][v_id]<votecoin_cost[v_id]: 
            print(acc['votecoin'][v_id])
            print(votecoin_cost[v_id])
            print('not enough votecoin: ' +str(v_id))
            return False
    return True


def spend_verify(tx, txs, DB):

    def sigs_match(sigs, pubs, msg):
        return all(tools.verify(msg, sig, pub) for sig in sigs for pub in pubs)

    tx_copy = copy.deepcopy(tx)
    tx_copy_2 = copy.deepcopy(tx)
    if not E_check(tx, 'to', [str, unicode]):
        print('no to')
        return False
    if len(tx['to'])<=30:
        #this system supports a maximum of 10^30 blocks.
        print('that address is too short')
        return False
    if not E_check(tx, 'signatures', list):
        print('no signautres')
        return False
    if not E_check(tx, 'pubkeys', list):
        print('no pubkeys')
        return False
    if not E_check(tx, 'amount', int):
        print('no amount')
        return False
    tx_copy.pop('signatures')
    if len(tx['pubkeys']) == 0:
        print('pubkey error')
        return False
    if len(tx['signatures']) > len(tx['pubkeys']):
        print('sigs too long')
        return False
    msg = tools.det_hash(tx_copy)
    if not sigs_match(copy.deepcopy(tx['signatures']),
                      copy.deepcopy(tx['pubkeys']), msg):
        print('sigs do not match')
        return False
    if not fee_check(tx, txs, DB):
        print('fee check error')
        return False
    return True


def mint_verify(tx, txs, DB):
    return 0 == len(filter(lambda t: t['type'] == 'mint', txs))
def total_coins(jury):
    votecoins=0
    for member in tx['jury']:
        votecoins+=member['amount']
    return votecoins

def create_jury_check(tx, txs, DB):
    address=addr(tx)
    if not E_check(tx, 'vote_id', [str, unicode]): 
        print('vote id error')
        return False
    if len(tx['vote_id'])>1000: return False
    if blockchain.db_existence(tx['vote_id'], DB): 
        print('this vote_id is already being used')
        return False
    if not blockchain.db_existence(address, DB): 
        print('this address is not used by anyone')
        return False
    acc=blockchain.db_get(address, DB)
    #if acc['amount']<=custom.create: return False
    #votecoins=total_coins(tx['jury'])
    #if votecoins>1000000: return False
    for t in txs:
        if 'jury_id' in t:
            if t['jury_id']==tx['jury_id']:
                return False
    if not fee_check(tx, txs, DB): return False
    return True
def propose_decision_check(tx, txs, DB):
    if not E_check(tx, 'vote_id', [str, unicode]): return False
    if not E_check(tx, 'decision_id', [str, unicode]): return False
    if len(tx['decision_id'])>6**4: return False
    if not blockchain.db_existence(tx['vote_id'], DB): return False
    if blockchain.db_existence(tx['decision_id'], DB): return False
    for t in txs:
        if 'decision_id' in t:
            if t['decision_id']==tx['decision_id']:
                return False
    if not fee_check(tx, txs, DB): return False
    if not E_check(tx, 'txt', [str, unicode]): return False
    if len(tx['txt'])>6**5: return False
    return True
'''
def decision_vote_common(tx, txs, fee, decisions, prop_acce, yes, no, DB):
    if not E_check(tx, 'accept?', bool): return False
    if not E_check(tx, 'jury_id', [str, unicode]): return False
    if not E_check(tx, 'decision_id', [str, unicode]): return False
    if not blockchain.db_existence(tx['jury_id'], DB): return False
    if not blockchain.db_existence(tx['decision_id'], DB): return False
    if fee>0:
        if not fee_check(tx, txs, fee, DB): return False
    jury=blockchain.db_get(tx['jury_id'], DB)
    if not E_check(jury, decisions, dict): return False
    if not E_check(jury[decisions], tx['decision_id'], dict): return False
    decision=blockchain.db_get(tx['decision_id'], DB)
    if not E_check(decision, 'state', prop_acce): return False
    address=tools.addr(tx)
    if address in decision[yes]+decision[no]: return False
    return True
'''
'''
def accept_decision_check(tx, txs, DB):
    if not decision_vote_common(tx, txs, custom.accept_decision_fee, 'potential_decisions', 'proposed', 'accept_list', 'deny_list', DB): return False
    return True
'''
def jury_vote_check(tx, txs, DB):
    if not E_check(tx, 'decision_id', [str, unicode]): return False
    if not E_check(tx, 'vote_id', [str, unicode]): return False
    if not E_check(tx, 'old_vote', [str, unicode]): return False
    if not E_check(tx, 'new_vote', [str, unicode]): return False
    decision=blockchain.db_get(tx['decision_id'])
    if decision['state']!='proposed':
        print('this decision has already been decided')
        return False
    if not blockchain.db_existence(tx['decision_id'], DB): 
        print('decision error')
        return False
    if tools.reveal_time_p(DB): 
        print('reveal time check')
        return False
    if len(tx['new_vote'])<4: 
        print('secret too short error')
        return False
    #make sure we own the right kind of votecoins
    #make sure we can afford the fee.
    return True
def reveal_jury_vote_check(tx, txs, DB):
    print('reveal jury vote check')
    address=tools.make_address([custom.pubkey], 1)#this might be wrong
    acc=blockchain.db_get(address, DB)
    if not E_check(tx, 'decision_id', [str, unicode]): 
        print('decision id error')
        return False
    decision=blockchain.db_get(tx['decision_id'])
    if decision['state']!='proposed':
        print('this decision has already been decided')
        return False
    if not E_check(tx, 'old_vote', [str, unicode]): return False
    if not E_check(tx, 'secret', [str, unicode]): return False
    if not E_check(tx, 'new_vote', [str, unicode]): 
        print('new vote error')
        return False
    if tx['decision_id'] not in acc['votes']:
        print('decision id not in acc[votes] error')
        return False
    answer_hash=acc['votes'][tx['decision_id']]
    if not answer_hash==tools.det_hash([tx['new_vote'], tx['secret']]):
        print('hash does not match')
        return False
    if not E_check(tx, 'old_vote', [str, unicode]): 
        print('old vote does not exist error')
        return False
    return True
def SVD_consensus_check(tx, txs, DB):
    if not E_check(tx, 'vote_id', [str, unicode]): return False    
    if not E_check(tx, 'decisions', [list]): return False    
    if not tools.reveal_time_p(DB, 5): return False
    jury=blockchain.db_get(tx['vote_id'], DB)
    if len(decisions)<5:
        print('need at least 5 decisions to compute SVD')
        return False
    if len(jury['members'])<3: 
        print('need at least 3 voters in order to compute SVD')
        return False
    matrix=decision_matrix(jury, tx['decisions'], DB)
    for i in part_cert(matrix):
        if i<0.6:
            print('participation and certainty too low')
            print('matrix: ' +str(matrix))
            return False
    return True
def prediction_market_check(tx, txs, DB):
    address=addr(tx)
    for l in ['states', 'states_combinatory', 'shares_purchased', 'decisions']:
        if not E_check(tx, l, list): 
            print('tx: ' +str(tx))
            print(str(l)+ ' error')
            return False
    for dec in tx['decisions']:
        if not blockchain.db_existence(dec, DB): 
            print('decision is not in the database: ' +str(dec))
            return False
    if len(tx['states'])>200:
        print('too many states')
        return False
    if not E_check(tx, 'B', int):
        print('B error')
        return False
    for comb in tx['states_combinatory']:
        if len(comb)!=len(tx['decisions']):
            print(str(comb)+' comb error')
            return False
    for l in [tx['states_combinatory'], tx['states'], tx['decisions']]:
        for comb in l:
            copies=len(filter(lambda comb2: comb==comb2, l))
            if copies!=1:
                print(str(comb)+' not mutually exclusive')
                return False
    if len(tx['states'])!=len(tx['states_combinatory'])+1:
        print('wrong number of possible states?')
        return False
    if not E_check(tx, 'PM_id', [str, unicode]):
        print('PM_id error')
        return False        
    if len(tx['PM_id'])>1000: return False
    if blockchain.db_existence(tx['PM_id'], DB): 
        print('PM: ' +str(blockchain.db_get(tx['PM_id'], DB)))
        print('this PM_id is already being used')
        return False
    for t in txs:
        if 'PM_id' in t:
            if t['PM_id']==tx['PM_id']:
                print('Someone used that PM in this block already')
                return False
    acc=blockchain.db_get(address, DB)
    if not fee_check(tx, txs, DB): return False#
    return True

def cost_to_buy_shares(tx, DB):
    pm=blockchain.db_get(tx['PM_id'], DB)
    shares_purchased=pm['shares_purchased']
    buy=tx['buy']
    B=pm['B']
    def C(shares, B): return B*math.log(sum(map(lambda x: math.e**(x/B), shares)))
    C_old=C(shares_purchased, B)
    def add(a, b): return a+b
    C_new=C(map(add, shares_purchased, buy), B)
    return C_new-C_old


def buy_shares_check(tx, txs, DB):
    if not E_check(tx, 'buy', list):
        print('buy error')
        return False
    if not E_check(tx, 'PM_id', [str, unicode]):
        print('pm id error')
        return False
    pm=blockchain.db_get(tx['PM_id'], DB)
    if len(tx['buy'])!=len(pm['shares_purchased']):
        print('buy length error')
        return False
    for purchase in tx['buy']:
        if type(purchase)!=int:
            return False
    for i in range(len(tx['buy'])):
        if tx['buy'][i]+pm['shares_purchased'][i]<0:
            print('PM cannot have negative shares')
            return False
    if not fee_check(tx, txs, DB):
        print('fee check error')
        return False
    return True
def collect_winnings_check(tx, txs, DB):
    if not E_check(tx, 'address', [str, unicode]):
        print('no address error')
        return False
    acc=blockchain.db_get(tx['address'], DB)
    if not E_check(tx, 'PM_id', [str, unicode]):
        print('no PM_id error')
        return False
    if tx['PM_id'] not in acc['shares']:
        print('you do not own any shares for this PM')
        return False
    if not E_check(tx, 'shares', acc['shares'][tx['PM_id']]):
        print('that is not how many shares you have error')
        return False
    for dec in pm['decisions']:
        decision = blockchain.db_get(dec, DB)
        if decisions['state'] not in ['yes', 'no']:
            print('we have not yet reached consensus on the outcome of this market error')
            return False
    return True

tx_check = {'spend': spend_verify, 
            'mint': mint_verify,
            'create_jury':create_jury_check,
            'propose_decision':propose_decision_check,
            #'accept_decision':accept_decision_check,
            'jury_vote':jury_vote_check,
            'reveal_jury_vote':reveal_jury_vote_check,
            'SVD_consensus':SVD_consensus_check,
            'prediction_market':prediction_market_check,
            'buy_shares':buy_shares_check,
            'collect_winnings':collect_winnings_check}
            
#------------------------------------------------------
#DB['add_block']=True -> adding a block.
def get_(loc, thing): 
    if loc==[]: return thing
    return get_(loc[1:], thing[loc[0]])

def set_(loc, dic, val):
    get_(loc[:-1], dic)[loc[-1]] = val
    return dic

def adjust(location, pubkey, DB, f):#location shouldn't be here.
    acc = blockchain.db_get(pubkey, DB)
    f(acc)
    blockchain.db_put(pubkey, acc, DB)    
def adjust_int(key, pubkey, amount, DB):
    def f(acc, amount=amount):
        if not DB['add_block']: amount=-amount
        set_(key, acc, (get_(key, acc) + amount))
    adjust(key, pubkey, DB, f)
def adjust_string(location, pubkey, old, new, DB):
    def f(acc, old=old, new=new):
        current=get_(location, acc)
        if DB['add_block']: 
            set_(location, acc, new)
        else: set_(location, acc, old)
    adjust(location, pubkey, DB, f)
def adjust_dict(location, pubkey, remove, dic, DB):
    def f(acc, remove=remove, dic=dic):
        current=get_(location, acc)
        if remove != (DB['add_block']):# 'xor' and '!=' are the same.
            current=dict(dic.items() + current.items())
        else: 
            current.pop(dic.keys()[0])
        set_(location, acc, current)
    adjust(location, pubkey, DB, f)    
def adjust_list(location, pubkey, remove, item, DB):
    def f(acc, remove=remove, item=item):
        current=get_(location, acc)
        if remove != (DB['add_block']):# 'xor' and '!=' are the same.
            current.append(item)
        else: 
            current.remove(item)
        set_(location, acc, current)
    adjust(location, pubkey, DB, f)    
def symmetric_put(id_, dic, DB):
    if DB['add_block']: blockchain.db_put(id_, dic, DB)
    else: blockchain.db_delete(id_, DB)

def mint(tx, DB):
    address = addr(tx)
    adjust_int(['amount'], address, custom.block_reward, DB)
    adjust_int(['count'], address, 1, DB)

def initialize_to_zero_helper(loc, address, DB):
    acc=blockchain.db_get(address, DB)
    if loc[1] not in acc[loc[0]]:
        acc[loc[0]][loc[1]]=0
        blockchain.db_put(pubkey, acc, DB)    
def memory_leak_helper(loc, address, DB):
    acc=blockchain.db_get(address, DB)
    bool_=get_(acc, loc)==0
    if bool_:
        adjust_dict(loc, address, True, {loc[-1]: 0}, DB)
    return bool_
def initialize_to_zero_votecoin(vote_id, address, DB):
    initialize_to_zero_helper(['votecoin', vote_id], address, DB)
    if address not in blockchain.db_get(vote_id, DB)['members']:
        adjust_list(['members'], vote_id, False, address, DB)
def memory_leak_votecoin(vote_id, address, DB):
    bool_=memory_leak_helper(['votecoin', vote_id], address, DB)
    if bool_:
        adjust_list(['members'], vote_id, True, address, DB)

'''
def initialize_to_zero(address, loc, DB, type_=''):#addresses, vote_id, DB):
    acc=blockchain.db_get(address, DB)
    print('acc: ' +str(acc))
    if vote_id not in acc['votecoin']:
        #acc['votecoin'][vote_id]=0
        adjust(42, address, DB, lambda acc: set(acc, loc, 0))
        #adjust(42, vote_id, DB, lambda acc: acc['members'].append(add))
        if type_=='vote_id':
            print('jury: ' +str(blockchain.db_get(vote_id, DB)))
            adjust_list(['members'], address, False, add, DB)
            print('jury: ' +str(blockchain.db_get(vote_id, DB)))
def memory_leak(addresses, vote_id, DB):
    for add in addresses:
        def f(acc):
            if acc['votecoin'][vote_id]==0:
                acc['votecoin'].pop(vote_id)
                #adjust(42, vote_id, DB, lambda acc: acc['members'].pop(add))
                adjust_list(['members'], vote_id, True, add, DB)
        adjust(42, add, DB, f)
'''
def spend(tx, DB):#we should have the ability to spend shares eventually.
    #check to see if we won any bets. If so, convert winnings into truthcoins.
    #wait 120 blocks before collecting truthcoin (if we want to copy bitcoin)
    address = addr(tx)
    if 'vote_id' in tx:
        initialize_to_zero_votecoin(tx['vote_id'], address, DB)
        initialize_to_zero_votecoin(tx['vote_id'], tx['to'], DB)
        adjust_int(['votecoin', tx['vote_id']], address, -tx['amount'], DB)
        adjust_int(['votecoin', tx['vote_id']], tx['to'], tx['amount'], DB)
        memory_leak_votecoin(tx['vote_id'], addresses, DB)#this should get rid of any zeros in the jury so we don't leak memory.
        memory_leak_votecoin(tx['vote_id'], tx['to'], DB)#this should get rid of any zeros in the jury so we don't leak memory.
    else:
        adjust_int(['amount'], address, -tx['amount'], DB)
        adjust_int(['amount'], tx['to'], tx['amount'], DB)
    adjust_int(['amount'], address, -custom.fee, DB)
    adjust_int(['count'], address, 1, DB)
def create_jury(tx, DB):
    #specify when voting rounds end.
    address=addr(tx)
    adjust_int(['count'], address, 1, DB)
    adjust_int(['amount'], address, -custom.create_jury_fee, DB)
    adjust_dict(['votecoin'], address, False, {tx['vote_id']: 6**4}, DB)
    jury={'decisions':[], 'members':[address]}
    symmetric_put(tx['vote_id'], jury, DB)
def propose_decision(tx, DB):
    address=addr(tx)
    adjust_int(['count'], address, 1, DB)
    adjust_list(['decisions'], tx['vote_id'], False, tx['decision_id'], DB)
    adjust_int(['amount'], address, -custom.propose_decision_fee, DB)
    decision={'state':'proposed',#proposed, yes, no
              'txt':tx['txt']}
    symmetric_put(tx['decision_id'], decision, DB)

def jury_vote(tx, DB):
    address=addr(tx)
    acc=blockchain.db_get(address, DB)
    if tx['decision_id'] not in acc['votes']:
        acc['votes'][tx['decision_id']]='unsure'
        #this memory leak needs to be cleaned up somewhere else.
        blockchain.db_put(address, acc, DB)
    adjust_int(['count'], address, 1, DB)
    adjust_int(['amount'], address, -custom.jury_vote_fee, DB)
    print('before adjust: ' +str(blockchain.db_get(address, DB)))
    adjust_string(['votes', tx['decision_id']], address, tx['old_vote'], tx['new_vote'], DB)
    print('after adjust: ' +str(blockchain.db_get(address, DB)))
    
def reveal_jury_vote(tx, DB):    
    address=addr(tx)
    adjust_int(['count'], address, 1, DB)
    adjust_string(['votes', tx['decision_id']], address, tx['old_vote'], tx['new_vote'], DB)
    
def decision_matrix(jury, decisions, DB):
    matrix=[]
    for decision in decisions:
        row=[]
        for member in jury['members']:#empty
            acc=blockchain.db_get(member, DB)
            vote='unsure'
            try:
                vote=acc['votes'][decision]
            except: pass
            if vote=='yes': 
                row.append(1)
            elif vote=='no': 
                row.append(0)
            elif vote=='half': 
                row.append(0.5)
            else:
                row.append('NA')
        matrix.append(row)
    return matrix

def part_cert(matrix):
    result=ConsensusMechanism.main(matrix)
    print('result: ' +str(result))
    participation=result['participation']
    certainty=result['certainty']
    def mul(x, y): return float(x)*float(y)
    return map(mul, participation, certainty)

def SVD_consensus(tx, DB):
    address=addr(tx)
    adjust_int(['count'], address, 1, DB)
    jury=blockchain.db_get(tx['vote_id'], DB)
    matrix=decision_matrix(jury, tx['decisions'], DB)
    result=ConsensusMechanism.main(matrix)
    #create fee. If there are more decisions, then the fee is lower.
    print('matrix: ' +str(matrix))
    pprint.pprint(result)
    for i in range(len(tx['decisions'])):
        adjust_list(['decisions'], tx['vote_id'], True, tx['decisions'][i], DB)
        new='yes'
        if float(result['outcome'][i])<0.5: 
            new='no'
        adjust_string(['state'], decision, 'proposed', new, DB)
    #if a prediction market expires, then we should give 1/2 it's fees to votecoin holders, and 1/2 it's fees to the author
    #the prediction market may have unused seed capital. This seed capital should go to the author

def prediction_market(tx, DB):#also used to increase liquidity of existing market, eventually
    address=addr(tx)
    adjust_int(['count'], address, 1, DB)
    adjust_int(['amount'], address, -tx['B'], DB)
    pm={}
    for i in ['fees', 'B', 'states', 'states_combinatory', 'shares_purchased', 'decisions']:
        pm[i]=tx[i]
    pm['author']=address
    pm['shares_purchased']=[]
    for i in range(len(tx['states'])): pm['shares_purchased'].append(0)
    #pm={'fees':0, 'B':tx['B'], 'states':['not cloudy', 'cloudy', 'cloudy+rain/sleet', 'cloudy+snow'], 'states_combinatory':[[0,0,0],[1,0,0],[1,1,0]], 'shares_puchased':[0,0,0,0],'decisions':[decision_id_cloudy, decision_id_rain, decision_id_snow], 'owner':address}
    symmetric_put(tx['PM_id'], pm, DB)
    print('created PM: '+str(tx['PM_id']))
    #has a 'buy_shares' inside of it, eventually
def buy_shares(tx, DB):
    address = addr(tx)
    acc = blockchain.db_get(address, DB)
    adjust_int(['count'], address, 1, DB)
    #tx={'buy':[10, -5, 0, 0, 0], PM_id:''} this would buy 10 shares of the first state, and sell 5 of the second.
    cost=cost_to_buy_shares(tx, DB)
    fee=int(abs(cost*0.01))
    adjust_int(['fees'], tx['PM_id'], fee, DB)
    adjust_int(['amount'], address, -fee, DB)
    adjust_int(['amount'], address, -cost, DB)
    all_zeros=[]
    for i in tx['buy']: all_zeros.append(0)
    dic={tx['PM_id']:all_zeros}
    if tx['PM_id'] not in acc['shares']:#initialize to zero
        adjust_dict(['shares'], address, False, dic, DB)
    for i in range(len(tx['buy'])):
        adjust_int(['shares_purchased', i], tx['PM_id'], tx['buy'][i], DB)
        adjust_int(['shares', tx['PM_id'], i], address, tx['buy'][i], DB)
    acc = blockchain.db_get(address, DB)
    if acc['shares'][tx['PM_id']]==all_zeros:
        adjust_dict(['shares'], address, True, dic, DB)
def collect_winnings(tx, DB):
    address = addr(tx)
    acc = blockchain.db_get(address, DB)
    pm = blockchain.db_get(tx['PM_id'], DB)
    outcome_combination=[]
    for dec in pm['decisions']:
        decision = blockchain.db_get(dec, DB)
        do={'yes':(lambda: outcome_combination.append(1)), 
            'no':(lambda: outcome_combination.append(0))}
        do[decision['state']]()
    decs=len(pm['states_combinatory'])
    else_=True
    for i in range(decs):
        if pm['states_combinatory'][i]==outcome_combination:
            adjust_int(['amount'], address, acc['shares'][tx['PM_id']][i], DB)
            else_=False
    if else_:
        adjust_int(['amount'], address, acc['shares'][tx['PM_id']][-1], DB)
    adjust_dict(['shares'], address, True, {tx['PM_id']:tx['shares']}, DB)

update = {'mint': mint, 
          'spend': spend,
          'create_jury':create_jury,
        'propose_decision':propose_decision,
#        'accept_decision':accept_decision,
        'jury_vote':jury_vote,
          'reveal_jury_vote':reveal_jury_vote,
          'SVD_consensus':SVD_consensus,
        'prediction_market':prediction_market,
          'buy_shares':buy_shares,
          'collect_winnings':collect_winnings}
#-----------------------------------------
