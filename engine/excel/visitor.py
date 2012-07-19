#$Id$

import pyXLWriter as xl
#from dbcook.util.hacksrc import hacksrc

#hacksrc( xl.Workbook._store_all_num_formats,
#                    'if not re.match(r"^0+\d", num_format):',
#                    'if 0:', )

import builder

class Visitor:
    def XcelBuilder( me, v, enter):
        if enter:
            me.book = xl.Writer( v.filename) #+'.xls')
            me.book.set_codepage(0x04E3)     # encoding cp1251
        else:
            me.book.close()
            me.book = None

    def Sheet( me, v, enter):
        if enter:
            me.s = me.book.add_worksheet()
            me.cdfs=[]
        else:
            for (start_cell, data_array, format, vert) in me.cdfs:
                stil = me.book.add_format(**format)
                if vert:
                    me.s.write_col( start_cell, data_array, stil)
                else:
                    me.s.write( start_cell, data_array, stil)
            if v.protect: me.s.protect()
            me.s = None

    def Cell( me, v, enter):
        if enter: return
        if v.picture: me.s.insert_bitmap((v.y, v.x), v.picture)
        me.cdfs.append( (( v.y, v.x), v.formula or v.value, getattr( me,'format', {}), None) )
        me.format=  {}

    def Merge( me, v, enter):
        if enter: return
        stil = me.book.add_format( **dict(getattr( me,'format', {})))
        me.s.merge_range( v.range, v.value, stil)
        me.format = {}

    def Freeze( me, v, enter):
        if enter: return
        if v.label :
            me.s.thaw_panes( v.height, v.width, v.x, v.y)
        else:
            me.s.freeze_panes( v.x, v.y)

    def Range( me, v, enter):
        if enter: return
        me.cdfs.append( ((v.y,v.x), v.values, getattr( me, 'format', {}), v.vert) )

    def RowColumn( me, v, enter =True, horz =True):
        if enter: return
        if horz:
            me.s.set_row(    **convert( v.__dict__, row_commands))
        else:
            me.s.set_column( **convert( v.__dict__, column_commands))

    def Format4Cell( me, v, enter):
        if enter: return
        all = v.__dict__.copy()
        for k in '_border _font'.split():
            del all[k]
        me.format = convert( all,format_commands)
        if v._font is not None:
            me.format.update( convert( v._font.__dict__,   font_commands,   ignore_None= True))
        if v._border is not None:
            me.format.update( convert( v._border.__dict__, border_commands, ignore_None= False))

    def Page_Break( me, v, enter):
        if enter:return
        me.s.set_h_pagebreaks(v.row)
        me.s.set_v_pagebreaks(v.col)

    def Outline( me, v, enter):
        if enter: return
        me.s.set_row( v.row, level= v.level)

def convert( commands, prevod, ignore_None =False):
    full = {}
    for k,v in commands.iteritems():
        if k not in prevod: continue
        kout = prevod[k]
        vnone = None
        if isinstance( kout, tuple):
            kout,vnone = kout
        if v is None:
            if ignore_None: continue
            v = vnone
        full[ kout or k ] = v

    return full

#prevod { builder_key: xlwriter_key or xlwriter_key,None_Value }
format_commands = dict(
                color      = '',
                align      = '',
                valign     = '',
                background = 'bg_color',
                numformat  = ('num_format', '0'),
                pattern    = ('', 0),
                protect    = ('locked', 0),
        )

border_commands = dict(
                top        = ('',0),
                bottom     = ('',0),
                left       = ('',0),
                right      = ('',0),
        )

font_commands = dict(
                name       = 'font',
                size       = '',
                weight     = 'bold',
                slant      = 'italic',
        )

row_commands = dict(
                hidden     = '',
                width      = 'height',
                nomer      = 'row',
                level      = '',
        )

column_commands = dict(
                hidden     = '',
                width      = ('',10),
                nomer      = 'colrange'
        )

# vim:ts=4:sw=4:expandtab
