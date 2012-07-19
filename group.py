#$Id$
# -*- coding: utf-8 -*-

class Group( object):
    ''' Групата е класификатор на редове от справката по дадено условие (праг) и филтър.
    Тя може да съдържа един или повече пакети.
    Във всеки момент в групата има точно един отворен пакет.
    Той може да се затваря автоматично от праговата функция или принудително.
    '''

    def __init__( me, packet_order, group_id, name =None,
                aggregators =None, threshold_func =None, filter_func =None):
        me.group_id = group_id
        me.name = name
        me.aggregators = aggregators or []
        me.threshold_func = threshold_func
        me.filter_func = filter_func
        me.packets = []
        me.packet_order = packet_order

    def is_compatible( me, packet, row):
        return not ( me.threshold_func and me.threshold_func( row, packet.rows) )

    def _get_packet( me, row):
        if me.packets:
            p = me.packets[-1]
            if me.is_compatible( p, row):
                return p
            me.close( reason=me.threshold_func.func_name)
        return me._start_new_packet()

    def _start_new_packet( me):
        from packet import Packet
        new = Packet( me)
        me.packets.append( new)
        return new

    def add( me, r):
        p = me._get_packet( r)
        is_new_packet = p.empty
        p.add( r)
        return is_new_packet

    def close( me, reason):
        if me.packets:
            p = me.packets[-1]
            me._close_packet( p, reason)

    def _close_packet( me, packet, reason):
        packet.reason2close = reason
        packet.close( me.aggregators, me.filter_func)
        me.packet_order.append( packet)
        print len( me.packet_order)

    def __str__( me):
        return me.__class__.__name__ + ' %(group_id)s current: %(current)s' % self.__dict__


class UnorderedGroup( Group):
    def _get_packet( me, row):
        for p in me.packets:
            if me.is_compatible( p, row):
                return p
        return me._start_new_packet()

    def close( me, reason):
        for p in me.packets:
            assert not p.empty
            me._close_packet( p, reason)


# vim:ts=4:sw=4:expandtab
