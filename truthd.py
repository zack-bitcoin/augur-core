#!/usr/bin/env python
import networking, sys, tools, custom#, threads

def main():
    info=sys.argv
    p={'command':sys.argv[1:]}
    if len(p['command'])==0:
        p['command'].append(' ')
    if p['command'][0]=='make_PM':
        print('PM')
        #build up PM question by question
    elif p['command'][0]=='buy_shares':
        print('Buy shares')
        #build up buy_shares question by question
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

