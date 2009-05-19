#$Id$
class Actions:
    OK = 'OK'
    NO = 'NO'
    YES = 'YES'
    CANCEL = 'CANCEL'

class View:
    '''interface to the controller'''
    class SelfClose:
        '''indication to close, returned from ctl.action'''
        pass

    def MakeNewWindow(self, ctl, typ=None, xml=None):
        pass

    def SetValue(self, name, value):
        '''set value to be displayed to control name'''
        pass
    def GetValue(self, name):
        '''get displayed value from control name'''
        return None

    def SetState(self, name, state):
        '''set control state - disabled, hidden, etc..'''
        pass
    def GetState(self, name):
        '''get control state'''
        return None

    def Message(self, message, *args, **kargs):
        pass

    def Keys(self):
        pass

    def Raise(self):
        pass

class Controller(object):
#   interface to the view

    def Init(self, view, notifier = None):
        self.notifier = notifier
        pass

    def Redraw(self, view):
        pass

    def Change(self, name, value, view):
        print 'CTL: %s -> %s' % (name, value)

    def Action(self, name, view):
        print 'Action: %s' % name

    def Listener(self, e, view):
        '''returns View.SelfClose or id to focus to'''
#        print 'event: %s, control: %s, event data: %s' % (e.event, e.name, e.val or 'none')
        if e.event == 'CHANGE':
            return self.Change(e.name, e.val, view)
        elif e.event == 'CLOSE':
            return view.SelfClose
        elif e.event == 'BUTTON':
            return self.Action(e.name, view)
        else:
            print 'Listener?', e
        return None


class FBrowsable:
    """Interface to sequence of data fed to browser
    based on current positon and scrolling
    """
    def SavePos( self ):
        """save current position in self.memory (no nesting)"""
        pass
    def RestorePos( self ):
        """restore current position from self.memory"""
        return error
    def First( self ):
        """set current position to first element"""
        return error
    def Last( self ):
        """set current position to last element"""
        return error
    def Next( self ):
        """move current position to next element"""
        return error
    def Prev( self ):
        """move current position to previous element"""
        return error
    def GetHeader( self, x=0):
        """return column headers (h1,h2,...)"""
        return None
    def GetRow( self ):
        """return current row as text (t1,t2,...)"""
        return None
    def __iter__(self):
        raise NotImplementedError


# vim:ts=4:sw=4:expandtab
