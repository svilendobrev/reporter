#$Id$
# -*- coding: cp1251 -*-
MODEL_ENCODING = 'utf-8'
PREFERRED_ENCODING = 'cp1251'
# which is which bitch?

def TXT( txt):  #to unicode.
    if isinstance(txt, unicode):
        return txt
    try:
        return unicode( txt, MODEL_ENCODING)
    except UnicodeDecodeError:
        return unicode( txt, PREFERRED_ENCODING)

def TXTL( lst):
    return [ TXT(i) for i in lst ]

_ = TXT

def u2s( value):
    if isinstance(value, unicode):
        value = value.encode('utf-8')
    return value

def XTX( txt):  #from unicode
    assert isinstance(txt, unicode)
    try:
        return txt.encode( PREFERRED_ENCODING)
    except UnicodeDecodeError:
        return txt.encode( MODEL_ENCODING)

# vim:ts=4:sw=4:expandtab
