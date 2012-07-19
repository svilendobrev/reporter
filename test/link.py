#$Id$


import unittest

class SimpleCase( unittest.TestCase):
    def setUp( me):
        me.data = LinkDict(
            b = Link('a'),
            c = Link('b'),
            a = 5,
            d = Link('c'),
        )

    def test_( me):
        me.assertEqual( me.data['b'], me.data['a'], 'link to value, direct')
        me.assertEqual( me.data['c'], me.data['a'], '2 level depth')
        me.assertEqual( me.data['d'], me.data['a'], '3 level depth')
        me.assertEqual( me.data['a'], 5, 'corrupt data')

        me.data['b'] += 1
        me.assertNotEqual( me.data['b'], me.data['a'], 'change')
        me.assertNotEqual( me.data['c'], me.data['b'], 'change')
        me.assertEqual( me.data['a'], me.data['c'])


from reporter.engine.util.attr import get_attrib
from test_set import Case, get_test_suite, P
all_cases = [
    P( dict( a=1, b='a', c='b', d='c'),
        expected=dict(a=1, b=1, c=1, d=1),
        descr='simple case'),

    P( dict( a='b', b=dict(a='c',b=10), c=dict(a=15, b=20)),
        expected={  'a.a' : 15, 'a.b' : 10,
                    'b.a' : 15, 'b.b' : 10,
                    'c.a' : 15, 'c.b' : 20 },
        descr='link_containers involved'),

    P( dict( a=5, b=dict(a='c',b=10), c=dict(a=15, b=20)),
        expected={  'a'   : 5,
                    'b.a' : 15, 'b.b' : 10,
                    'c.a' : 15, 'c.b' : 20 },
        descr='link_containers involved 2'),

    P( dict(a=dict( a=5  , b=dict( x=10, y='b', z='c')),
            b=dict( a='c', b=dict( x=20, y='c', z='c')),
            c=dict( a=15 , b=dict( x=30, y=40 , z=50 ))),
        expected={  'a.a' : 5, 'a.b.x':10, 'a.b.y':40, 'a.b.z':50,
                    'b.a' :15, 'b.b.x':20, 'b.b.y':40, 'b.b.z':50,
                    'c.a' :15, 'c.b.x':30, 'c.b.y':40, 'c.b.z':50 },
        descr='nested containers'),
]
###############################################

from reporter.link import Link, LinkContainer#, LinkDict

#this from r5000!
from reporter.link import LinkBase
class LinkDict( dict):
    def __init__( me, *args, **kargs):
        dict.__init__( me, *args, **kargs)
        for k,v in me.iteritems():
            if isinstance( v, LinkBase):
                me[ k] = v.dereference( me)

    def __setattr__( me, name, value):
        me[ name ] = value
    def __getattr__( me, name):
        try:
            return me[ name ]
        except KeyError:
            raise AttributeError, name


def test_case_factory( case_params, TestCaseClass):
    class LinkCase( TestCaseClass):
        name = case_params.pop('description')
        params = case_params
    return LinkCase


class TestContainer( LinkContainer):
    def __init__( me, prefix ='', **kargs):
        for k,v in kargs.iteritems():
            setattr( me, k, v)
        #me.__dict__.update( kargs)
        LinkContainer.__init__( me, prefix)

    def __str__( me):
        return str( me.__dict__)


def build_links( data_dict, prefix='', depth=0):
    dic = data_dict.copy()
    for k in dic:
        if isinstance( dic[ k], dict):
            pfx = ''
            if depth:
                pfx = k
                if prefix:
                    pfx = prefix + '.' + pfx
            depth += 1
            dic[k]=TestContainer( prefix=pfx, **build_links( dic[k], prefix=pfx, depth=depth))
            depth -= 1
        if isinstance( dic[ k], str):
            dic[ k] = Link( dic[k])
    return dic

class RegularTestCase( Case):
    def setUp( me):
        me.test_data = LinkDict( **build_links( me.params.obj))

    def test_( me):
        for attr_name, expected_val in me.params.expected.iteritems():
            v = get_attrib( me.test_data, attr_name)
            me.assertEqual( v, expected_val, me.name+' '+attr_name)


if __name__ == '__main__':
    import sys
    sys.setrecursionlimit(100)
    s = get_test_suite( all_cases, RegularTestCase)
    unittest.TextTestRunner( unittest.sys.stdout, verbosity=3, descriptions=True, ).run( s)


# vim:ts=4:sw=4:expandtab
