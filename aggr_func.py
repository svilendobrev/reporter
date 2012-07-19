#$Id$


from reporter.row import AggrRow

def make_aggregator( sets, calcs):
    class TemplateAgg( AggrRow):
        _set_ = sets
        _calc_ = calcs
    return TemplateAgg

class AggFuncWrapper( object):
    def __init__(me, func, field_name):
        me.function = func
        me.field_name = field_name

    def __call__( me, obj):
        return me.function( obj.column( me.field_name))

    def __str__( me):
        return 'Aggregation: '+ ' '.join( str( attr) for attr in [ me.function, me.field_name])

def aggr_template( agg_func, *fld_calc, **fld_set):
    calc = dict()
    for fld in fld_calc:
        #calc[ fld] = lambda me, fld=fld: agg_func( me.column( fld))
        calc[ fld] = AggFuncWrapper( agg_func, field_name=fld)
    return make_aggregator( fld_set, calc)

###########################

def SUM( *fld_calc, **fld_set):
    return aggr_template( sum, *fld_calc, **fld_set)

def AVG( *fld_calc, **fld_set):
    def avg( column):
        assert len( column) > 0 and 'Aggregation over empty set of data'
        return sum( column) / len( column)
    return aggr_template( avg, *fld_calc, **fld_set)

def COUNT( *fld_calc, **fld_set):
    return aggr_template( len, *fld_calc, **fld_set)

def MAX( *fld_calc, **fld_set):
    return aggr_template( max, *fld_calc, **fld_set)

def MIN( *fld_calc, **fld_set):
    return aggr_template( min, *fld_calc, **fld_set)



# vim:ts=4:sw=4:expandtab
