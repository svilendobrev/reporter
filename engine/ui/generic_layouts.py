#$Id$
# -*- coding: utf-8 -*-

#from reporter.engine.ui.layout import Panel
from layout import Panel

BTN_SIZE = (-1, 28) #(120, 28) is way faster under linux XXX

def makeOkCancelPanel( col_span =1, save =False, default =True, printout =False):
    layout = ''
    if printout:
        layout += '<Printout>'
    if save:
        layout += '<SaveAndNew>'
    layout += '<OK> <Cancel>'
    return Panel( layout,
                field_map= dict( OK         = dict( default= default, label = ' ', img = 'ok.png', size= BTN_SIZE),
                                SaveAndNew  = dict( label = 'Съхрани и създай нов', img = 'save&new.png', size= BTN_SIZE),
                                Printout    = dict( label = 'Печат', img = 'print.png', size = BTN_SIZE),
                                Cancel      = dict( default= default, label = 'Изход', img = 'exit.png', size= BTN_SIZE)
                                ),
                align = 'right',
                col_span = col_span
            )

def makeCloseButtonPanel( col_span=1, default=False):
    return Panel( '<Cancel>',
                field_map= dict( Cancel= dict( default= default, label='Изход', img = 'exit.png', size= BTN_SIZE)),
                align = 'right',
                col_span = col_span
            )

def panel4filter_ime(with_code=False):
    return Panel( ' [filter_ime] ' + (with_code and '[_ by_code ]' or ''),
            field_map= dict(
                filter_ime = dict( label='Филтър', expand='x', search_on_change =True),
                by_code = dict(label='По код'),
#               Refresh    = dict( label='Търсене', default=True), #leave it for now
            ),
        )

chooser_LAYOUT = '''\
    [? chooser_data]
    [+ chooser_data]
    [+ chooser_data]
    [+ chooser_data]
    [+ chooser_data]
'''
chooser_MAP = dict(
    chooser_data= dict(view_type='list_multi', label='')
)

panel4filter_date = Panel( '''@Филтър
    [ interval.valid_date_from] [ interval.valid_date_to] [ interval.trans_date] [_ interval.group]< refresh>
''', field_map= {
    'interval.valid_date_from'  : dict(label='От дата:', choosable='calendar'),
    'interval.valid_date_to'    : dict(label='До дата:', choosable='calendar'),
    'interval.trans_date'       : dict(label='Kam дата:', choosable='calendar'),
    'interval.group'            : dict(label='Po dati'),
    'refresh'                   : dict(label='Tarsi', default=True),
    },
)

def makeChooserPanel(
        horizontal =False,
        with_ok_cancel=False,
        with_history =True,
        with_date_interval =False,
        title ='?',
        buttons_list = (),
        buttons_map  = {},
        with_code = False,
        prefix = ''
    ):
    if not buttons_list:
        buttons_list = '<New> <Edit>'.split()
    if with_history:
        buttons_list = buttons_list + ['<History>' ]
        buttons_map = buttons_map.copy()
        buttons_map.update( History= dict( default= False) )

    if not with_ok_cancel:
        closeBtn_Panel = makeCloseButtonPanel( col_span=2)
    else:
        closeBtn_Panel = makeOkCancelPanel( col_span=2, default=False)  #XXX why False

    p = Panel( prefix= prefix)
    p += with_date_interval and panel4filter_date or panel4filter_ime(with_code)
    p += Panel( chooser_LAYOUT, chooser_MAP)    #grid

    if horizontal:
        buttons_Panel = Panel( ' '.join( buttons_list), buttons_map)
        p += Panel('') * buttons_Panel * Panel('') * Panel('') * closeBtn_Panel
    else:
        buttons_Panel = Panel( '\n'.join( buttons_list), buttons_map)
        p *= buttons_Panel
        p += closeBtn_Panel
    if not with_ok_cancel:
        p.fielddata['confirm'] = 'Close'
    p.fielddata['minsize'] = (640, 480)
    return p

# vim:ts=4:sw=4:expandtab
