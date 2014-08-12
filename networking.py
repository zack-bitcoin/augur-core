"""This file explains how sockets work for networking."""
import socket
import subprocess
import re
import tools
import custom
import time
MAX_MESSAGE_SIZE = 60000


def kill_processes_using_ports(ports):
    popen = subprocess.Popen(['netstat', '-lpn'],
                             shell=False,
                             stdout=subprocess.PIPE)
    (data, err) = popen.communicate()
    pattern = "^tcp.*((?:{0})).* (?P<pid>[0-9]*)/.*$"
    pattern = pattern.format(')|(?:'.join(ports))
    prog = re.compile(pattern)
    for line in data.split('\n'):
        match = re.match(prog, line)
        if match:
            pid = match.group('pid')
            subprocess.Popen(['kill', '-9', pid])

def can_unpack(o):
    try:
        tools.unpackage(o)
        return True
    except:
        return False

def serve_forever(message_handler_func, PORT, queue):
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', PORT))
    #server.listen(100)
    server.setblocking(0)
    while True:
        time.sleep(0.1)
        data=''
        flag=True
        try:
            client, addr = server.accept()
        except:
            flag=False
        if flag:
            tools.log('heard peer!')
            (ip, port) = addr
            while not can_unpack(data):
                time.sleep(0.1)
                data = client.recv(MAX_MESSAGE_SIZE)
                if len(response) == 0:
                    error('peer disconnected')
                    #we could insert security checks here
                tools.log('serve forever recieved: ' +str(data))
            data = tools.unpackage(data)
            client.sendall(tools.package(message_handler_func(data, queue)))

'''old
def serve_forever(message_handler_func, PORT, queue):
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', PORT))
    server.listen(100)
    while True:
        time.sleep(0.1)
        client, addr = server.accept()
        (ip, port) = addr
        data = client.recv(MAX_MESSAGE_SIZE)
        #we could insert security checks here
        data = tools.unpackage(data)
        client.sendall(tools.package(message_handler_func(data, queue)))
'''

def connect(msg, host, port):
    #tools.log('attempting to connect')
    if len(msg) < 1 or len(msg) > MAX_MESSAGE_SIZE:
        tools.log('wrong sized message')
        return
    s = socket.socket()
    s.setblocking(0)
    try:
        #s.settimeout(2)
        #tools.log('how far1')
        s.connect((str(host), int(port)))
        tools.log('how far2')
        msg['version'] = custom.version
        tools.log('how far3')
        s.sendall(tools.package(msg))
        tools.log('how far4')
        response = ''
        while not can_unpack(response):
            tools.log('in send message loop')
            time.sleep(0.1)
            response = s.recv(MAX_MESSAGE_SIZE)
            if len(response) == 0:
                error('peer disconnected')
        #print(response)
        return tools.unpackage(response)
    except Exception as e:
        #print('THE ERROR WAS: ' +str(e))
        #print('disconnect')
        return {'error': e}


def send_command(peer, msg):
    return connect(msg, peer[0], peer[1])
