#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.sax.handler import ContentHandler
import sys


class SmallSMILHandler(ContentHandler):

    def __init__(self):
        """
        Constructor. Inicializamos las variables
        """
        self.list_tags = []
        self.tags = {'root-layout': ['width', 'height', 'background-color'],
                     'region': ['id', 'top', 'bottom', 'left', 'right'],
                     'img': ['src', 'region', 'begin', 'dur'],
                     'audio': ['src', 'begin', 'dur'],
                     'textstream': ['src', 'region']}

    def startElement(self, name, attrs):
        """
        Método para cuando se abre una etiqueta SMIL
        """
        diccionario = {}
        if name in self.tags:
            diccionario['tag'] = name
            for elem in self.tags[name]:
                diccionario[elem] = attrs.get(elem, "")
            self.list_tags.append(diccionario)

    def get_tags(self):
        """
        Devuelve la lista
        """
        return self.list_tags
