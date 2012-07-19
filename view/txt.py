#$Id$


def align_l( txt, sz):  return txt.ljust( sz)
def align_r( txt, sz):  return txt.rjust( sz)
def center( txt, sz):
    print sz
    return txt.center( sz)


def make_border( thickness =1, space =0):
    b = thickness * '|'
    return b.ljust( space)

def left_border( txt, thickness =1, space =0):
    return make_border( thickness, space) + txt

def right_border( txt, thickness =1, space =0):
    return txt + make_border( thickness, space)

def wrap_to_fit( txt, width):
    assert width
    rows = txt.strip().split()
    res = ''
    last_row = res
    for r in rows:
        if len(' '.join( [last_row, r])) > width and last_row:
            res = '\n'.join( [res,r])
            last_row = r
        else:
            if res: res += ' '
            if last_row: last_row += ' '
            res += r
            last_row += r
    return res


from view_base import FldViewBase, ViewAttr
class FldView( FldViewBase):
    view_context_name = 'txt'

    common_attribs = dict(
        align       = ViewAttr( 'l'),
        border      = ViewAttr( None),
        width       = ViewAttr( None), # None = automatic
        indent      = ViewAttr( 0),
        fit         = ViewAttr( 'truncate'), # wrap
    )

    _align_funcs = dict( r=align_r, l=align_l, c=center)

    def format( me, txt, force_width =None, min_number_of_rows =1,
                is_label=False, l_space =0, r_space =0):
        me.switch_formatted( is_label)
        if force_width is None:
            force_width = me.eval( 'width')
        width = force_width
        align_func = me._align_funcs.get( me.eval( 'align'))
        border = me.eval( 'border')

        res = []
        fit = me.eval('fit')
        if fit == 'wrap':
            txt = wrap_to_fit( txt, width)

        cell_rows = txt.split('\n')
        for i in range( min_number_of_rows):
            if i < len( cell_rows):
                s = cell_rows[ i]
            else:
                s = ''
            if align_func and width > len(s):
                s = align_func( s, width)
            if fit == 'truncate':
                s = s[: width]
            s = ' '* me.eval('indent') + s

            if border:
                s = left_border( s, border.count('l'), l_space)
                s = right_border( s, border.count('r'), r_space)
            res.append(s)
        return '\n'.join( res)


class TxtContextViewer( object):
    DEFAULT_OUTPUT_ENCODING = 'cp1251' # TODO get it from some outside config
    view_context_name = FldView.view_context_name

    def make_output( me, layout =None, view_descr =None):
        return me.make_embeddable_output( layout, view_descr)

from view_base import ViewRedovaBase, ViewPolevaBase

####### Redova
class ViewRedovaTxt( TxtContextViewer, ViewRedovaBase):

    def calc_row_height( me, row_cells):
        return max( len( cell_txt.split('\n')) for cell_txt in row_cells)

    class ColumnSizeData( object):
        data_width = None
        border_widths = None

    def calc_column_width( me, column):
        raw_view = me.view_descr[ column]
        def border2widths( s):
            return s and [ s.count(c) for c in 'lr'] or [0,0]

        res = me.ColumnSizeData()
        res.data_width = me.get_view_attr_static( column, 'width')
        border_str = me.get_view_attr_static( column, 'border')
        if border_str:
            res.border_widths = border2widths( border_str)
        if res.data_width and res.border_widths:
            return res

        max_sz = 0
        max_left = 0
        max_right = 0
        for r in me.rows:
            view = me.get_view( column, context=r)

            if not res.data_width:
                fld = me.get_fld_data( r, column)
                label = me.convert_label( view).strip()
                txt = me.convert_data( fld, view).strip()
                fld_sz = max( len(s) for s in txt.split('\n'))
                max_sz = max( max_sz, fld_sz, len( label.strip()) )

            if not res.border_widths:
                widths = border2widths( me.get_view_attr( view, 'border'))
                max_left = max( max_left, widths[0])
                max_right = max( max_right, widths[1])

        if not res.data_width: res.data_width = max_sz
        if not res.border_widths: res.border_widths = [ max_left, max_right ]
        return res

    def make_embeddable_output( me, layout =None, view_descr =None):
        me.update( layout, view_descr)

        me.widths = [ me.calc_column_width( name) for name in me.layout]
        table_data, column_styles = ViewRedovaBase.get_table_data( me, me.layout)

        out=[]
        #pass 2
        for row_cells in table_data:
            out += [ ''.join( row) for row in zip( *row_cells ) ]
        return '\n'.join( out)

    def convert_row( me, row_obj, row_txt, is_label =False):
        row_height = me.calc_row_height( row_txt)
        result = []
        for cell,name,width in zip( row_txt, me.layout, me.widths):
            view = me.get_view( name, context=row_obj)
            txt = view.format( cell, width.data_width,
                                min_number_of_rows= row_height,
                                is_label= is_label,
                                l_space=width.border_widths[0],
                                r_space=width.border_widths[1] )
            txt = txt.split('\n')
            result.append( txt)
        return result


################################################## Crosstab

class CrosstabVisitorTxt( object):
    def __init__( me, viewer):
        me.viewer = viewer

        me.column_field = viewer.layout.column_field
        me.row_field    = viewer.layout.row_field
        me.data_field   = viewer.layout.data_field

        me.table_data = []
        me.widths = []
        me.heights = []

    def append_field( me, row_obj, field_name):
        data = me.viewer.get_fld_data( row_obj, field_name)
        view = me.viewer.get_view( field_name, row_obj)
        txt = me.viewer.convert_data( data, view)#.strip()
        me.append_txt( txt, view)

    def append_view_label( me, corner_name):
        view = me.viewer.view_descr[ corner_name]
        label = me.viewer.convert_label( view)
        me.append_txt( label, view)

    def update_max_width( me, widths, pos, new_width):
        try:
            if widths[ pos] < new_width:
                widths[ pos ] = new_width
        except IndexError:
            widths.append( new_width)

    def append_txt( me, txt, view):
        cell_lines = txt.split('\n')
        w = max( len(s) for s in cell_lines )
        me.update_max_width( me.widths, len( me.output_row), w)
        h = len( cell_lines)
        me.update_max_width( me.heights, len( me.table_data), h)
        me.output_row.append( (txt, view))

    # protocol implementation
    def top_left( me):
        me.append_view_label( 'top_left')
    def top_right( me):
        me.append_view_label( 'top_right')
    def bottom_left( me):
        me.append_view_label( 'bottom_left')
    def bottom_right( me):
        me.append_view_label( 'bottom_right')

    def open_row( me):
        me.output_row = []
    def close_row( me):
        me.table_data.append( me.output_row)

    def column_label( me, xp):
        me.append_field( xp.rows[0], me.column_field.field_name)
    def row_label( me, yp):
        me.append_field( yp.rows[0], me.row_field.field_name)

    def fact_field( me, yp, xp):
        data_rows = set( xp.rows) & set( yp.rows)
        if data_rows:
            row = me.data_field.aggregator and me.data_field.aggregator( data_rows) or data_rows.pop()
            me.append_field( row, me.data_field.field_name)
        else:
            me.append_view_label( 'empty_cell')

    def row_total( me, yp):
        me.append_field( yp.agg_rows[0], me.data_field.field_name)
    def column_total( me, xp):
        me.append_field( xp.agg_rows[0], me.data_field.field_name)


from reporter.view.view_base import ViewRedovaBase
class ViewCrosstabTxt( TxtContextViewer, ViewRedovaBase):
    Visitor = CrosstabVisitorTxt

    def __init__( me, spr):
        ViewRedovaBase.__init__( me, spr)
        me.layout = spr.layout
        for name in 'top_left top_right bottom_left bottom_right empty_cell'.split():
            view_def = getattr( me.layout, name)
            view = getattr( view_def, me.view_context_name)
            me.view_descr[ name] = view

    def convert_row( me, cells, widths, row_height):
        res = []
        i = 0
        for c in cells:
            width = widths[ i]
            cell_txt, view = c
            cell_txt = view.format( cell_txt, width, min_number_of_rows= row_height).split('\n')
            res.append( cell_txt)
            i += 1
        return res

    def make_embeddable_output( me, layout =None, view_descr =None):
        me.update( layout, view_descr)
        v = me.Visitor( me)
        me.walk_table( v)
        out = []
        i = 0
        for row_cells in v.table_data:
            row_cells_txt = me.convert_row( row_cells, v.widths, v.heights[ i])
            out += [ ''.join( row) for row in zip( *row_cells_txt) ]
            i += 1
        return '\n'.join( out)

    def walk_table( me, visitor): #left to right, top down
        column_field = me.layout.column_field
        row_field = me.layout.row_field
        x_group = me.spr.row_classifier.get_group_by_name( column_field.group_name)
        y_group = me.spr.row_classifier.get_group_by_name( row_field.group_name)
        v = visitor

        v.open_row()
        v.top_left()
        for xp in x_group.packets:
            v.column_label( xp)

        if row_field.show_total:
            v.top_right()
        v.close_row()

        for yp in y_group.packets:
            v.open_row()
            v.row_label( yp)
            for xp in x_group.packets:
                v.fact_field( yp, xp)

            if row_field.show_total:
                v.row_total( yp)
            v.close_row()

        v.open_row()
        if column_field.show_total:
            v.bottom_left()
            for xp in x_group.packets:
                v.column_total( xp)

            if row_field.show_total:
                v.bottom_right()
        v.close_row()


####################################################### Poleva

from reporter.engine.ui import layout
from reporter.engine.ui.fielddata import FieldData

class LayoutField( layout.Field):
    def getFieldData( me):  # **fielddata won't work
        return me.fielddata

class Panel( layout.Panel):
    Field = LayoutField

class ViewPolevaTxt( TxtContextViewer, ViewPolevaBase):
    class PanelVisitor( Panel.Visitor):
        def __init__( me, viewer):
            me.all_rows = []
            me.viewer = viewer
        def openRow( me, row):
            me.row = []
        def openField( me, field):
            if field.typ == 'input':
                me.row.append( me.viewer.fld2str( field))
        def closeRow( me, row):
            me.all_rows.append( me.row)

        def output( me):
            s = ''
            for r in me.all_rows:
                s += ''.join( r) + '\n'
            return s
    ######################################

    def make_panel( me, layout =None, view_descr ={}):
        if layout is None:
            layout = me.spr.layout
        me.view_descr.update( view_descr)
        field_map = me.spr.layout_commands.copy()
        field_map.update( me.view_descr)
        return Panel( layout, field_map=field_map)

    def fld2str( me, fld):
        view = me.get_view( fld)
        data = me.get_fld_data( fld.name)

        txt   = me.convert_data( data, view)
        label = me.convert_label( view)
        s = view.format( label, is_label=True) + view.format( txt)
        return s

    def make_embeddable_output( me, layout =None, view_descr =None):
        me.update( layout, view_descr)
        p = me.make_panel( layout=me.layout, view_descr=me.view_descr)
        visitor = me.PanelVisitor( me)
        p.walk( visitor)
        return visitor.output()


# vim:ts=4:sw=4:expandtab
