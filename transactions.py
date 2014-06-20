"""This file explains how we tell if a transaction is valid or not, it explains
how we update the system when new transactions are added to the blockchain."""
import blockchain
import custom
import copy
import tools


def addr(tx):
    return tools.make_address(tx['pubkeys'], len(tx['signatures']))

E_check=tools.E_check

def fee_check(tx, txs, DB):
    address = addr(tx)
    total_cost = 0
    votecoin_cost = {}
    for Tx in filter(lambda t: address == addr(t), [tx] + txs):
        if Tx['type'] == 'spend':
            total_cost += custom.fee
            if 'votecoin' not in tx:
                total_cost += Tx['amount']
            else:
                if tx['votecoin_id'] not in votecoin_cost: votecoin_cost[tx['votecoin_id']]=0
                votecoin_cost[tx['votecoin_id']]+=Tx['amount']
        if Tx['type'] == 'mint':
            total_cost -= custom.block_reward
        if Tx['type'] == 'create_jury':
            total_cost += custom.create_jury_fee
        if Tx['type'] == 'propose_decision':
            total_cost += custom.propose_decision_fee
    acc=blockchain.db_get(address, DB)
    if int(acc['amount']) < total_cost: 
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
    print('create jury check')
    address=addr(tx)
    if not E_check(tx, 'jury_id', [str, unicode]): 
        print('jury id error')
        return False
    if len(tx['jury_id'])>1000: return False
    if blockchain.db_existence(tx['jury_id'], DB): 
        print('this jury_id is already being used')
        return False
    if not blockchain.db_existence(address, DB): 
        print('this address is not used by anyone')
        return False
    acc=blockchain.db_get(address, DB)
    #if acc['amount']<=custom.create: return False
    #votecoins=total_coins(tx['jury'])
    #if votecoins>1000000: return False
    if not fee_check(tx, txs, DB): return False
    return True
def propose_decision_check(tx, txs, DB):
    if not E_check(tx, 'jury_id', [str, unicode]): return False
    if not E_check(tx, 'decision_id', [str, unicode]): return False
    if len(tx['decision_id'])>1000: return False
    if not blockchain.db_existence(tx['jury_id'], DB): return False
    if blockchain.db_existence(tx['decision_id'], DB): return False
    if not E_check(tx, 'amount', int): return False
    if not fee_check(tx, txs, DB): return False
    if not E_check(tx, 'txt', [str, unicode]): return False
    jury=blockchain.db_get(tx['jury_id'], DB)
    if len(jury['potential_decisions'])>1000: return False
    if not E_check(tx, 'expiration', float): return False
    if not E_check(tx, 'tip', int): return False
    return True
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
def accept_decision_check(tx, txs, DB):
    if not decision_vote_common(tx, txs, custom.accept_decision_fee, 'potential_decisions', 'proposed', 'accept_list', 'deny_list', DB): return False
    return True
'''
def jury_vote_check(tx, txs, DB):
    decision=blockchain.db_get(tx['decision_id'], DB)
    if decision['expiration']>time.time(): return False
    if not decision_vote_common(tx, txs, 0, 'decisions', 'accepted', 'yes_result_list', 'no_result_list', DB): return False
    return True
def reveal_jury_vote_check(tx, txs, DB):
    return False
def SVD_consensus_check(tx, txs, DB):
    return False
def prediction_market_check(tx, txs, DB):
    return False
def buy_shares_check(tx, txs, DB):
    return False
def sell_shares_check(tx, txs, DB):
    return False



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
          'sell_shares':sell_shares_check}####
            
#------------------------------------------------------
#DB['add_block']=True -> adding a block.
def get_(loc, thing): 
    if loc==[]: return thing
    print('loc: ' +str(loc))
    print('thing: ' +str(thing))
    return get_(loc[1:], thing[loc[0]])
def set_(loc, dic, val):
    get_(loc[:-1], dic)[loc[-1]] = val
    return dic
def adjust(location, pubkey, DB, f):
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
            current.pop(current.keys[0])
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

def initialize_to_zero(addresses, vote_id, DB):
    for add in addresses:
        def f(acc, add=add, vote_id=vote_id):
            #acc=blockchain.db_get(add, DB)
            print('acc: ' +str(acc))
            if vote_id not in acc['votecoin']:
                acc['votecoin'][vote_id]=0
        adjust(['votecoin', vote_id], add, DB, f)

def memory_leak(addresses, vote_id, DB):
    for add in addresses:
        acc=blockchain.db_get(add, DB)
        if acc['votecoin'][vote_id]==0:
            acc['votecoin'].pop(vote_id)
def spend(tx, DB):
    address = addr(tx)
    addresses=[address, tx['to']]
    bool_='vote_id' in tx
    if bool_:
        initialize_to_zero(addresses, tx['vote_id'], DB)
        adjust_int(['votecoin', tx['vote_id']], address, -tx['amount'], DB)
        adjust_int(['votecoin', tx['vote_id']], tx['to'], tx['amount'], DB)
    else:
        adjust_int(['amount'], address, -tx['amount'], DB)
        adjust_int(['amount'], tx['to'], tx['amount'], DB)
    adjust_int(['amount'], address, -custom.fee, DB)
    adjust_int(['count'], address, 1, DB)
    if bool_:
        memory_leak(addresses, tx['vote_id'], DB)
def create_jury(tx, DB):
    #specify when voting rounds end.
    address=addr(tx)
    adjust_int(['count'], address, 1, DB)
    adjust_int(['amount'], address, -custom.create_jury_fee, DB)
    adjust_dict(['votecoin'], address, False, {tx['jury_id']: 6**4}, DB)
    jury={'decisions':{},
          'potential_decisions':{}}
    symmetric_put(tx['jury_id'], jury, DB)
def propose_decision(tx, DB):
    address=addr(tx)
    adjust_int(['count'], address, 1, DB)
    adjust_list(['potential_decisions'], tx['jury_id'], False, tx['decision_id'], DB)
    adjust_int(['amount'], address, -custom.propose_decision_fee-tx['amount'], DB)
    decision={'state':'proposed',#proposed, accepted, denied, yes, no
              'expiration':tx['experation'],
              'accept':0,
              'deny':0,
              'asker':address,
              'tip':tx['amount'],
              'txt':tx['txt']}
    symmetric_put(tx['decision_id'], decision, DB)
'''
def simple_vote(tx, DB, yes, no, pass_continuation, fail_continuation):
    address=addr(tx)
    adjust_int(['count'], address, 1, DB)
    if tx['accept?']: location=[yes]
    else: location=['no_result']
    acc=blockchain.db_get(address, DB)
    adjust_int(location, tx['decision_id'], acc['votecoins'][tx['jury_id']], DB)
    location=[location[0]+'_list']#so they cannot vote twice
    adjust_list(location, tx['decision_id'], False, address, DB)
    decision=blockchain.db_get(tx['decision_id'], DB)
    difference=decision[yes]-decision[no]
    jury=blockchain.db_get(tx['jury_id'], DB)
    gap=jury['total_coins']*jury['consensus_percent']
    if difference>gap:
        pass_continuation(tx, DB)
    elif -difference>gap or decision['deny']>jury['total_coins']*0.4:
        fail_continuation(tx, DB)
def accept_decision(tx, DB):
    address=addr(tx)
    adjust_int(['amount'], address, -custom.accept_decision_fee, DB)
    def deny_decision(tx, DB):
        adjust_list(['potential_decisions'], tx['jury_id'], True, tx['decision_id'], DB)
        adjust_string(['state'], tx['decision_id'], 'proposed', 'denied', DB)
        adjust_int(['amount'], decision['address'], decision['tip'], DB)
    def accept_decision(tx, DB):
        adjust_list(['decisions'], tx['jury_id'], False, tx['decision_id'], DB)
        adjust_list(['potential_decisions'], tx['jury_id'], True, tx['decision_id'], DB)
        adjust_string(['state'], tx['decision_id'], 'proposed', 'accepted', DB)
        for voter in jury['jury']:#need to update spend to support votecoins in this way
            voter_=blockchain.db_get(voter, DB)
            portion=voter['votecoins'][tx['jury_id']]/jury['total_coins']
            adjust_int(['amount'], voter, portion*decision['tip'], DB)
    simple_vote(tx, DB, 'accept', 'deny', accept_decision, deny_decision)
'''
def jury_vote(tx, DB):
    def fails(tx, DB):
        adjust_list(['decisions'], tx['jury_id'], True, tx['decision_id'], DB)
        adjust_string(['state'], tx['decision_id'], 'accepted', 'no', DB)
    def passes(tx, DB):
        adjust_list(['decisions'], tx['jury_id'], True, tx['decision_id'], DB)
        adjust_string(['state'], tx['decision_id'], 'accepted', 'yes', DB)
    simple_vote(tx, DB, 'yes_result', 'no_result', passes, fails)
def reveal_jury_vote(tx, DB):
    adjust_int(['count'], address, 1, DB)
    pass
def SVD_consensus(tx, DB):
    adjust_int(['count'], address, 1, DB)
    pass
def prediction_market(tx, DB):#also used to increase liquidity of existing market
    adjust_int(['count'], address, 1, DB)
    #liquidity constant
    #has a 'buy_shares' inside of it.
    pass
def buy_shares(tx, DB):
    adjust_int(['count'], address, 1, DB)
    pass
def sell_shares(tx, DB):
    adjust_int(['count'], address, 1, DB)
    pass


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
        'sell_shares':sell_shares}####

#-----------------------------------------
