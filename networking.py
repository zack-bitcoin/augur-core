import socket, tools, custom, time, sys, select
from json import dumps as package, loads as unpackage
MAX_MESSAGE_SIZE = 60000
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
    time.sleep(1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host,port))
    except:
        tools.kill_processes_using_ports([str(port)])
        time.sleep(2)
        return serve_forever(handler, port, heart_queue)
    s.listen(backlog)
    try:
        while 1:
            serve_once(s, MAX_MESSAGE_SIZE, handler)
    except:
        tools.log('networking error: ' +str(port) + ' ' + str(sys.exc_info()))
def serve_once(s, size, handler):
    client, address = s.accept()
    data = client.recv(size)
    try:
        data=unpackage(data)
    except:
        print('recieved bad data: ' +str(data))
        return serve_once(s, size, handler)
    if data=='stop': return
    data=handler(data)
    data=package(data)
    if data:
        client.send(data)
    client.close() 

def connect_error(msg, host, port, counter):
    if counter>3:
        return({'error':'could not get a response'})
    tools.log('no response from peer')
    tools.log('port: ' +str(port))
    tools.log('host: ' +str(host))
    return(connect(msg, port, host, counter+1))


def connect(msg, port, host='localhost', counter=0):
    #port = 50000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(5)
    try:
        s.connect((host,port))
    except:
        return({'error': 'cannot connect'})
    try:
        msg['version'] = custom.version
    except:
        pass
    s.send(tools.package(msg))
    ready=select.select([s],[],[], 1)
    if ready[0]:
        try:
            data = s.recv(MAX_MESSAGE_SIZE)
        except:
            return(connect_error(msg, port, host, counter))
    else:
        return connect_error(msg, host, port, counter)
    try:
        data=tools.unpackage(data)
    except:
        pass
    return(data)
def send_command(peer, msg, response_time=1):
    return connect(msg, peer[1], peer[0])
