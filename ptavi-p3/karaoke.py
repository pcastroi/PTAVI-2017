#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import urllib.request
import smallsmilhandler
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class KaraokeLocal:

    def __init__(self, fsmil):
        """
        Inicializa y construye la lista
        """
        ssHandler = smallsmilhandler.SmallSMILHandler()
        parser = make_parser()
        parser.setContentHandler(ssHandler)
        parser.parse(open(fsmil))
        self.taglist = ssHandler.get_tags()

    def __str__(self):
        """
        Devuelve una cadena de texto con todas las etiquetas y atributos
        """
        listcad = []
        for dic in self.taglist:
            listcad.append(dic['tag'])
            for atribs in dic:
                if atribs != 'tag' and dic[atribs]:
                    listcad.append('\t' + atribs + '=' + dic[atribs] + '\t')
            listcad.append('\n')
        return(''.join(listcad))

    def to_json(self, fsmil, fjson=''):
        """
        Guarda la lista en un json
        """
        if fjson == '':
            fjson = fsmil.split('.')[0] + '.json'
        json.dump(self.taglist, open(fjson, 'w'))

    def do_local(self):
        """
        Descarga los recursos remotos
        """
        for dic in self.taglist:
            for atribs in dic:
                if atribs == 'src' and 'http:' in dic[atribs]:
                    urllib.request.urlretrieve(dic[atribs],
                                               dic[atribs]
                                               [dic[atribs].rfind('/') + 1:])
                    dic[atribs] = dic[atribs][dic[atribs].rfind('/') + 1:]

if __name__ == '__main__':
    try:
        karloc = KaraokeLocal(sys.argv[1])
    except (FileNotFoundError, IndexError):
        sys.exit("Usage: python3 karaoke.py file.smil")
    print(karloc.__str__())
    karloc.to_json(sys.argv[1])
    karloc.do_local()
    karloc.to_json(sys.argv[1], 'local.json')
    print(karloc.__str__())
