#$Id$
# -*- coding: utf-8 -*-
''' 
За да се направи тестът, трябва първо да се стартира 'simple.py'
'''
import xlrd


w = xlrd.open_workbook('simple.xls')
ws0 = w.sheet_by_index(0)

for xr in range(0,10):
    print ws0.row_values(xr)

ws1 = w.sheet_by_name('Sheet2')


print ws1.cell_value(5,5)

print ws0.col_values(5)

# vim:ts=4:sw=4:expandtab
