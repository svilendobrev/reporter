# $Id$
#s.dobrev 2k4

import difflib

def diff( h1, h2, h1name ='', h2name ='', type='context'):
    if isinstance( h1, str): h1 = h1.splitlines(1)
    if isinstance( h2, str): h2 = h2.splitlines(1)

    try:
        differ = type=='context' and difflib.context_diff or difflib.unified_diff
    except NameError:
        d = difflib.Differ()
        N = 2
        buff=[]
        a = False
        for line in d.compare( h1,h2):
            if line[0]==' ':
                buff.append( line)
                if len(buff)>N: del buff[0]
            else:
                if not a:
                    yield '-', h1name, '->', '+', h2name
                    a=True
                for l in buff:      #pre-context only
                    yield l,
                buff = []
                yield line
    else:
        for l in differ( h1, h2, h1name, h2name):
            yield l

def diff_print( h1, h2, h1name ='', h2name =''):
    for l in diff( h1, h2, h1name, h2name):
        print l,


# vim:ts=4:sw=4:expandtab

