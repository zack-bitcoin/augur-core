#!/usr/bin/env python
import networking, sys, tools, custom, os, multiprocessing, threads, txs_tools, truthcoin_api, blockchain

def daemonize(f):
    pid=os.fork()
    if pid==0: f()
    else: sys.exit(0)
def get_address(tx):
    pubkey=str(raw_input('What is your address or pubkey\n>'))
    if len(pubkey)>40:
        out=tools.make_address([pubkey], 1)
    else:
        out=pubkey    
    return tx
def build_buy_shares():
    tx={'type':'buy_shares', 'PM_id':str(raw_input('What is the unique name for this prediction market?\n>'))}
    num_states=int(raw_input('how many states does this pm have?\n>'))
    tx['buy']=[]
    for i in range(num_states):
        tx['buy'].append(int(raw_input('how many shares do you want to buy of state '+str(i)+'? To sell states, use negative numbers.\n>')))
    brainwallet=str(raw_input('What is your brainwallet\n>'))
    privkey=tools.det_hash(brainwallet)
    pubkey=tools.privtopub(privkey)
    address=tools.make_address([pubkey], 1)
    tx['pubkeys']=[pubkey]
    tx['count'] = tools.count(address, {})
    cost=txs_tools.cost_to_buy_shares(tx)
    tx['price_limit']=int(cost*1.01)
    print('now for a little proof of work. This may take several minutes. The purpose of this pow is to make it more difficult for a front runner to steal your trade.')
    tx=tools.unpackage(tools.package(tx))
    tx=tools.POW(tx)
    tx['signatures']=[tools.sign(tools.det_hash(tx), privkey)]
    print('tx for copy/pasting into pushtx: '+tools.package(tx).encode('base64'))
    return tx
def build_pm():
    tx={'type':'prediction_market', 'fees':0}
    pubkey=str(raw_input('What is the address or pubkey of the owner of the PM?\n>'))
    if len(pubkey)>40:
        tx['owner']=tools.make_address([pubkey], 1)
    else:
        tx['owner']=pubkey
    tx['PM_id']=str(raw_input('What is the unique name for this new prediction market?\n>'))
    tx['B']=int(raw_input('how big should B be? Initial investment is B*ln(n) where n is the number of states\n>'))
    num_decisions=int(raw_input('how many decisions is this prediction market to be based upon?\n>'))
    tx['decisions']=[]
    for i in range(num_decisions):
        tx['decisions'].append(str(raw_input('What is the unique name of the '+str(i)+' decision?\n>')))
    num_states=int(raw_input('how many states can this PM result in?\n>'))
    if num_states>2**num_decisions: 
        print('too many states')
        return False
    tx['states_combinatory']=[]
    tx['states']=[]
    for i in range(num_states):
        tx['states'].append(str(raw_input('what is the text title of the '+str(i)+' state?\n>')))
        if i!=num_states-1:
            next_comb=(str(raw_input('how does the '+str(i)+' state depend upon the outcome of the decisions? For example: if there are 2 decisions, and this market only comes true when the first is "yes" and the second is "no", then you would put: "1 0" here.\n>')))
            tx['states_combinatory'].append(map(int, next_comb.split(' ')))
    print('tx for copy/pasting into pushtx: '+tools.package(tx).encode('base64'))
    return tx
def main():
    info=sys.argv
    p={'command':sys.argv[1:]}
    if len(p['command'])==0:
        p['command'].append(' ')
    c=p['command']
    if c[0]=='make_PM':
        tx=build_pm()
        run_command({'command':['pushtx', tools.package(tx).encode('base64')]})
    elif c[0]=='buy_shares':
        tx=build_buy_shares()
        run_command({'command':['pushtx', tools.package(tx).encode('base64')]})
    elif c[0]=='start':
        r=connect({'command':'blockcount'})
        if is_truthcoin_off(r):
            p=raw_input('what is your password?\n')
            daemonize(lambda: threads.main(p))
        else:
            print('truthcoin is already running')
    elif c[0]=='new_address':
        if len(c)<2:
            print('what is your brain wallet? not enough inputs.')
        else:
            privkey=tools.det_hash(c[1])
            pubkey=tools.privtopub(privkey)
            address=tools.make_address([pubkey], 1)
            print('brain: ' +str(c[1]))
            print('privkey: ' +str(privkey))
            print('pubkey: ' +str(pubkey))
            print('address: ' +str(address))
    else:
        run_command(p)
def connect(p):
    peer=['localhost', custom.api_port]
    response=networking.send_command(peer, p, 5)
    if tools.can_unpack(response):
        response=tools.unpackage(response)
    return response
def is_truthcoin_off(response): return type(response)==type({'a':1}) and 'error' in response
def run_command(p):
    response=connect(p)
    if is_truthcoin_off(response):
        print('response was: ' +str(response))
        print('truthcoin is probably off. Use command: "./truth_cli.py start" to turn it on.')
    else:
        print(response)

main()

