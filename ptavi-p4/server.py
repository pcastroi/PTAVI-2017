#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import socketserver
import sys
import time


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    SIP Handler
    """
    sipdic = {}

    def register2json(self):
        """
        Creates a json file with the dictionary inside
        """
        json.dump(self.sipdic, open('registered.json', 'w'))

    def json2register(self):
        """
        Open a json file and extract the dictionary
        """
        try:
            with open('registered.json', 'r') as fich:
                self.sipdic = json.load(fich)
        except (FileNotFoundError, ValueError, json.decoder.JSONDecodeError):
            pass

    def handle(self):
        """
        handle method of the server class
        (all requests will be handled by this method)
        if the dictionary its empty, run normally.
        if not, call method json2register
        """
        if self.sipdic == {}:
            self.json2register()

        for line in self.rfile:

            declinsp = line.decode('utf-8').split(' ')
            if not line:
                continue
            elif declinsp[0] == 'REGISTER':
                print(line.decode('utf-8'))
                sipusr = declinsp[1][declinsp[1].find(':') + 1:]
                self.sipdic[sipusr] = [self.client_address[0], 0]

            elif declinsp[0] == 'Expires:':
                print(line.decode('utf-8'))
                listdel = []
                expt = float(declinsp[1]) + time.time()
                now = time.strftime('%Y-%m-%d %H:%M:%S',
                                    time.gmtime(time.time()))
                self.sipdic[sipusr][1] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                       time.gmtime(expt))
                for user in self.sipdic:
                    if self.sipdic[user][1] <= now:
                        listdel.append(user)
                for user in listdel:
                    del self.sipdic[user]
                self.register2json()
                self.wfile.write(b'SIP/2.0 200 OK\r\n\r\n')

        print(self.sipdic)

if __name__ == "__main__":
    # Listens at localhost ('') port 6001
    # and calls the SIPRegisterHandler class to manage the request
    if len(sys.argv) != 2:
        sys.exit('Usage: python3 server.py port')
    serv = socketserver.UDPServer(('', int(sys.argv[1])), SIPRegisterHandler)

    print("Lanzando servidor UDP de eco...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
