"""This file explains how we tell if a transaction is valid or not, it explains
how we update the database when new transactions are added to the blockchain."""
import blockchain, custom, copy, tools, txs_tools
import txs_truthcoin as tt
E_check=tools.E_check
def sigs_match(Sigs, Pubs, msg):
    pubs=copy.deepcopy(Pubs)
    sigs=copy.deepcopy(Sigs)
    def match(sig, pubs, msg):
        for p in pubs:
            if tools.verify(msg, sig, p):
                return {'bool':True, 'pub':p}
        return {'bool':False}
    for sig in sigs:
        a=match(sig, pubs, msg)
        if not a['bool']:
            return False
        sigs.remove(sig)
        pubs.remove(a['pub'])
    return True
def signature_check(tx):
    tx_copy = copy.deepcopy(tx)
    if not E_check(tx, 'signatures', list):
        tools.log('no signautres')
        return False
    if not E_check(tx, 'pubkeys', list):
        tools.log('no pubkeys')
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
    return True

def spend_verify(tx, txs, out, DB):
    if not E_check(tx, 'to', [str, unicode]):
        out[0]+='no to'
        return False
    if not signature_check(tx):
        out[0]+='signature check'
        return False
    if len(tx['to'])<=30:
        out[0]+='that address is too short'
        out[0]+='tx: ' +str(tx)
        return False
    if not E_check(tx, 'amount', int):
        out[0]+='no amount'
        return False
    if not txs_tools.fee_check(tx, txs, DB):
        out[0]+='fee check error'
        return False
    if 'vote_id' in tx:
        if not tx['to'][:-29]=='11':
            out[0]+='cannot hold votecoins in a multisig address'
            return False
    return True
def mint_verify(tx, txs, out, DB):
    return 0 == len(filter(lambda t: t['type'] == 'mint', txs))
tx_check = {'spend':spend_verify,
            'mint':mint_verify,
            'create_jury':tt.create_jury_check,
            'propose_decision':tt.propose_decision_check,
            'jury_vote':tt.jury_vote_check,
            'slasher_jury_vote':tt.slasher_jury_vote_check,
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
    address = tools.addr(tx)
    if 'vote_id' in tx:
        txs_tools.initialize_to_zero_votecoin(tx['vote_id'], address, DB)
        txs_tools.initialize_to_zero_votecoin(tx['vote_id'], tx['to'], DB)
        adjust_int(['votecoin', tx['vote_id']], address, -tx['amount'], DB)
        adjust_int(['votecoin', tx['vote_id']], tx['to'], tx['amount'], DB)
        txs_tools.memory_leak_votecoin(tx['vote_id'], address, DB)#this should get rid of any zeros in the jury so we don't leak memory.
        txs_tools.memory_leak_votecoin(tx['vote_id'], tx['to'], DB)#this should get rid of any zeros in the jury so we don't leak memory.
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
          'slasher_jury_vote':tt.slasher_jury_vote,
          'SVD_consensus':tt.SVD_consensus,
          'prediction_market':tt.prediction_market,
          'buy_shares':tt.buy_shares,
          'collect_winnings':tt.collect_winnings}
