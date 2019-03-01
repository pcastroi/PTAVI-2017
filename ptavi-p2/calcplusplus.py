#!/usr/bin/python3

import sys
import csv
import calcoohija

with open(sys.argv[1], 'r') as fich:
    reader = csv.reader(fich)
    calc = calcoohija.CalculadoraHija()
    for line in reader:
        operat = line[0]
        line.pop(0)
        nums = line
        if operat == 'suma':
            i = 0
            result = 0
            for num in nums:
                result = calc.suma(result, int(nums[i]))
                i = i + 1

        elif operat == 'resta':
            i = 0
            result = int(nums[i])
            for num in nums:
                if i < (len(nums) - 1):
                    result = calc.resta(result, int(nums[i + 1]))
                    i = i + 1

        elif operat == 'multiplica':
            i = 0
            result = 1
            for num in nums:
                result = calc.multiplica(result, int(nums[i]))
                i = i + 1

        elif operat == 'divide':
            i = 0
            result = int(nums[i])
            for num in nums:
                try:
                    if i < (len(nums) - 1):
                        result = calc.divide(result, int(nums[i + 1]))
                        i = i + 1
                except ZeroDivisionError:
                    sys.exit('División por cero')

        print('Resultado:', result)
