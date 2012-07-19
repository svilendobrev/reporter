#$Id$


from reporter.engine.util.struct import DictAttr

class FldType( object):
    view_defaults = DictAttr() # TODO to be flattened for type inheritance

    @classmethod
    def to_str( cls, val, format_str):
        if format_str is None:
            format_str = cls.view_defaults.format_str
        return cls._format( format_str, val)

    @classmethod
    def _format( cls, format_str, val):
        return format_str % val


class Float( FldType):
    view_defaults = DictAttr(
        empty_value = 0,
        format_str  = '%.2f',
        align       = 'r',
    )

class Int( FldType):
    view_defaults = DictAttr(
        empty_value = 0,
        format_str  = '%d',
        align       = 'r',
    )

class Text( FldType):
    view_defaults = DictAttr(
        empty_value = '',
        format_str  = '%s',
        align       = 'l',
    )

class Date( FldType):
    view_defaults = DictAttr(
        empty_value = '',
        format_str  = '%d.%m.%Y',
        align       = 'l',
    )

    @classmethod
    def _format( cls, format_str, val):
        return val.strftime( format_str)


class DateTime( Date):
    view_defaults = DictAttr(
        empty_value = '',
        format_str  = '%d.%m.%Y %H:%M:%S',
        align       = 'l',
    )

class DataF( FldType):
    ''' data field type is for declaring fields that are not to be shown anywhere,
        but to be used as arguments for other fields '''
    view_defaults = DictAttr(
        empty_value = '',
        format_str  = '%s',
        align       = 'l',
    )
    @classmethod
    def _format( cls, format_str, val):
        return str(val)


from view.txt import FldView
from view.wx_view import wxBrowsableView, wxPrintoutView
from view.pdf import PdfView
from view.html import HtmlView
from view.view_base import FldViewBase, get_label_kargs
from view.xl_view import XlsView
from reporter.engine.util.attr import issubclass, get_attrib

class ViewDef( object):
    views_to_create = [ FldView, wxBrowsableView, PdfView, wxPrintoutView, XlsView ]

    def __init__( me, *views):
        me.views = {}
        for v in views:
            k = v.view_context_name
            assert isinstance(v,FldViewBase)
            assert k not in me.views, 'multiple definition of view %s' % k
            me.views[ k] = v
        me.prepare_views()

    def inherit( me, parent, **inh_settings):
        assert parent
        for name,pv in parent.views.iteritems():
            v = me.views.get( name)
            if not v:
                me.views[ name] = pv.copy_strip_inherited() #FIXME copy DONT strip inherited
                setattr( me, name, me.views[ name])
            else:
                v.update_from_view( pv, lock=True)

    def zzzz_get_view(me, name):
        return me.views.get( name)

    def prepare_views( me):
        for view_factory in me.views_to_create:
            name = view_factory.view_context_name
            me.views.setdefault( name, view_factory())
        me.perform_view_inheritance()

    def perform_view_inheritance( me):
        for k,v in me.views.iteritems():
            assert k == v.view_context_name, ('ERROR: wrong name %s for view type %s' %
                                                (k, v.__class__.__name__))
            setattr( me, k, v)
            v.do_inheritance( me.views)


class Style( ViewDef):
    def __init__( me, parent, *views):
        ViewDef.__init__( me, *views)
        if parent: me.inherit( parent)


from link import LinkContainer
class FieldDef( LinkContainer, ViewDef):
    def __init__( me, label =None,
                data =None, type =Text, model =None,
                setup =None, style=None,
                views =(), **views_as_kargs):
        me.typ   = type
        me.model = model
        assert not callable( model)
        me.data  = data
        me.setup = setup
        me.label = label

        if isinstance( views, dict):
            views = views.values()
        elif isinstance( views, tuple):
            views = list( views)
        elif isinstance( views, FldViewBase):
            views = [ views ]
        views += views_as_kargs.values()

        # inheritance is performed first in order to set the correct view prefix to links
        ViewDef.__init__( me, *views)
        me._set_view_defaults()
        if style:
            me.inherit( style)
        LinkContainer.__init__( me)

    def _set_view_defaults( me):
        label_kargs = get_label_kargs( me.label)
        view_defaults = getattr( me.typ, 'view_defaults', {})
        for v in me.views.itervalues():
            v.label.update( label_kargs, only_missing=False,
                            lock=True, not_inheritable=True)
            v.update( view_defaults, only_missing=False,
                        lock=False, not_inheritable=True)
            v.data_type = me.typ

    def inherit( me, parent_field, *a, **ka):
        if isinstance( parent_field, me.__class__):
            if me.model is None: me.model = parent_field.model
            if me.data is None: me.data = parent_field.data
            if me.label is None: me.label = parent_field.label
        ViewDef.inherit( me, parent_field)
        me._set_view_defaults()

    def copy( me, ignore_style =True):
        if ignore_style:
            views = dict( (name, view.copy_strip_inherited())
                          for name,view in me.views.iteritems())
        else:
            views = me.views
        return me.__class__( label=me.label
                            , data=me.data
                            , type=me.typ
                            , model=me.model
                            , setup=me.setup
                            , **views)


from reporter.engine.util.struct import DictAttr
from reporter.engine.util.attr import iscollection, issubclass
from reporter.engine.util.func2code import get_attr_usage

import itertools as it

class Fields( DictAttr, ViewDef, LinkContainer):
    def __init__( me, *args, **kargs):
        from spravka import Spravka
        DictAttr.__init__( me, **kargs) # links need this when dereferencing,
                                        # also needed for inheritance by flattening
        style = Style( None)
        for v in args:
            #if iscollection(v):
            #    style.update( get_views_from_args(v))
            if isinstance( v, FldViewBase):
                style.inherit( Style( None, v))
                #style[ v.view_context_name] = v
            elif isinstance( v, Style):
                style.inherit( v)
                #style.update( v.views)
            elif isinstance( v, me.__class__):
                me.inherit( v, ignore_style=style)
            elif issubclass( v, Spravka):
                me.inherit( v.description, ignore_style=style)

        ViewDef.__init__( me, *style.views.itervalues())
        views = me.views # to be deleted from me

        for k in me.keys(): # flatten all field containers
            v = me[k]
            if isinstance( v, me.__class__):
                me.update( v.get_fields())
            if not isinstance( v, FieldDef):
                del me[k]

        s = Style( None, *views.itervalues())
        for field in me.itervalues():
            assert isinstance( field, FieldDef), 'neshto za zachistvane e ostanalo'
            field.inherit( s, lock=True, not_inheritable=True)

        me.dereference( me) # FIXME only the outermost container should do this

    def get_fields( me):
        res = dict()
        for k,v in me.iteritems():
            if isinstance(v, FieldDef):
                res[k] = v
            elif isinstance(v, me.__class__):
                res.update( v.get_fields()) # TODO how to handle duplicates in nested containers
        return res

    def get_field_deps( me, field, container, skip=()):
        if not callable( field.data):
            return
        deps = list( get_attr_usage( field.data, [0,]))
        res = set( deps)
        skip = skip or set()
        skip.update( res)
        for name in deps:
            if name not in container:
                print 'unknown', name
                continue
            if name in skip:
                print 'skip', name
                continue
            field = container[ name]
            sub_deps = me.get_field_deps( field, container, skip=skip)
            if sub_deps:
                res.update( sub_deps)
        return res

    def inherit( me, container, names =(), names_prefix ='', ignore_style =True):
        if isinstance( names, str):
            names = names.split()

        for name, field in container.get_fields().iteritems():
            if names and name not in names:
                continue
            if 0:
                names2inherit = set([ name ])
                deps =  me.get_field_deps( field, container)
                if deps:
                    print name, '->', deps
                if deps:
                    names2inherit.update( deps)

                for inh_name in names2inherit:
                    if inh_name not in me:
                        assert getattr( me, inh_name, None) is None
                        setattr( me, inh_name, field.copy( ignore_style=ignore_style))
            else:
                if isinstance( names, dict):
                    name = names.get( name) or name
                name = names_prefix + name
                if name not in me:
                    setattr( me, name, field.copy( ignore_style=ignore_style))
                else:
                    me[ name].inherit( field)


# vim:ts=4:sw=4:expandtab
