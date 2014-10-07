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
        tools.kill_processes_using_ports([str(port)])
        time.sleep(2)
        return serve_forever(handler, port, heart_queue)
    s.listen(backlog)
    try:
        while 1:
            serve_once(s, MAX_MESSAGE_SIZE, handler)
    except:
        tools.log('networking error: ' +str(port) + ' ' + str(sys.exc_info()))
def recvall(client, data=''):
    tools.log('recvall 1')
    data+=client.recv(MAX_MESSAGE_SIZE)
    tools.log('recvall 2')
    if not data:
        return 'broken connection'
    tools.log('recvall 3')
    if len(data)<5: return recvall(client, data)
    tools.log('recvall 4')
    try:
        length=int(data[0:5])
        tools.log('length: ' +str(length))
    except:
        return 'no length'
    tools.log('recvall 5: '+str(length))
    tries=0
    data=data[5:]
    tools.log('recvall 6:'+str(data))
    while len(data)<length:
        tools.log('data: ' +str(data))
        d=client.recv(MAX_MESSAGE_SIZE-len(data))
        if not d:
            return 'broken connection'
        data+=d
    tools.log('recvall 7: '+str(data))
    return data

def serve_once(s, size, handler):
    client, address = s.accept()
    data=recvall(client)
    if data=='broken connection':
        print('broken connection')
        return serve_once(s, size, handler)
    if data=='no length':
        print('recieved data that did not start with its length')
        return serve_once(s, size, handler)
    try:
        data=unpackage(data)
    except:
        print('recieved bad data: ' +str(data))
        return serve_once(s, size, handler)
    if data=='stop': return
    data=handler(data)
    data=package(data)
    if data:
        send_msg(data, client)
    client.close() 

def connect_error(msg, host, port, counter):
    if counter>3:
        return({'error':'could not get a response'})
    tools.log('no response from peer')
    tools.log('port: ' +str(port))
    tools.log('host: ' +str(host))
    return(connect(msg, port, host, counter+1))
def send_msg(msg, s):
    msg=tools.package(msg)
    s.send(tools.buffer_(str(len(msg)), 5)+msg)


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
    send_msg(msg, s)
    #ready=select.select([s],[],[], 1)
    #if ready[0]:
    try:
        tools.log('about to try recvall from: '+str(msg))
        data= recvall(s)
        tools.log('data: ' +str(data))
    except:
        return(connect_error(msg, port, host, counter))
    if data=='broken connection':
        print('could not connect')
        return(connect_error(msg, port, host, counter))
    if data=='no length':
        print('should start with length')
        return(connect_error(msg, port, host, counter))
    #else:
    #    return connect_error(msg, host, port, counter)
    data=tools.unpackage(data)
    return(data)
def send_command(peer, msg, response_time=1):
    return connect(msg, peer[1], peer[0])
if __name__ == "__main__":
    serve_forever(lambda x: x, 8000)
