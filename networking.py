import socket, tools, custom, time, sys
from json import dumps as package, loads as unpackage

def serve_forever(handler, port, heart_queue='default', external=False):
    if heart_queue=='default':
        import Queue
        heart_queue=Queue.Queue()
    if external:
        host='0.0.0.0'
    else:
        host = 'localhost'
    #port = 50000
    backlog = 5
    size = 1024
    time.sleep(1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host,port))
    except:
        tools.kill_processes_using_ports([str(port)])
        time.sleep(2)
        return serve_forever(handler, port, heart_queue)
    s.listen(backlog)
    while 1:
        heart_queue.put('server: '+str(port))
        client, address = s.accept()
        data = client.recv(size)
        data=unpackage(data)
        data=handler(data)
        data=package(data)
        if data:
            client.send(data)
        client.close() 
def connect(msg, port, host='localhost'):
    #port = 50000
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host,port))
    except:
        return({'error': 'cannot connect'})
    try:
        msg['version'] = custom.version
    except:
        pass
    s.send(tools.package(msg))
    try:
        data = s.recv(size)
    except:
        tools.log('no response from peer')
        return(connect(msg, port, host))
    try:
        data=tools.unpackage(data)
    except:
        pass
    return(data)
def send_command(peer, msg, response_time=1):
    return connect(msg, peer[1], peer[0])
