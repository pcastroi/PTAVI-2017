#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys

# Compruebo los argumentos de entrada
if len(sys.argv) != 3:
    sys.exit("Usage: python3 client.py method receiver@IP:SIPport")

# Contenido que vamos a enviar
METHOD = sys.argv[1]
MLOGIN = sys.argv[2][:sys.argv[2].find('@')]
MSERVER = sys.argv[2][sys.argv[2].find('@') + 1: sys.argv[2].find(':')]
MPORT = sys.argv[2][sys.argv[2].rfind(':') + 1:]

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:

    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((MSERVER, int(MPORT)))

    Msend = 'sip:' + MLOGIN + '@' + MSERVER + ' SIP/2.0\r\n'
    my_socket.send(bytes(METHOD + ' ' + Msend, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print(data.decode('utf-8'))

    if data.decode('utf-8').split()[1] == "100":
        my_socket.send(bytes("ACK" + ' ' + Msend, 'utf-8') + b'\r\n')
    print("Conection finished.")
