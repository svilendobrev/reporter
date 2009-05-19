#$Id$
# -*- coding: cp1251 -*-

if 1:
    def conv(txt, to='utf-8'):
        if txt is None:
            return ''
        if isinstance( txt, unicode):
            return txt.encode(to)
        encodings2try = ['utf-8', 'cp1251']
        for enc in encodings2try:
            try:
                s = unicode( str(txt), enc)
                return s.encode(to)
            except UnicodeDecodeError:
                pass
        return txt
else:
    def conv(txt): # FIXME not working properly for reportlab
        if txt is None:
            return ''

        try:
            return txt.encode('utf-8')
        except UnicodeDecodeError:
            print txt
            s = unicode( str(txt), 'cp1251')
            return s.encode('utf-8')


from reporter.engine.util.attr import get_attrib

class ViewerBase( object):
    view_context_name = None
    DEFAULT_OUTPUT_ENCODING = 'utf-8'

    def __init__( me, spr):
        me.spr = spr
        me.view_descr = {}
        for name, flddef in me.spr.description.iteritems():
            # some fields may have no view as they are not shown anywhere
            me.view_descr[ name] = getattr( flddef, me.view_context_name, None)
        me.layout = spr.layout
        if not me.layout:
            me.layout = me.make_default_layout()

    def conv( me, txt):
        return conv( txt, me.DEFAULT_OUTPUT_ENCODING)

    def convert_label( me, view):
        view.switch_formatted( is_label=True)
        return me.conv( me.get_view_attr( view, 'label.text'))

    def convert_data( me, data, view):
        view.switch_formatted( is_label=False)
        from reporter.spravka import Spravka
        if isinstance( data, Spravka):
            from reporter.common import Viewer
            subv = Viewer( data, dc=me.view_context_name)
            kargs4subviewer = me.get_view_attr( view, 'kargs4subviewer') or {}
            return subv.make_embeddable_output( **kargs4subviewer)
        return me.conv( view.fld2str( data) )

    def get_fld_data( me, r, name):
        return getattr( r, name, '')

    def get_view( me, name, context):
        raw_view = me.view_descr.get( name)
        return me.calc_view( raw_view, context, name)

    def calc_view( me, raw_view, context, name):
        view = calc_by_context( raw_view, context)
        if view is None or ( hasattr( view, 'validate') and view.validate()):
            print 'ERROR: Missing or invalid view data for %(name)s' % locals()
        view.context = context
        return view

    def get_view_attr( me, view, attr_name):
        res = view.eval( attr_name)
        if res is None:
            return me.get_default( view=view, attr_name=attr_name)
        return res

    def get_view_attr_translated( me, view, attr_name):
        res = view.eval( attr_name)
        if res is None:
            return view.translate_value( attr_name,
                                        me.get_default( view=view, attr_name=attr_name))
        return view.translate_value( attr_name, res)

    def get_view_attr_static( me, field_name, view_attr_name):
        ''' returns view attribute value if it is data independent, otherwise returns None '''
        raw_view = me.view_descr[ field_name]
        if not callable( raw_view):
            attr = getattr( raw_view, view_attr_name)
            if not callable( attr):
                return attr
        return None

    def get_default( me, attr_name, view =None, default =None):
        # FIXME тука що търся във view след като неговите defaults са му сетнати
        # още след наследяванията
        # layout_defaults явно не е за атрибути на view-то а само за страничните неща margins etc.
        last_name = attr_name.split('.')[-1]
        spr_defaults = getattr( me.spr, 'layout_defaults', {})
        res = spr_defaults.get( last_name)
        if res is None and view:
            res = get_attrib( view, attr_name)
        if res is None:
            res = default
        return res

    def update( me, layout, view_descr):
        if view_descr:
            me.view_descr.update( view_descr)
        me.layout = layout or me.layout


from sequence_rle import SequenceRLE

class ViewRedovaBase( ViewerBase):
    def __init__( me, spr):
        ViewerBase.__init__( me, spr)
        me.rows = me.spr.rows()

    def apply_view( me, view, style_sequence, start_row, is_label =False):
        pass
        #style_sequence.add( 'ime', view, start_row)
    def convert_row( me, row, row_txt, is_label=False): return row_txt

    def make_default_layout( me):
        return me.view_descr.keys()

    def get_table_data( me, layout):
        table_data = []
        current_labels = None
        column_styles = []

        for r in me.rows:
            new_labels = []
            field_views = []
            row = []
            is_empty_labels = True
            for name in layout:
                view = me.get_view( name, context=r)
                field_views.append( view)

                label = me.convert_label( view)
                is_empty_labels &= not label    #both bool
                new_labels.append( label)

                cell = me.convert_data( me.get_fld_data( r, name), view)
                row.append( cell)

            if new_labels != current_labels:
                if not is_empty_labels:
                    current_labels = new_labels
                    me.update_styles( field_views, column_styles, len( table_data), is_label=True)
                    table_data.append( me.convert_row( r, new_labels, is_label=True))

            me.update_styles( field_views, column_styles, len( table_data), is_label=False)
            table_data.append( me.convert_row( r, row))

        for style in column_styles:
            style.flush()
        return table_data, column_styles

    def update_styles( me, field_views, column_styles, row_idx, is_label):
        column_idx = 0
        for view in field_views:
            try:
                style = column_styles[ column_idx]
            except IndexError:
                style = SequenceRLE( column_idx)
                column_styles.append( style)
            me.apply_view( view, style, row_idx, is_label)
            column_idx += 1


class ViewPolevaBase( ViewerBase):
    def get_fld_data( me, name):
        return ViewerBase.get_fld_data( me, me.spr, name)

    def get_view( me, field):
        raw_view = field.getFieldData()
        return me.calc_view( raw_view, me.spr, field.name)

    def make_default_layout( me):
        return '\n'.join([ '[ '+name+' ]' for name in me.view_descr ])


def calc_by_context( func, context):
    if callable( func):
        return func( context)
    return func


#############################################

from reporter.engine.util.attr import isiterable
class CmdDescr( object):
    def __init__( me, cmd_name, value_convert =None, value_processor =None):
        me.cmd_name = cmd_name  # dict for command translation or just a name
        me.value_convert = value_convert or {}# map user's values to those you'd like to operate with
        me.value_processor = value_processor # value postprocess func

    def translate_value( me, value):
        return me.value_convert.get( value, value)

    def command_names_and_values( me, value):
        if isinstance( me.cmd_name, dict):
            if isiterable( value, string_is_iterable=True):
                return [ me.value2command( v) for v in value ]
            return ( me.value2command( value), )
        return ( (me.cmd_name, me.process_value( me.translate_value( value)) ), )

    def process_value( me, val):
        if callable(me.value_processor):
            return me.value_processor( val)
        return val

    def value2command( me, v):
        res_name = me.cmd_name.get( v)
        res_val = me.translate_value( v)
        res_val = me.process_value( res_val)
        return res_name, res_val


class ViewAttr( object):
    def __init__( me, default, inherit =True, command =None):
        me.default = default
        me.inherit = inherit
        me.command = command

#############################################


from reporter.link import LinkContainer, Link

class Formatted( LinkContainer):
    def __init__( me, attrib_description, link_prefix ='', **init_attribs):
        me._check_init_args( init_attribs.keys(), attrib_description.keys())
        me.attrib_description = attrib_description

        me.locked_attribs = set() # attribs NOT changeable by inheritance, defaults or anything
        me.inheritable_attribs = set() # no defaults here
        me.update( init_attribs, lock=True)
        me.init_attribs = init_attribs
        LinkContainer.__init__( me, link_prefix)

    def _check_init_args( me, init_args, allowed_args):
        if not set( init_args).issubset( set(allowed_args)):
            print 'ERROR: unknown view attributes:', set( init_args) - set( allowed_args)
            print 'allowed attributes are:', allowed_args
            raise AttributeError

    def get_inheritable_values( me):
        return dict( (name, getattr(me, name)) for name in me.inheritable_attribs)

    def update( me, from_dict,
                only_missing    =False,
                lock            =False,
                not_inheritable =False):

        updated_attribs = set()
        for name, value in from_dict.iteritems():
            if name not in me.attrib_description or name in me.locked_attribs:
                continue
            if only_missing and hasattr( me, name):
                continue
            setattr( me, name, value)
            updated_attribs.add( name)

        if not not_inheritable:
            me.inheritable_attribs.update( updated_attribs)
        if lock:
            me.locked_attribs.update( updated_attribs)

    def set_defaults( me):
        ''' defaults only for attribs that haven't been set from init or inheritance '''
        defaults = dict( (name, value.default) for name, value in me.attrib_description.iteritems())
        me.update( defaults, only_missing=True, not_inheritable=True)

    def translate_value( me, name, value):
        name = name.split('.')[-1]
        attr = getattr( me, name)
        cmd = me.attrib_description[ name].command
        if cmd:
            return cmd.translate_value( value)
        return value

    def __str__( me):
        locked              = ' '.join( me.locked_attribs)
        init_attribs        = ' '.join( me.init_attribs.keys())
        inheritable         = ' '.join( me.inheritable_attribs)
        attrib_description  = ' '.join( me.attrib_description.keys())
        return '''
=================================
locked      = %(locked)s
init_attribs= %(init_attribs)s
inheritable = %(inheritable)s
attrib_descr= %(attrib_description)s
=================================
''' % locals()


class Label( object):
    def __init__( me, text=None, **kargs):
        me.kargs = kargs
        if isinstance( text, str):
            me.kargs['text'] = text
        else:
            pass # a default will be set later


def get_label_kargs( label):
    label_kargs = {}
    if isinstance( label, Label):
        label_kargs = label.kargs
    elif isinstance( label, str):
        label_kargs = dict(text=label)
    return label_kargs


from reporter.field_container import flatten_dict
class _FldViewMeta( type):
    def __init__( cls, name, bases, dct):
        for what in 'common_attribs data_attribs label_attribs'.split():
            dct.setdefault( what, {})
            flatten_dict( what, bases, dct)
            setattr( cls, what, dct[ what])
        cls.label_attribs.update( cls.common_attribs)
        cls.data_attribs.update( cls.common_attribs)

class FldViewBase( LinkContainer):
    view_context_name = None  # the name of view in field description
    inherit = '' # 'parent1 parent2 ... parentN'

    __metaclass__   = _FldViewMeta
    common_attribs  = {}
    data_attribs    = dict(
        format_str  = ViewAttr(None),
        empty_value = ViewAttr(''),
    )
    label_attribs   = dict( text = ViewAttr('') )

    def __init__( me, label =None, kargs4subviewer =None, style =None, **kargs):
        me.kargs4subviewer = kargs4subviewer
        me.context = None # passed as param to callable view attributes
        me.flattened = False

        me._create_formatteds( get_label_kargs( label), kargs)
        if style:
            style_view = style.get_view( me.view_context_name)
            if style_view:
                me.update_from_view( style_view, lock=True)
        LinkContainer.__init__( me)

    def _create_formatteds( me, label_kargs, data_kargs):
        me._data_field = Formatted( me.data_attribs, link_prefix=me.view_context_name, **data_kargs)
        me.label = Formatted( me.label_attribs, link_prefix='label', **label_kargs)
        me.set_defaults()
        me._use_formatted = me._data_field

    def copy_strip_inherited(me):
        ''' repeats the creation of the original
            thus ignoring inheritance and the original context
        '''
        new = me.__class__( kargs4subviewer=me.kargs4subviewer)
        label_kargs = dict( (k,getattr(me.label, k)) for k in me.label.init_attribs)
        data_kargs = dict( (k,getattr(me._data_field, k)) for k in me._data_field.init_attribs)
        new._create_formatteds( label_kargs, data_kargs)
        return new

    def __getattr__( me, name):
        return getattr( me._use_formatted, name)

    def switch_formatted( me, is_label):
        me._use_formatted = is_label and me.label or me._data_field

    def eval( me, name):
        context = me.context
        def attr_getter( self, name):
            attr = getattr( self, name)
            return calc_by_context( attr, context)
        return get_attrib( me, name, getattr=attr_getter)

    def validate(me):
        return False

    def fld2str( me, val):
        if val is None:
            return me.eval('empty_value')
        format_str = me.eval('format_str')
        try:
            return me.data_type.to_str( val, format_str)
        except (AttributeError, TypeError, ValueError), e:
            print 'ERROR: Can NOT convert value to string:', `val`, e
            print 'Expected type: ', getattr( me, 'data_type', 'unknown')
            txt = ''
        return txt

    def do_inheritance( me, views):
        if me.flattened: return
        me.flattened = True
        if me.inherit:
            parents = me.inherit and me.inherit.split() or []
            for parent_name in reversed(parents):
                parent = views.get( parent_name, None)
                if not parent: continue
                parent.do_inheritance( views)
                me.update_from_view( parent)

    def update_from_view( me, parent, **kargs):
        me._data_field.update( me.get_parent_data( parent), **kargs)
        me.label.update( me.get_parent_data( parent.label), **kargs)

    def set_defaults( me):
        me._data_field.set_defaults()
        me.label.set_defaults()

    def get_parent_data( me, parent):
        res = dict()
        for attr, val in parent.get_inheritable_values().iteritems():
            if isinstance( val, Link): # fix inherited links so they refer our type of view
                val = val.clone()
                val.attr_name = val.attr_name.replace( parent.view_context_name,
                                                       me.view_context_name, 1)
            res[ attr] = val
        return res

    def __str__( me):
        return me.__class__.__name__


if __name__ == '__main__':
    v = FldViewBase( a=1, b=2, c=lambda f: f > 5 and f or f*10)
    v.context = 5
    print v.a, v.b, v.c
    print v.eval('a'), v.eval('b'), v.eval('c')


# vim:ts=4:sw=4:expandtab
