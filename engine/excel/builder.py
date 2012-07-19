#$Id$
# -*- coding: utf-8 -*-

class Item( object):
    _delimiter=' '
    def __str__( me):
        return me.__class__.__name__ + '( '+ me._delimiter.join(
                    ('%s=%r' % (k,v))
                    for k,v in me.__dict__.iteritems()
                    if k!='parent' and v is not None
                ) + ' )'
    __repr__ = __str__

class Node( Item):
    def __init__( me, parent):
        me.parent = parent
    class Format: pass  # overide with specific
    def format( me, *a,**k):
        me._format = f = me.Format( *a,**k)
        return f

class _list(list):
    def __str__( me):
        return '\n'.join( ['['] +
                    [ 4*' '+str(x) for x in me
                    ]  + [']'] )
    __repr__ = __str__

class _dict(dict):
    def __str__( me):
        return '\n'.join( ['{'] +
                    [ '\n'.join( 8*' '+str(x) for x in v)
                            for k,v in me.iteritems()
                    ]  + [4*' '+'}'] )
    __repr__ = __str__


class XcelBuilder( Item):
    def __init__( me, filename):
        me.filename = filename
        me.sheets = _list()

    def sheet( me, **k):
        s = Sheet( me, **k)
        me.sheets.append( s)
        return s
    def pagesetup( me):
        p = me._pagesetup = PageSetup()
        return p
    def workbook( me):
        return me.filename

#    _delimiter = '\n   '
    def walk( me, visitor):
        visitor.XcelBuilder( me, True)
        for x in me.sheets:
          x.walk( visitor)
        visitor.XcelBuilder( me, False)

class Sheet( Node):
    def __init__(me, parent, name =None, protect =False ):
        Node.__init__( me, parent)
        assert isinstance( parent, XcelBuilder)
        me.name = name
        me.protect = protect
        me.containers = _dict()

    def _adder( me, factory, *a,**k):
        c = factory( me, *a,**k)
        me.containers.setdefault( factory.__name__, []).append(c)
        return c

    def cell( me, *a,**k):  return me._adder( Cell, *a, **k)
    def row ( me, *a,**k):  return me._adder( Row, *a, **k)
    def column( me, *a,**k): return me._adder( Column, *a, **k)
    col = column
    def range( me, *a,**k): return me._adder( Range, *a, **k)
#    def style( me, *a,**k): return me._adder( Style, *a, **k)
    def page_break( me, *a, **k): return me._adder( Page_Break, *a, **k)
    def outline( me, *a, **k): return me._adder( Outline, *a, **k)
    def merge( me, *a, **k): return me._adder( Merge_Cells, *a, **k)
    def freeze( me, *a, **k): return me._adder( Freeze, *a, **k)
    def walk( me, visitor):
        visitor.Sheet( me, True)
        for typename,items in me.containers.iteritems():
            for x in items:
                x.walk( visitor)
        visitor.Sheet( me, False)

#XXX всички форматски неща могат да са както избрани от палитра/набор,
# така и директно пълно специфицирани.
class Font( Item):
    'many kinds of fontspecs are available, e.g. X, windoze, etc'
    def __init__( me,
            name    =None,
            size    =None,
            weight  =None,  #maybe bold   =bool
            slant   =None,  #maybe italic =bool
            font_charset =None,
            #....
        ):
        me.__dict__.update(
            (k,v) for k,v in locals().iteritems() if k not in 'me k v' )

class Border( Item):
    def __init__( me,
            left        =None,
            right       =None,
            top         =None,
            bottom      =None,
            dia_lt_rb   =None,
            dia_rt_lb   =None,
            #....
        ):
        me.__dict__.update(
            (k,v) for k,v in locals().iteritems() if k not in 'me k v' )

class Format4Cell( Item):
    def __init__( me,
            numformat   =None,
            pattern     =None,
            color       =None,
            _font       =None,
            align       =None,
            valign      =None,
            _border     =None,
            protect     =None,
            background  =None,
            width       =None,
        ):
        me.__dict__.update(
            (k,v) for k,v in locals().iteritems() if k not in 'me k v' )

    def _adder( me, factory, *a,**k):
        c = factory( *a,**k)
        setattr( me, '_'+factory.__name__.lower(), c)
        return c

    def font( me,   *a,**k): return me._adder( Font, *a,**k)
    def border( me, *a,**k): return me._adder( Border, *a,**k)
    #..
    def walk( me, visitor):
        visitor.Format4Cell( me, False)

class Cell( Node):
    Format = Format4Cell
    def __init__( me, parent, x,y,
            value     =None,
            formula   =None,
            validator =None,
            comment   =None,
            name      =None,
            link      =None,
            _format   =None,
            picture   =None,
        ):
        assert isinstance( parent, Sheet)
        me.__dict__.update(
            (k,v) for k,v in locals().iteritems() if k not in 'me k v' )

    def walk( me, visitor):
        if me._format is not None:
            me._format.walk( visitor)
        visitor.Cell( me, False)

class Merge_Cells( Node):
    'Zadava se range ot kletki kato str. primer: "A1:A10" '
    Format = Format4Cell
    def __init__( me, parent,
            range   =None,
            value   =None,
            _format =None,
        ):
        assert isinstance( parent, Sheet)
        me.__dict__.update(
            (k,v) for k,v in locals().iteritems() if k not in 'me k v' )
    def walk( me,visitor):
        if me._format is not None:
            me._format.walk( visitor)
        visitor.Merge( me, False)

class Freeze( Node):
    def __init__( me, parent, y, x, height=12.75, width=8.43, label = False
        ):
        assert isinstance( parent, Sheet)
        me.__dict__.update(
            (k,v) for k,v in locals().iteritems() if k not in 'me k v' )
    def walk( me, visitor):
        visitor.Freeze( me, False)

class Row( Item):
    'metainfo only'
    horz = True
    def __init__( me, parent, nomer,
            width  =None,
            hidden =None,  # =bool, False = shown/hidden Row
            level  =None,  # sets Outlines
        ):
        assert isinstance( parent, Sheet)
        me.__dict__.update(
            (k,v) for k,v in locals().iteritems() if k not in 'me k v' )

    def walk( me, visitor):
        visitor.RowColumn( me, None,  horz=me.horz)

class Column( Row):
    horz = False

class Range( Node):
    '1D or 2D, horz or vert'
    Format = Cell.Format
    def __init__( me, parent, x,y, values, _format =None, vert =False ):
        assert isinstance( parent, Sheet)
        me.__dict__.update(
            (k,v) for k,v in locals().iteritems() if k not in 'me k v' )

    def walk( me, visitor):
        if me._format is not None:
            me._format.walk( visitor)
        visitor.Range( me, False)

class Page_Break( Item):
    def __init__( me,parent, col, row):
        assert isinstance( parent, Sheet)
        me.__dict__.update(
             (k,v) for k,v in locals().iteritems() if k not in 'me k v' )
    def walk( me,visitor):
        visitor.Page_Break(me, False)

class Outline( Item):
    '''You can use Row( level = smt.) instead'''
    def __init__( me, parent, row, level =None):
        assert isinstance( parent, Sheet)
        me.__dict__.update(
             (k,v) for k,v in locals().iteritems() if k not in 'me k v' )
    def walk( me,visitor):
        visitor.Outline(me, False)

class Style( Node):
    def __init__( me, parent, _format):
        Node.__init__( me, parent)
        me._format = _format

# vim:ts=4:sw=4:expandtab
