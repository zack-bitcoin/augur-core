#!/usr/bin/env python
import networking, sys, tools, custom#, threads

def main():
    info=sys.argv
    p={'command':sys.argv[1:]}
    if len(p['command'])==0:
        p['command'].append(' ')
    c=p['command']
    if c[0]=='make_PM':
        print('PM')
        #build up PM question by question
    elif c[0]=='buy_shares':
        print('Buy shares')
        #build up buy_shares question by question
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

