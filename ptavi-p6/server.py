#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import os
import socketserver
import sys


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):
        while 1:
            okinv = ("SIP/2.0 100 Trying\r\n\r\n" +
                     "SIP/2.0 180 Ringing\r\n\r\n" + "SIP/2.0 200 OK\r\n\r\n")
            line = self.rfile.read()
            dcline = line.decode('utf-8').split(' ')
            print(line.decode('utf-8'))
            if str(dcline[0]) != '':
                if ('sip:' not in dcline[1] or '@' not in dcline[1] or
                   dcline[2] != 'SIP/2.0\r\n\r\n'):
                    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")

                else:
                    if dcline[0] == 'INVITE':
                        self.wfile.write(bytes(okinv, 'utf-8'))

                    elif dcline[0] == 'ACK':
                        os.system('./mp32rtp -i 127.0.0.1 -p 23032 < ' +
                                  sys.argv[3])

                    elif dcline[0] == 'BYE':
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")

                    else:
                        self.wfile.write(bytes("SIP/2.0 405 Method Not " +
                                               "Allowed\r\n\r\n", 'utf-8'))

            if not line:
                break

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Usage: python3 server.py IP port audio_file")

    serv = socketserver.UDPServer((sys.argv[1], int(sys.argv[2])), EchoHandler)
    print("Listening...")
    serv.serve_forever()
