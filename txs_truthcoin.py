"""
These are transactions that make up a truthcoin system.
Transaction types that are used in blockchains more generally
are left in transactions.py
"""
import txs_tools
import ConsensusMechanism
import math
import pprint
import custom
import tools
import blockchain
import transactions
import numpy

addr=tools.addr
E_check=tools.E_check
is_number=tools.is_number

def create_jury_check(tx, txs, out):
    address=addr(tx)
    if not transactions.signature_check(tx):
        out[0]+='signature check'
        return False
    if not E_check(tx, 'vote_id', [str, unicode]): 
        out[0]+='vote id error'
        return False
    if tools.is_number(tx['vote_id']):
        out[0]+='vote_id can not be a number'
        return False
    if len(tx['vote_id'])>1000: return False
    if tools.db_existence(tx['vote_id']): 
        out[0]+='this vote_id is already being used'
        return False
    if not tools.db_existence(address): 
        out[0]+='this address is not used by anyone'
        return False
    acc=tools.db_get(address)
    for t in txs:
        if 'jury_id' in t:
            if t['jury_id']==tx['jury_id']:
                out[0]+='this zeroth confirmation transaction already exists'
                return False
    if not txs_tools.fee_check(tx, txs): return False
    return True

def propose_decision_check(tx, txs, out):
    if not transactions.signature_check(tx):
        out[0]+='signature check'
        return False
    if not E_check(tx, 'vote_id', [str, unicode]): 
        out[0]+='no vote id'
        return False
    if not E_check(tx, 'decision_id', [str, unicode]): 
        out[0]+='no decision id'
        return False
    if is_number(tx['vote_id']) or is_number(tx['decision_id']):
        out[0]+='that can not be a number'
        return False
    if len(tx['decision_id'])>6**4: 
        out[0]+='decision id too long'
        return False
    if not tools.db_existence(tx['vote_id']): 
        out[0]+='that vote id has not been created yet'
        return False
    if tools.db_existence(tx['decision_id']): 
        out[0]+='that decision id has not been created yet'
        return False
    for t in txs:
        if 'decision_id' in t:
            if t['decision_id']==tx['decision_id']:
                out[0]+='already have a zeroth confirmation tx of this'
                return False
    if not txs_tools.fee_check(tx, txs): 
        out[0]+='you do not have enough money'
        return False
    if not E_check(tx, 'txt', [str, unicode]): 
        out[0]+='what is the txt of this decision?'
        return False
    if len(tx['txt'])>6**5: 
        out[0]+='the txt of this decision is too long'
        return False
    return True

def jury_vote_check(tx, txs, out):
    if not transactions.signature_check(tx):
        out[0]+='signature check'
        return False
    if not E_check(tx, 'decision_id', [str, unicode]): return False
    if not E_check(tx, 'vote_id', [str, unicode]): return False
    if is_number(tx['vote_id']) or is_number(tx['decision_id']):
        out[0]+='that can not be a number'
        return False
    if not E_check(tx, 'old_vote', [str, unicode]): return False
    if not E_check(tx, 'new_vote', [str, unicode]): return False
    decision=tools.db_get(tx['decision_id'])
    if 'state' not in decision:
        out[0]+='that is not a decision_id'
        out[0]+='decision: ' +str(decision)
        out[0]+='tx: ' +str(tx)
        return False
    if decision['state']!='proposed':
        out[0]+='this decision has already been decided'
        return False
    if not tools.db_existence(tx['decision_id']): 
        out[0]+='decision error'
        return False
    if tools.reveal_time_p(): 
        out[0]+='reveal time check'
        return False
    if len(tx['new_vote'])<4: 
        out[0]+='secret too short error'
        return False
    if not txs_tools.fee_check(tx, txs): return False
    return True

def slasher_jury_vote_check(tx, txs, out):
    address=addr(tx)
    if tools.reveal_time_p(): 
        out[0]+='reveal time check slasher'
        return False
    if not transactions.signature_check(tx):
        out[0]+='signature check'
        return False
    if not E_check(tx, 'amount', int): 
        out[0]+='how many votecoins are we confiscating?'
        return False
    if not E_check(tx, 'reveal', dict): 
        out[0]+='no reveal'
        return False
    if not reveal_jury_vote_check(tx['reveal'], txs):
        out[0]+='this is an invalid reveal tx'
        return False
    victim=tools.db_get(addr(tx['reveal']))
    decision=tx['reveal']['decision_id']
    decision=tools.db_get(decision)
    if victim['votecoin'][tx['reveal']['vote_id']]!=tx['amount']:
        out[0]+='that is not how many votecoins they have'
        return False   
    return True

def reveal_jury_vote_check(tx, txs, out):
    if not transactions.signature_check(tx):
        out[0]+='signature check'
        return False
    address=addr(tx)
    acc=tools.db_get(address)
    if not E_check(tx, 'decision_id', [str, unicode]): 
        out[0]+='decision id error'
        return False
    if is_number(tx['decision_id']):
        out[0]+='that can not be a number'
        return False
    decision=tools.db_get(tx['decision_id'])
    if decision['state']!='proposed':
        out[0]+='this decision has already been decided'
        return False
    if not E_check(tx, 'old_vote', [str, unicode]): return False
    if not E_check(tx, 'secret', [str, unicode]): return False
    if not E_check(tx, 'new_vote', [str, unicode]): 
        out[0]+='new vote error'
        return False
    if tx['decision_id'] not in acc['votes']:
        out[0]+='decision id not in acc[votes] error'
        return False
    answer_hash=acc['votes'][tx['decision_id']]
    if not answer_hash==tools.det_hash([tx['new_vote'], tx['secret']]):
        out[0]+='hash does not match'
        return False
    if not E_check(tx, 'old_vote', [str, unicode]): 
        out[0]+='old vote does not exist error'
        return False
    if not txs_tools.fee_check(tx, txs): return False
    return True

def part_cert(matrix, weights):
    tools.log('before COnsensus: '+str(matrix))
    tools.log('weights: ' +str(weights))
    result=ConsensusMechanism.main(matrix, weights)
    tools.log('after COnsensus')
    tools.log('result: ' +str(result))
    participation=result['participation']
    certainty=result['certainty']
    out=[]
    tools.log('participation: ' +str(participation))
    tools.log('certainty: ' +str(certainty))
    for i in range(len(certainty)):
        out.append(float(participation)*float(certainty[i]))
    return out

def SVD_consensus_check(tx, txs, out):
    if not E_check(tx, 'vote_id', [str, unicode]): return False    
    if not E_check(tx, 'decisions', [list]): return False    
    if not tools.reveal_time_p(5): 
        out[0]+='this is not the correct time to do SVD'
        return False
    if is_number(tx['vote_id']):
        out[0]+='that can not be a number'
        return False
    jury=tools.db_get(tx['vote_id'])
    if len(tx['decisions'])<5:
        out[0]+='need at least 5 decisions to compute SVD'
        return False
    if not E_check(jury, 'members', [list]):
        out[0]+='that jury has not been created yet'
        return False
    if len(jury['members'])<3: 
        out[0]+='need at least 3 voters in order to compute SVD'
        return False
    try:
        matrix=txs_tools.decision_matrix(jury, tx['decisions'])
    except:
        tools.log(sys.exc_info())
        tools.log('matrix failure')
        return False
    w=txs_tools.weights(tx['vote_id'], jury)
    k=txs_tools.decisions_keepers(tx['vote_id'], jury)
    for decision in tx['decisions']:
        if not decision in k:
            out[0]+='one of the decisions has insufficient participation*certainty: ' +str(decision)
            return False
    if not txs_tools.fee_check(tx, txs): 
        out[0]+='you do not have enough money'
        return False
    return True

def prediction_market_check(tx, txs, out):
    if not transactions.signature_check(tx):
        out[0]+='signature check'
        return False
    address=addr(tx)
    for l in ['states', 'states_combinatory', 'decisions']:
        if not E_check(tx, l, list): 
            out[0]+=str(l)+ ' error'
            return False
    for dec in tx['decisions']:
        if not tools.db_existence(dec): 
            out[0]+='decision is not in the database: ' +str(dec)
            return False
        if is_number(dec):
            out[0]+='decision_id can not be a number'
            return False
    if is_number(tx['PM_id']):
        out[0]+='PM_id can not be a number'
        return False
    if len(tx['states'])>200:
        out[0]+='too many states'
        return False
    if not E_check(tx, 'B', int):
        out[0]+='B error'
        return False
    for comb in tx['states_combinatory']:
        if len(comb)!=len(tx['decisions']):
            out[0]+=str(comb)+' comb error'
            return False
    for l in [tx['states_combinatory'], tx['states'], tx['decisions']]:
        for comb in l:
            copies=len(filter(lambda comb2: comb==comb2, l))
            if copies!=1:
                out[0]+=str(comb)+' not mutually exclusive'
                return False
    if len(tx['states'])!=len(tx['states_combinatory'])+1:
        out[0]+='wrong number of possible states?'
        return False
    if not E_check(tx, 'PM_id', [str, unicode]):
        out[0]+='PM_id error'
        return False        
    if len(tx['PM_id'])>1000: 
        out[0]+='PM_id too long'
        return False
    if tools.db_existence(tx['PM_id']): 
        #out[0]+='PM: ' +str(tools.db_get(tx['PM_id'], DB))
        out[0]+='this PM_id is already being used'
        return False
    for t in txs:
        if 'PM_id' in t:
            if t['PM_id']==tx['PM_id']:
                out[0]+='Someone used that PM in this block already'
                return False
    acc=tools.db_get(address)
    if not txs_tools.fee_check(tx, txs): 
        out[0]+='you do not have enough money'
        return False
    return True

def buy_shares_check(tx, txs, out):
    #make sure that we can only buy the shares of undecided markets.
    if not transactions.signature_check(tx):
        out[0]+='signature check'
        return False
    if not E_check(tx, 'buy', list):
        out[0]+='buy error'
        return False
    if not E_check(tx, 'PM_id', [str, unicode]):
        out[0]+='pm id error'
        return False
    pm=tools.db_get(tx['PM_id'])
    if 'decisions' not in pm:
        out[0]+='that is not a prediction market yet'
        return False
    if len(tx['buy'])!=len(pm['shares_purchased']):
        out[0]+='buy length error'
        return False
    for purchase in tx['buy']:
        if type(purchase)!=int:
            return False
    for i in range(len(tx['buy'])):
        if tx['buy'][i]+pm['shares_purchased'][i]<0:
            out[0]+='PM cannot have negative shares'
            return False
    if not txs_tools.fee_check(tx, txs):
        out[0]+='fee check error'
        return False
    for dec in pm['decisions']:
        decision = tools.db_get(dec)
        bad=True
        if decision['state'] not in ['yes', 'no']:
            bad=False
        if bad:
            out[0]+='this PM is already expired. you cannot buy shares.'
            return False
    return True

def collect_winnings_check(tx, txs, out):
    if not transactions.signature_check(tx):
        out[0]+='signature check'
        return False
    if not E_check(tx, 'address', [str, unicode]):
        out[0]+='no address error'
        return False
    acc=tools.db_get(tx['address'])
    if not E_check(tx, 'PM_id', [str, unicode]):
        out[0]+='no PM_id error'
        return False
    if tx['PM_id'] not in acc['shares']:
        out[0]+='you do not own any shares for this PM'
        return False
    if not tx['shares']==acc['shares'][tx['PM_id']]:
        out[0]+='that is not how many shares you have error'
        return False
    pm=tools.db_get(tx['PM_id'])
    if 'decisions' not in pm:
        out[0]+='that is not a prediction market yet'
        return False
    for dec in pm['decisions']:
        decision = tools.db_get(dec)
        if decision['state'] not in ['yes', 'no']:
            out[0]+='we have not yet reached consensus on the outcome of this market error'
            return False
    return True

adjust_int=txs_tools.adjust_int
adjust_dict=txs_tools.adjust_dict
adjust_list=txs_tools.adjust_list
adjust_string=txs_tools.adjust_string
symmetric_put=txs_tools.symmetric_put

def create_jury(tx, add_block):
    #specify when voting rounds end.
    address=addr(tx)
    adjust_int(['count'], address, 1, add_block)
    adjust_int(['amount'], address, -custom.create_jury_fee, add_block)
    adjust_dict(['votecoin'], address, False, {tx['vote_id']: 6**4}, add_block)
    jury={'decisions':[], 'members':[address]}
    symmetric_put(tx['vote_id'], jury, add_block)

def propose_decision(tx, add_block):
    address=addr(tx)
    adjust_int(['count'], address, 1, add_block)
    adjust_list(['decisions'], tx['vote_id'], False, tx['decision_id'], add_block)
    adjust_int(['amount'], address, -custom.propose_decision_fee, add_block)
    decision={'state':'proposed',#proposed, yes, no
              'txt':tx['txt']}
    symmetric_put(tx['decision_id'], decision, dd_block)

def jury_vote(tx, add_block):
    address=addr(tx)
    acc=tools.db_get(address)
    if tx['decision_id'] not in acc['votes']:
        acc['votes'][tx['decision_id']]='unsure'
        tools.db_put(address, acc)
    adjust_int(['count'], address, 1, add_block)
    adjust_int(['amount'], address, -custom.jury_vote_fee, add_block)
    adjust_string(['votes', tx['decision_id']], address, tx['old_vote'], tx['new_vote'], add_block)

def slasher_jury_vote(tx, add_block):
    address=addr(tx)
    adjust_int(['count'], address, 1, add_block)
    victim=addr(tx['reveal'])
    decision=tx['reveal']['decision_id']
    decision=tools.db_get(decision)
    txs_tools.initialize_to_zero_votecoin(tx['vote_id'], address, add_block)
    txs_tools.initialize_to_zero_votecoin(tx['vote_id'], victim, add_block)
    adjust_int(['votecoin',decision['vote_id']], victim, -tx['amount'], add_block)
    adjust_int(['votecoin',decision['vote_id']], address, (4*tx['amount'])/5, add_block)
    tx_tools.memory_leak_votecoin(tx['vote_id'], address, add_block)
    tx_tools.memory_leak_votecoin(tx['vote_id'], victim, add_block)

    #remove votecoins from victim, give 4/5ths to address.
def reveal_jury_vote(tx, add_block):    
    address=addr(tx)
    adjust_int(['count'], address, 1, add_block)
    adjust_string(['votes', tx['decision_id']], address, tx['old_vote'], tx['new_vote'], add_block)

def SVD_consensus(tx, add_block):
    address=addr(tx)
    adjust_int(['count'], address, 1, add_block)
    jury=tools.db_get(tx['vote_id'])
    matrix=txs_tools.decision_matrix(jury, tx['decisions'])
    w=txs_tools.weights(tx['vote_id'], jury)
    result=ConsensusMechanism.main(matrix, w)
    #create fee. If there are more decisions, then the fee is lower.
    #tools.log('matrix: ' +str(matrix))
    #tools.log(pprint.pformat(result))
    for i in range(len(tx['decisions'])):
        adjust_list(['decisions'], tx['vote_id'], True, tx['decisions'][i], add_block)
        new='yes'
        if float(result['outcome'][i])<0.5: 
            new='no'
        adjust_string(['state'], tx['decisions'][i], 'proposed', new, add_block)

    #if a prediction market expires, then we should give 1/2 it's fees to votecoin holders, and 1/2 it's fees to the author
    #the prediction market may have unused seed capital. This seed capital should go to the author
def prediction_market(tx, add_block):#also used to increase liquidity of existing market, eventually
    address=addr(tx)
    adjust_int(['count'], address, 1, add_block)
    adjust_int(['amount'], address, int(-tx['B']*math.log(len(tx['states']))), add_block)
    pm={}
    for i in ['fees', 'B', 'states', 'states_combinatory', 'decisions']:
        pm[i]=tx[i]
    pm['author']=address
    pm['shares_purchased']=[]
    for i in range(len(tx['states'])): pm['shares_purchased'].append(0)
    symmetric_put(tx['PM_id'], pm, add_block)
    #tools.log('created PM: '+str(tx['PM_id']))

    #has a 'buy_shares' inside of it, eventually
def buy_shares(tx, add_block):
    address = addr(tx)
    acc = tools.db_get(address)
    adjust_int(['count'], address, 1, add_block)
    cost=txs_tools.cost_to_buy_shares(tx)
    fee=int(abs(cost*0.01))
    adjust_int(['fees'], tx['PM_id'], fee, add_block)
    adjust_int(['amount'], address, -fee, add_block)
    adjust_int(['amount'], address, -cost, add_block)
    all_zeros=[]
    for i in tx['buy']: all_zeros.append(0)
    dic={tx['PM_id']:all_zeros}
    if tx['PM_id'] not in acc['shares']:#initialize to zero
        adjust_dict(['shares'], address, False, dic, add_block)
    for i in range(len(tx['buy'])):
        adjust_int(['shares_purchased', i], tx['PM_id'], tx['buy'][i], add_block)
        adjust_int(['shares', tx['PM_id'], i], address, tx['buy'][i], add_block)
    acc = tools.db_get(address)
    if acc['shares'][tx['PM_id']]==all_zeros:
        adjust_dict(['shares'], address, True, dic, add_block)
def collect_winnings(tx, add_block):
    address = addr(tx)
    acc = tools.db_get(address)
    pm = tools.db_get(tx['PM_id'])
    outcome_combination=[]
    for dec in pm['decisions']:
        decision = tools.db_get(dec)
        do={'yes':(lambda: outcome_combination.append(1)), 
            'no':(lambda: outcome_combination.append(0))}
        do[decision['state']]()
    decs=len(pm['states_combinatory'])
    else_=True
    for i in range(decs):
        if pm['states_combinatory'][i]==outcome_combination:
            adjust_int(['amount'], address, tx['shares'][i], add_block)
            else_=False
    if else_:
        adjust_int(['amount'], address, tx['shares'][-1], add_block)
    adjust_dict(['shares'], address, True, {tx['PM_id']:tx['shares']}, add_block)
