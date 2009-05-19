#$Id$
# -*- coding: cp1251 -*-

''' Тества дали групата:
    - предава редовете към пакета
    - дава агрегаторите си на пакета при затварянето му
    - записва пакета си при затварянето му в общия списък
'''
from test_set import *
from reporter.group import Group

class GroupParams( object):
    def __init__( me, th, filter, aggregators, expected_rows, expected_rows2agg, descr):
        me.threshold_func = th
        me.filter_func = filter
        me.aggregators = aggregators
        me.expected_rows = expected_rows
        me.expected_rows2agg = expected_rows2agg
        me.descr = descr

G = GroupParams
#expected description example:
#   '/' is packet delimiter
#   '0:2/3:5,6:8/9:11' means 3 packets
#   the first one contains rows[0:2]
#   the second one rows[3:5]+rows[6:8]
#   the last has rows[9:11]

all_cases = [ # threshold_func    filter      aggregators    expected_rows   expected_rows2agg   descr
            G( None        , None     , None              , '0:12'        , '0:12'            , 'simple group'       ),
            G( th_otrab_dni, None     , None              , '0:3/3:9/9:12', '0:3/3:9/9:12'    , 'threshold involved'  ),
            G( th_otrab_dni, ivan_only, None              , '0:3/3:9/9:12', '0:2/3:5,6:8/9:11', 'threshold and filter'),
            G( th_otrab_dni, None     , [ AggAvg, AggSum ], '0:3/3:9/9:12', '0:3/3:9/9:12'    , 'threshold and aggregators'),
            G( th_otrab_dni, ivan_only, [ AggAvg, AggSum ], '0:3/3:9/9:12', '0:2/3:5,6:8/9:11', 'th and filter and aggs'),
            G( None        , ivan_only, [ AggAvg, AggAvg ], '0:12'        , '0:2,3:5,6:8,9:11', 'filter only'),
            ]

class GrpCase( Case):
    def setUp( me):
        me.rows = test_db_data[:]
        me.packet_order = []
        me.group = Group( 1, me.packet_order)
        me.group.threshold_func = me.params.threshold_func
        me.group.filter_func = me.params.filter_func
        me.group.aggregators = me.params.aggregators

        for r in me.rows:
            me.group.add( r)
        me.group.close('end')

    def get_expected( me, expected_str):
        res = []
        expected = expected_str.split('/')
        for p in expected:
            exp_pack= []
            segments = p.split(',')
            for seg in segments:
                low, high = seg.split(':')
                exp_pack.extend( me.rows[ int(low):int(high) ])
            res.append( exp_pack)
        return res

    def test_group( me):
        me.assertEqual( len( me.group.packets), len( me.packet_order), 'non registered packet')

        expected_rows = me.get_expected( me.params.expected_rows)
        expected_rows2agg = me.get_expected( me.params.expected_rows2agg)
        me.assertEqual( len(expected_rows), len( expected_rows2agg), 'wrong test definition')
        me.assertEqual( len(expected_rows), len( me.group.packets), 'different number of packets')
        me.assertEqual( len(expected_rows2agg), len( me.group.packets), 'different number of packets')

        for i in range( len( me.group.packets)):
            p = me.group.packets[i]
            me.failIf( p.opened, 'opened packet')
            me.assertEqual( p.rows, expected_rows[i], 'wrong data in packet')

            if me.params.aggregators is None:
                me.params.aggregators = []
            me.assertEqual( len(p.agg_rows), len( me.params.aggregators), 'wrong agg_rows')
            for j in range( len( p.agg_rows)):
                agg = p.agg_rows[j]
                if agg.rows != expected_rows2agg[i]:
                    print '\n_________got rows: ', agg.rows
                    print '\n_________expected: ', expected_rows2agg[i]

                me.assertEqual( agg.__class__, me.params.aggregators[j], 'wrong agg __class__')
                me.assertEqual( agg.rows, expected_rows2agg[i], 'agg calcs over wrong rows')

if __name__ == "__main__":
    unittest.TextTestRunner( unittest.sys.stdout, verbosity=2, descriptions=True, ).run( get_test_suite( all_cases, GrpCase))

# vim:ts=4:sw=4:expandtab
