#$Id$
# -*- coding: cp1251 -*-

class Cached( object):
    '''function in obj.__dict__ gets overwritten with it's result'''
    def __init__( me, func, attr):
        me.func = func
        me.attr_name = attr

    def __get__( me, obj, cls): #
        if obj is None:
            return me
        res = me.func( obj)
        setattr( obj, me.attr_name, res)
        return res

class FieldSource( object):
    def __init__( me, name, **kargs):
        me.name = name
        for k,v in kargs.iteritems():
            setattr( me, k, v)

def default_updater( src, dest):
    dest.update( src)

def flatten_dict( what, bases, dct):
    flat = dict()
    for b in bases:
        c = getattr( b, what, None)
        if c:
            flat.update( c)

    target = dct.setdefault( what, {}) # not to replace target's type if any
    for k,v in flat.iteritems():
        target.setdefault( k, v)


def reverse( order):
    res = order[:]
    res.reverse()
    return res

from reporter.engine.util.attr import get_attrib
def manage_descr_inheritance( cls, bases, dct):
    ''' simulates inheritance by overlapping field sources'''
    all = dict()
    for src in reverse( cls._field_sources):
        if src.inherit:
            flatten_dict( src.name, bases, dct)

        update = getattr( src, 'update_func', default_updater)
        if not callable( update):
            print 'wrong updater %s in field_source: %s' % (str( update), str(src))
            update = default_updater
        if src.name in dct:
            update( dct[ src.name], all)
    cls._all = all


class _DescrInheritanceMeta( type):
    ''' metaclass for simulating field_source inheritance;
        extends current description with parent's data
    '''
    _field_sources = []  #where to look for field sources; defines lookup order
    _all = dict() #the result goes here

    def __init__( cls, name, bases, dct):
        manage_descr_inheritance( cls, bases, dct)


from reporter.engine.util.attr import flatten_vars

class _FieldContainerMeta( _DescrInheritanceMeta):
    ''' metaclass that lets a class contain the fields described in _field_sources;
        introduces optimized access to computable fields
    '''
    USE_CACHE = False # True -> calculation is done only once at first field access
    def __new__( cls, name, bases, dct):
        manage_descr_inheritance( cls, bases, dct)

        for k,v in cls._all.iteritems():
            v = getattr( v, 'data', v)
            if callable( v):
                dct[k] = cls.USE_CACHE and Cached( v, k) or property( v)
            else:
                dct[k] = v
        new_cls = type.__new__( cls, name, bases, dct)
        return new_cls

# vim:ts=4:sw=4:expandtab
