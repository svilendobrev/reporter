#$Id$
# -*- coding: cp1251 -*-
from pyExcelerator import *
imena = ['Varna','samokov']
w = Workbook()
a = w.add_sheet('a')
b = w.add_sheet('bb')
font = Font()
font.name='Comic Sans MS'
font.bold = True
font.height = 400
borders = Borders()
borders.left = 5
borders.right = 5
borders.top = 9
borders.bottom = 6

al = Alignment()
al.horz = Alignment.HORZ_CENTER
al.vert = Alignment.VERT_CENTER

style = XFStyle()
style.font = font
style.borders = borders
style.alignment = al
a.write(0,5,imena[0],style)
a.write(0,0,Formula('1'),style)
a.write(0,1,Formula('2'),style)
a.write(0,2,Formula('SUM($A$1:$B$1)'))
a.write(0,3,Formula('SUM(A1:C1)'),style)
a.write(0,4,Formula('AVERAGE(A1:D1)'),style)
a.write(0,6,Formula('IF(B1>A1;1;"no")'),style)
w.save('probno211.xls')
# vim:ts=4:sw=4:expandtab
