#$Id$
# -*- coding: utf-8 -*-

from test_set import *
from reporter.row_classifier import RowClassifier
from reporter.engine.util.testeng.testbase import Case as _Case

class Test:
    VERBOSE = 0

    class Sample( object):
        def __init__( me, threshold, filter_func, aggregators, expected, test_name=''):
            me.threshold = threshold
            me.filter_func = filter_func
            me.aggregators = aggregators
            me.expected = expected
            me.name = test_name

        def testData( me):
            th_name = me.threshold is None and 'NO TRESHOLD' or me.threshold.__name__
            fltr_name = me.filter_func is None and 'NO FILTER' or me.filter_func.__name__
            aggs = me.aggregators is None and 'NO AGGREGATORS' or ' '.join( a.__class__.__name__ for a in me.aggregators)
            return ' '.join( [ th_name, fltr_name, aggs])

        def __str__( me):
            return 'SAMPLE: %s %s' % (me.testData(), me.expected)

    t = Sample
    samples = [#   threshold_func    filter      aggregators         (packet sz, agg rows)
                t( None           , None      , None              , ([ 12]  ,  None     ), 'група без нищо'                      ),
                t( th_otrab_dni   , None      , None              , ([3,6,3],  None     ), 'група с праг'                        ),
                t( th_otrab_dni   , ivan_only , None              , ([3,6,3],  None     ), 'група с праг и филтър'               ),
                t( th_otrab_dni   , None      , [ AggAvg, AggSum ], ([3,6,3],  [3,6,3]  ), 'група с праг и агрегатори'           ),
                t( th_otrab_dni   , ivan_only , [ AggAvg, AggSum ], ([3,6,3],  [2,4,2]  ), 'група с праг, филтър и агрегатори'   ),
                t( None           , ivan_only , None              , ([12]   ,  None     ), 'група с филтър'                      ),
                t( None           , ivan_only , [ AggAvg, AggSum ], ([12]   ,  [8]      ), 'група с филтър и агрегатори'         ),
                t( None           , None      , [ AggAvg, AggSum ], ([12]   ,  [12]     ), 'група само с агрегатори'             ),
            ]

    class Case( _Case):
        def __init__( me, *a,**k):
            _Case.__init__( me, *a,**k)
            me.spr = RowClassifier()

        def setupEach( me, f):
            me.spr.add( f)

        def setup( me):
            for g in me.testSamples:
                me.spr.group( g.threshold, filter_func=g.filter_func, aggregators=g.aggregators)
            _Case.setup( me)
            me.spr.end()

        def testEach( me, t):
            group_id = Test.samples.index(t)
            group = me.spr._groups[ group_id]

            packet_sizes = [ len( p.rows) for p in group.packets ]
            agg_sizes = [ (p.agg_rows and len( p.agg_rows[0].rows) or None) for p in group.packets ]
            if agg_sizes.count( None) == len( agg_sizes):
                agg_sizes = None

            return ( packet_sizes, agg_sizes )

        def test( me):
            _Case.test( me)
            if me.verbosity > 0:
                import viewer
                fld_names = ['slujitel', 'osn_zaplata', 'otrab_dni', 'dni_za_mes', 'realna_zap']
                aligns = dict(  slujitel    ='l',
                                osn_zaplata ='r',
                                otrab_dni   ='r',
                                dni_za_mes  ='r',
                                realna_zap  ='r')

                captions = dict(slujitel    ='Служител'        ,
                                osn_zaplata ='Осн.заплата'     ,
                                otrab_dni   ='Отработени дни'  ,
                                dni_za_mes  ='Раб.дни в месеца',
                                realna_zap  ='Реална заплата'  )

                vborders = dict(slujitel    = 'lr',
                                osn_zaplata = 'r',
                                otrab_dni   = 'r',
                                dni_za_mes  = 'r',
                                realna_zap  = 'r',)

                #view = viewer.View( me.spr.rows, fld_names)
                #view = viewer.Titled( view, captions)
                view = viewer.Aligned( view, aligns)
                #view = viewer.VBordered( view, vborders)
                #view = viewer.HBordered( view, 'ud')
                print view

if __name__ == "__main__":
    from reporter.engine.util.testeng.testutils import testMain
    testMain( [ Test.Case( 'test_db', test_db_data[:], Test.samples)], verbosity= Test.VERBOSE )


# vim:ts=4:sw=4:expandtab
