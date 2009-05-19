#$Id$
# -*- coding: cp1251 -*-

class Packet( object):
    ''' Пакетът е списък от редове, получен в резултат от праговата функция на групата,
    към която принадлежи. Може да притежава агрегиращи редове.
    Те могат да се изчисляват върху част от редовете в пакета получена от филтрова функция
    от групата. Пакетът има две състояния - отворен и затворен. Нови редове могат да се
    добавят само в отворен пакет.
    '''

    def __init__( me, group):
        me.rows = []
        me.agg_rows = []
        me.opened = True
        me.group = group
        me.reason2close = ''

    @property
    def empty( me):
        return not me.rows

    def close( me, aggregators, filter_func):
        if aggregators:
            if filter_func:
                rows2agg = [ r for r in me.rows if filter_func(r) ] #filter( filter_func, me.rows)
            else:
                rows2agg = me.rows

            me.agg_rows = []
            for agg in aggregators:
                row = agg( rows2agg)
                row.set_packet( me)
                me.agg_rows.append( row)
        me.opened = False

    def add( me, r):
        if not me.opened:
            return
        r.set_packet( me)
        me.rows.append( r)

    def __str__( me):
        delim = '\n      '
        s = delim + delim.join( [ str(r) for r in me.rows])
        s += '\n'
        s += 'Agg rows:' + delim + delim.join( [ str(agg) for agg in me.agg_rows])
        s += delim + me.reason2close
        return s

# vim:ts=4:sw=4:expandtab
