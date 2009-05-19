#$Id$
# -*- coding: cp1251 -*-

from field import Float, Int, Text, Date, DateTime
from field import FieldDef as Field, FieldDef, FieldDef as FldDef, ViewDef, Style
from field import Fields

from view.txt import FldView
from view.view_base import Label
from view.wx_view import wxBrowsableView, wxPrintoutView
from view.pdf import PdfView
from view.html import HtmlView

from link import Link as AS
from view.view_base import FldViewBase, ViewAttr


from reporter.engine.util.dictOrder import dictOrder
class Groups( object):
    def __init__( me, **kargs):
        me.data = dictOrder() # topology order
        for name, g in kargs.iteritems():
            assert isinstance( g, Group)
            me._add_group( name, kargs)

    def _and_parent_func( me, func, parent_func):
        if callable(parent_func):
            def new_func( *args, **kargs):
                return parent_func( *args, **kargs) and func( *args, **kargs)
            return callable(func) and new_func or parent_func
        return func

    def _add_group( me, name, all_groups, parent_threshold =None, parent_filter =None):
        if name in me.data: return

        g = all_groups[ name]
        new_threshold = me._and_parent_func( g.threshold, parent_threshold)
        new_filter = me._and_parent_func( g.filter_func, parent_filter)

        subgroups = g.subgroups
        if not subgroups:
            g.threshold = new_threshold
            g.filter_func = new_filter
            me.data[ name] = g
            return

        if isinstance( subgroups, str): subgroups = subgroups.split()
        for subname in subgroups:
            me._add_group( subname, all_groups, new_threshold, new_filter)

from reporter.engine.ui.layout import Panel

def make_field_builder( data_type):
    def builder( model=None, label=None, *args, **kargs):
        views = dict( (v.view_context_name, v) for v in args if isinstance(v,FldViewBase))
        for k in kargs:
            assert k not in views, 'multiple definition of view %s' % k
        kargs.update( views)
        return FieldDef( type=data_type, model=model, label=label, **kargs)
    return builder

TextF   = make_field_builder( Text)
IntF    = make_field_builder( Int)
FloatF  = make_field_builder( Float)
DateF   = make_field_builder( Date)
DateTimeF= make_field_builder( DateTime)

def label_builder( txt, style =None, **label_kargs):
    return TextF( label=Label( txt, **label_kargs), style=style)
LabelF = label_builder

use_excel =True
try:
    import pyXLWriter
except ImportError, e:
    print e
    use_excel = False
    ViewRedovaXl='alabala'
    XlsView=PdfView
else:
    from view.xl_view import XlsView

from aggr_func import *
from decimal import Decimal

from row import Row, AggrRow
#from reporter.engine.basedb.simpleDB import DB

use_pdf = True
try:
    import reportlab
except ImportError, e:
    print e
    use_pdf = False    # dummy pdf
    PdfView = FldViewBase
    default_pagesize = (595, 842)
    class units:
        cm = inch = 0
else:
    from reportlab.lib.pagesizes import LETTER, A4, cm, inch
    from reportlab.lib import pagesizes
    from reportlab.lib import units
    default_pagesize = A4


class PivotField( object):
    def __init__( me, field_name, group_name=None, show_total=False, aggregator=None):
        me.field_name = field_name
        me.group_name = group_name # None if data field
        me.show_total = show_total
        me.aggregator = aggregator # if set we show AggRow.field_name as data field

class CrosstabLayout( object):
    __slots__ = '''column_field row_field data_field
                top_left top_right bottom_left bottom_right
                empty_cell'''.split()
    def __init__( me, **kargs):
        for k,v in kargs.iteritems():
            setattr( me, k, v)


class ReportDefaults( object):
    layout_defaults = dict(
        indent       = 0,
        font_name    = 'ArialMT',
        font_size    = 12,

        space_above  = 0,
        space_below  = 0,
        border       = '',

        pagesize     = A4,
        landscape    = False,
        top_margin   = 1 * units.cm,
        bottom_margin= 1 * units.cm,
        left_margin  = 1 * units.cm,
        right_margin = 1 * units.cm,

        background   = 'WHITE',
        text_color   = 'BLACK',
    )


from spravka import RedovaSpravka, PolevaSpravka
class Crosstab( RedovaSpravka, ReportDefaults):
    preserve_input_order = False

class RedovaSpravka( RedovaSpravka, ReportDefaults): pass

Group = RedovaSpravka.GroupDef

def nomer_v_packet(red):
    return red.get_packet().rows.index( red)+1

def nomer_na_agreg_red(red):
    from reporter.packet import Packet
    if not isinstance( red, AggrRow): return 0
    packet = red.get_packet()
    agg_rows = []
    all = packet.group.packet_order
    i = 0
    for p in all:
        if not isinstance( p, Packet): continue
        agg_rows += p.agg_rows
    return agg_rows.index( red)+1

class PolevaSpravka( PolevaSpravka, ReportDefaults):
    layout_commands = dict(
        hline               = dict( command='cmd_horizontal_line',
                                    kargs=dict( width='100%', color='BLACK')),
        keep_with_next_on   = dict( command='cmd_keep_with_next', kargs=dict(value=True)),
        keep_with_next_off  = dict( command='cmd_keep_with_next', kargs=dict(value=False)),
        vspace              = dict( command='cmd_vertical_space', kargs=dict(space=20)),
        page_break          = dict( command='cmd_page_break'),
        left                = dict( command='cmd_horizontal_align', kargs=dict( direction=-1)),
        center              = dict( command='cmd_horizontal_align', kargs=dict( direction=0)),
        right               = dict( command='cmd_horizontal_align', kargs=dict( direction=1)),
        header              = dict( command='cmd_add_repeatable', kargs=dict( header=True)),
        footer              = dict( command='cmd_add_repeatable', kargs=dict( header=False)),
        para                = dict( command='cmd_paragraph', kargs=dict( start=True)),
        para_end            = dict( command='cmd_paragraph', kargs=dict( start=False)),
        nest_table          = dict( command='cmd_nested_table'),
    )

class Viewer( object):
    from spravka import RedovaSpravka, PolevaSpravka
    from view.txt import ViewRedovaTxt, ViewPolevaTxt, ViewCrosstabTxt
    if use_pdf:
        from view.pdf import ViewRedovaPdf, ViewPolevaPdf, ViewCrosstabPdf
    else:
        ViewPolevaPdf = ViewPolevaTxt
        ViewRedovaPdf = ViewRedovaTxt
        ViewCrosstabPdf = ViewCrosstabTxt

    if use_excel:
        from view.xl_view import ViewRedovaXl, ViewCrosstabXl
    else:
        ViewRedovaXl = ViewRedovaTxt
        ViewCrosstabXl = ViewCrosstabTxt

    from view.wx_view import ViewRedovaWxPrintout, ViewPolevaWxPrintout, ViewCrosstabWxPrintout
    from view.html import ViewRedovaHtml
    viewers = dict(
        txt = { RedovaSpravka   : ViewRedovaTxt,
                PolevaSpravka   : ViewPolevaTxt,
                Crosstab        : ViewCrosstabTxt,
              },
        pdf = { RedovaSpravka   : ViewRedovaPdf,
                PolevaSpravka   : ViewPolevaPdf,
                Crosstab        : ViewCrosstabPdf,
              },
        wx = {
                RedovaSpravka   : ViewRedovaWxPrintout,
                PolevaSpravka   : ViewPolevaWxPrintout,
                Crosstab        : ViewCrosstabWxPrintout,
              },
        html= { RedovaSpravka   : ViewRedovaHtml,
              },
        xls = { RedovaSpravka   : ViewRedovaXl,
                Crosstab        : ViewCrosstabXl,
              },
    )
    report_types = (RedovaSpravka, PolevaSpravka, Crosstab)

    def __init__( me, spr, dc='txt'):
        dc_viewers = me.viewers[ dc]
        viewer_factory = None
        for typ in me.report_types:
            if isinstance( spr, typ):
                viewer_factory = dc_viewers[ typ ]
                break
        assert viewer_factory, '''
No viewer available for context: %s report: %s''' % (dc, spr.__class__.__name__)
        me.viewer = viewer_factory( spr)

    def make_output( me, **kargs):
        return me.viewer.make_output( **kargs)

    def make_embeddable_output( me, **kargs):
        return me.viewer.make_embeddable_output( **kargs)

    @classmethod
    def register_context_viewers( klas, dc,
                            redova_viewer =None,
                            poleva_viewer =None,
                            crosstab_viewer =None):
        klas.viewers[ dc] = dict(
            zip( klas.report_types, (redova_viewer, poleva_viewer, crosstab_viewer))
        )


def threshold( attr2compare_or_func):
    ''' decorates threshold funcs to return False if row list is empty before
        the actual threshold logic is checked;
        can be used as threshold func itself to check if a field has changed
    '''
    if callable( attr2compare_or_func):
        threshold_checker = attr2compare_or_func
        def new_th( r, rows):
            if not rows: return False
            return threshold_checker( r, rows)
        return new_th

    fieldname= attr2compare_or_func
    def threshold_on_value_change( r, rows):
        if not rows: return False
        assert hasattr( rows[-1], fieldname)
        assert hasattr( r, fieldname)
        return getattr( rows[-1], fieldname) != getattr( r, fieldname)
    return threshold_on_value_change # threshold( threshold_on_value_change)


import wx
from reporter.engine.ui.uitools import _
class CustomizedPreviewControlBar( wx.PyPreviewControlBar):
    '''
    def SetZoomControl( me, zoom):
        i = 0
        for perc_str in me.ZoomControl.GetStrings():
            perc_val = int( perc_str[ : len( perc_str) - len('%')] )
            if perc_val >= zoom: break
            i += 1
        me.ZoomControl.SetSelection( i)

    def GetZoomControl( me):
        if (m_zoomControl && (m_zoomControl->GetStringSelection() != wxEmptyString))
            long val;
            if (m_zoomControl->GetStringSelection().BeforeFirst(wxT('%')).ToLong(&val))
                return int(val);
        return 0;
    '''
    def CreateButtons( me):
        me.SetSize( (400, 40) )
        sizer = wx.BoxSizer( wx.HORIZONTAL)

        navButtonSize = wx.Size(40, wx.DefaultSize.y)

        buttons_description = [
            ( wx.ID_PREVIEW_CLOSE     , _('&Отказ')      , wx.DefaultSize , wx.ALIGN_CENTRE | wx.ALL ),
            ( wx.ID_PREVIEW_PRINT     , _('&Печат...')   , wx.DefaultSize , wx.ALIGN_CENTRE | wx.ALL ),
            ( wx.ID_PREVIEW_FIRST     , _('|<<')         , navButtonSize  , wx.ALIGN_CENTRE | wx.ALL ),
            ( wx.ID_PREVIEW_PREVIOUS  , _('<<')          , navButtonSize  , wx.ALIGN_CENTRE | wx.RIGHT | wx.TOP | wx.BOTTOM ),
            ( wx.ID_PREVIEW_NEXT      , _('>>')          , navButtonSize  , wx.ALIGN_CENTRE | wx.RIGHT | wx.TOP | wx.BOTTOM ),
            ( wx.ID_PREVIEW_LAST      , _('>>|')         , navButtonSize  , wx.ALIGN_CENTRE | wx.RIGHT | wx.TOP | wx.BOTTOM ),
            ( wx.ID_PREVIEW_GOTO      , _('&Страница...'), wx.DefaultSize , wx.ALIGN_CENTRE | wx.ALL ),
        ]

        for descr in buttons_description:
            btn = wx.Button( me, descr[0], descr[1], wx.DefaultPosition, descr[2], 0)
            sizer.Add( btn, 0, descr[ 3], 5)

        choices = [ str(i)+'%' for i in range(10, 101, 5) ]
        me.zoom = wx.Choice( me, wx.ID_PREVIEW_ZOOM,  choices=choices, style=0)
        sizer.Add( me.zoom, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        me.zoom.SetStringSelection( '100%')
        #me.SetZoomControl( 100) #me.GetPrintPreview().GetZoom())

        me.SetSizer( sizer)
        sizer.Fit( me)

class CustomPrintPreview( wx.PyPrintPreview):
    def GetZoom( me):
        res = wx.PyPrintPreview.GetZoom( me)
        print 'GetZoom', res
        return 100


if 0:
    class CustomPreviewFrame( wx.PyPreviewFrame):
        def CreateControlBar( me):
            me.m_controlBar = CustomizedPreviewControlBar( me.m_printPreview, 0, me, wx.Point(0,0), wx.Size( 400, 40))
            me.m_controlBar.CreateButtons()

def preview_recorder( page_rec, frame_title ='', pagesize =A4, landscape =False, parent =None):
    printData = wx.PrintData()
    printData.SetPaperId( wx.PAPER_A4)
    printData.SetPrintMode( wx.PRINT_MODE_PRINTER)
    if landscape:
        pagesize = pagesizes.landscape( pagesize)
        printData.SetOrientation( 2)
    data = wx.PrintDialogData( printData)

    from reporter.engine.rl2wx.printout import MyPrintout as Printout
    printout  = Printout( page_rec)
    printout2 = Printout( page_rec)

    preview   = wx.PrintPreview( printout, printout2, data)
    preview.SetZoom( 100 or 200)
    if not preview.Ok():
        print 'No printer is installed...\n'
        return

    pfrm = wx.PreviewFrame( preview, parent, frame_title)
    pfrm.Initialize()
    #controlbar = CustomizedPreviewControlBar( preview, 0, pfrm)
    #pfrm.SetControlBar( controlbar)
    #controlbar.CreateButtons()

    #pfrm.SetPosition( frame.GetPosition())
    pfrm.SetSize( (1024,768))
    pfrm.MakeModal(True)
    pfrm.Show(True)

def show_preview( spravka, title, parent =None):
    viewer = Viewer( spr=spravka, dc='wx')
    pagesize = spravka.layout_defaults.get( 'pagesize', A4)
    page_rec = viewer.make_output( pagesize=pagesize)
    landscape = spravka.layout_defaults.get( 'landscape', False)
    preview_recorder( page_rec, title, pagesize, landscape) #, parent=parent)

def show_report( spr, context):
    ''' expects command line parameters like:
        txt,wx,pdf arg1=arg1 arg2=val2 ...'''
    import sys
    params = sys.argv[1:]
    if not params: params = ['txt']
    contexts = params[0]
    contexts = contexts.split(',')

    kargs = dict( [ p.split('=') for p in params[1:] ])
    spr.refresh( context)
    for dc in contexts:
        if dc == 'wx': #show me a window
            app=wx.PySimpleApp()
            show_preview( spr, 'TEST')
            app.MainLoop()
            return

        out = Viewer( spr, dc=dc).make_output( **kargs)
        if dc == 'txt':
            print out


# vim:ts=4:sw=4:expandtab
