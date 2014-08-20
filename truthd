#!/usr/bin/env python
import networking, sys, tools, custom#, threads

def main():
    info=sys.argv
    peer=['127.0.0.1', custom.truthd_port]
    p={'command':sys.argv[1:]}
    if len(p['command'])==0:
        p['command'].append(' ')
    response=networking.send_command(peer, p, 5)
    if 'error' in response:
        if (response['error'] in ['cannot connect', 'cannot download']) and len(sys.argv)>1 and (sys.argv[1]=='start'):
            print('truthcoin is probably off. Use command: "python threads.py" to turn it on')
            #threads.main()
            sys.exit(1)
    return(response)
        
print(main())
