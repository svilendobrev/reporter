#$Id$
# -*- coding: cp1251 -*-

from test_set import *
from reporter.row_classifier import RowClassifier

class Classifier1( RowClassifier):
    def __init__( me):
        RowClassifier.__init__(me)
        me.group( th_otrab_dni, filter_func=ivan_only, aggregators=[ AggAvg, AggSum])
        me.group( None,         filter_func=ivan_only, aggregators=[ AggAvg, AggSum])

class Classifier2( RowClassifier):
    def __init__( me):
        RowClassifier.__init__(me)
        me.group( None,         filter_func=ivan_only, aggregators=[ AggAvg, AggSum])
        me.group( th_otrab_dni, filter_func=ivan_only, aggregators=[ AggAvg, AggSum])

class Classifier3( RowClassifier):
    def __init__( me):
        RowClassifier.__init__(me)
        me.group( None, aggregators=[])

all_cases = [                  # expected = { position_in_spr_row_stream : group_id_of_packet }
                P( obj= Classifier1(), expected= { 3 : 0, 10 : 0, 14 : 0, 15 : 1 }, descr= '1=th+filter; 2=filter'),
                P( obj= Classifier2(), expected= { 3 : 1, 10 : 1, 14 : 0, 15 : 1 }, descr= '1=filter; 2=th+filter'),
                P( obj= Classifier3(), expected= { 12: 0 }, descr= '1=None'),
            ]

class ClassifierCase( Case):
    def setUp( me):
        me.spr = me.params.obj
        me.rows = test_db_data[:]
        for r in me.rows:
            me.spr.add( r)
        me.spr.end()

    def test_spravka( me):
        from reporter.packet import Packet
        expected = me.params.expected

        me.assert_( me.spr._rows_and_packets, 'got no data')
        pos = 0
        for r in me.spr._rows_and_packets:
            if isinstance( r, Packet):
                me.failUnless( pos in expected, 'have unexpected packet at pos %s' % pos)
                me.assertEqual( r.group_id, expected[ pos], 'expected: %s found: %s' % (str(expected[pos]), str(r.group_id)) )
            else:
                me.failIf( pos in expected, 'got row instead of packet at pos %s' % pos)
            pos += 1

if __name__ == "__main__":
    unittest.TextTestRunner( unittest.sys.stdout, verbosity=2, descriptions=True, ).run( get_test_suite(all_cases, ClassifierCase))


# vim:ts=4:sw=4:expandtab
