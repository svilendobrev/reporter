#$Id$


def align_l( txt, sz):    return txt.ljust( sz)
def align_r( txt, sz):    return txt.rjust( sz)
def center( txt, sz):     return txt.center( sz)
align_funcs = { 'r' : align_r, 'l' : align_l, 'c' : center }

def left_border( txt):  return ' | '+txt
def right_border( txt): return txt+' | '
border_funcs = { 'l' : left_border, 'r' : right_border }#, 'u':upper_border, 'd':down_border }

class View( object):
    def __init__( me, spr, fld_names):
        me.spr = spr
        me.rows = list( me.spr.rows())
        me.fld_names = fld_names

    def str_row_fld( me, row, fld_name):
        res = str( getattr( row, fld_name, ''))
        return res.strip()

    def __str__( me):
        s = '\n'.join(
                ''.join( me.str_row_fld( row, n) for n in me.fld_names)
                for row in me.rows
             ) + '\n'
        return s


if 1: # decorators to probe
    class ViewDecorator( object):
        def __init__( me, view): me.view = view
#        def __str__( me): return str( me.view )
        def __getattr__( me, name): return getattr( me.view, name)

    class Titled( ViewDecorator):
        def __init__( me, view, captions):
            ViewDecorator.__init__( me, view)
            me.captions = captions
            me.rows = [None] + view.rows  #copy

        def str_row_fld( me, row, fld_name):
            if row is not None:
                return me.view.str_row_fld( row, fld_name)
            else:
                return me.captions.get( fld_name, '')


    class Aligned( ViewDecorator):
        align_funcs = { 'r' : align_r, 'l' : align_l, 'c' : center }

        def __init__( me, view, col_aligns):
            ViewDecorator.__init__( me, view)
            me.col_sizes = dict()

            me.calc_col_sizes()
            me.col_aligns = col_aligns

        def calc_col_sizes( me):
            for n in me.view.fld_names:
                max_sz = max( len( me.view.str_row_fld( row, n)) for row in me.view.rows)
                me.col_sizes[ n] = max_sz   +1 #leave some space

        def str_row_fld( me, row, fld_name):
            res = me.view.str_row_fld( row, fld_name)
            try:
                direction = me.col_aligns[ fld_name]
                align = me.align_funcs[ direction]
                size = me.col_sizes[ fld_name]
                res = align( res, size)
            except KeyError: pass
            return res


    def left_border( txt):  return '|'+txt
    def right_border( txt): return txt+'|'

    class VBordered( ViewDecorator):
        border_funcs = { 'l' : left_border, 'r' : right_border }#, 'u':upper_border, 'd':down_border }

        def __init__( me, view, col_borders):
            ViewDecorator.__init__( me, view)
            me.col_borders = col_borders

        def str_row_fld( me, row, fld_name):
            res = me.view.str_row_fld( row, fld_name)
            try:
                brd = me.col_borders[ fld_name]     #TODO .get( fld_name, ()) -> no try-except
                for b in brd:
                    func = me.border_funcs[ b]
                    res = func( res)
            except KeyError: pass
            return res

    def upper_border( txt):
        if '\n' in txt:
            line = txt.index('\n')*'-'
        else:
            line = len(txt)*'-'
        line += '\n'
        return line + txt

    def down_border( txt):
        if '\n' in txt:
            line = txt.index('\n')*'-'
        else:
            line = len(txt)*'-'
        return txt + '\n'+line


    class HBordered( ViewDecorator):
        border_funcs = { 'u' : upper_border, 'd' : down_border}

        def __init__( me, view, border_type):
            ViewDecorator.__init__( me, view)
            me.border_type = border_type

        def __str__(me):
            s = ''
            for row in me.rows:
                row_str = ''.join( me.str_row_fld( row, n) for n in me.fld_names)
                if me.border_type in me.border_funcs:
                    row_str = me.border_funcs[ me.border_type]( row_str)
                s += row_str+'\n'
            return s

'''
class HtmlViewer( ViewDecorator):
    def __init__( me, view):
        ViewDecorator.__init__( me, view)

    def __str__(me):
        s = '<table>'
        for row in me.rows:
            row_str = ''.join( me.str_row_fld( row, n) for n in me.fld_names)
            if me.border_type in me.border_funcs:
                row_str = me.border_funcs[ me.border_type]( row_str)
            s += row_str+'\n'
        s += '</table>'
        return s
'''
# vim:ts=4:sw=4:expandtab
