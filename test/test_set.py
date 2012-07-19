#$Id$
# -*- coding: utf-8 -*-

class Fld( object):
    def __init__( me, data=None):
        me.data = data

    def __str__( me):
        return str( me.data)

class TextFld( Fld):
    def __init__( me, data=''):
        Fld.__init__( me, data)

class FloatFld( Fld):
    def __init__( me, data=0):
        Fld.__init__( me, data)

    def __str__( me):
        if me.data.__class__.__name__ == 'Decimal':
            return '%.2f' % me.data
        else:
            return Fld.__str__( me)

class IntFld( FloatFld):
    def __str__( me):
        if me.data.__class__.__name__ == 'int':
            return '%d' % me.data
        else:
            return Fld.__str__( me)

#######################################################

from reporter.row import Row, AggrRow
class ZaplataRow( Row):
    _set_ = dict(   sluzhitel   = TextFld(  ''),
                    osn_zaplata = FloatFld(  0),
                    otrab_dni   = IntFld(    0),
                    dni_za_mes  = IntFld(    0),
                    realna_zap  = FloatFld(  0) )

import decimal as dec
def avg( li):
    if not li: return 0
    return sum( li) / dec.Decimal(len( li))

class AggAvg( AggrRow):
    def avg_zap_get(me):
        return FloatFld( avg( me.column( 'realna_zap')))
    def avg_days_get(me):
        return FloatFld( avg( me.column( 'dni_za_mes')))

    _set_ = dict( otrab_dni=TextFld( 'Средно:'))
    _calc_ = dict( realna_zap=avg_zap_get, dni_za_mes=avg_days_get)

class AggSum( AggrRow):
    def sum_zap_get(me):
        return FloatFld(  sum( me.column('realna_zap')))
    def sum_days_get(me):
        return FloatFld(  sum( me.column('dni_za_mes')))

    _set_ = dict( otrab_dni=TextFld( 'Общо:'))
    _calc_ = dict( realna_zap=sum_zap_get, dni_za_mes=sum_days_get)

from reporter.common import threshold
th_otrab_dni = threshold( 'otrab_dni')

def ivan_only(r):
    return r.sluzhitel != 'Ivan Shivachev'

def get_rows_db():
#    from reporter.engine.basedb.models import * #TrudovDogovor, Person, SalaryCalculation, Naznachenie
    from reporter.engine.basedb import docs #TrudovDogovor, Person, SalaryCalculation, Naznachenie
    from reporter.engine.basedb.simpleDB import DB
    #print "\n\nLOCALS:\n", locals()
    #print "\n\nDOCS_LOCALS:\n", docs.__dict__
    DB.reset( docs.__dict__)

    baiIvan = docs.Person()
    aln = baiIvan.ime
    #boza was aln.alias
    boza, aln.ime = ( 'baiIvan', 'Ivan Shivachev')
    baiMamul = docs.Person()
    aln = baiMamul.ime
    boza, aln.ime = ( 'baiMamul', 'Kalmuk Mamulev')
    shefa = docs.Rabotodatel()
    shefa.ime.ime = 'Chichko Mnogov Parichkov'

    td = baiIvanNaznachenie = docs.TrudovDogovor()
    td.rabotodatel = shefa
    td.sluzhitel = baiIvan
    td.osnovna_zaplata = 2000
    td1 = baiMamulNaznachenie = docs.TrudovDogovor()
    td1.rabotodatel = shefa
    td1.sluzhitel = baiMamul
    td1.osnovna_zaplata = 2500
    DB.save( locals())
    #print "\n\nLOCALS:\n", locals()

    test_data =(3*[[ 18, 19]] +
                3*[[ 16, 19]] +
                3*[[ 16, 20]] +
                3*[[ 45, 45]] )
    k = 0
    test_db = []
    for i in test_data:
        k += 1
        sc = docs.SalaryCalculation()
        sc.naznachenie = k % 3 and baiIvanNaznachenie or baiMamulNaznachenie
        sc.otraboteni_dni           = i[0]
        sc.rabotni_dni_za_perioda   = i[1]

        r = ZaplataRow( sluzhitel    = sc.naznachenie.sluzhitel.ime.ime,
                        osn_zaplata = sc.osnovna_zaplata              ,
                        otrab_dni   = sc.otraboteni_dni               ,
                        dni_za_mes  = sc.rabotni_dni_za_perioda       ,
                        realna_zap  = sc.realna_zaplata               )

        test_db.append( r)
    return test_db

#test_db_data = get_rows_db()

class TestParams( object):
    def __init__( me, obj, expected, descr):
        me.obj = obj
        me.expected = expected
        me.descr = descr
P = TestParams

def test_case_factory( case_params, TestCaseClass):
    class SpravkaTestCase( TestCaseClass):
        params = case_params
        name = case_params.descr
    return SpravkaTestCase

import unittest
class Case( unittest.TestCase):
    name = None
    params = None

    def __str__( me):
        return "  (%s)" % me.name

def get_test_suite( cases, TestCaseClass):
    cases = [ unittest.defaultTestLoader.loadTestsFromTestCase(
                test_case_factory( c, TestCaseClass) ) for c in cases
            ]
    return unittest.TestSuite( cases)

# vim:ts=4:sw=4:expandtab
