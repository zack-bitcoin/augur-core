import txs_tools
import ConsensusMechanism
import math
import pprint
import custom
import tools
import blockchain

addr=tools.addr
E_check=tools.E_check
is_number=tools.is_number
def create_jury_check(tx, txs, DB):
    address=addr(tx)
    if not E_check(tx, 'vote_id', [str, unicode]): 
        print('vote id error')
        return False
    if tools.is_number(tx['vote_id']):
        print('vote_id can not be a number')
        return False
    if len(tx['vote_id'])>1000: return False
    if blockchain.db_existence(tx['vote_id'], DB): 
        print('this vote_id is already being used')
        return False
    if not blockchain.db_existence(address, DB): 
        print('this address is not used by anyone')
        return False
    acc=blockchain.db_get(address, DB)
    for t in txs:
        if 'jury_id' in t:
            if t['jury_id']==tx['jury_id']:
                return False
    if not txs_tools.fee_check(tx, txs, DB): return False
    return True
def propose_decision_check(tx, txs, DB):
    if not E_check(tx, 'vote_id', [str, unicode]): return False
    if not E_check(tx, 'decision_id', [str, unicode]): return False
    if is_number(tx['vote_id']) or is_number(tx['decision_id']):
        print('that can not be a number')
        return False
    if len(tx['decision_id'])>6**4: return False
    if not blockchain.db_existence(tx['vote_id'], DB): return False
    if blockchain.db_existence(tx['decision_id'], DB): return False
    for t in txs:
        if 'decision_id' in t:
            if t['decision_id']==tx['decision_id']:
                return False
    if not txs_tools.fee_check(tx, txs, DB): return False
    if not E_check(tx, 'txt', [str, unicode]): return False
    if len(tx['txt'])>6**5: return False
    return True
def jury_vote_check(tx, txs, DB):
    if not E_check(tx, 'decision_id', [str, unicode]): return False
    if not E_check(tx, 'vote_id', [str, unicode]): return False
    if is_number(tx['vote_id']) or is_number(tx['decision_id']):
        print('that can not be a number')
        return False
    if not E_check(tx, 'old_vote', [str, unicode]): return False
    if not E_check(tx, 'new_vote', [str, unicode]): return False
    decision=blockchain.db_get(tx['decision_id'], DB)
    if 'state' not in decision:
        print('that is not a decision_id')
        print('decision: ' +str(decision))
        print('tx: ' +str(tx))
        error()
        return False
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
    if not txs_tools.fee_check(tx, txs, DB): return False
    return True
def reveal_jury_vote_check(tx, txs, DB):
    print('reveal jury vote check')
    address=addr(tx)
    acc=blockchain.db_get(address, DB)
    if not E_check(tx, 'decision_id', [str, unicode]): 
        print('decision id error')
        return False
    if is_number(tx['decision_id']):
        print('that can not be a number')
        return False
    decision=blockchain.db_get(tx['decision_id'], DB)
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
    if not txs_tools.fee_check(tx, txs, DB): return False
    return True
def SVD_consensus_check(tx, txs, DB):
    def part_cert(matrix):
        result=ConsensusMechanism.main(matrix)
        print('result: ' +str(result))
        participation=result['participation']
        certainty=result['certainty']
        def mul(x, y): return float(x)*float(y)
        return map(mul, participation, certainty)
    if not E_check(tx, 'vote_id', [str, unicode]): return False    
    if not E_check(tx, 'decisions', [list]): return False    
    if not tools.reveal_time_p(DB, 5): return False
    if is_number(tx['vote_id']) or is_number(tx['decision_id']):
        print('that can not be a number')
        return False
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
    if not txs_tools.fee_check(tx, txs, DB): return False
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
        if is_number(dec):
            print('decision_id can not be a number')
            return False
    if is_number(tx['PM_id']):
        print('PM_id can not be a number')
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
    if not txs_tools.fee_check(tx, txs, DB): return False#
    return True


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
    if not txs_tools.fee_check(tx, txs, DB):
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


adjust_int=txs_tools.adjust_int
adjust_dict=txs_tools.adjust_dict
adjust_list=txs_tools.adjust_list
adjust_string=txs_tools.adjust_string
symmetric_put=txs_tools.symmetric_put
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
    #print('before adjust: ' +str(blockchain.db_get(address, DB)))
    adjust_string(['votes', tx['decision_id']], address, tx['old_vote'], tx['new_vote'], DB)
    #print('after adjust: ' +str(blockchain.db_get(address, DB)))
    
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
    cost=txs_tools.cost_to_buy_shares(tx, DB)
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


