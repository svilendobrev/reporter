#$Id$
# -*- coding: utf-8 -*-

class Spravka( object):
    ''' Базовия клас за всички справки'''
    description = dict()
    model_mapping = dict()

    def __init__( me, **kargs):
        assert me.description and 'At least one field must be declared'
        me.init( **kargs)

    def init( me, **kargs):
        '"init" is prettier than "__init__"'
        me.__dict__.update( kargs)

    def query( me, context, dbcontext=None):    #db, project и прочие
        return context

    def refresh( me, context, container =None, data_obj =None, dbcontext=None):
        res = None
        if container is not None and data_obj is not None:
            res = me._refresh_from_parent( container, data_obj, context)
        if res is None:
            res = me.query( context, dbcontext=dbcontext)
        me.data_source = res

    def _refresh_from_parent( me, parent, parent_data_source, parent_context):
        return None # or not None to avoid query

    class input_params( object): pass

################################

from svd_util.attr import get_attrib, issubclass

def set_container_data( container, data_obj, description, context, **kargs):
    for name, fld in description.iteritems():
        if issubclass( fld.typ, Spravka):
            subrep = isinstance( fld.setup, dict) and fld.typ( **fld.setup) or fld.typ()
            if callable( fld.setup):
                fld.setup( container, subrep)
            o = data_obj
            if fld.model:
                o = get_attrib( data_obj, fld.model)
            subrep.refresh( context, container, o, **kargs)
            setattr( container, name, subrep)
        elif fld.model:
            try: value = get_attrib( data_obj, fld.model)
            except AttributeError:
                value = None
                print container.__class__.__name__, '''
warning: query obj has no attr "%s"''' % fld.model
            setattr( container, name, value)


def update_from_description( descr, all):
    for name, field in descr.iteritems():
        all[ name] = field.copy() # preserve parents from further changes


from field import FieldDef
def update_from_model_mapping( model_mapping, all):
    for k,v in model_mapping.iteritems():
        setup_kargs = { callable(v) and 'data' or 'model' : v }
        if k in all:
            for attr, val in setup_kargs.iteritems(): setattr( all[k], attr, val)
        else:
            all[ k ] = FieldDef( **setup_kargs)

from field_container import _FieldContainerMeta, FieldSource, flatten_dict

def inherit_dict_attributes( cls, bases, dct, flatten_names =()):
    for name in flatten_names:
        flatten_dict( name, bases, dct)
        setattr( cls, name, dct[ name])


class _PolevaMeta( _FieldContainerMeta):
    _field_sources = [
        FieldSource( 'model_mapping', inherit=True, update_func = update_from_model_mapping),
        FieldSource( 'description', inherit=True), #, update_func = update_from_description),
    ]
    def __init__( cls, name, bases, dct): #XXX __new__ has already done the inheritance here
        cls.description.update( cls._all)
        dicts2flatten = '''
            layout_defaults
            layout_commands
            page_description
            '''.split()
        inherit_dict_attributes( cls, bases, dct, dicts2flatten)


class PolevaSpravka( Spravka):
    __metaclass__ = _PolevaMeta
    description = dict()
    model_mapping = dict()
    layout = ''
    layout_commands = dict()

    def refresh( me, context, container =None, data_obj =None, dbcontext=None):
        Spravka.refresh( me, context, container, data_obj, dbcontext=dbcontext)
        set_container_data( me, me.data_source, me.description, context, dbcontext=dbcontext)

############################################

def update_from_rowtype( RowType, all):
    if RowType:
        names = ('_extcalc_', '_calc_', '_set_',) #reversed for update
        for name in names:
            try:
                descr = getattr( RowType, name)
            except AttributeError:
                pass
            else:
                all.update( descr)


from field_container import _DescrInheritanceMeta
from row_classifier import RowClassifier
class _RedovaMeta( _DescrInheritanceMeta):
    _field_sources = [
        FieldSource( 'model_mapping', inherit=True , update_func = update_from_model_mapping),
        FieldSource( 'description'  , inherit=True), #, update_func = update_from_description),
        FieldSource( 'RowType'      , inherit=False, update_func = update_from_rowtype),
    ]
    def __new__( cls, name, bases, dct):
        dct.setdefault( 'groups', {}) # disable inheritance for group definitions
        return _DescrInheritanceMeta.__new__( cls, name, bases, dct)

    def __init__( cls, name, bases, dct):
        _DescrInheritanceMeta.__init__( cls, name, bases, dct)
        cls.description.update( cls._all)
        dicts2flatten = '''
            layout_defaults
            page_description
            '''.split()
        inherit_dict_attributes( cls, bases, dct, dicts2flatten)
        if isinstance( cls.layout, str):
            cls.layout = cls.layout.split()
        else:
            assert isinstance( cls.layout, (list, tuple)), 'ERROR: wrong layout type'


class RedovaSpravka( Spravka):
    ''' Oгъвка на класификатора на редове (RowClassifier),
        която добавя интерфейс за дефиниране на полетата.
    '''
    __metaclass__ = _RedovaMeta
    RowType = None

    class GroupDef( object):
        '''object for defining groups in a declarative manner'''
        ALL, AGG_HIDE, AGG_ONLY, HIDE = range(4)

        def __init__( me, threshold, aggregators, subgroups=None, filter_func =None,
                    view_mode=ALL):
            me.threshold = threshold
            me.aggregators = aggregators
            me.filter_func = filter_func
            me.subgroups = subgroups
            me.view_mode = view_mode

    # grouping rows
    preserve_input_order = False # True = packets are ordered as rows come from input
                                 # False= all rows of a type are in the same packet
    layout = [] # column order
    groups = {} # name : GroupDef()

    def __init__( me, **kargs):
        me._setup_classifier()
        if me.RowType is None:
            me._create_row_type()

        Spravka.__init__( me, **kargs)

    def _create_row_type( me):
        simple = dict()
        calc = dict()
        for k,v in me.description.iteritems():
            if callable( v.data):
                calc[k] = v
            else:
                simple[k] = v
        from row import Row
        class SprRow( Row):
            _set_ = simple
            _calc_ = calc
        me.RowType = SprRow

    def rows( me):
        group_defs = getattr( me.groups, 'data', me.groups) # FIXME
        if not group_defs:
            return me.row_classifier._rows_and_packets
        from packet import Packet
        res = []
        for row in me.row_classifier._rows_and_packets: # FIXME row_classifier shd do this
            if isinstance( row, Packet):
                packet = row # rename
                view_mode = group_defs[ packet.group.name].view_mode
                if view_mode == me.GroupDef.ALL or view_mode == me.GroupDef.AGG_HIDE:
                    res += packet.rows
                if view_mode == me.GroupDef.ALL or view_mode == me.GroupDef.AGG_ONLY:
                    res += packet.agg_rows
        return res

    def add( me, obj, context):
        r = me.RowType()
        r.db_object = obj
        set_container_data( r, obj, me.description, context)
        me.row_classifier.add( r)

    def _setup_classifier( me):
        me.row_classifier = RowClassifier( me.preserve_input_order)
        group_defs = getattr( me.groups, 'data', me.groups) #FIXME
        if not group_defs: # FIXME гадно спасяване за момента
            group_defs = me.groups = dict( za_nomer_na_red_FIXME = me.GroupDef( None, None) )
        for name, g in group_defs.iteritems():
            me.row_classifier.group(
                threshold=g.threshold,
                aggregators=g.aggregators,
                name=name,
                filter_func=g.filter_func)

    def refresh( me, context, container =None, data_obj =None, **kargs):
        Spravka.refresh( me, context, container, data_obj, **kargs)
        me._setup_classifier()
        for obj in me.data_source:
            me.add( obj, context)
        me.row_classifier.end()


# vim:ts=4:sw=4:expandtab
