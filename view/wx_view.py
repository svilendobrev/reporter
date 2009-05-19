#$Id$
# -*- coding: cp1251 -*-

from txt import FldView, ViewAttr
class wxBrowsableView( FldView):
    view_context_name = 'wx_browsable'
    inherit = 'view'

    common_attribs  = dict(
        align = ViewAttr('l'),
        min_width = ViewAttr( 10),
        max_width = ViewAttr( -1),
    )

    align_funcs = dict( l=lambda s: s+' ',
                        r=lambda s: ' '+s,
                        c=lambda s: ' '+s+' '
                      )

    def format( me, txt, is_label=False):
        me.switch_formatted( is_label)
        align_func = me.align_funcs.get( me.eval('align'), None)
        if is_label:
            txt = txt.replace('\n', ' ') # multiline labels don't look good for windows
        if align_func:
            return align_func( txt)
        return txt


from view_base import FldViewBase, ViewRedovaBase
class ViewRedovaWxBrowsable( ViewRedovaBase):
    view_context_name = wxBrowsableView.view_context_name

    def make_output( me, layout=None, view_descr=None):
        me.update( layout, view_descr)
        return me.get_labels(), me.spr.rows()

    def get_labels( me):
        res = []
        for name in me.layout:
            view = me.get_view( name, None)
            label_txt = me.convert_label( view)
            res.append( view.format( label_txt, is_label=True))
        return res


from txt import ViewCrosstabTxt
class ViewCrosstabWxBrowsable( ViewCrosstabTxt):
    view_context_name = wxBrowsableView.view_context_name
    DEFAULT_OUTPUT_ENCODING = 'utf-8'

    from txt import CrosstabVisitorTxt
    class Visitor( CrosstabVisitorTxt):
        def append_txt( me, txt, view):
            me.output_row.append( txt)

    def convert_data( me, data, view):
        txt = ViewCrosstabTxt.convert_data( me, data, view)
        return view.format( txt)
    def convert_label( me, view):
        txt = ViewCrosstabTxt.convert_label( me, view)
        return view.format( txt, is_label=True)

    def make_output( me, layout =None, view_descr =None):
        me.update( layout, view_descr)
        v = me.Visitor( me)
        me.walk_table( v)
        return v.table_data[0], v.table_data[1:]


################################################################ Printout
from pdf import ViewRedovaPdf, PdfView, ViewCrosstabPdf, ViewPolevaPdf
class wxPrintoutView( PdfView):
    view_context_name = 'wx'
    inherit = 'pdf'

    common_attribs = PdfView.common_attribs.copy()
    common_attribs['width'] = ViewAttr( None, inherit=True)


def make_pagerecorder( story, pagesize =None, **kargs):
    from reporter.engine.rl2wx.page_recorder import PageRecorder
    from reporter.engine.rl2wx.canvas import Canvas as wxCanvas
    from reportlab.platypus.doctemplate import SimpleDocTemplate
    page_recorder = PageRecorder( pagesize)
    doc = SimpleDocTemplate( filename=page_recorder, pagesize=pagesize, **kargs)
    doc.setPageCallBack( getattr( page_recorder, 'new_page', None))
    doc.build( list(story), canvasmaker=wxCanvas)
    page_recorder.debug_doc = doc
    return page_recorder

from pdf import PdfContextViewer, check_page_layout
class WxContextViewer( PdfContextViewer):
    view_context_name = wxPrintoutView.view_context_name
    DEFAULT_OUTPUT_ENCODING = 'utf-8'

    overwrite_fonts_in_style= False

    def make_output( me, pagesize =None, layout =None, view_descr =None):
        story = me.make_embeddable_output( layout, view_descr)
        doc_args = me.get_doc_args( pagesize)
        recorder = make_pagerecorder( story, **doc_args)
        return recorder


class ViewCrosstabWxPrintout( WxContextViewer, ViewCrosstabPdf):  pass

class ViewPolevaWxPrintout( WxContextViewer, ViewPolevaPdf):
    def make_output( me, pagesize=None, layout =None, view_descr =None):
        return (check_page_layout( me, me.__class__,
                                    layout=layout, view_descr=view_descr,
                                    pagesize=pagesize) or
                WxContextViewer.make_output( me, pagesize, layout, view_descr))

class ViewRedovaWxPrintout( WxContextViewer, ViewRedovaPdf):
    def make_output( me, pagesize =None, layout =None, view_descr =None):
        return (check_page_layout( me, ViewPolevaWxPrintout,
                    pagesize=pagesize, layout=layout, view_descr=view_descr) or
                WxContextViewer.make_output( me, pagesize, layout, view_descr))


# vim:ts=4:sw=4:expandtab
