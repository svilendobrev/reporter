#$Id$
# -*- coding: cp1251 -*-

''' Да се пробва че:
    - се добавят редове
    - не се добавят редове в затворен пакет
    - всички редове участват в агрегацията
'''
import unittest
from test_set import *
from reporter.packet import *

class TestPacket( unittest.TestCase):
    def setUp( me):
        me.packet = Packet(1)
        me.rows = list( test_db_data)   #copy?
        me.aggregators = [ AggSum, AggAvg ]

    def test_add( me):
        for i in range( len( me.rows)):
            r = me.rows[i]
            me.assertEqual( me.packet.rows, me.rows[:i])
            me.packet.add( r)

    def test_close( me):
        me.packet.close( me.aggregators, lambda: False)
        me.failIf( me.packet.opened)
        me.assertEqual( len(me.packet.agg_rows), len( me.aggregators))
        for agg_row, aggregator in zip( me.packet.agg_rows, me.aggregators ):
            me.assertEqual( agg_row.__class__, aggregator)
            me.assertEqual( agg_row.rows, me.packet.rows)

class TestClosedPacket( TestPacket):
    def setUp( me):
        TestPacket.setUp( me)
        me.packet.close( me.aggregators, lambda: False)

    def test_add( me):
        for i in range( len( me.rows)):     #XXX WTF прави това?
            r = me.rows[i]
            me.assertEqual( me.packet.rows, [])

if __name__ == "__main__":
    unittest.main()

# vim:ts=4:sw=4:expandtab
