#!/usr/bin/python3
# -*- coding: utf-8 -*-

import hashlib
import socket
import socketserver
import sys
import time
import uaclient
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class PXMLHandler(ContentHandler):

    def __init__(self):
        '''
        Constructor. Inicializamos las variables
        '''
        self.tags = []
        self.list_tags = ['server', 'database', 'log']
        self.dict_attrs = {'server': ['name', 'ip', 'puerto'],
                           'database': ['path', 'passwdpath'],
                           'log': ['path']}

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


def proxy_parser_xml(fxml):
    '''
    Función que dado un fichero xml, devuelve una lista de diccionarios
    '''
    parser = make_parser()
    handxml = PXMLHandler()
    parser.setContentHandler(handxml)
    parser.parse(open(fxml))
    return (handxml.get_tags())


def ReadPassword(path, user):
    '''
    Función que devuelve la contraseña del usuario en cuestión,
    leyendo del fichero passwords.txt
    '''
    fich = open(path, "r")
    lineas = fich.readlines()
    for linea in lineas:
        if linea.split(' ')[0] == user:
            password = linea.split(' ')[1][:-1]
    return password


def UserDatabase(Userdic, path):
    '''
    Función que escribe en un fichero de texto "user: ip port time expires"
    '''
    fich = open(path, "w")
    for User in Userdic:
        Info = (Userdic[User][0] + ': ' + str(Userdic[User][1]) +
                ' ' + str(Userdic[User][2]) + ' ' + str(Userdic[User][3]) +
                ' ' + str(Userdic[User][4]))
        fich.write(Info)


class PHandler(socketserver.DatagramRequestHandler):
    '''
    Handler del Proxy
    '''
    datosxml = proxy_parser_xml(sys.argv[1])
    dbpath = datosxml[1]['path']
    dbpasswpath = datosxml[1]['passwdpath']
    logpath = datosxml[2]['path']

    dicdb = {}  # Diccionario de listas en el que se van a guardar los usuarios
    # Key: Username; Value: lista que tiene username, userip,
    # userport, userdate(desde 1970) y userexp

    def Register(self, data):
        '''
        Funcion para el register
        '''
        nonce = '767676'
        user = data[0].split(':')[1]
        userip = self.client_address[0]
        userport = data[0].split(' ')[1].split(':')[2]
        userdate = time.time()
        userexp = data[1].split(':')[1][1:]
        uslist = [user, userip, userport, userdate, userexp]
        if user in self.dicdb:  # usuario ya está en el diccionario
            msend = 'SIP/2.0 200 OK\r\n\r\n'
            uaclient.CLog('Sent to ' + userip + ':' +
                          userport + ': ' +
                          msend, datosxml[2]['path'])
            self.wfile.write(bytes(msend, 'utf-8'))
            self.dicdb[user][3] = userdate
            self.dicdb[user][4] = userexp
            UserDatabase(self.dicdb, self.dbpath)
        else:
            try:
                if data[3].split(':')[0] == 'Authorization':
                    passin = self.datosxml[1]['passwdpath']
                    password = ReadPassword(passin, user)
                    h = hashlib.sha1(bytes(password, 'utf-8'))
                    h.update(bytes(nonce, 'utf-8'))
                    # comprobamos que las claves son las correctas
                    pswd = data[3].split('=')[1].split('\r')[0][1:-1]
                    if pswd == h.hexdigest():
                        msend = 'SIP/2.0 200 OK\r\n\r\n'
                        uaclient.CLog('Sent to ' + userip + ':' +
                                      userport + ': ' +
                                      msend, datosxml[2]['path'])
                        self.wfile.write(bytes(msend, 'utf-8'))
                        self.dicdb[user] = uslist
                        UserDatabase(self.dicdb, self.dbpath)
            except IndexError:
                msend = ('SIP/2.0 401 Unauthorized' + '\r\n' +
                         'WWW Authenticate: Digest nonce="' +
                         nonce + '"' + '\r\n\r\n')
                uaclient.CLog('Sent to ' + userip + ':' +
                              userport + ': ' + msend, datosxml[2]['path'])
                self.wfile.write(bytes(msend, 'utf-8'))

    def Invite(self, data):
        '''
        Función para reeenviar el Invite al server y reenvio el 100, 180,...
        '''
        datosxml = proxy_parser_xml(sys.argv[1])
        user = data[0].split(':')[1].split(' ')[0]
        if user in self.dicdb:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((self.dicdb[user][1],
                                   int(self.dicdb[user][2])))
                msend = ''.join(data)
                uaclient.CLog('Sent to ' + self.dicdb[user][1] + ':' +
                              str(self.dicdb[user][2]) + ': ' +
                              msend + '\r\n', datosxml[2]['path'])
                my_socket.send(bytes(msend, 'utf-8') + b'\r\n')
                msend = my_socket.recv(1024).decode('utf-8')
                uaclient.CLog('Received from 127.0.0.1:6003: ' +
                              msend + '\r\n', datosxml[2]['path'])
                self.wfile.write(bytes(msend, 'utf-8'))
                uaclient.CLog('Sent to ' + self.dicdb[user][1] + ':' +
                              str(self.dicdb[user][2]) + ': ' +
                              msend + '\r\n', datosxml[2]['path'])
        else:  # 404 User not found
            msend = 'SIP/2.0 404 User Not Found' + '\r\n'
            uaclient.CLog('Sent to 127.0.0.1:6001: ' +
                          msend + '\r\n', datosxml[2]['path'])
            self.wfile.write(bytes(msend, 'utf-8'))

    def Ack(self, data):
        '''
        Funcion para reenviar el Ack al server
        '''
        datosxml = proxy_parser_xml(sys.argv[1])
        user = data[0].split(':')[1].split(' ')[0]
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((self.dicdb[user][1], int(self.dicdb[user][2])))
            msend = ''.join(data)
            uaclient.CLog('Sent to ' + self.dicdb[user][1] + ':' +
                          str(self.dicdb[user][2]) + ': ' +
                          msend + '\r\n', datosxml[2]['path'])
            my_socket.send(bytes(msend, 'utf-8') + b'\r\n')

    def Bye(self, data):
        '''
        Funcion para reenviar el Bye al server y reeenvio el 200
        '''
        datosxml = proxy_parser_xml(sys.argv[1])
        user = data[0].split(':')[1].split(' ')[0]
        if user in self.dicdb:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((self.dicdb[user][1],
                                   int(self.dicdb[user][2])))
                msend = ''.join(data)
                uaclient.CLog('Sent to ' + self.dicdb[user][1] + ':' +
                              str(self.dicdb[user][2]) + ': ' +
                              msend + '\r\n', datosxml[2]['path'])
                my_socket.send(bytes(msend, 'utf-8') + b'\r\n')
                msend = my_socket.recv(1024).decode('utf-8')
                uaclient.CLog('Received from 127.0.0.1:6003: ' +
                              msend + '\r\n', datosxml[2]['path'])
                self.wfile.write(bytes(msend, 'utf-8'))
        else:  # 404 User not found
            msend = 'SIP/2.0 404 User Not Found' + '\r\n'
            uaclient.CLog('Sent to ' + self.dicdb[user][1] + ':' +
                          str(self.dicdb[user][2]) + ': ' +
                          msend + '\r\n', datosxml[2]['path'])
            self.wfile.write(bytes(msend, 'utf-8'))

    def handle(self):

        DATOS = []
        for line in self.rfile:
            DATOS.append(line.decode('utf-8'))
        datx = DATOS[0].split(' ')
        if ('sip:' not in datx[1] or '@' not in datx[1] or datx[2] != 'SIP/2.0\r\n'):
            msend = 'SIP/2.0 400 Bad Request\r\n\r\n'
            uaclient.CLog('Sent to ' + self.dicdb[datx[1].split(':')][1] + ':' +
                          int(self.dicdb[datx[1].split(':')][2]) + ': ' +
                          msend + '\r\n', datosxml[2]['path'])
            self.wfile.write(bytes(msend, 'utf-8'))
        else:
            if DATOS[0].split(' ')[0] == 'REGISTER':
                self.Register(DATOS)
            elif DATOS[0].split(' ')[0] == 'INVITE':
                self.Invite(DATOS)
            elif DATOS[0].split(' ')[0] == 'ACK':
                self.Ack(DATOS)
            elif DATOS[0].split(' ')[0] == 'BYE':
                self.Bye(DATOS)
            else:
                msend = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                uaclient.CLog('Sent to ' + self.dicdb[username][1] + ':' +
                              int(self.dicdb[username][2]) + ': ' +
                              msend + '\r\n', datosxml[2]['path'])
                self.wfile.write(bytes(msend, 'utf-8'))

if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.exit('Usage: python3 proxy_registrar.py config')

    datosxml = proxy_parser_xml(sys.argv[1])
    username = datosxml[0]['name']
    if username == '':
        username = 'default'
    proxyip = datosxml[0]['ip']
    if proxyip == '':
        proxyip = '127.0.0.1'
    proxyport = datosxml[0]['puerto']
    uaclient.CLog('Starting...', datosxml[2]['path'])
    try:
        serv = socketserver.UDPServer((proxyip, int(proxyport)), PHandler)
        print('Server ' + username + ' listening at port ' + proxyport + '...')
        serv.serve_forever()
    except KeyboardInterrupt:
        print('Finalizado servidor proxy')
        uaclient.CLog('Finishing.', datosxml[2]['path'])
