#$Id$
# -*- coding: cp1251 -*-

def direct( map, x): return ''.join( map.get(a,a) for a in x )

def do321( map, x):
    r = ''
    while x:
        try:
            r += map[ x[:3] ]
            x = x[3:]
            continue
        except KeyError: pass
        try:
            r += map[ x[:2] ]
            x = x[2:]
            continue
        except KeyError: pass

        r += map.get( x[0], x[0] )
        x = x[1:]
    return r

def make( cyr, lat, cyr2lat):
    cl = dict( zip( cyr,lat ) )
    cl.update( (low2up(k), capital(v)) for k,v in cl.items() )

    cyr2lat.update( (low2up(k), capital(v)) for k,v in cyr2lat.items() )
    cyr2lat.update( cl )

    lat2cyr = dict( (v,k) for k,v in cyr2lat.iteritems() if v )
    lat2cyr.update( (v,k) for k,v in cl.iteritems() if v )
    return cyr2lat,lat2cyr

def low2up( k): return chr(ord(k)-32)
def capital(v): return v and v[0].upper()+v[1:] or v

class transliterator:
    @classmethod
    def dump( me):
        print 'cyr2lat:', ' '.join( k+':'+v for k,v in me.cyr2lat.items() )
        print 'lat2cyr:', ' '.join( k+':'+v for k,v in me.lat2cyr.items() )
    @classmethod
    def cyr2lat( me, x): return direct( me._cyr2lat, x)
    @classmethod
    def lat2cyr( me, x): return do321( me._lat2cyr, x)

class zvuchene( transliterator):
    _cyr2lat,_lat2cyr = make(
        cyr= 'абвгдезийклмнопрстуфхц',
        lat= 'abvgdezijklmnoprstufhc',
        cyr2lat = {
        'ж': 'zh',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'sht',
        'ь': '',
        'ъ': 'y',
        'ю': 'yu',
        'я': 'ia',
        'э': 'e',
        'ы': 'i',
        })

#TODO parse [abc] \\a
class zvuchene_qw( transliterator):
    _cyr2lat,_lat2cyr = make(
        cyr= 'абвгдезийклмнопрстуфхц',
        lat= 'abwgdeziiklmnoprstufhc',
        cyr2lat = {
        'ж': '[j]',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'sht',
        'ь': '',
        'ъ': 'y',
        'ю': '[ji]u',
        'я': '[ji]a',
        'э': 'e',
        'ы': 'i',
        'в': 'v',
        })

class qwerty_keyboard( transliterator):    #fonetic
    _cyr2lat,_lat2cyr = make(
        cyr= 'абвгдежзийклмнопрстуфхц',
        lat= 'abwgdevzijklmnoprstufhc',
        cyr2lat = {
        'ч': '`',
        'ш': '\\[',
        'щ': '\\]',
        'ь': '',
        'ъ': 'y',
        'ю': '\\\\',
        'я': 'q',
        'э': '@',
        'ы': '^',
        })

class qwerty_keyboard_yu( transliterator):   #fonetic
    _cyr2lat,_lat2cyr = make(
        cyr= 'абвгдежзиклмнопрстуфхц',
        lat='abvgde`ziklmnoprstufhc',
        cyr2lat = {
        #'й':'j',
        '-': 'j',
        'ч': '~',
        'ш': '\\{',
        'щ': '\\}',
        'ь': '',
        'ъ': 'y',
        'ю': '\\\\',
        'я': 'q',
        'э': '@',
        'ы': '^',
        })

class desi( transliterator):   #digito-fonetic
    _cyr2lat,_lat2cyr = make(
        cyr= 'абвгдежзийклмнопрстуфхц',
        lat= 'abvgdejziiklmnoprstufhc',
        cyr2lat = {
        'ч': '4',
        'ш': '6',
        'щ': '6t',
        'ь': '',
        'ъ': 'y',
        'ю': 'iu',
        'я': 'ia',
        'э': '@',
        'ы': '^',
        })

if __name__ == '__main__':
    import sys
    nm = sys.argv.pop(0)
    l2c = 'lat2cyr' in nm
    c2l = 'cyr2lat' in nm
    try: sys.argv.remove( '-cyr2lat')
    except: pass
    else: c2l = 1; l2c = 0
    try: sys.argv.remove( '-lat2cyr')
    except: pass
    else: c2l = 0; l2c = 1

    map = zvuchene
    convert = getattr( map, l2c and 'lat2cyr' or 'cyr2lat' )
    for l in sys.stdin:
        sys.stdout.write( convert( l) )

# vim:ts=4:sw=4:expandtab
