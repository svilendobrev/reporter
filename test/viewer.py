#$Id$
# -*- coding: cp1251 -*-
from test_set import *
from reporter.row_classifier import RowClassifier

fld_names = ['sluzhitel', 'osn_zaplata', 'otrab_dni', 'dni_za_mes', 'realna_zap']
aligns = dict(  sluzhitel   ='l',
                osn_zaplata ='r',
                otrab_dni   ='r',
                dni_za_mes  ='r',
                realna_zap  ='r')

captions = dict(sluzhitel   ='Служител'        ,
                osn_zaplata ='Осн.заплата'     ,
                otrab_dni   ='Отработени дни'  ,
                dni_za_mes  ='Раб.дни в месеца',
                realna_zap  ='Реална заплата'  )

vborders = dict(sluzhitel   = 'lr',
                osn_zaplata = 'r',
                otrab_dni   = 'r',
                dni_za_mes  = 'r',
                realna_zap  = 'r',)

spr = RowClassifier()
spr.group( th_otrab_dni, filter_func=ivan_only, aggregators=[ AggAvg, AggSum])
spr.group( None,         filter_func=ivan_only, aggregators=[ AggAvg, AggSum])
for r in test_db_data:
    spr.add( r)
spr.end()

from viewer4tests import *
view = View( spr, fld_names)
all_cases = [
                P( view                      , 'view_.txt'           , 'view_'          ),
#                P( Titled( view, captions)   , 'view_Titled.txt'     , 'view_Titled'    ),
#                P( Aligned( view, aligns)    , 'view_Aligned.txt'    , 'view_Aligned'   ),
#                P( VBordered( view, vborders), 'view_VBordered.txt'  , 'view_VBordered' ),
#                P( VBordered( Aligned( view, aligns), vborders), 'view_Aligned_VBordered.txt'  , 'Aligned Bordered' ),
#                P( VBordered( Aligned( Titled( view, captions), aligns), vborders), 'view_Al_Bord_Captioned.txt'  , 'Aligned Bordered Titled' ),
#                P( HBordered( view, 'u')     , 'view_HBordered.txt'  , 'view_HBordered' ),
            ]

class ViewCase( Case):
    def setUp( me):
        me.view = me.params.obj

    def test_view( me):
        f = open( me.params.expected)
        expected = ''
        spr_txt = str( me.view)
        try:
            expected = ''.join( line for line in f)
        finally:
            f.close()
        me.assertEqual( spr_txt, expected, 'should be: '+expected+ ' have: '+spr_txt)

def gen_test_result( cases):
    print 'generating new samples'
    for params in cases:
        view = params.obj
        f = open( params.expected, 'w')
        f.write( str( view))
        f.close()

import sys
if __name__ == '__main__':
    if len( sys.argv) > 1 and sys.argv[1] == 'gen':
        gen_test_result( all_cases)

    unittest.TextTestRunner(
        unittest.sys.stdout, verbosity=2, descriptions=True, ).run( get_test_suite( all_cases, ViewCase))


# vim:ts=4:sw=4:expandtab
