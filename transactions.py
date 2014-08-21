"""This file explains how we tell if a transaction is valid or not, it explains
how we update the database when new transactions are added to the blockchain."""
import blockchain, custom, copy, tools, txs_tools
import txs_truthcoin as tt
E_check=tools.E_check
def spend_verify(tx, txs, DB):
    def sigs_match(sigs, pubs, msg):
        return all(tools.verify(msg, sig, pub) for sig in sigs for pub in pubs)
    tx_copy = copy.deepcopy(tx)
    tx_copy_2 = copy.deepcopy(tx)
    if not E_check(tx, 'to', [str, unicode]):
        tools.log('no to')
        return False
    if len(tx['to'])<=30:
        tools.log('that address is too short')
        tools.log('tx: ' +str(tx))
        return False
    if not E_check(tx, 'signatures', list):
        tools.log('no signautres')
        return False
    if not E_check(tx, 'pubkeys', list):
        tools.log('no pubkeys')
        return False
    if not E_check(tx, 'amount', int):
        tools.log('no amount')
        return False
    tx_copy.pop('signatures')
    if len(tx['pubkeys']) == 0:
        tools.log('pubkey error')
        return False
    if len(tx['signatures']) > len(tx['pubkeys']):
        tools.log('sigs too long')
        return False
    msg = tools.det_hash(tx_copy)
    if not sigs_match(copy.deepcopy(tx['signatures']),
                      copy.deepcopy(tx['pubkeys']), msg):
        tools.log('sigs do not match')
        return False
    if not txs_tools.fee_check(tx, txs, DB):
        tools.log('fee check error')
        return False
    return True
def mint_verify(tx, txs, DB):
    return 0 == len(filter(lambda t: t['type'] == 'mint', txs))
tx_check = {'spend':spend_verify,
            'mint':mint_verify,
            'create_jury':tt.create_jury_check,
            'propose_decision':tt.propose_decision_check,
            'jury_vote':tt.jury_vote_check,
            'reveal_jury_vote':tt.reveal_jury_vote_check,
            'SVD_consensus':tt.SVD_consensus_check,
            'prediction_market':tt.prediction_market_check,
            'buy_shares':tt.buy_shares_check,
            'collect_winnings':tt.collect_winnings_check}
#------------------------------------------------------
adjust_int=txs_tools.adjust_int
adjust_dict=txs_tools.adjust_dict
adjust_list=txs_tools.adjust_list
symmetric_put=txs_tools.symmetric_put
def mint(tx, DB):
    address = tools.addr(tx)
    adjust_int(['amount'], address, custom.block_reward, DB)
    adjust_int(['count'], address, 1, DB)
def spend(tx, DB):
    def initialize_to_zero_helper(loc, address, DB):
        acc=tools.db_get(address, DB)
        if loc[1] not in acc[loc[0]]:
            acc[loc[0]][loc[1]]=0
            tools.db_put(address , acc, DB)    
    def initialize_to_zero_votecoin(vote_id, address, DB):
        initialize_to_zero_helper(['votecoin', vote_id], address, DB)
        if address not in tools.db_get(vote_id, DB)['members']:
            adjust_list(['members'], vote_id, False, address, DB)
    def memory_leak_helper(loc, address, DB):
        acc=tools.db_get(address, DB)
        bool_=txs_tools.get_(loc, acc)==0
        if bool_:
            adjust_dict(loc, address, True, {loc[-1]: 0}, DB)
        return bool_
    def memory_leak_votecoin(vote_id, address, DB):
        bool_=memory_leak_helper(['votecoin', vote_id], address, DB)
        if bool_:
            adjust_list(['members'], vote_id, True, address, DB)
    address = tools.addr(tx)
    if 'vote_id' in tx:
        initialize_to_zero_votecoin(tx['vote_id'], address, DB)
        initialize_to_zero_votecoin(tx['vote_id'], tx['to'], DB)
        adjust_int(['votecoin', tx['vote_id']], address, -tx['amount'], DB)
        adjust_int(['votecoin', tx['vote_id']], tx['to'], tx['amount'], DB)
        memory_leak_votecoin(tx['vote_id'], address, DB)#this should get rid of any zeros in the jury so we don't leak memory.
        memory_leak_votecoin(tx['vote_id'], tx['to'], DB)#this should get rid of any zeros in the jury so we don't leak memory.
    else:
        adjust_int(['amount'], address, -tx['amount'], DB)
        adjust_int(['amount'], tx['to'], tx['amount'], DB)
    adjust_int(['amount'], address, -custom.fee, DB)
    adjust_int(['count'], address, 1, DB)
update = {'mint':mint,
          'spend':spend,
          'create_jury':tt.create_jury,
          'propose_decision':tt.propose_decision,
          'jury_vote':tt.jury_vote,
          'reveal_jury_vote':tt.reveal_jury_vote,
          'SVD_consensus':tt.SVD_consensus,
          'prediction_market':tt.prediction_market,
          'buy_shares':tt.buy_shares,
          'collect_winnings':tt.collect_winnings}
