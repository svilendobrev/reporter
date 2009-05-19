#$Id$
# -*- coding: cp1251 -*-

from data_model import Browseable as Browsable, FBR, ColDef
from myctl import ActionChooser, BasicController, Chooser
from uitools import _
from reporter.engine.util.attr import setattr_from_kargs
################ spravka model

class ColDef4Spr( object):
    def __init__( me, minwidth =None,
            maxwidth =None, # None: no resize, -1: no limit
        ):
        me.minwidth=minwidth
        me.maxwidth=maxwidth

class SprDataModel( object):
    spravka = None
    column_defs = None

    def __init__( me, spravka =None, column_defs =None, **kargs):
        column_defs = column_defs or me.column_defs
        if column_defs is not None:
            kk = dict(
                min_col_sizes= [ c.minwidth for c in column_defs ],
                max_col_sizes= [ c.maxwidth for c in column_defs ],
            )
            for k in kk:
                assert k not in kargs, '__init__: both column_defs=.. and %(k)s=.. specified' % locals()
            kargs.update( kk)
        me.__init__2( spravka, **kargs)

    def __init__2( me, spravka, context= 'ignored', current_choice='ignored', **kargs4browseable):
        me.name = 'test name'
        spravka = spravka or me.spravka
        me.spr = spravka()
        from reporter.view.wx_view import ViewRedovaWxBrowsable
        viewer = ViewRedovaWxBrowsable( me.spr)
        me.viewer = viewer
        me.kargs4browseable = kargs4browseable
        me._chooser_data = me._make_browsable( [], me.viewer.get_labels())

    def is_empty( me):
        return not (me._chooser_data and me._chooser_data.data)

    def refresh( me, context, current_choice =None):
        #assert current_choice is None
        me.spr.refresh( context=None, dbcontext=context)
        header, data = me.viewer.make_output()
        me._chooser_data.SetData( data)

    def _make_browsable( me, data, header):
        return Browsable( data= data, header= header,
                          data_column_names= me.spr.layout,
                          default_column_value= [''],
                          formatter= me._formatter,
                          **me.kargs4browseable
                        )

    def _formatter( me, data, data_column):
        view = me.viewer.get_view( data_column, data)
        if view:
            return me.viewer.convert_data( data, view)
        return data

class SprCrosstabDataModel( SprDataModel):
    default_min_col_width = 100
    default_max_col_width = -1

    def __init__( me, spravka =None, default_min_col_width =None, default_max_col_width =None, **kargsignore):
        me.name = 'test name'
        spravka = spravka or me.spravka
        me.spr = spravka()
        if default_min_col_width is not None: me.default_min_col_width = default_min_col_width
        if default_max_col_width is not None: me.default_max_col_width = default_max_col_width
        from reporter.view.wx_view import ViewCrosstabWxBrowsable
        me.viewer = ViewCrosstabWxBrowsable( me.spr)
        me._chooser_data = None

    class CrosstabBrowsable( Browsable):
        def GetRow( me):
            return FBR.GetRow( me)

    def _make_browsable( me, data, header):
        return me.CrosstabBrowsable( data= data,
                          header= header,
                          min_col_sizes= len( header) * (me.default_min_col_width,),
                          max_col_sizes= len( header) * (me.default_max_col_width,),
                        )

    def refresh( me, context, current_choice =None):
        assert current_choice is None
        me.spr.refresh( context=None, dbcontext=context)
        header, data = me.viewer.make_output()
        me._chooser_data = me._make_browsable( data, header)

##############
class ExportFmt(object):
    def __init__(me, fmt = 'fmt', desc = 'desc'):
        me.fmt = fmt
        me.desc = desc
    def __str__(me):
        return me.fmt + ' ' + me.desc

class SpravkaExportChooser( BasicController):

    def data_model_factory(me, *a, **ka):
        class Fmt:
            _format = Browsable(data = [], column_defs = (
                ColDef('fmt', 'Формат', minwidth = 100),
                ColDef('desc', 'Описание', minwidth = 100, maxwidth = -1),
            ))
        return Fmt()

    def __init__(me, *a, **ka):
        setattr_from_kargs( me, ka, remote_notifier = None)
        BasicController.__init__(me, *a, **ka)
        me.model = me.data_model_factory()
        data = [
            ExportFmt('pdf', 'Portable Document Format'),
            ExportFmt('ps',  'Adobe PostScript'),
            #ExportFmt('txt', 'Plain text'),
            #ExportFmt('bin', 'Raw binary dump (core)'),
        ]
        from reporter.common import use_excel
        if use_excel:
            data.insert(0,ExportFmt('xls', 'Excel Workbook'))
        me.model._format.SetData(data)
        me.model._format.refresh( current_choice = 0, as_index = True)

    @property
    def layout(me):
        from reporter.engine.ui.layout import Panel
        from reporter.engine.ui.generic_layouts import makeOkCancelPanel
        fmap = dict( _format = dict( label = '', view_type = 'list_multi', expand = 'xy'))
        txt = '@Изберете формат\n[? _format ]'
        p = (Panel( title = 'Експорт', minsize = (320,240)) +
             Panel( txt = txt, field_map = fmap, expand = 'xy') +
             makeOkCancelPanel())
        return p

    def export(me, data):
        if me.remote_notifier:
            me.remote_notifier(data)

    def cursor_confirm(me, name, idx):
        me.export(me.model._format.get_current())
        return me.view.SelfClose

    def Confirm(me, ok):
        if ok: me.export(me.model._format.get_current())
        return BasicController.Confirm(me, ok)


class SpravkaController( ActionChooser):
    ok_closes = True
    spr_layout = None
    def __init__( me, layout =None, **kargs):
        me.layout = layout or me.spr_layout
        ActionChooser.__init__( me, **kargs)

    EXTRA_ACTIONS = ActionChooser.EXTRA_ACTIONS + ['action_Refresh', 'action_Printout', 'action_Export']

    def action_Refresh( me, *args, **kargs):
        updater = me.view.ProgressDialog( title= _('Моля, изчакайте..'),
                                          message= _('Зареждане на данни'))
        updater.update()
        me.setValue( *args, **kargs)
        #me.Redraw()
        updater.close()

    def action_Printout( me):
        from reporter.common import show_preview
        updater = me.view.ProgressDialog( title= _('Моля, изчакайте..'),
                                          message= _( 'Подготовка на печат') )
        updater.update()
        label = 'Печат на '+str( me.title)
        show_preview( me.model.spr, label, parent=me.view.frame)
        updater.close()

    def action_Export( me):
        me._newChild(SpravkaExportChooser, modal = True,
                    data_model = me.model,
                    remote_notifier = me.action_Format)

    def action_Format(me, export_fmt):
        print 'action_Format'
        from reporter.common import Viewer
        filename = me.view.SaveFile( default_name = 'Export',
                                     extension =  export_fmt.desc + '| *.'+export_fmt.fmt)
        if filename is not None:
            filename = filename.decode('utf8')
            dc = export_fmt.fmt
            Viewer( me.model.spr, dc=dc).make_output( filename=filename)
            if dc == 'xls':
                from ui.filter.xl import is_exists, XL, get_XL
                if is_exists:
                    xlapp = get_XL()
                    xl = XL( xlapp, filename)
                    xl.show()



    def newChild( me, data_model =None, **kargs):
        db_obj = getattr( data_model, 'db_object', None)
        if db_obj:
            from reporter.engine.ui.myctl import EditorModes
            kargs['mode'] = EditorModes.UPDATE
            return ActionChooser.newChild( me, data_model=db_obj,  **kargs)


# vim:ts=4:sw=4:expandtab
