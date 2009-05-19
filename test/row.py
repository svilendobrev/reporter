#$Id$
# -*- coding: cp1251 -*-
''' Тества че:
    за класа Row:
    - един ред притежава полетата на своя родител
    - един ред изчислява правилно своите изчислими полета, със и без родител

    за класа AggrRow:
    - притежава полетата на своя родител
    - агрегиращата функция се изчислява върху всички редове
    - вдига изцепка ако в някой от редовете липсва търсеното поле
'''
from test_set import *
from reporter.row import *

class BaseRow( Row):
    _set_ = dict( a=1, b=2, c=3)
    _calc_ = dict( d = lambda(me): me.a + me.b)

class MyRow( BaseRow):
    _set_ = dict( a=5, d=10, e=15)
    def get_f(me):
        return me.d + me.c
    _calc_ = dict( f=get_f)

class BaseAgg( AggrRow):
    def sum_a(me):
        return sum( me.column( 'a'))
    def sum_b(me):
        return sum( me.column( 'b'))
    _set_ = dict( text='Сума:', value=50)
    _calc_ = dict( a=sum_a, b=sum_b)

class MyAgg( BaseAgg):
    def sum_c(me):
        return sum( me.column( 'c'))
    _set_ = dict( text='Пума:', value=100)
    _calc_ = dict( b=sum_c)

class MyAgg2( BaseAgg):
    def sum_e(me):
        return sum( me.column( 'e'))
    def sum_b(me):
        return sum( me.column( 'b'))

    _calc_ = dict( e=sum_e, b=sum_b)


rows = 3*[ MyRow() ]
rows2 = rows + 2*[ BaseRow() ]

all_cases = [
                P( BaseRow()     , dict(a=1,b=2,c=3,d=3)           , 'base row, defaults'   ),
                P( BaseRow(a=5)  , dict(a=5,b=2,c=3,d=7)           , 'base row, init values'),
                P( MyRow()       , dict(a=5,b=2,c=3,d=10,e=15,f=13), 'child row, defaults'     ),
                P( MyRow(a=6,h=1), dict(a=6,b=2,c=3,d=10,e=15,f=13), 'child row, init values'  ),

                P( BaseAgg(rows)                , dict(a=15,b=6,text='Сума:',value=50)  , 'base agg, defaults'   ),
                P( BaseAgg(rows, text='Suma')   , dict(a=15,b=6,text='Suma',value=50)   , 'base agg, init values'),
                P( MyAgg(rows)                  , dict(a=15,b=9,text='Пума:',value=100) , 'child agg, defaults'   ),
                P( MyAgg(rows, text='Guma')     , dict(a=15,b=9,text='Guma',value=100)  , 'child agg, init values'),

#                P( MyAgg2(rows2), dict(a=17, b=10, d=32, text='Сума:', value=100), 'base agg, init values'),
            ]

class RowCase( Case):
    def setUp( me):
        me.row = me.params.obj
        me.expected = me.params.expected
        me.descr = me.params.descr

    def test_row( me):
        for k,v in me.expected.iteritems():
            a = getattr( me.row, k)
            me.assertEqual( a, v, 'wrong value, should be:' + str(v) + ' have:' + str(a))
        me.assertRaises( AttributeError, lambda(me): me.row.whatever, 'changed behaviour')

if __name__ == "__main__":
    unittest.TextTestRunner( unittest.sys.stdout, verbosity=2, descriptions=True, ).run( get_test_suite( all_cases, RowCase))

# vim:ts=4:sw=4:expandtab
