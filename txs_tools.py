"""These are functions that are exclusively used for the truthcoin aspects of the blockchain.
tools.py contains functions that are used everywhere.
"""
import blockchain, custom, tools
from cdecimal import Decimal

addr=tools.addr

def weights(vote_id, DB, jury='default'):
    out=[]
    if jury=='default':
        jury=tools.db_get(jury, DB)
    if 'members' not in jury:
        return 'error'
    for member in jury['members']:
        acc=tools.db_get(member, DB)
        out.append([acc['votecoin'][vote_id]])
    return out
def decision_matrix(jury, decisions, DB):
    matrix=[]
    if 'members' not in jury:
        tools.log('DECISION MATRIX ERROR UNINITIALIZED JURY')
    for member in jury['members']:#empty
        acc=tools.db_get(member, DB)
        row=[]
        for decision in decisions:
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
def decisions_keepers(vote_id, jury, DB):
    #this is returning something of length voters.
    
    wt=map(lambda x: x[0], weights(vote_id, DB, jury))
    if wt=='error': return 'error'
    total_weight=sum(wt)
    matrix=decision_matrix(jury, jury['decisions'], DB)
    #exclude decisions with insufficient participation*certainty
    decisions=[]
    if len(matrix)<3: 
        return []
    if len(matrix[0])<5:
        return []
    attendance=[]
    certainty=[]
    for decision in range(len(matrix[0])):
        a=0
        c=0
        for juror in range(len(matrix)):
            if not matrix[juror][decision]=='NA':
                a+=wt[juror]
                if matrix[juror][decision]==1:
                    c+=wt[juror]
            else:
                c+=wt[juror]/2.0
        attendance.append(a*1.0/total_weight)
        certainty.append(abs(c-0.5)*2.0/total_weight)
    out=[]
    for i in range(len(certainty)):
        if certainty[i]*attendance[i]>0.55:
            out.append(jury['decisions'][i])
        else:
            tools.log('participation times certainty was too low to include this decision: ' +str(jury['decisions'][i]))
    l=tools.db_get('length')
    for i in out:
        o=[]
        dec=tools.db_get(i)
        if not'maturation' in dec and dec['maturation']>l:
            o.append(i)
    return o
'''
from decimal import Decimal
def log_e(x):
    return(x.ln)
def cost_to_buy_shares(tx):
    pm=tools.db_get(tx['PM_id'])
    shares_purchased=pm['shares_purchased']
    buy=tx['buy']
    B=Decimal(pm['B'])
    E=Decimal('2.718281828459045')
    dec C(shares, B): return B*((sum(map(lambda x: E**(x/B), shares))).ln())
    C_old=C(shares_purchased, B)
    def add(a, b): return a+b
    C_new=C(map(add, shares_purchased, buy), B)
    return int(C_new-C_old)
'''
E=Decimal('2.718281828459045')
def cost_to_buy_shares(tx):
    pm=tools.db_get(tx['PM_id'])
    shares_purchased=pm['shares_purchased']
    buy=tx['buy']
    B=pm['B']*Decimal('1.0')
    def C(shares, B): return B*(sum(map(lambda x: E**(x/B), shares))).ln()
    C_old=C(shares_purchased, B)
    def add(a, b): return a+b
    C_new=C(map(add, shares_purchased, buy), B)
    return int(C_new-C_old)
def cost_0(txs, address):
    #cost of the zeroth confirmation transactions
    total_cost = []
    votecoin_cost = {}
    #address=tools.db_get('address')
    for Tx in filter(lambda t: address == addr(t), txs):
        def spend_(total_cost=total_cost, votecoin_cost=votecoin_cost):
            total_cost.append(custom.fee)
            if 'vote_id' not in Tx:
                total_cost += [Tx['amount']]
            else:
                if Tx['vote_id'] not in votecoin_cost: 
                    votecoin_cost[Tx['vote_id']]=0
                votecoin_cost[Tx['vote_id']]+=Tx['amount']
        def buy_shares_(total_cost=total_cost):
            cost = cost_to_buy_shares(Tx)
            total_cost.append(custom.buy_shares_fee)
            total_cost.append(cost)
            total_cost.append(int(abs(cost*0.01)))
        Do={'spend':spend_,
            'mint':(lambda: total_cost.append(-custom.block_reward)), 
            'create_jury':(lambda: total_cost.append(custom.create_jury_fee)), 
            'propose_decision':(lambda: total_cost.append(custom.propose_decision_fee)), 
            'jury_vote':(lambda: total_cost.append(custom.jury_vote_fee)),
            'reveal_jury_vote':(lambda: total_cost.append(custom.reveal_jury_vote_fee)),
            'SVD_consensus':(lambda: total_cost.append(custom.SVD_consensus_fee)),
            'collect_winnings':(lambda: total_cost.append(-custom.collect_winnings_reward)),
            'buy_shares':buy_shares_,
            'prediction_market':(lambda: total_cost.append(Tx['B']*(Decimal(len(Tx['states']))).ln()))}
        Do[Tx['type']]()
    return {'truthcoin_cost':sum(total_cost), 'votecoin_cost':votecoin_cost}
def fee_check(tx, txs, DB):
    address = addr(tx)
    cost_=cost_0(txs+[tx], address)
    truthcoin_cost = cost_['truthcoin_cost']
    votecoin_cost = cost_['votecoin_cost']
    acc=tools.db_get(address, DB)
    if int(acc['amount']) < truthcoin_cost: 
        tools.log('insufficient truthcoin')
        return False
    for v_id in votecoin_cost:
        if v_id not in acc['votecoin']: 
            tools.log('votecoin_cost: ' +str(votecoin_cost))
            tools.log('acc: ' +str(acc))
            tools.log('0 votecoin: ' +str(v_id))
            return False
        if acc['votecoin'][v_id]<votecoin_cost[v_id]: 
            tools.log(acc['votecoin'][v_id])
            tools.log(votecoin_cost[v_id])
            tools.log('not enough votecoin: ' +str(v_id))
            return False
    return True
'''
db={}
def put_x(s):
    def f(d, x): return tools.db_put(x+s, d)
    return f
def get_x(s): return (lambda x: tools.db_get(x+s))
def existence_x(s): return (lambda x: tools.db_existence(x+s))
verbs=[put_x, get_x, existence_x]
verb_names=['get', 'put', 'existence']
adj=['jury', 'pm', 'dec', 'block', 'addr']
prefix=['j_', 'p_', 'd_', 'b_', '']
for v in range(len(verbs)):
    db[verb_names[v]]={}
    for a in range(len(adj)):
        db[verb_names[v]][adj[a]]=verbs[v](prefix[a])
def put_x(s, d, x): return db_put(x+s, d)
def put_jury(s, d): return put_x(s, d, 'j_')
def put_pm(s, d): return put_x(s, d, 'p_')
def put_dec(s, d): return put_x(s, d, 'd_')
def put_block(n, d): return put_x(s, d, 'b_')
def put_addr(n, d): return db_put(s, d)
def get_x(s, x): return db_get(x+s)
def get_jury(s): return get_x(s, 'j_')
def get_pm(s): return get_x(s, 'p_')
def get_dec(s): return get_x(s, 'd_')
def get_block(n): return get_x(s, 'b_')
def get_addr(n): return db_get(s)
def existence_x(s, x): return db_existence(x+s)
def existence_jury(s): return existence_x(s, 'j_')
def existence_pm(s): return existence_x(s, 'p_')
def existence_dec(s): return existence_x(s, 'd_')
def existence_block(s): return existence_x(s, 'b_')
def existence_addr(n): return db_existence(s)
'''

def get_(loc, thing): 
    if loc==[]: return thing
    return get_(loc[1:], thing[loc[0]])
def set_(loc, dic, val):
    get_(loc[:-1], dic)[loc[-1]] = val
    return dic
def adjust(pubkey, DB, f):#location shouldn't be here.
    acc = tools.db_get(pubkey, DB)
    f(acc)
    tools.db_put(pubkey, acc, DB)    
def adjust_int(key, pubkey, amount, DB, add_block):
    def f(acc, amount=amount):
        if not add_block: amount=-amount
        set_(key, acc, (get_(key, acc) + amount))
    adjust(pubkey, DB, f)
def adjust_string(location, pubkey, old, new, DB, add_block):
    def f(acc, old=old, new=new):
        current=get_(location, acc)
        if add_block: 
            set_(location, acc, new)
        else: set_(location, acc, old)
    adjust(pubkey, DB, f)
def adjust_dict(location, pubkey, remove, dic, DB, add_block):
    def f(acc, remove=remove, dic=dic):
        current=get_(location, acc)
        if remove != add_block:# 'xor' and '!=' are the same.
            current=dict(dic.items() + current.items())
        else: 
            try:
                current.pop(dic.keys()[0])
            except:
                tools.log('current dic: ' +str(current) + ' ' +str(dic)+' '+str(location))
        set_(location, acc, current)
    adjust(pubkey, DB, f)    
def adjust_list(location, pubkey, remove, item, DB, add_block):
    def f(acc, remove=remove, item=item):
        current=get_(location, acc)
        if remove != (add_block):# 'xor' and '!=' are the same.
            current.append(item)
        else: 
            current.remove(item)
        set_(location, acc, current)
    adjust(pubkey, DB, f)    
def symmetric_put(id_, dic, DB, add_block):
    if add_block: tools.db_put(id_, dic, DB)
    else: tools.db_delete(id_, DB)
def initialize_to_zero_helper(loc, address, DB):
    acc=tools.db_get(address, DB)
    if loc[1] not in acc[loc[0]]:
        acc[loc[0]][loc[1]]=0
        tools.db_put(address , acc, DB)    
def initialize_to_zero_votecoin(vote_id, address, DB, add_block):
    initialize_to_zero_helper(['votecoin', vote_id], address, DB)
    jury=tools.db_get(vote_id, DB)
    if 'members' not in jury:
        tools.log('initialized to zero error')
    if address not in jury['members']:
        adjust_list(['members'], vote_id, False, address, DB, add_block)
def memory_leak_helper(loc, address, DB, add_block):
    acc=tools.db_get(address, DB)
    bool_=get_(loc, acc)==0
    if bool_:
        adjust_dict(loc, address, True, {loc[-1]: 0}, DB, add_block)
    return bool_
def memory_leak_votecoin(vote_id, address, DB, add_block):
    bool_=memory_leak_helper(['votecoin', vote_id], address, DB, add_block)
    if bool_:
        adjust_list(['members'], vote_id, True, address, DB, add_block)
