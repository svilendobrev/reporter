#$Id$


from reportlab.platypus import TableStyle, LongTable
from reportlab.platypus.para import Paragraph

from reporter.engine.rl2wx.fonts import register_font
from sequence_rle import SequenceRLE, SingleCellFormat

def border_processor( border_value):
    return (0.5, 'BLACK') # TODO user control border thickness and color

#####################################################

from txt import FldView, wrap_to_fit
from view_base import ViewAttr, CmdDescr
class PdfView( FldView):
    view_context_name = 'pdf'
    inherit = 'view'

    common_attribs = dict(
        width           = ViewAttr( None, inherit=False), # None = auto
        width_chars     = ViewAttr( None), # None = no limit
        height          = ViewAttr( None), # None = auto
        align           = ViewAttr( 'l'     , command=CmdDescr('ALIGN',
                                                value_convert = { 'l':'LEFT', 'r':'RIGHT',
                                                                'c':'CENTER', '.':'DECIMAL'})
                                  ),
        valign          = ViewAttr( 't'     , command=CmdDescr('VALIGN',
                                                                value_convert=dict( t='TOP', b='BOTTOM', c='MIDDLE'))),
        font_name       = ViewAttr( None    , command=CmdDescr('FONTNAME',
                                                                value_processor=register_font)),
        font_size       = ViewAttr( None    , command=CmdDescr('FONTSIZE')),
        leading         = ViewAttr( None    , command=CmdDescr('LEADING')),
        border          = ViewAttr( None    , command=CmdDescr( dict( u='LINEABOVE' , d='LINEBELOW',
                                                                      l='LINEBEFORE', r='LINEAFTER'),
                                                                value_processor=border_processor)),
        text_color      = ViewAttr( 'BLACK' , command=CmdDescr('TEXTCOLOR')),
        background      = ViewAttr( 'WHITE' , command=CmdDescr('BACKGROUND')),
        space_above     = ViewAttr( 0),                              # empty space above in points
        space_below     = ViewAttr( 0),                              # empty space below in points
        left_padding    = ViewAttr( None    , command=CmdDescr('LEFTPADDING')),
        right_padding   = ViewAttr( None    , command=CmdDescr('RIGHTPADDING')),  # horiz position in the cell
        top_padding     = ViewAttr( None    , command=CmdDescr('TOPPADDING')),    # vertical position in the cell
        bottom_padding  = ViewAttr( None    , command=CmdDescr('BOTTOMPADDING')), # vertical position in the cell
    )
    #common_attribs['indent'] = common_attribs['left_padding']

    def fld2str( me, val):
        txt = FldView.fld2str( me, val)
        fit = me.eval('fit')
        w_chars = me.eval('width_chars')
        if w_chars:
            if fit == 'wrap':
                txt = wrap_to_fit( txt, w_chars)
            elif fit == 'truncate':
                rows = map( lambda r: r[:w_chars], rtxt.split('\n'))
                txt = '\n'.join( rows)
        return txt


#####################################################

class PdfContextViewer( object):
    ''' Common PDF viewer functionalities'''
    overwrite_fonts_in_style = True

    DEFAULT_OUTPUT_ENCODING = 'utf-8'
    view_context_name = PdfView.view_context_name

    def get_doc_args( me, pagesize):
        layout_settings = dict(
            pagesize        = 'pagesize',
            bottom_margin   = 'bottomMargin',
            top_margin      = 'topMargin',
            left_margin     = 'leftMargin',
            right_margin    = 'rightMargin',
        )
        doc_args = {}
        for name, rl_name in layout_settings.iteritems():
            val = me.get_default( name)
            if val is not None: # else reportlab's default
                doc_args[ rl_name] = val
        if pagesize:
            doc_args['pagesize'] = pagesize

        is_landscape = me.get_default('landscape', False)
        from reportlab.lib.pagesizes import landscape, portrait
        doc_args['pagesize'] = (is_landscape and landscape or portrait)( doc_args['pagesize'])
        return doc_args

    def make_output( me, filename, pagesize=None, layout =None, view_descr =None):
        from reportlab.platypus.doctemplate import SimpleDocTemplate
        story = me.make_embeddable_output( layout, view_descr)
        doc_args = me.get_doc_args( pagesize)
        doc = SimpleDocTemplate( filename, **doc_args)
        doc.build( story)
        return doc # always True

    def make_rl_story( me, style_commands, table_data,
                        col_widths =None, row_heights =None, hAlign='CENTER'):
        if not table_data: return [] # unless you rely on how reportlab would handle it
        table = LongTable( table_data, repeatRows=1, colWidths=col_widths, rowHeights=row_heights)
        table.hAlign = hAlign

        style = TableStyle( style_commands)
        res = []

        if 0*'DEBUG STYLE':
            for cmd in style_commands:
                print cmd
        if me.overwrite_fonts_in_style:
            font_name='ArialMT'
            register_font(font_name)
            style.add( 'FONTNAME', (0,0), (-1,-1), font_name, 14)
        if 0*'DEBUG CELLS':
            style.add( 'INNERGRID', (0,0), (-1,-1), 0.25, 'BLACK')
            style.add( 'BOX', (0,0), (-1,-1), 0.25, 'BLACK')
            style.add( 'TOPPADDING', (0,0), (-1,-1), 0)
            style.add( 'LEFTPADDING', (0,0), (-1,-1), 0)
            style.add( 'RIGHTPADDING', (0,0), (-1,-1), 0)
            style.add( 'BOTTOMPADDING', (0,0), (-1,-1), 0)
            from reportlab.platypus.flowables import Spacer
            #res.insert( 0, Spacer( width=0, height=3))

        table.setStyle( style)
        res.append( table)
        return res

    def apply_view( me, view, style, row_idx, is_label =False):
        view.switch_formatted( is_label)
        attribs = view.common_attribs
        for attr_name, attr_descr in attribs.iteritems():
            val = me.get_view_attr( view, attr_name)
            if val is not None and attr_descr.command:
                for cmd_name, cmd_value in attr_descr.command.command_names_and_values( val):
                    style.add( cmd_name, cmd_value, row_idx)

    def styles2commands( me, styles):
        cmds = []
        for style in styles:
            style.flush()
            cmds += [ cmd.as_tuple() for cmd in style.container ]
        return cmds



########################################### Crosstab

from reporter.view.txt import ViewCrosstabTxt
from txt import CrosstabVisitorTxt
class ViewCrosstabPdf( PdfContextViewer, ViewCrosstabTxt):
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
        rl_style = me.styles2commands( v.column_styles)
        return me.make_rl_story( rl_style, v.table_data)


########################################### Poleva


from txt import ViewPolevaTxt, Panel
from reportlab.platypus.flowables import (
    PageBreak, KeepTogether, Spacer,
    HRFlowable, PTOContainer)

class PdfPanelVisitor( Panel.Visitor):
    def __init__( me, viewer):
        me.viewer = viewer
        me.main_story = []
        me.keep_together_story = []
        me.header_story = []
        me.footer_story = []

        me.repeatable_story = None
        me.keep_with_next = False
        me.paragraph_mode = False
        me.para_text = ''
        me.is_bullet = False
        me.bullet_text = ''
        me.hAlign = 'LEFT'
        me.conv = viewer.conv

    def output( me):
        if me.header_story or me.footer_story:
            return [ PTOContainer( content=me.main_story,
                                header=me.header_story,
                                trailer=me.footer_story) ]
        return me.main_story

    @property
    def story( me):
        if me.repeatable_story is not None:
            return me.repeatable_story
        if me.keep_with_next:
            return me.keep_together_story
        return me.main_story

    # visitor interface
    def openPanel( me, panel): pass

    def openRow( me, row):
        me.nested_table = False
        me.table_style = []
        me.widths      = []
        me.current_height = None
        me.row_data    = []
        me.para_row    = ''
        me.space_above = 0
        me.space_below = 0
        me.repeatable_story = None

    def openField( me, field):
        proc = me._fieldtype_processors.get( field.typ)
        if proc:
            return proc( me, field)
        print 'Error: unknown field type in report layout: %s' % (field.name)

    def addField( me, field): pass
    def closeField( me, field): pass

    def closeRow( me, row):
        if me.paragraph_mode:
            if me.is_bullet:
                me.bullet_text += me.conv(me.para_row)
            else:
                me.para_text += me.conv(me.para_row) + '\n' # put some space when concatenating layout lines
            return

        if not me.row_data: return

        if len(me.row_data) == 1 and isinstance( me.row_data[0], list) and not me.nested_table:
            add_story = me.row_data[0]
        else:
            rl_style  = me.viewer.styles2commands( me.table_style)
            add_story = me.viewer.make_rl_story( rl_style, [ me.row_data ],
                                             col_widths=me.widths,
                                             row_heights=[ me.current_height ],
                                             hAlign=me.hAlign )
        if me.space_above:
            me.story.append( me.cmd_vertical_space( space=me.space_above))
        me.story.extend( add_story)
        if me.space_below:
            me.story.append( me.cmd_vertical_space( space=me.space_below))

    def closePanel( me, panel): # FIXME in future we may have more than one panel in the layout
        me.main_story.extend( getattr(me.viewer, 'story2inject', []))

    # internals
    def _process_command( me, field):
        descr = field.getFieldData()
        if descr:
            command = getattr( me, descr['command'], None)
            if callable( command):
                kargs = descr.get('kargs', {})
                flowable = command( **kargs)
                if flowable:
                    from svd_util.attr import iscollection
                    me.story.extend( iscollection( flowable) and list( flowable) or [ flowable ])
        else:
            print 'ERROR: unknown layout command: %s' % field.name

    def _process_field( me, field):
        view = me.viewer.get_view( field)
        data = me.viewer.get_fld_data( field.name)
        fld_out = me.viewer.convert_data( data, view)
        if isinstance( fld_out, list):
            align_dir = me.viewer.get_view_attr_translated( view, 'align')
            for flowable in fld_out:
                flowable.hAlign = align_dir
        label = me.viewer.convert_label( view)
        if label:
            me._add_text( label, view, is_label=True)
        me._add_text( fld_out, view, is_label=False)

    def _process_outside( me, field):
        text = field.name
        if not me.paragraph_mode:
            print 'ignoring non paragraph text:', text
            return
        me.para_row += me.conv( text)

    _fieldtype_processors = dict(
        button = _process_command,
        input  = _process_field,
        outside= _process_outside,
    )

    def _add_text( me, txt, view, is_label =False):
        if me.paragraph_mode:
            s = me._format_para_text( txt, view, is_label=is_label)
            me.para_row += me.conv(s)
            return
        view.switch_formatted( is_label)
        style = SingleCellFormat( len( me.row_data) )
        me.viewer.apply_view( view, style, 0, is_label)
        me.widths.append( me.viewer.get_view_attr( view, 'width'))
        me.current_height = max( me.current_height, me.viewer.get_view_attr( view, 'height'))

        me.table_style.append( style)
        me.space_above = max( me.space_above, me.viewer.get_view_attr( view, 'space_above'))
        me.space_below = max( me.space_below, me.viewer.get_view_attr( view, 'space_below'))
        me.row_data.append( txt)

    attr2tag = dict(
        align       = 'alignment',
        font_name   = 'fontName',
        font_size   = 'fontSize',
        leading     = 'leading',
        text_color  = 'textColor',
        background  = 'backColor',
        space_above = 'spaceBefore',
        space_below = 'spaceAfter',
        indent      = 'leftIndent',
        first_line_indent = 'firstLineIndent',
        right_padding = 'rightIndent',
    )

    para_field_format = dict(
        font_name   = 'face',
    )

    def _format_para_text( me, txt, view, is_label):
        if is_label: return '' # no labels in paragraph mode
        #return ' <b>'+txt+'</b>'
        view.switch_formatted( is_label)
        s = '\n<font'
        for name, tag in me.para_field_format.iteritems():
            val = me.viewer.get_view_attr( view, name)
            if 1 and tag in 'textColor backColor'.split(): # FIXME
                print val
                val = val.lower()
                val = 'red'

            s += ' %(tag)s="%(val)s"' % locals()
        s += '>\n%s\n</font>\n' % me.conv(txt)
        #print '=========================\n', s, '\n----------------'
        return s

    # layout commands
    def cmd_paragraph( me, start, style=None):
        me.paragraph_mode = start
        if start:
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
            style = style or {}
            for k,v in me.viewer.spr.layout_defaults.iteritems():
                style.setdefault( k, v)
            align_map = dict( l=TA_LEFT, r=TA_RIGHT, c=TA_CENTER, j=TA_JUSTIFY)
            para_kargs = {}
            for name, para_name in me.attr2tag.iteritems():
                val = style.get( name)
                if val is not None:
                    if name=='align':
                        val = align_map[ val]
                    elif name=='text_color':
                        val = val.lower()
                    para_kargs[ para_name] = val
            me.para_style = ParagraphStyle('tmp_style', **para_kargs)
        elif me.para_text:
            res = Paragraph( me.conv( me.para_text), me.para_style)
            me.para_text = ''
            return res

    def cmd_bullets( me, start, numbered =True):
        assert me.paragraph_mode
        tags = numbered and ('<ol>', '</ol>') or ('<ul>', '</ul>')
        me.para_text += me.conv( start and tags[0] or tags[1] )

    def cmd_bullet_row( me, start):
        me.is_bullet = start
        if not start and me.bullet_text:
            me.para_text += me.conv('<li>') + me.conv(me.bullet_text) + me.conv('</li>')
            me.bullet_text = ''

    def cmd_horizontal_line( me, **kargs):
        return HRFlowable( **kargs)

    def cmd_vertical_space( me, space):
        return Spacer( width=1, height=space)

    def cmd_page_break( me):
        return PageBreak()

    def cmd_keep_with_next( me, value):
        me.keep_with_next = value
        if not me.keep_with_next and me.keep_together_story:
            res = []
            page_story = []
            for flowable in me.keep_together_story:
                if isinstance( flowable, PageBreak):
                    if page_story:
                        res.append( KeepTogether( page_story))
                        page_story = []
                    res.append( flowable)
                else:
                    page_story.append( flowable)
            if page_story:
                res.append( KeepTogether( page_story))
            me.keep_together_story = []
            return res

    def cmd_horizontal_align( me, direction):
        align_types = { -1:'LEFT', 0:'CENTER', 1:'RIGHT' }
        me.hAlign = align_types[ direction ]

    def cmd_add_repeatable( me, header):
        if header:
            me.repeatable_story = me.header_story
        else:
            me.repeatable_story = me.footer_story

    def cmd_nested_table( me):
        me.nested_table = True



class ViewPolevaPdf( PdfContextViewer, ViewPolevaTxt):
    PanelVisitor = PdfPanelVisitor
    def make_output( me, filename, pagesize=None, layout =None, view_descr =None):
        return (check_page_layout( me, me.__class__,
                                    layout=layout, view_descr=view_descr,
                                    filename=filename, pagesize=pagesize) or
                PdfContextViewer.make_output( me, filename, pagesize, layout, view_descr))


############################### Redova / Tablichna


from view_base import ViewRedovaBase

def check_page_layout( me, factory_viewer_poleva, layout, view_descr, **poleva_kargs):
    page_description = getattr( me.spr, 'page_description', None)
    page_layout = getattr( me.spr, 'page_layout', None)
    if page_description and page_layout:
        from reporter.common import PolevaSpravka
        class TempPolevaSpravka( PolevaSpravka):
            description = page_description.copy()
            layout = page_layout
            input_params = me.spr.input_params
            layout_defaults = me.spr.layout_defaults.copy()
        viewer_poleva = factory_viewer_poleva( TempPolevaSpravka())
        redova_story = me.make_embeddable_output( layout, view_descr)
        viewer_poleva.story2inject = redova_story
        return viewer_poleva.make_output( **poleva_kargs)

class ViewRedovaPdf( PdfContextViewer, ViewRedovaBase):
    def get_table_data( me, column_order):
        table_data, column_styles = ViewRedovaBase.get_table_data( me, column_order)

        style_commands = []
        for style in column_styles:
            style_commands += [ cmd.as_tuple() for cmd in style.container ]
        return table_data, style_commands

    def make_embeddable_output( me, layout =None, view_descr =None):
        me.update( layout, view_descr)
        data, style_commands = me.get_table_data( me.layout)

        col_widths = []
        current_height = None
        for col_name in me.layout:
            col_widths.append( me.get_view_attr_static( col_name, 'width'))
            current_height = max( current_height, me.get_view_attr_static( col_name, 'height'))
        row_heights = len(data) * [ current_height ]
        if len( me.layout)==1 and data:
            import itertools as it
            cell = data[0][0]
            if isinstance( cell, (list, tuple)):
                return it.chain( *[ r[0] for r in data ])  # chain subreport stories
        return me.make_rl_story( style_commands, data,
                                col_widths=col_widths, row_heights=row_heights)

    def make_output( me, filename, pagesize=None, layout =None, view_descr =None):
        return (check_page_layout( me, ViewPolevaPdf,
                                    layout=layout, view_descr=view_descr,
                                    filename=filename, pagesize=pagesize) or
                PdfContextViewer.make_output( me, filename, pagesize, layout, view_descr))


# vim:ts=4:sw=4:expandtab
