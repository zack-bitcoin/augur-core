""" The easiest way to understand this file is to try it out and have a look at
the html it creates. It creates a very simple page that allows you to spend
money."""
import copy
import tools
import blockchain
import custom
import http
import random

def create_jury(pubkey, privkey, jury_id, DB):
    tx = {'type': 'create_jury', 'vote_id': jury_id}
    easy_add_transaction(tx, privkey, DB)
    
def spend(amount, pubkey, privkey, to_pubkey, DB):
    amount = int(amount * (10 ** 5))
    tx = {'type': 'spend', 'amount': amount, 'to': to_pubkey}
    easy_add_transaction(tx, privkey, DB)

def votecoin_spend(amount, pubkey, privkey, to_pubkey, votecoin_id, DB):
    tx = {'type': 'spend', 'amount': int(amount), 'to': to_pubkey, 'vote_id':votecoin_id}
    easy_add_transaction(tx, privkey, DB)

def ask_decision(pubkey, privkey, votecoin_id, decision_id, txt, DB):
    tx={'type':'propose_decision', 'vote_id':votecoin_id, 'decision_id':decision_id, 'txt':txt}
    easy_add_transaction(tx, privkey, DB)

memoized_votes={}

def vote_on_decision(pubkey, privkey, vote_id, decision_id, answer, DB):
    address=tools.make_address([pubkey], 1)#this might be wrong
    acc=blockchain.db_get(address, DB)
    value=[answer, str(random.random())+str(random.random())]
    answer_hash=tools.det_hash(value)
    memoized_votes[answer_hash]=value
    old_vote='unsure'
    if decision_id in acc['votes']: #this is always False...
        old_vote=acc['votes'][decision_id]
    tx={'type':'jury_vote', 'vote_id':vote_id, 'decision_id':decision_id, 'old_vote':old_vote, 'new_vote':answer_hash}
    easy_add_transaction(tx, privkey, DB)

def easy_add_transaction(tx_orig, privkey, DB):
    tx = copy.deepcopy(tx_orig)
    pubkey = tools.privtopub(privkey)
    address = tools.make_address([pubkey], 1)
    if 'pubkeys' not in tx:
        tx['pubkeys']=[pubkey]
    try:
        tx['count'] = blockchain.count(address, DB)
    except:
        tx['count'] = 1
    tx['signatures'] = [tools.sign(tools.det_hash(tx), privkey)]
    print('CREATED TX: ' + str(tx))
    blockchain.add_tx(tx, DB)

submit_form='''
<form name="first" action="{}" method="{}">
<input type="submit" value="{}">{}
</form> {}
'''
empty_page = '<html><body>{}</body></html>'


def easyForm(link, button_says, more_html='', form_type='post'):
    a = submit_form.format(link, '{}', button_says, more_html, "{}")
    if form_type == 'get':
        return a.format('get', '{}')
    else:
        return a.format('post', '{}')

linkHome = easyForm('/', 'HOME', '', 'get')


def page1(DB, brainwallet=custom.brainwallet):
    out = empty_page
    txt = '<input type="text" name="BrainWallet" value="{}">'
    out = out.format(easyForm('/home', 'Enter BasicCoin wallet passphrase: ', txt.format(brainwallet)))
    return out.format('')


def home(DB, dic):
    if 'BrainWallet' in dic:
        dic['privkey'] = tools.det_hash(dic['BrainWallet'])
    elif 'privkey' not in dic:
        return "<p>You didn't type in your brain wallet.</p>"
    privkey = dic['privkey']
    pubkey = tools.privtopub(dic['privkey'])
    address = tools.make_address([pubkey], 1)
    if 'do' in dic:
        if dic['do'] == 'vote_on_decision':
            vote_on_decision(pubkey, privkey, dic['vote_id'], dic['decision_id'], dic['answer'], DB)
        if dic['do'] == 'ask_decision':
            ask_decision(pubkey, privkey, dic['vote_id'], dic['decision_id'], dic['txt'], DB)
        if dic['do'] == 'create_jury':
            create_jury(pubkey, privkey, dic['jury_id'], DB)
        if dic['do'] == 'spend':
            spend(float(dic['amount']), pubkey, privkey, dic['to'], DB)
        if dic['do'] == 'votecoin_spend':
            votecoin_spend(float(dic['amount']), pubkey, privkey, dic['to'], dic['votecoin_id'], DB)
    out = empty_page
    out = out.format('<p>your address: ' + str(address) + '</p>{}')
    out = out.format('<p>current block: ' + str(DB['length']) + '</p>{}')
    acc = blockchain.db_get(address, DB)
    balance = acc['amount']
    for tx in DB['txs']:
        if tx['type'] == 'spend' and tx['to'] == address and 'vote_id' not in tx:
            balance += tx['amount']
        if tx['type'] == 'spend' and tx['pubkeys'][0] == pubkey:
            if 'vote_id' not in tx:
                balance -= tx['amount']                
            balance -= custom.fee
    out = out.format('<p>current balance is: ' + str(balance/100000.0) + '</p>{}')
    if balance > 0:
        out = out.format(easyForm('/home', 'spend money', '''
        <input type="hidden" name="do" value="spend">
        <input type="text" name="to" value="address to give to">
        <input type="text" name="amount" value="amount to spend">
        <input type="hidden" name="privkey" value="{}">'''.format(privkey)))
        out = out.format(easyForm('/home', 'ask decision', '''
        <input type="hidden" name="do" value="ask_decision">
        <input type="text" name="vote_id" value="name of jury">
        <input type="text" name="decision_id" value="unique title for decision">
        <input type="text" name="txt" value="decision txt">
        <input type="hidden" name="privkey" value="{}">'''.format(privkey)))
    if balance > custom.create_jury_fee:
        out = out.format(easyForm('/home', 'create jury', '''
        <input type="hidden" name="do" value="create_jury">
        <input type="text" name="jury_id" value="name of jury">
        <input type="hidden" name="privkey" value="{}">'''.format(privkey)))
    for pool in acc['votecoin']:
        out = out.format('amount: {} {}'.format(acc['votecoin'][pool], '{}'))
        out = out.format(easyForm('/home', 'spend votecoins: '+str(pool), '''
        <input type="hidden" name="do" value="votecoin_spend">
        <input type="text" name="to" value="address to give to">
        <input type="text" name="amount" value="amount to spend">
        <input type="hidden" name="votecoin_id" value="{}">
        <input type="hidden" name="privkey" value="{}">'''.format(pool, privkey)))
        votecoin_pool=blockchain.db_get(pool, DB)
        for decision in votecoin_pool['decisions']:
            dec=blockchain.db_get(decision, DB)
            out = out.format(easyForm('/home', 'vote on decision: '+str(decision)+' : '+(dec['txt']), '''
            <input type="hidden" name="do" value="vote_on_decision">
            <input type="text" name="answer" value="yes/no/unsure">
            <input type="hidden" name="vote_id" value="{}">
            <input type="hidden" name="decision_id" value="{}">
            <input type="hidden" name="privkey" value="{}">'''.format(pool, decision, privkey)))

    txt='''    <input type="hidden" name="privkey" value="{}">'''
    s = easyForm('/home', 'Refresh', txt.format(privkey))
    return out.format(s)


def hex2htmlPicture(string, size):
    txt = '<img height="{}" src="data:image/png;base64,{}">{}'
    return txt.format(str(size), string, '{}')


def main(port, brain_wallet, db):
    global DB
    DB = db
    http.server(DB, port, page1, home)
