#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import calcoo


class CalculadoraHija(calcoo.Calculadora):
    "clase CalculadoraHija hereda de Calculadora"

    def multiplica(self, valor1, valor2):
        """multiplico valor1 con valor2"""
        return valor1 * valor2

    def divide(self, valor1, valor2):
        """divide valor1 entre valor2"""
        return valor1 / valor2

if __name__ == "__main__":
    try:
        valor1us = int(sys.argv[1])
        valor2us = int(sys.argv[3])
    except ValueError:
        sys.exit("Error: Non numerical parameters")

    calc = CalculadoraHija()

    if sys.argv[2] == "suma":
        result = calc.suma(valor1us, valor2us)
    elif sys.argv[2] == "resta":
        result = calc.resta(valor1us, valor2us)
    elif sys.argv[2] == "multiplica":
        result = calc.multiplica(valor1us, valor2us)
    elif sys.argv[2] == "divide":
        try:
            result = calc.divide(valor1us, valor2us)
        except ZeroDivisionError:
            sys.exit('Division by zero is not allowed')
    else:
        sys.exit('Operación sólo puede ser: suma, resta, multiplica, divide')

    print(result)
