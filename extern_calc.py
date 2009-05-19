#$Id$
# -*- coding: cp1251 -*-

from spravka2 import SprDef
from row import Row, AggrRow
from field import *

def th_mod_1000( r, rows):
    return r.osn_zaplata % 1000 == 0

from viewer2 import *

class AggTrDogovor( AggrRow):
    def get_zaplata( me):
        return sum( me.column('osn_zaplata'))
    _set_ = dict( short_name = 'Общо:')
    _calc_ = dict( osn_zaplata = get_zaplata)


from decimal import Decimal

class SprExtCalc( SprDef):
    class RowTrDogovor( Row):
        _set_ = dict( sluzhitel=FldDef(), short_name=FldDef(), osn_zaplata=FldDef())

        _calc_ = dict( names=FldDef( type=Text, data=lambda r: r.sluzhitel+r.short_name,
                                     view=FldView(label='Imena', align='l', border='r')))

        _extcalc_ = dict( percent=FldDef( type=Float,
              data=lambda row: Decimal(row.osn_zaplata) * 100 / row.packet.agg_rows[0].osn_zaplata,
              view=FldView( label='Процент', align='r', border='r')))

    RowType = RowTrDogovor

    model_mapping = dict( sluzhitel   = 'employment.slujitel.name.name',
                          short_name  = 'employment.slujitel.name.alias',
                          osn_zaplata = 'employment.osnovna_zaplata')
    def setup( me):
        me.group( th_mod_1000, None, [ AggTrDogovor])

from reporter.engine.basedb.docs import TrudovDogovor, Person, SalaryCalculation, Employment, populateAll

if __name__ == "__main__":
    from reporter.engine.basedb.simpleDB import DB
    populateAll( DB, 10)
    column_order = ['sluzhitel', 'short_name', 'osn_zaplata', 'percent']

    spr = SprExtCalc()
    if 10:
        viewdescr = dict(
            sluzhitel   = FldView( align='l', border='lr'),
            short_name  = FldView( align='l', border='r'),
            osn_zaplata = FldView( format_str='%.2f', align='r', border='r'),
            percent     = FldView( format_str='%.2f %%', align='r', border='r'),
        )
    else:
        viewdescr = dict()

    spr.update( iter(DB.query( TrudovDogovor)))
    print View2( spr, viewdescr).make_str( column_order)

# vim:ts=4:sw=4:expandtab
