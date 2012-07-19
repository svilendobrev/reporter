#$Id$


class RowClassifier( object):
    ''' Arranges rows into groups using classifier thresholds. Each group
        may have a list of aggregation rows. Filters are supported as well.
        Groups are not necessarily mutually exclusive, it depends on the given
        thresholds and filters. The threshold defines how the group is splitted
        into packets.
    '''
    def __init__( me, preserve_input_order =True, use_dynamic_grouping =False):
        me.preserve_input_order = preserve_input_order # True: only one packet is open for new rows
                                                       # False: the first compatible packet gets the new row

        me.use_dynamic_grouping = use_dynamic_grouping # enable creating new groups on the fly
        me.clear()

    def clear( me):
        me._rows_and_packets = []   # here we put _EACH_ incoming row,
                                    # but only after all groups have decided whether to register their packets or not
        me._groups = []
        me.finished = False

    @property
    def empty( me):
        return not me._rows_and_packets

    def group( me, threshold =None, aggregators =None, name =None, filter_func =None):
        if not me.use_dynamic_grouping and (me.finished or not me.empty):
            return
        from row import AggrRow
        from group import Group, UnorderedGroup
        from reporter.engine.util.attr import issubclass
        if issubclass( aggregators, AggrRow):
            aggregators = [ aggregators ]
        group_factory = me.preserve_input_order and Group or UnorderedGroup
        g = group_factory( me._rows_and_packets, len(me._groups), name, aggregators, threshold, filter_func)
        me._groups.append( g)

        if not me.empty:
            me._update_group( g)

    def _update_group( me, group):
        # FIXME dirty hack
        # TODO add tests for this
        insert_positions = []
        current_pos = 0
        for r in me._rows_and_packets:
            if not isinstance( r, Packet):
                if group.add( r) and current_pos:
                    insert_positions.append( current_pos)
            current_pos += 1
        if me.preserve_input_order:
            insert_positions.reverse()
            i = 0
            for pos in insert_positions:
                me._rows_and_packets.insert( pos, group.packets[ i])
                i += 1

    def add( me, r):
        if not me.finished:
            for g in me._groups:
                g.add( r)
            me._rows_and_packets.append( r)

    def end( me):
        if not me.finished:
            for g in me._groups:
                g.close('end of report')
            me.finished = True


    def get_group_by_name( me, name):
        for g in me._groups:
            if g.name == name:
                return g
        return None

# vim:ts=4:sw=4:expandtab
