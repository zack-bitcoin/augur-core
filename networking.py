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
    #ready=select.select([client],[],[], 1)
    #if not ready[0]:
    try:
        data+=client.recv(MAX_MESSAGE_SIZE)
    except:
        time.sleep(0.1)
        tools.log('not ready')
        recvall(client, data)        
    if not data:
        return 'broken connection'
    if len(data)<5: return recvall(client, data)
    try:
        length=int(data[0:5])
    except:
        return 'no length'
    tries=0
    data=data[5:]
    while len(data)<length:
        d=client.recv(MAX_MESSAGE_SIZE-len(data))
        if not d:
            return 'broken connection'
        data+=d
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
def send_msg(data, sock):
    data=tools.package(data)
    data=tools.buffer_(str(len(data)), 5)+data
    while data:
        time.sleep(0.1)
        sent = sock.send(data)
        data = data[sent:]

def connect(msg, port, host='localhost', counter=0):
    #port = 50000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(5)
    try:
        s.connect((host,port))
    except:
        return({'error': 'cannot connect '+str(host) + ' ' +str(port)})
    try:
        msg['version'] = custom.version
    except:
        pass
    send_msg(msg, s)
    data= recvall(s)
    if data=='broken connection':
        print('could not connect')
        return(connect_error(msg, port, host, counter))
    if data=='no length':
        print('should start with length')
        return(connect_error(msg, port, host, counter))
    data=tools.unpackage(data)
    return(data)
def send_command(peer, msg, response_time=1):
    return connect(msg, peer[1], peer[0])
if __name__ == "__main__":
    serve_forever(lambda x: x, 8000)
