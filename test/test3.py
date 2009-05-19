#$Id$
# -*- coding: cp1251 -*-

from test_set import *

''' два вида тестове:
    1. една справка как се държи при различни данни
    2. при едни и същи данни как се изменя справката при смяна на параметрите

    може би сравняване на текстове
'''
from reporter.row_classifier import RowClassifier
import unittest

class TestSpravka( unittest.TestCase):
    def setUp(me):
        me.spr = RowClassifier()
        me.spr.group( th_otrab_dni, filter_func=ivan_only, aggregators=[ AggSum])
        me.spr.group( None,         filter_func=ivan_only, aggregators=[ AggAvg, AggSum])
        me.input_rows = test_db_data[:]
        for r in me.input_rows:
            me.spr.add(r)

#        from viewer import View
#        view = View( me.spr.rows, ['slujitel','osn_zaplata'])
#        print view

    def test_rows(me):
        normal_rows = filter( lambda(r): r.__class__ not in [ AggSum, AggAvg ], me.spr.rows())
        me.assertEqual( me.input_rows, normal_rows, 'wrong data in rows')

    def test_groups(me):
        if not me.spr.finished:
            for g in me.spr._groups:
                me.failUnless( g.current.opened, 'groups are not treated equally')
        else:
            for g in me.spr._groups:
                me.failIf( g.current.opened, 'groups are not treated equally')

class EmptySpravka( unittest.TestCase):
    def setUp(me):
        me.spr = RowClassifier()

    def checkEmpty( me):
        pfx = 'empty report should have no '
        me.failIf( len( me.spr.rows()), pfx+'rows or packets')
        me.failIf( len( me.spr._groups), pfx+'groups')
        me.failUnless( me.spr.empty, 'empty is wrong')

    def runTest(me):
        me.checkEmpty()

        me.spr.end()
        me.checkEmpty()

        me.spr.add( 1)
        me.checkEmpty()

class SpravkaGroups( unittest.TestCase):
    def setUp(me):
        me.spr = RowClassifier()
        me.spr.group( 1, 2, 3) #dummy values
        me.spr.group( 4, 5, 6) #dummy values

    def runTest(me):
        me.assertEquals( len(me.spr._groups), 2, 'wrong group list')
        for i in range( len( me.spr._groups)):
            me.assertEquals( i, me.spr._groups[i].group_id)
        me.spr.add( 10) # add dummy row
        me.spr.group( 7, 8, 9)
        me.assertEquals( len(me.spr._groups), 2, 'adds groups even when not empty()')

if __name__ == '__main__':
    unittest.main()


# vim:ts=4:sw=4:expandtab
