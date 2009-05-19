#$Id$
# -*- coding: cp1251 -*-

from reporter.engine.excel.builder import *

font_commands = 'name size weight slant'.split()
cell_commands = 'width numformat align valign color background pattern'.split()
border_commands = 'top bottom left right'.split()

def style_builder( column_styles):
    for style in column_styles:
        name_ignored, start, end, value = style

        fontv = dict( (cmd, value[ cmd]) for cmd in font_commands if cmd in value)
        bordv = dict( (cmd, value[ cmd]) for cmd in border_commands if cmd in value)
        fmt = dict( (cmd, value[ cmd]) for cmd in cell_commands if cmd in value)

        fmt.update( _border= Border(**bordv), _font= Font(**fontv) )
        yield fmt, start, end


######################################
def column_generator(layout, start =0):
    alfa = ord('A')
    col= {}
    for c in layout:
        h = {c: chr(alfa)}
        col.update(h)
        alfa+=1
    return col

######################################

from reporter.view.view_base import FldViewBase, ViewAttr, CmdDescr
class XlsView( FldViewBase):
    view_context_name = 'xls'
    inherit = 'view'

    common_attribs = dict(
        num_format          = ViewAttr( '@'     , command=CmdDescr('numformat')),
        width               = ViewAttr( None    , inherit=False,
                                                  command=CmdDescr('width')),
        align               = ViewAttr( 'l'     , command=CmdDescr('align',
                                    value_convert=dict( l='left', r='right', c='center'))),
        valign              = ViewAttr( 't'     , command=CmdDescr('valign',
                                    value_convert=dict( c='vcenter', t='top', b='bottom'))),
        font_name           = ViewAttr( 'Times New Roman', command=CmdDescr('name')),
        font_size           = ViewAttr( 10      , command=CmdDescr('size')),
        font_bold           = ViewAttr( False   , command=CmdDescr('weight')),
        font_italic         = ViewAttr( False   , command=CmdDescr('slant')),
        border              = ViewAttr( ''      , command=CmdDescr( dict( u='top', d='bottom',
                                                                          l='left', r='right'))),
        text_color          = ViewAttr( 'black' , command=CmdDescr('color')),
        background          = ViewAttr( None    , command=CmdDescr('background')),
        background_pattern  = ViewAttr( 0       , command=CmdDescr('pattern')),
    )

from pdf import PdfContextViewer
class ExcelContextViewer( PdfContextViewer):
    DEFAULT_OUTPUT_ENCODING = 'cp1251'
    view_context_name = XlsView.view_context_name

    def apply_view( me, view, style_sequence, start_row, is_label =False):
        view.switch_formatted( is_label)
        if is_label:
            attribs = view.label_attribs
        else:
            attribs = view.data_attribs

        fmt = {}
        for attr_name, attr_descr in attribs.iteritems():
            val = me.get_view_attr( view, attr_name)
            if val is not None and attr_descr.command:
                for cmd_name, cmd_value in attr_descr.command.command_names_and_values( val):
                    fmt[ cmd_name] = cmd_value
        style_sequence.add( 'format', fmt, start_row)

    def make_output( me, filename, pagesize=None, layout =None, view_descr =None):
        table_data, column_styles = me.make_embeddable_output( layout, view_descr)

        if isinstance( filename, unicode):
            filename = filename.encode('utf8')

        builder = XcelBuilder( filename)
        s = builder.sheet()
        aggr_idx = []
        from reporter.engine.excel.data_parse import data_parse
        data, aggregate_rows = data_parse( table_data, aggr_idx)
        for fmt, start, end in style_builder( column_styles):
            #Razpredelqne na dannite spored formata
            x,y = start
            if  end[1] == -1: end = (end[0], None)
            ex,ey= end
            assert x == ex
            width = fmt.pop( 'width', None)

            s.column( x, width=width)         # TODO row-height
            c = s.range( x=x,y=y, values= data[x][y:ey], vert= True)
            c.format( **fmt)

        from reporter.engine.excel.visitor import Visitor
        visitor = Visitor()
        builder.walk( visitor)


from reporter.view.pdf import ViewRedovaPdf
class ViewRedovaXl( ExcelContextViewer, ViewRedovaPdf):
    def get_aggr_row( me):
        from reporter.row import AggrRow
        row_idx  = []
        aggr_idx = []
        functors = []
        x = None
        for r in me.rows:
            if not isinstance(r, AggrRow): continue
            aggr_idx.append(me.rows.index(r))
            x =r._calc_.keys()  # vzimane na poletata, koito se smyatat
            #vzima funkciyata, 4rez koyato se smyata
            for pole in x:
                functors.append(r._calc_[pole].function)

                for agr in r.rows:  #iteraciq po redovete, vurhu koito smqta
                    if agr in me.rows:
                        row_idx.append( me.rows.index(agr)) #index na reda koito se smqta v vsichki redov
        #Ne se izpolzva zasega
        #                         for z in x :
        #                             #Tova vzima value na reda za dadenoto pole!!!
        #                             view = me.get_view( z, context=r)
        #                             cell = me.convert_data( me.get_fld_data( agr, z),view )
        #Zasega Priemame che se izpulnqva edna formula na mnogo poleta
        return functors, row_idx, x, aggr_idx

    def make_formula(me, sheet, layout):
        avg = 'avg'
        functions = {
                    sum :   'SUM(',
                    avg :   'AVERAGE(',
                    min :   'MIN(',
                    max :   'MAX(',
                    len :   'COUNT(',
                    }
        formula_col =   []
        funktor, row_idx, calc, agr_idx = me.get_aggr_row() #izpulnqva purvata formula namerena!!!
        col =column_generator(layout)
        aggr_idx = []
        if calc:
            calc.append('percent')
        formuli = []
        ##########################Sglobqvane na Formulata
        for f in funktor:
            for c in calc:
                for a in agr_idx:
                    b = agr_idx.pop(agr_idx.index(a))
                    aggr_idx.append(b+2)#pribavqme edno zaradi label-a ( labels, ne se sadurjat v spr.rows !?)
                    agr_idx.append(b)
                formula= '='
                column = col[c]
        #Nachalna Faza -> Otvarqne na formula
                sep    = ','
                if f in functions:
                    func =  functions[f]
                formula = formula + func
        #Osnovna Faza -> natrupvane na vsivhki kletki uchastvashti v formulata
                for idx in row_idx:
                    row =str(idx+2) #pribavqme edno zaradi label-a ( labels, ne se sadurjat v spr.rows !?)
                    if idx == (len(row_idx)-1): sep = ')'
                    formula+= column + row + sep

                formula_col.append(column)
                formuli.append(formula)
        ####################################################
        return formuli, aggr_idx, formula_col

    def make_embeddable_output( me, layout =None, view_descr =None):
        me.update( layout, view_descr)
        data, style_commands = me.get_table_data( me.layout)
        return data, style_commands


###########################################################

from reporter.view.txt import ViewCrosstabTxt
from txt import CrosstabVisitorTxt
from sequence_rle import SequenceRLE
class ViewCrosstabXl( ExcelContextViewer, ViewCrosstabTxt):
    class Visitor( CrosstabVisitorTxt):
        def __init__( me, viewer):
            CrosstabVisitorTxt.__init__( me, viewer)
            me.column_styles = []

        def append_txt( me, txt, view):
            col_idx = len( me.output_row)
            try:
                style = me.column_styles[ col_idx]
            except IndexError:
                style = SequenceRLE( col_idx)
                me.column_styles.append( style)
            me.viewer.apply_view( view, style, len( me.table_data))
            me.output_row.append( txt)

    def make_embeddable_output( me, layout =None, view_descr =None):
        me.update( layout, view_descr)
        v = me.Visitor( me)
        me.walk_table( v)
        table_data = v.table_data
        style_commands = me.styles2commands( v.column_styles)
        return table_data, style_commands


##########################

if 0:
    from reporter.view.pdf import ViewPolevaPdf
    #class ViewPolevaXl( ExcelContextViewer, ViewPolevaPdf):




# vim:ts=4:sw=4:expandtab

