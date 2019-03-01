#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Programa User Agent Client
'''

import hashlib
import os
import socket
import sys
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class XMLHandler(ContentHandler):  # Clase para leer el xml

    def __init__(self):
        '''
        Constructor. Inicializamos las variables
        '''
        self.tags = []
        self.list_tags = ['account', 'uaserver', 'rtpaudio',
                          'regproxy', 'log', 'audio']
        self.dict_attrs = {'account': ['username', 'passwd'],
                           'uaserver': ['ip', 'puerto'],
                           'rtpaudio': ['puerto'],
                           'regproxy': ['ip', 'puerto'],
                           'log': ['path'],
                           'audio': ['path']}

    def startElement(self, name, attrs):
        '''
        Método de inicio
        '''

        if name in self.list_tags:
            diccionario = {}
            diccionario['tag'] = name
            for atributo in self.dict_attrs[name]:
                diccionario[atributo] = attrs.get(atributo, '')
            self.tags.append(diccionario)

    def get_tags(self):
        '''
        Devuelve la lista
        '''
        return self.tags


def parser_xml(fxml):
    '''
    Función que dado un fichero xml, devuelve una lista de diccionarios
    '''
    parser = make_parser()
    handxml = XMLHandler()
    parser.setContentHandler(handxml)
    parser.parse(open(fxml))
    return (handxml.get_tags())


def CLog(data, log):
    '''
    Función que crea el log
    '''
    timenow = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
    flog = open(log, 'a')
    data = data.replace('\r\n', ' ')
    flog.write(timenow + ' ' + data + '\r\n')
    flog.close()


def ClientRegister(data):
    '''
    Funcion para Register: Asumimos que el valor de option es
    un Expires correcto, devuelve el mensaje que se envía para
    reusarlo en la autorización
    '''
    try:
        int(sys.argv[3])
    except ValueError:
        sys.exit('Usage: python3 uaclient.py config method option')
        CLog('Finishing.', data[4]['path'])
    msend = ('REGISTER' + ' sip:' + data[0]['username'] +
             ':' + data[1]['puerto'] + ' SIP/2.0\r\n' +
             'Expires: ' + sys.argv[3] + '\r\n')
    CLog('Sent to ' + data[3]['ip'] + ':' + data[3]['puerto'] +
         ': ' + msend, data[4]['path'])
    my_socket.send(bytes(msend, 'utf-8') + b'\r\n')
    try:
        datarec = my_socket.recv(1024).decode('utf-8')
        dataline = datarec.split('\r\n')
        CLog('Received from ' + data[3]['ip'] + ':' + data[3]['puerto'] +
             ': ' + datarec, data[4]['path'])
        # Autorización del cliente
        if dataline[0].split(' ')[1] == '401':
            nonce = dataline[1].split('=')[1][1:-1]
            h = hashlib.sha1(bytes(data[0]['passwd'], 'utf-8'))
            h.update(bytes(nonce, 'utf-8'))
            msend = (msend + '\r\n' + 'Authorization: Digest response="' +
                     h.hexdigest() + '"\r\n\r\n')
            my_socket.send(bytes(msend, 'utf-8') + b'\r\n')
            CLog('Sent to ' + data[3]['ip'] + ':' + data[3]['puerto'] +
                 ': ' + msend, data[4]['path'])
            data2 = my_socket.recv(1024).decode('utf-8')
            dataline2 = data2.split('\r\n')
            CLog('Received from ' + data[3]['ip'] + ':' +
                 data[3]['puerto'] + ': ' + data2, data[4]['path'])
            CLog('Finishing.', data[4]['path'])
    # Este error deberia salir al intentar conectar un ua
    # con el servidor proxy apagado.
    except ConnectionRefusedError:
        CLog('Error: No server listening at ' + data[3]['ip'] + ' port ' +
             data[3]['puerto'], data[4]['path'])
        CLog('Finishing.', data[4]['path'])


def ClientInvite(data, receiver):
    '''
    Funcion para Invite: el valor de option se comprueba en el proxy(error 404)
    '''
    msend = ('INVITE' + ' sip:' + receiver + ' SIP/2.0\r\n' +
             'Content-Type: application/sdp\r\n\r\n' + 'v=0\r\n' +
             'o=' + data[0]['username'] + ' ' + data[1]['ip'] +
             '\r\n' + 's=mysession\r\n' + 't=0\r\n' + 'm=audio ' +
             data[2]['puerto'] + ' RTP\r\n')
    CLog('Sent to ' + data[3]['ip'] + ':' + data[3]['puerto'] +
         ': ' + msend, data[4]['path'])
    my_socket.send(bytes(msend, 'utf-8') + b'\r\n')
    datarec = my_socket.recv(1024).decode('utf-8')
    CLog('Received from ' + data[3]['ip'] + ':' +
         data[3]['puerto'] + ': ' + datarec, data[4]['path'])
    dataline = datarec.split('\r\n')
    # recibo el 100, 180, 200 y sdp. Mando el ACK
    if dataline[0].split(' ')[1] == '100':
        my_socket.send(bytes('ACK sip:' + receiver +
                             ' SIP/2.0\r\n', 'utf-8') + b'\r\n')
        CLog('Sent to ' + data[3]['ip'] + ':' + data[3]['puerto'] +
             ': ' + 'ACK sip:' + receiver + ' SIP/2.0\r\n', data[4]['path'])
        # Una vez mandado el Ack, mando los datos RTP
        os.system('./mp32rtp -i ' + data[1]['ip'] + ' -p ' +
                  data[2]['puerto'] + ' < ' + data[5]['path'])
    busca404 = dataline[0].split(' ')[1] == '404'
    if busca404 or dataline[0].split(' ')[1] == '400':
        CLog('Error: ' + datarec, data[4]['path'])
        CLog('Finishing.', data[4]['path'])


def ClientBye(data, receiver):
    '''
    Funcion para Bye: comprueba que el parámetro introducido es el correcto
    '''
    if '@' not in receiver or '.com' not in receiver:
        CLog('Finishing.', data[4]['path'])
    else:
        try:
            my_socket.send(bytes('BYE sip:' + receiver +
                                 ' SIP/2.0\r\n', 'utf-8') + b'\r\n')
            CLog('Sent to ' + data[3]['ip'] + ':' + data[3]['puerto'] +
                 ': ' + 'BYE sip:' + receiver +
                 ' SIP/2.0\r\n', data[4]['path'])
            # recibo el ok
            datarec = my_socket.recv(1024).decode('utf-8')
            CLog('Received from ' + data[3]['ip'] + ':' +
                 data[3]['puerto'] + ': ' + datarec, data[4]['path'])
            dataline = datarec.split('\r\n')
        except ConnectionRefusedError:
            CLog('Error: No server listening at ' + data[3]['ip'] +
                 ' port ' + data[3]['puerto'], data[4]['path'])
            CLog('Finishing.', data[4]['path'])

if __name__ == '__main__':
    '''
    Programa principal
    '''
    # Compruebo los argumentos de entrada
    # (nº de parámetros y si son correctos o no)
    if len(sys.argv) != 4:
        sys.exit('Usage: python3 uaclient.py config method option')
    DATAXML = parser_xml(sys.argv[1])

    # Variables que vamos a usar
    METHOD = sys.argv[2]
    OPTION = sys.argv[3]
    LOGPATH = DATAXML[4]['path']
    DATAXML[1]['ip'] = '127.0.0.1'
    CLog('Starting...', LOGPATH)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:

        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((DATAXML[3]['ip'], int(DATAXML[3]['puerto'])))

        if METHOD == 'REGISTER':
            ClientRegister(DATAXML)
        elif METHOD == 'INVITE':
            ClientInvite(DATAXML, OPTION)
        elif METHOD == 'BYE':
            ClientBye(DATAXML, OPTION)
        # Excepción si el método introducido no es válido
        else:
            CLog('Finishing.', LOGPATH)
            sys.exit('Usage: python3 uaclient.py config method option')

        CLog('Finishing.', LOGPATH)
