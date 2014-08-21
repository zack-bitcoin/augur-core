"""These are functions that are exclusively used for the truthcoin aspects of the blockchain.
tools.py contains functions that are used everywhere.
"""
import blockchain, custom, math, tools
addr=tools.addr
def cost_to_buy_shares(tx, DB):
    pm=tools.db_get(tx['PM_id'], DB)
    shares_purchased=pm['shares_purchased']
    buy=tx['buy']
    B=pm['B']
    def C(shares, B): return B*math.log(sum(map(lambda x: math.e**(x/B), shares)))
    C_old=C(shares_purchased, B)
    def add(a, b): return a+b
    C_new=C(map(add, shares_purchased, buy), B)
    return C_new-C_old
def cost_0(txs, DB):
    #cost of the zeroth confirmation transactions
    total_cost = []
    votecoin_cost = {}
    for Tx in filter(lambda t: DB['address'] == addr(t), txs):
        def spend_(total_cost=total_cost, votecoin_cost=votecoin_cost):
            #global total_cost
            #global votecoin_cost
            total_cost.append(custom.fee)
            if 'vote_id' not in Tx:
                total_cost += Tx['amount']
            else:
                if Tx['vote_id'] not in votecoin_cost: 
                    votecoin_cost[Tx['vote_id']]=0
                votecoin_cost[Tx['vote_id']]+=Tx['amount']
        def buy_shares_(total_cost=total_cost):
            #global total_cost
            cost = cost_to_buy_shares(Tx, DB)
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
            'prediction_market':(lambda: total_cost.append(Tx['B']*math.log(len(Tx['states']))))}
        Do[Tx['type']]()
    return {'truthcoin_cost':sum(total_cost), 'votecoin_cost':votecoin_cost}
def fee_check(tx, txs, DB):
    address = addr(tx)
    cost_=cost_0(txs, DB)
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
def get_(loc, thing): 
    if loc==[]: return thing
    return get_(loc[1:], thing[loc[0]])
def set_(loc, dic, val):
    get_(loc[:-1], dic)[loc[-1]] = val
    return dic
def adjust(location, pubkey, DB, f):#location shouldn't be here.
    acc = tools.db_get(pubkey, DB)
    f(acc)
    tools.db_put(pubkey, acc, DB)    
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
    if DB['add_block']: tools.db_put(id_, dic, DB)
    else: tools.db_delete(id_, DB)
