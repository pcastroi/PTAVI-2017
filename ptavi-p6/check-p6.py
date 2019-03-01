#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script de comprobación de entrega de práctica

Para ejecutarlo, desde la shell:
 $ python3 check-p6.py login_laboratorio

"""

import os
import random
import sys


files = ['README.md',
         'LICENSE',
         '.gitignore',
         'client.py',
         'server.py',
         'invite.libpcap',
         'check-p6.py',
         'mp32rtp',
         '.git',
         'cancion.mp3']


if len(sys.argv) != 2:
    print()
    sys.exit("Usage: $ python3 check-p6.py login_github")

repo_git = "http://github.com/" + sys.argv[1] + "/ptavi-p6"

aleatorio = str(int(random.random() * 1000000))

error = 0

print
print("Clonando el repositorio " + repo_git)
os.system('git clone ' + repo_git + ' /tmp/' + aleatorio + ' > /dev/null 2>&1')
try:
    student_file_list = os.listdir('/tmp/' + aleatorio)
except OSError:
    error = 1
    print("Error: No se ha podido acceder al repositorio " + repo_git + ".")
    print()
    sys.exit()

if len(student_file_list) != len(files):
    error = 1
    print("Error: solamente hay que subir al repositorio los ficheros indicados en las guion de practicas, que son en total " + str(len(student_file_list)) + " (incluyendo .git):")

    for filename in files:
        error = 1
        print("\tError: " + filename + " no encontrado. Tienes que subirlo al repositorio.")

if not error:
    print("Parece que la entrega se ha realizado bien.")
    print()
    print("La salida de pep8 es: (si todo va bien, no ha de mostrar nada)")
    print()
    os.system('pep8 --repeat --show-source --statistics /tmp/' + aleatorio + '/client.py /tmp/' + aleatorio + '/server.py')
print()
