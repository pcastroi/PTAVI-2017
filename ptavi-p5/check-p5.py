#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Script de comprobación de entrega de práctica

Para ejecutarlo, desde la shell:
 $ python3 check-p5.py login_github

"""

import os
import random
import sys


files = ['README.md',
         'LICENSE',
         'p5.txt',
         'sip.libpcap.gz',
         'p5.pcapng',
	 'check-p5.py',
         '.git']


if len(sys.argv) != 2:
    sys.exit("Usage : $ python3 check-p5.py login_github")

repo_git = "http://github.com/" + sys.argv[1] + "/ptavi-p5"

aleatorio = str(int(random.random() * 1000000))

error = 0

print("Clonando el repositorio " + repo_git)
os.system('git clone ' + repo_git + ' /tmp/' + aleatorio + ' > /dev/null 2>&1')
try:
    student_file_list = os.listdir('/tmp/' + aleatorio)
except OSError:
    error = 1
    print("Error: No se ha creado el repositorio git correctamente.")
    print()
    sys.exit()

if len(student_file_list) != len(files):
    error = 1
    print("Error en el número de ficheros encontrados en el repositorio")

for filename in files:
    if filename not in student_file_list:
        error = 1
        print("Error: " + filename + " no encontrado. Tienes que subirlo al repositorio.")

if not error:
    print("Parece que la entrega se ha realizado bien.")
    print("Recuerda que también tienes que realizar un test en Moodle.")
    print()
