#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys


class Calculadora:
    "clase Calculadora"

    def suma(self, valor1, valor2):
        """sumo valor1 a valor2"""
        return valor1 + valor2

    def resta(self, valor1, valor2):
        """resto valor2 a valor1"""
        return valor1 - valor2

if __name__ == "__main__":
    try:
        valor1us = int(sys.argv[1])
        valor2us = int(sys.argv[3])
    except ValueError:
        sys.exit("Error: Non numerical parameters")

    calc = Calculadora()

    if sys.argv[2] == "suma":
        result = calc.suma(valor1us, valor2us)
    elif sys.argv[2] == "resta":
        result = calc.resta(valor1us, valor2us)
    else:
        sys.exit('Operación sólo puede ser suma o resta.')

    print(result)
