#!/usr/bin/env python
import networking, sys, tools, custom#, threads

def build_buy_shares():
    tx={'type':'buy_shares', 'PM_id':str(raw_input('What is the unique name for this prediction market?'))}
    num_states=int(raw_input('how many states does this pm have?'))
    tx['buy']=[]
    for i in range(num_states):
        tx['buy'].append(int(raw_input('how many shares do you want to buy of state '+str(i)+'? To sell states, use negative numbers.')))
    return tx
def build_pm():
    tx={'type':'prediction_market', 'fees':0}
    pubkey=str(raw_input('What is the address or pubkey of the owner of the PM?'))
    if len(pubkey)>40:
        tx['owner']=tools.make_address([pubkey], 1)
    else:
        tx['owner']=address
    tx['PM_id']=str(raw_input('What is the unique name for this new prediction market?\n'))
    tx['B']=int(raw_input('how big should B be? Initial investment is B*ln(n) where n is the number of states'))
    num_decisions=int(raw_input('how many decisions is this prediction market to be based upon?'))
    tx['decisions']=[]
    for i in range(num_decisions):
        tx['decisions'].append(str(raw_input('What is the unique name of the '+str(i)+' decision?')))
    num_states=int(raw_input('how many states can this PM result in?'))
    if num_states>2**num_decisions: 
        print('too many states')
        return False
    tx['states_combinatory']=[]
    tx['states']=[]
    for i in range(num_states):
        tx['states'].append(str(raw_input('what is the text title of the '+str(i)+' state?')))
        if i!=num_states-1:
            next_comb=(str(raw_input('how does the '+str(i)+' state depend upon the outcome of the decisions? For example: if there are 2 decisions, and this market only comes true when the first is "yes" and the second is "no", then you would put: "1 0" here.')))
            tx['states_combinatory'].append(map(int, next_comb.split(' ')))
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
def run_command(p):
    peer=['127.0.0.1', custom.truthd_port]
    response=networking.send_command(peer, p, 5)
    if tools.can_unpack(response):
        response=tools.unpackage(response)
    if type(response)==type({'a':1}) and 'error' in response:
        print('response was: ' +str(response))
        print('truthcoin is probably off. Use command: "python threads.py" to turn it on. (you may need to reboot it a couple times to get it working)')
    else:
        print(response)

main()

