#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente UDP que abre un socket a un servidor
"""
import socket
import sys

# Cogemos las variables del puerto, servidor y el tipo de mensaje a enviar
SERVER = sys.argv[1]
PORT = int(sys.argv[2])
LINE = sys.argv[3]

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    if len(sys.argv) != 6:
        sys.exit('Usage: client.py ip puerto' +
                 'register sip_address expires_value')

    my_socket.connect((SERVER, PORT))
    if LINE == 'register':
        line = 'REGISTER sip:' + sys.argv[4] + ' SIP/2.0\r\n'
        expr = 'Expires: ' + sys.argv[5] + ' \r\n'
        my_socket.send(bytes(line + expr, 'utf-8') + b'\r\n')
    else:
        sys.exit()

    data = my_socket.recv(1024)
    print(data.decode('utf-8'))

print('Socket terminado.')
