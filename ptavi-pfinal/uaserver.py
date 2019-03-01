#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Clase (y programa principal) para un servidor de eco en UDP simple
'''

import os
import socket
import socketserver
import sys
import uaclient


class SHandler(socketserver.DatagramRequestHandler):
    '''
    Echo server class
    '''
    def handle(self):

        DATOS = []
        DATAXML = uaclient.parser_xml(sys.argv[1])
        DATAXML[1]['ip'] = '127.0.0.1'
        for line in self.rfile:
            DATOS.append(line.decode('utf-8'))
        uaclient.CLog('Received from ' + DATAXML[3]['ip'] +
                      ':' + DATAXML[3]['puerto'] + ': ' +
                      '\r\n'.join(DATOS), DATAXML[4]['path'])
        if DATOS[0].split(' ')[0] == 'INVITE':
            msend = ('SIP/2.0 100 Trying\r\n\r\n' +
                     'SIP/2.0 180 Ringing\r\n\r\n' + 'SIP/2.0 200 OK\r\n\r\n' +
                     'Content-Type: application/sdp\r\n\r\n' + 'v=0\r\n' +
                     'o=' + DATAXML[0]['username'] + ' ' + DATAXML[1]['ip'] +
                     '\r\n' + 's=mysession\r\n' + 't=0\r\n' + 'm=audio ' +
                     str(DATAXML[2]['puerto']) + ' RTP\r\n')
            uaclient.CLog('Sent to ' + DATAXML[3]['ip'] + ':' +
                          DATAXML[3]['puerto'] + ': ' +
                          msend, DATAXML[4]['path'])
            self.wfile.write(bytes(msend, 'utf-8'))
        elif DATOS[0].split(' ')[0] == 'ACK':
            os.system('./mp32rtp -i ' + DATAXML[1]['ip'] + ' -p ' +
                      DATAXML[2]['puerto'] + ' < ' + DATAXML[5]['path'])
        elif DATOS[0].split(' ')[0] == 'BYE':
            msend = 'SIP/2.0 200 OK\r\n\r\n'
            uaclient.CLog('Sent to ' + DATAXML[3]['ip'] + ':' +
                          DATAXML[3]['puerto'] + ': ' +
                          msend, DATAXML[4]['path'])
            self.wfile.write(bytes(msend, 'utf-8'))

if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.exit('Usage: python3 uaserver.py config')
    DATAXML = uaclient.parser_xml(sys.argv[1])
    DATAXML[1]['ip'] = '127.0.0.1'
    PORT = DATAXML[1]['puerto']
    uaclient.CLog('Starting...', DATAXML[4]['path'])
    try:
        serv = socketserver.UDPServer((DATAXML[1]['ip'], int(PORT)), SHandler)
        print('Listening...')
        serv.serve_forever()
    except KeyboardInterrupt:
        uaclient.CLog('Finishing.', DATAXML[4]['path'])
        print('Finalizado uaserver')
