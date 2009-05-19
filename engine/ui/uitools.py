#$Id$
import wx

if wx.USE_UNICODE:
    def TXT(txt):
        if txt is None: return ''
        if isinstance(txt, unicode): return txt
        if hasattr( txt, 'UIstr'):
            txt = txt.UIstr()
        else:
            txt = str(txt)
        try:
            return unicode( txt, MODEL_ENCODING)
        except UnicodeDecodeError:
            return unicode( txt, PREFERRED_ENCODING)

    def UNICODE2STR(txt):
        if isinstance( txt, unicode):
            return txt.encode( MODEL_ENCODING)
        return txt
else:
    def TXT(txt):
        if txt is None: return ''
        if hasattr( txt, 'UIstr'):
            r = txt.UIstr()
        else:
            r = str( txt)
        try:
            r = unicode( r, MODEL_ENCODING)
        except UnicodeDecodeError:
            pass
        else:
            r = r.encode( PREFERRED_ENCODING)
        return r

    def UNICODE2STR(txt):
        txt = str(txt)
        try:
            txt = unicode( txt, MODEL_ENCODING)
        except UnicodeDecodeError:
            txt = unicode( txt, PREFERRED_ENCODING)
        return txt.encode( MODEL_ENCODING)

_ = TXT

if 0:
    import os, sys
    from layout import Panel

    from reporter.engine.util.vreme import UniversalTime

    IMGPATH = os.path.join( os.path.abspath( os.path.dirname( sys.executable)), 'image')

    WXWIN = wx.Platform == "__WXMSW__"
    WXGTK = wx.Platform == "__WXGTK__"
    ISVISTA = WXWIN and sys.getwindowsversion()[0] == 6 or False

    DEFAULT_CONFIRM_KEY = wx.WXK_F2
    DEFAULT_CANCEL_KEY = wx.WXK_ESCAPE
    SEARCH_KEYS = wx.WXK_F4, wx.WXK_DOWN
    CURSOR_EDIT_KEY = wx.WXK_F5
    CONFIRM_BTN = 'OK'
    CANCEL_BTN = 'Cancel'
    SEARCH_BTN_LABEL = '...'
    IMAGE_WILDCARD = 'All image files|*.jpg;*.jpe;*.jpeg;*.png;*.gif;*.bmp'\
            '|JPG files (*.jpg)|*.jpg;*.jpe;*.jpeg'\
            '|PNG files (*.png)|*.png'\
            '|GIF files (*.gif)|*.gif'\
            '|BMP files (*.bmp)|*.bmp'\
            '|All files (*.*)|*.*'

    MODEL_ENCODING = 'utf-8'
    PREFERRED_ENCODING = 'cp1251'
    print 'USING UNICODE:', wx.USE_UNICODE

    if WXWIN:
        import locale
        strlocale = locale.setlocale(locale.LC_ALL, '')
        print 'USING LOCALE:', strlocale
        del strlocale
        UniversalTime._UIformat = '%x'

    UNIT = WXWIN and 22 or 25

    from controller import Actions as ACT
    Actions = { wx.ID_YES    : ACT.YES,
                wx.ID_NO     : ACT.NO,
                wx.ID_OK     : ACT.OK,
                wx.ID_CANCEL : ACT.CANCEL }

    ALIGNMENT = { #horizontal
                 'center' : wx.ALIGN_CENTER,
                 'left'   : wx.ALIGN_LEFT,
                 'right'  : wx.ALIGN_RIGHT,
                 #vertical
                 'top'    : wx.ALIGN_TOP,
                 'middle' : wx.ALIGN_CENTER_VERTICAL,
                 'bottom' : wx.ALIGN_BOTTOM,
                 }


    #theese should be inited from a map
    PRINT_EVENT_IDS_AS_NAMES = 1
    EVENTMAP = {}
    if PRINT_EVENT_IDS_AS_NAMES:
        for e in dir(wx):
            if e.startswith('EVT'):
                try:
                    wxev = eval('wx.' + e)
                    EVENTMAP[ wxev.evtType[0] ] = e
                except Exception, ex:
                    continue

    def ID2STR( Id):
        return EVENTMAP.get(Id, Id)

    def EVT_DUMP(evt):
        etype = evt.GetEventType()
        tirenca =  10 * '-'
        print tirenca, EVENTMAP.get( etype, etype), tirenca
        for i in dir(evt):
            if i.startswith('Get') and callable(getattr(evt,i)):
                print i,
                try:
                    print getattr(evt, i)()
                except:
                    print 'err'
        print tirenca * 2
    #----------------------------------------------------------------------------------
    CUSTOM_WIDGET_SIZE = 1
    #----------------------------------------------------------------------------------

    def getTextSize(text, font=None, memorydc=None, margin_percents=(10,10)):
        if not isinstance( text, unicode):
            text = TXT(text)
        memory = memorydc or wx.MemoryDC() #probably this could be made only once before making the layout
        #font = font or memory.GetFont()
        if font: memory.SetFont( font)
        textLines = text.split('\n')
        totalWidth, totalHeight = 0, 0
        for line in textLines:
            width, height = memory.GetTextExtent(line.rstrip())
            totalWidth = max( totalWidth, width)
            totalHeight = (totalHeight + height)
        if margin_percents:
            totalWidth = totalWidth + float(totalWidth * margin_percents[0] / 100)
            totalHeight = totalHeight + float(totalHeight * margin_percents[1] / 100)
        return int(totalWidth), int(totalHeight)

    def getAlignment4Column(txt, for_list=False):
        h  = txt.strip()
        if   txt.startswith(h): align = (wx.ALIGN_LEFT, wx.LIST_FORMAT_LEFT)
        elif txt.endswith(h)  : align = (wx.ALIGN_RIGHT, wx.LIST_FORMAT_RIGHT)
        else                  : align = (wx.ALIGN_CENTER, wx.LIST_FORMAT_CENTER)
        return align[ for_list ]


    def findsizer(sizer, widget):
        children = sizer.GetChildren()
        for i in children:
            if isinstance(i, wx.SizerItem):
                subsizer = i.GetSizer()
                if subsizer:
                    return findsizer(subsizer, widget)
                elif i.GetWindow() == widget:
                    return i
            elif i.IsSizer():
                return findsizer(i, widget)

    def makeMenu( menuitems, menumap, valuemap = None):
        w = wx.Menu()
        for item in menuitems:
            if not item:# or item is Menu.Separator:
                w.AppendSeparator() #kind = wx.wxITEM_SEPARATOR
            else:
                submenu = None
                if item.menu:
                    submenu = makeMenu( item.menu, menumap, valuemap)
                if not menumap:
                    key = 0
                else:
                    key = len(menumap)
                menumap[key] = item.id
                if valuemap is not None:
                    valuemap[key] = item.value

                kind = wx.ITEM_NORMAL
                try:
                    if item.is_check is not None: kind = wx.ITEM_CHECK
                except AttributeError: pass
                try:
                    if item.is_radio is not None: kind = wx.ITEM_RADIO
                except AttributeError: pass
                w_item = wx.MenuItem(   parentMenu = w,
                                        id= key,#????  so what: global map to item.id ??
                                        text= item.label,
                                        help= item.help,
                                        kind= kind,
                                        subMenu= submenu
                            )  #icon, check, radio, ...
                _w = w.AppendItem( w_item)
                if item.is_radio is not None: _w.Check( item.is_radio)
                if item.is_check is not None: _w.Check( item.is_check)
                enabled = False
                if callable(item.enabled):
                    enabled = item.enabled()
                else:
                    enabled = item.enabled
                if not enabled: _w.Enable( False)
        return w

    from layout import Int
    def getWidgetSize(fd, font=None):
        defsize = getTextSize('x', font)
        w = getattr(fd, 'width', None)
        h = getattr(fd, 'height', None)
        if w is None or isinstance(w, Int):
            w = -1 #default
        else:
            w = w * defsize[0]
        if h is None or isinstance(h, Int):
            pass
            #h = h == 1 and 30# or h * defsize[1]
        else:
            pass
            #h = h * defsize[1]
        #print getattr(fd, 'name', None), 'WxH=%sx%s' % (w,h)
        return CUSTOM_WIDGET_SIZE and (w, h) or wx.DefaultSize

    def add_additional_widgets( widget, parent, fielddata):
        widgets = []
        fd = fielddata
        label_before, label_after = fd.get_label_before().strip(), fd.get_label_after().strip()
        choosable = isinstance(widget, wx.TextCtrl) and getattr(fielddata, 'choosable', None)
        if label_before or label_after or choosable:
            size = getTextSize(label_before, margin_percents=None)
            if label_before:
                widgets += wx.StaticText(parent, -1, label_before, size= size),
            widgets += widget,
        if choosable == 'button':
            widgets += wx.Button(parent=parent, name=widget.GetName(), label=SEARCH_BTN_LABEL, size=(UNIT,UNIT)),
        elif choosable == 'calendar':
            widgets += wx.Button(parent=parent, name=widget.GetName(), label='+', size=(UNIT,UNIT)),
        if label_after:
            size = getTextSize(label_after, margin_percents=None)
            lbl = wx.StaticText(parent, -1, label_after, size= size)
            widgets += lbl,
        return widgets

    def addSizer( title, parent, orientation=wx.VERTICAL):
        if title:
            if title == '-': title = ''
            psizer = wx.StaticBoxSizer( wx.StaticBox( parent, 0, title), orientation)
        else:
            psizer = wx.BoxSizer(orientation)
        return psizer

    def EID(e): return e.evtType[0]
    def isEID( e_in, *eee):
        for e in eee:
            if e_in == e.evtType[0]: return True
        return False

    class _Any(object):
        def __init__(self, layout):
            self.choosers = {}
            self.inspect( layout)
        def inspect(self, panel):
            from data_model import _Browseable
            for rows in panel.rows:
                for x in rows:
                    if isinstance(x, Panel):
                        self.inspect(x)
                    else:
                        typ = x.getType()
                        name = getattr( x.getFieldData(), 'name')
                        if typ == 'Chooser':
                            self.choosers[ name ] = _Browseable(
                                data = [ '%s - %d ' % ( name, i) for i in range(20) ],
                            )
                        elif typ == 'treeview':
                            self.choosers[ name ] = self.make_tree( name)

        def __getattr__(self, name):
            choosers = self.__getattribute__('choosers')
            if name in choosers:
                return choosers[ name ]
            return name #+ ' <^*&#@'

        @staticmethod
        def make_tree(name):
            class MyModel( object): pass
            def populateModeli(name, c=120):
                modeli = []
                for i in range(c):
                    o = MyModel()
                    o.roditel = modeli and modeli[ len(modeli)/10 ] or None
                    o.ime = '%s%d' % (name, i)
                    o.desc = 'description %d' % i
                    modeli.append(o)
                return modeli
            from data_model import ColDef
            from treemodel import GenericTreeModel, SimpleTreeModelWrapper
            oo = GenericTreeModel( data=populateModeli(name), relation_attr='roditel')
            treesome = SimpleTreeModelWrapper(oo, column_defs=[ ColDef(address='ime', header='Ime',
                                                                       minwidth=40,   maxwidth=-1)])
            return treesome

    class RemoteNotifier(object):
        def __init__(self, func, userData):
            self.func = func
            self.userData = userData
        def __call__(self, data, is_confirmed):
            return self.func( data, is_confirmed, userData=self.userData)
        #def __del__(self):
        #    print self, 'is seriosly dead'

    class Binder(object):
        log = None
        def __init__(self, widget, evt, cb, *args, **kargs):
            self.cb = cb
            widget.Bind(evt, self, *args, **kargs)
        def __call__(self, evt):
            try:
                self.cb( evt)
            except Exception, e:
                if self.log:
                    self.log( sys.exc_info())
                else:
                    import traceback
                    traceback.print_exc()
        @classmethod
        def setLogger(klas, log):
            klas.log = log

        #def __del__(self):
        #    print self, 'is dying in harmony'

    from imager import Imager
    def getImageFromFileOrStream( imageName):
        'return wx.Image'
        if imageName is None: return
        s = Imager.get( imageName, pfx=True)
                #if wx.Image.CanRead( im): wx.Image( im, wx.BITMAP_TYPE_ANY)
        if s is not None: s = wx.ImageFromStream( s)
        return s

    def getImageType(filename):
        import imghdr
        try:
            return imghdr.what( UNICODE2STR(filename))
        except:
            return None

    def getGrowableFlag( field, default=''):
        if isinstance( field, Panel):
            fd = field.header
            growable = fd.get('expand', default)
        else:
            fd = field.getFieldData()
            growable = getattr( fd, 'expand', default)
        return dict(
                xy    = wx.BOTH,
                x     = wx.HORIZONTAL,
                y     = wx.VERTICAL,
                no    = None,
                False = None,
            ).get( growable, 0)

    class ListColumnResizer(object):
        def __init__(self):
            Binder(self, wx.EVT_SIZE, self.__OnSize)
            self.columns_inited = False
            self.min_col_sizes = None
            self.max_col_sizes = None
            self.columns = []

        def _doResize(self, col=None):
            if self.columns_inited and col is None: return
            columns_nr = self.GetColumnCount()
            if not columns_nr: return
            cx = self.GetClientSize()[0]
            if WXGTK and self.IsVScrollVisible():
                cx -= wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
            if self.min_col_sizes:
                assert len(self.columns) == len(self.max_col_sizes) == len(self.min_col_sizes), '%s - %s - %s' % (len(self.columns), len(self.max_col_sizes), len(self.min_col_sizes))
                columns = []
                columns_to_resize = []
                for i in range( len( self.columns)):
                    _max = self.max_col_sizes[i]
                    _min = self.min_col_sizes[i]
                    assert _min > 0, 'minwidth is %d, should be grater than 0' % _min
                    if _max is None: self.max_col_sizes[i] = _max = _min
                    if _max < 0 or _max > _min:
                        columns_to_resize.append(i)
                    elif _max < _min: #avoid witty programmers
                        print ('PLEASE FIX: min_col_size(%d) > max_col_size(%d) for column(%d)' % ( _min, _max, i))
                        self.max_col_sizes[i] = _min
                    columns.append(_min)
                while columns_to_resize:
                    total_requested_width = sum(columns)
                    if cx <= total_requested_width: break
                    whats_left = cx - total_requested_width
                    per_column = int(whats_left/len(columns_to_resize))
                    start_again = False
                    for col in columns_to_resize:
                        # first obtain columns width which have limits
                        _max = self.max_col_sizes[col]
                        if _max > 0:
                            if columns[col] + per_column > _max:
                                columns[col] = _max
                                start_again = True #recalculation needed
                            else:
                                columns[col] = columns[col] + per_column
                            columns_to_resize.remove(col)
                    if start_again: continue
                    for col in columns_to_resize:
                        # then spread the rest of the space to the unlimited ones
                        columns[col] += per_column
                        columns_to_resize.remove(col)

                for c in range(columns_nr):
                    self.SetColumnWidth(c, columns[c])
                self.columns_inited = True
                return
            return

        def __OnSize(self, ev):
            if 0:
                self.columns_inited = False
                def cb():
                    if not wx.GetMouseState().LeftDown():
                        try: self._doResize()
                        except wx.PyDeadObjectError: pass #ugly, but nothing to be afraid of
                wx.CallAfter(cb)
            if 1:
                if not wx.GetMouseState().LeftDown():
                    self.columns_inited = False
                    self._doResize()
            ev.Skip()

        def InitColumns(self, data):
            header = data.GetHeader()
            if self.columns:
                if self.columns is not header: #reinit
                    self.DeleteAllColumns()
                    #self.DeleteAllItems()
                    self.columns = None
                    self.columns_inited = False
                    self.min_col_sizes = None
                    self.max_col_sizes = None
            else:
                self.columns = header
                for i in range(len(self.columns or [])):
                    c = self.columns[i]
                    align = getAlignment4Column( c, isinstance( self, wx.ListCtrl))
                    self.InsertColumn(i, TXT(c.strip(' ')), align)

            if not self.min_col_sizes and not self.max_col_sizes:
                self.min_col_sizes = getattr( data, 'min_col_sizes', None)
                self.max_col_sizes = getattr( data, 'max_col_sizes', None)

# vim:ts=4:sw=4:expandtab
