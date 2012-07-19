#$Id$
# -*- coding: utf-8 -*-
import itertools
from reporter.engine.util import attr

from field_container import _FieldContainerMeta, FieldSource
class _RowMeta( _FieldContainerMeta):
    USE_CACHE = True # compute field data at first access only
    _field_sources = [
        FieldSource( '_set_', inherit=True),
        FieldSource( '_calc_', inherit=True),
        FieldSource( '_extcalc_', inherit=True),
    ]

class Row( object):
    ''' Редът е контейнер на полета и съдържа тяхното описание. Данните в полетата може да са първични или изчислими.
    Редовете могат да се наследяват. Всеки ред съдържа полетата на своя базов ред.
    '''
    __metaclass__ = _RowMeta
    #_set_ = ...    - NOT assigned: meant to fail if undefined
    _set_ = dict()
    _calc_ = dict()

    db_object = None

    def __init__( me, **kargs):
        for k,vdefault in me._set_.iteritems():
            val = kargs.get( k, vdefault)
            setattr( me, k, getattr( val, 'data', val))

    def get_packet( me):
        return me.__packet
    def set_packet( me, packet):
        me.__packet = packet

    def __str__( me):
        return ' '.join( str( getattr( me, k))
                         for k in itertools.chain( me._set_.iterkeys(), me._calc_.iterkeys()))


from reporter.engine.util.attr import get_attrib
class AggrRow( Row):
    ''' Притежава всички свойства на нормален ред. Има списък с редове върху които изчислява своите полета.'''
    _set_ = {}
    _calc_ = {}

    def __init__( me, rows, **kargs):
        Row.__init__( me, **kargs)
        me.rows = rows

    def column( me, name):
        return [ get_attrib( r, name) for r in me.rows ]


if __name__ == '__main__':
    class Row1(Row):
        _set_ = dict(a=1,c=3)
        _calc_ = dict(a=lambda r: r.a*10, d=lambda r: r.b*100)
    class Row2(Row1):
        _set_ = dict(a=10,b=5)
        _calc_ = dict(a=lambda r: r.a*100, d=lambda r: r.b*1000)
    class Row3(Row2):
        _set_ = dict(a=100,c=300)
        _calc_ = dict(d=lambda r: r.b*10000)
    class Row4(Row3):
        _set_ = dict( a=345)
        _calc_ = dict( d=lambda r: r.b*3)

    r1 = Row4()
    print r1.a, r1.b, r1.c, r1.d

# vim:ts=4:sw=4:expandtab
