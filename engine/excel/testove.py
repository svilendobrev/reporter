#$Id$
# -*- coding: utf-8 -*-

from builder import XcelBuilder
from visitor import Visitor

if 0:
    import sys
    try: sys.argv.remove( 'com')
    except:
        from apiprob import XcelBuilder4xlwriter as XcelBuilder
    else:
        from apiprob import XcelBuilder4win32com as XcelBuilder

name = 'test.xls'
builder = XcelBuilder( '%(name)s' % locals() )

def save():
    print builder
    visitor = Visitor()
    builder.walk( visitor)


class Meta(type):
    def __new__( meta, name, bases, adict):
        #adict[ 'builder'] = XcelBuilder( 'out/%(name)s' % locals() )
        if name is not 'Test_Xcel':
            adict['sheet'] = builder.sheet( name=name )
        return type.__new__( meta, name, bases, adict)

import unittest
class Test_Xcel( unittest.TestCase):
    __metaclass__ = Meta
#    def setUp( me): me.sheet = me.builder.sheet()
#    def test_zzzzzzzzzzzzzzzzzzzzzzzzzzz( me):
#        print me.builder

class ZZZZZZ( unittest.TestCase):
    def test_zzzzzzzzzzzzzzzzzzzzzzzzzzz( me):
        save()

#############################################################################
class Cell_value( Test_Xcel): ##### sheet 1

    def test00_1( me):
        s = me.sheet
        s.cell(0,0).value= 'proba123'

    def test01_chislo( me):
        s = me.sheet

        s.cell(0,1).value= 0
        s.cell(0,2).value= 6
        s.cell(0,3).value= -4363.54
        s.cell(0,4).value= 5783.4888
        s.cell(0,5).value= 70000000000000000000L

    def test02_text( me):
        s = me.sheet

        s.cell(0,6).value= ''
        s.cell(0,7).value= ' '
        s.cell(0,8).value= '7'
        s.cell(0,9).value= 'alabala'
        s.cell(0,10).value= '''asefwefqew weqwew w weqwe werterftyujtr '''
        s.cell(0,11).value= '''asefwefqew weqwew
 w weqwe
werterftyujtr '''*5
        s.col(0, width= 40)

    def test03_ascii( me):
        s = me.sheet
        s.cell(0,12).value= 'liuloiunl'

    def test04_cirilic( me):
        s = me.sheet
        s.cell(0,13).value= 'алабаланица'

    def test05_unicode( me):
        s = me.sheet
        s.cell(0,14).value= unicode('drty')

    def test06_date( me):
        s = me.sheet
        from datetime import datetime
        s.cell(0,15).value= datetime(2000, 1, 1)

    def test07_bool( me):
        s = me.sheet
        s.cell(0,16).value= True
        s.cell(0,17).value= False

#############################################################################################

class Cell_Value_Format( Test_Xcel): ##### sheet 2

    def test09_font( me):
        s = me.sheet
        s.cell(0,7, value='coolfont').format().font( name='Courier New', slant= 1, weight=1, size=12)

    def test10_align( me):
        s = me.sheet
        s.cell(0,8, value=34).format( align= 'center')
        s.cell(0,9, value=34).format( align= 'center', valign= 'vcenter')

    def test11_value_color( me):
        s = me.sheet
        s.cell(0,10, value=34).format( color= 'blue' )

###############################################################


class Cell_format( Test_Xcel): ##### sheet 3

    def test12_border( me):
        s = me.sheet
        s.cell(0,0, value=34).format().border( left= 5, top=4, right=5, bottom=3)

    def test13_background( me):
        s = me.sheet
        s.cell(0,1, value=34).format( background= 'yellow' )
        s.cell(0,2, value='ruin fynt').format( background= 'orange' )


##############################################################################################

class Row_Column( Test_Xcel): ##### sheet 4

    def test16_Hide( me):
        s = me.sheet
        s.cell(0,1, value=1)
        s.cell(0,2, value=2)
        s.cell(0,3, value=5)
        s.row(25, hidden=True)
        s.col(15, hidden=True)

    def test17_width( me):
        s = me.sheet
        s.cell(5,2, value=1)
        s.row(6, width=31 )
        s.col(2, width=27 )

##############################################################################################


class Cell_formulas( Test_Xcel): ##### sheet 5

    def test18_Operatori( me):
        #aritm: +-*/ **   compare:  == = < > <=
        s = me.sheet
        s.cell( 1,0, value= 8)
        s.cell( 1,1, value= 2)
        s.cell( 1,2).formula= '=B1+B2'  # със SUM
        s.cell( 1,3).formula= '=B1-B2'
        s.cell( 1,4).formula= '=B1*B2'  # с POWER също
        s.cell( 1,5).formula= '=B1/B2'
        s.cell( 1,6).formula= '=B1**B2'

        s.cell( 2,2).formula= '=SUM( B1,B2 )'
        s.cell( 2,3).formula= '=POWER( B1,B2 )'

    def test19_Functions_simple( me):
        s = me.sheet
        s.cell(3,0).formula= '=SIN( B2 )'
        s.cell(3,1).formula= '=COS( B2 )'
        s.cell(3,2).formula= '=TAN( B2 )'
        # iff(cond,thenexpr,lsexpr)

    def test20_Functions_range_cell( me):
        '''sum([...]), fxxx2([..],[...]),'''
        s = me.sheet
        s.cell(1,8).formula= '=SUM( B3:B7 )'


#########################################################################################

class Cell_Other( Test_Xcel ): ## sheet 6
    def test21_merge_split_cells( me):
        s = me.sheet
        s.merge('A1:F1','WELCOME').format(background= 'red',
                                          align= 'center',
                                          ).border( left=3, top= 3, right= 3, bottom= 3)
        s.merge('A2:F2','SDHGLIULIULIULGFS').format(background= 'cyan',
                                                    align= 'center',
                                                    ).border(left= 3, top= 3, right= 3, bottom= 3)
        s.merge('A3:F3','wwwwwoowwwwwww').format(background= 'magenta',
                                                    align= 'center',
                                                    ).border(left= 3, top= 3, right= 3, bottom= 3)
    def test22_freeze( me):
        s = me.sheet
        s.freeze(2,3)
        s.freeze(0,1,label= True)

#########################################################################################

class Objects( Test_Xcel):  ##### sheet 7

    def test23_link( me): ## за клетка
        s = me.sheet
        s.cell( 7,0, value= 'http://www.razni.com' )

    def test24_pagebreak( me):
        s = me.sheet
        s.page_break(3,3) # колона, ред

    def test25_picture( me):
        s = me.sheet
        s.cell(9,4).picture= 'proba/republic.bmp' # пътя към картинката

#########################################################################################

class FileMetaData( Test_Xcel): ##### sheet 8
    def test26_protect( me):
        s = me.sheet
        s.protect= True
        s.cell( 0,3, value= 'razni.com' ).format( background= 'cyan').protect= False

#########################################################################################

class Outline ( Test_Xcel):
    def test27_outline( me):
        s = me.sheet
        #s.row(0, level= 1)
        s.row(1, level= 1)
        s.row(2, level= 2)
        s.row(3, level= 2)
        s.row(4, level= 3)
        s.row(5, level= 3)
        s.row(6, level= 4)
        s.outline( 0, level = 1)
        s.cell(0,0, value= 'drun-drun').format().font( weight = 1)
        s.cell(0,1, value= '76547537').format().font( name = 'Times New Roman')
        s.cell(0,2, value= 'sk.djfnk')
        s.cell(0,3, value= '2345275')
        s.cell(0,4, value= 'ding-dong')
        s.cell(0,5, value= 'blaa-blaaa')
        s.cell(0,6, value= 'dura-dura')

if __name__ == '__main__':
    unittest.main()

# vim:ts=4:sw=4:expandtab
