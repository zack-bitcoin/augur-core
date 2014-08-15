"""This file explains how sockets work for networking."""
import socket
import subprocess
import re
import tools
import custom
import time
import sys
MAX_MESSAGE_SIZE = 60000


def recvall(sock, max_size):
    data = ''
    while not tools.can_unpack(data):
        time.sleep(0.1)
        try:
            d=sock.recv(max_size - len(data))
            if not d:
                #connection broken
                return {'recvall error':data}
            data += d
        except:
            tools.log("error: " + str(sys.exc_info()[0]))
            tools.log("error: " + str(sys.exc_info()[1]))
            tools.log("error: " + str(sys.exc_info()[2]))
            pass

    return data
def sendall(sock, data):
    while data:
        time.sleep(0.1)
        sent = sock.send(data)
        data = data[sent:]

#def test_handler_func(data, DB):
#    return str(data)+str(data)+str(data)
#def test_server():
#    kill_processes_using_ports([str(8700)])
#    serve_forever(test_handler_func, 8700, {})
#def connect_socket(sock, ip, port):
#    while True:
#        try:
#            sock.connect((ip, port))
#            return 
#        except:
#            tools.log("error in connect_socket: " + str(sys.exc_info()#[0]))
#            pass
def test_connect():
    s = socket.socket()
    s.setblocking(0)
    connect_socket(s, '127.0.0.1', 8700)
    tools.log('connecting')
    sendall(s, tools.package('123456790'*100))
    tools.log('connected')
    response=recvall(s, 100000)
    return response

def serve_forever(peers_queue, PORT):
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tools.kill_processes_using_ports([str(PORT)])
    server.bind(('127.0.0.1', PORT))
    server.listen(100)
    server.setblocking(0)
    while True:
        flag=True
        try:
            client, addr = server.accept()
        except:
            flag=False
        if flag:
            tools.log('heard peer!')
            (ip, port) = addr
            peers_queue.put(client)
def connect(msg, host, port):
    #tools.log('attempting to connect')
    if len(msg) < 1 or len(msg) > MAX_MESSAGE_SIZE:
        tools.log('wrong sized message')
        return
    s = socket.socket()
    s.setblocking(0)
    try:
        #s.settimeout(2)
        tools.log('how far1 '+str(host)+' '+str(port))
        s.connect((str(host), int(port)))
        tools.log('how far2')
        msg['version'] = custom.version
        tools.log('how far3')
        sendall(s, tools.package(msg))
        #s.sendall(tools.package(msg))
        tools.log('how far4')
        response=recvall(s, MAX_MESSAGE_SIZE)
         return tools.unpackage(response)
    except Exception as e:
        tools.log('THE ERROR WAS: ' +str(e))
        #print('disconnect')
        return {'error': e}

def send_command(peer, msg):
    return connect(msg, peer[0], peer[1])
