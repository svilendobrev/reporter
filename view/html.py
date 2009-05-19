#$Id$
# -*- coding: cp1251 -*-

from pdf import PdfView
class HtmlView( PdfView):
    inherit = 'pdfview' #'wx_printout_view'
    view_context_name = 'html_view'

    value_translator = dict( align=dict( l='left', r='right', c='center'))

    def format( me, txt, is_label =False):
        me.switch_formatted( is_label)
        attribs = dict( (name,me.eval(name))
                        for name in 'align valign background text_color'.split())
        attribs['txt'] = txt

        s = is_label and "<th" or "<td"
        s += ' align="%(align)s" valign="%(valign)s" bgcolor="%(background)s"><font color="%(text_color)s">%(txt)s </font>' % attribs
        s += is_label and "</th>" or "</td>"
        return '\t\t' + s + '\n'

from view_base import ViewRedovaBase
class ViewRedovaHtml( ViewRedovaBase):
    view_context_name = HtmlView.view_context_name
    DEFAULT_OUTPUT_ENCODING = 'cp1251'

    def convert_row( me, row_obj, row_txt, is_label =False):
        result = []
        for cell,name in zip( row_txt, me.layout):
            view = me.get_view( name, context=row_obj)
            txt = view.format( cell, is_label=is_label)
            result.append( txt)
        return result

    def make_output( me, layout =None, view_descr =None):
        me.update( layout, view_descr)

        html = '<table>\n'
        table_data, column_styles = ViewRedovaBase.get_table_data( me, me.layout)
        for row_cells in table_data:
            html += '\t<tr>\n' + ''.join( row_cells) + '\n'
        html += '</table>\n'
        return html


# vim:ts=4:sw=4:expandtab
