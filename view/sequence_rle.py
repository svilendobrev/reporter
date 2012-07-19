#$Id$


class BaseCommandContainer( object):
    ''' basic interface for command manager/container '''
    class Command( object):
        def __init__( me, name ='', value =None,
                        from_column =0, from_row =0,
                        to_column =-1, to_row =-1):
            me.name = name
            me.value = value
            me.from_column = from_column
            me.from_row = from_row
            me.to_column = to_column
            me.to_row = to_row

        def as_tuple( me):
            cmd = [ me.name,
                    (me.from_column, me.from_row),
                    (me.to_column, me.to_row),
                  ]
            val = me.value
            if val is not None:
                if isinstance( me.value, (list, tuple)):
                    cmd += val
                else:
                    cmd.append( val)
            return tuple( cmd)

    ###########

    def __init__( me, col_idx):
        me.col_idx = col_idx
        me.container = []

    def add( me, name, value, start_row):
        raise NotImplementedError
    def flush( me):
        raise NotImplementedError


class SequenceRLE( BaseCommandContainer):
    ''' Merges redundant commands in one with wider range '''
    def __init__( me, col_idx):
        BaseCommandContainer.__init__( me, col_idx)
        me.open_commands = dict()

    def add( me, name, value, start_row):
        cmd = me.open_commands.get( name, None)
        if cmd:
            if cmd.value != value:
                me._close_command( cmd, start_row)
                me._open_command( name, value, start_row)
        else:
            me._open_command( name, value, start_row)

    def flush( me):
        for cmd_name, cmd_obj in me.open_commands.iteritems():
            me._close_command( cmd_obj)
        me.open_commands.clear()
        return me.container

    def _open_command( me, name, value, start_row):
        me.open_commands[ name] = me.Command( name, value, me.col_idx, start_row, me.col_idx, -1)

    def _close_command( me, cmd, to_row =-1):
        cmd.to_row = to_row
        me.container.append( cmd)


class SingleCellFormat( BaseCommandContainer):
    ''' Unlike SequenceRLE, each command applies to a single cell. '''
    def add( me, name, value, start_row):
        me.container.append( me.Command( name, value, me.col_idx, start_row, me.col_idx, start_row))

    def flush( me):
        return me.container



# vim:ts=4:sw=4:expandtab
