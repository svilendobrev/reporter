#$Id$
# -*- coding: cp1251 -*-
from win32com.client import Dispatch

# Работи под Win32(иска Excel)

def read_formulas( sheets =None , file_for_read =None , output_file =None ):
    xlApp = Dispatch("Excel.Application")
    xlApp.Visible = True
    xlWb = xlApp.Workbooks.Open( file_for_read)
    f = open( output_file , 'w')
    for s in sheets:
        sheet = xlWb.Worksheets( s[0])
        f.write('\n В sheet %s :'%( str( s[0])) )
        for x in range(1,s[1]):
            for y in range(1,s[2]):
                try:
                    m= sheet.Cells(x,y).Formula
                    if m and str(m)[0]=='=':
                        f.write('\n '+chr( 64+y)+str( x)+'='+str( m)+';')
                except UnicodeEncodeError: pass

    f.close()
    xlWb.Close(SaveChanges=0)
    xlApp.Quit()

if __name__ == '__main__':
    # Тук се слага [ име_на_sheet, брой_редове, брой_колони]
    sheets = [['приходи',103,18],['разходи_изпълнение',217,17] ]

    read_formulas( sheets = sheets,
          file_for_read = "c:/modules/win32com charts read/08_2007_budget_Burgas.xls",
          output_file =  'out.txt' )


# vim:ts=4:sw=4:expandtab
