"""This file explains how sockets work for networking."""
import socket
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
            pass

    return data
def sendall(sock, data):
    while data:
        time.sleep(0.1)
        sent = sock.send(data)
        data = data[sent:]
def connect_socket(sock, ip, port):
    tries=0
    while True:
        time.sleep(0.1)
        tries+=1
        if tries>100: return False
        try:
            sock.connect((ip, port))
            return True
        except:
            pass
def serve_forever(PORT, handler):
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tools.kill_processes_using_ports([str(PORT)])
    time.sleep(2)
    server.bind(('127.0.0.1', PORT))
    server.listen(100)
    server.setblocking(0)
    while True:
        try:
            client, addr = server.accept()
            (ip, port) = addr
            data=recvall(client, MAX_MESSAGE_SIZE)
            if type(data)==type('string'):
                data=tools.unpackage(data)
            sendall(client, tools.package(handler(data)))
            client.close()
        except:
            pass
def connect(msg, host, port):
    if len(msg) < 1 or len(msg) > MAX_MESSAGE_SIZE:
        tools.log('wrong sized message')
        return
    s = socket.socket()
    s.setblocking(0)
    try:
        b=connect_socket(s, str(host), int(port))
        if not b: return {'error':'here'}
        msg['version'] = custom.version
        sendall(s, tools.package(msg))
        response=recvall(s, MAX_MESSAGE_SIZE)
        return tools.unpackage(response)
    except Exception as e:
        tools.log('THE ERROR WAS: ' +str(e))
        return {'error': e}
    s.close()

def send_command(peer, msg):
    return connect(msg, peer[0], peer[1])
