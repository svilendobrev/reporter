#$Id$
# -*- coding: cp1251 -*-

from data_model import Browseable4DB
from spravka import SprDataModel
from reporter.engine.basedb.types_base import _static_type, Date

class DateInterval( _static_type.StaticStruct):
    date_from = Date()
    date_to = Date()

class SprDate2Model( SprDataModel):
    interval = DateInterval()

    def refresh( me, context, current_choice =None):
        me.spr.date_from = getattr( me.interval, 'date_from', None)
        me.spr.date_to = getattr( me.interval, 'date_to', None)
        SprDataModel.refresh( me, context, current_choice)

# vim:ts=4:sw=4:expandtab
