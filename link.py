#$Id$


from svd_util.attr import get_attrib

class LinkBase( object):
    def dereference( me, namespace):
        return me or 'dereferenced value'

class Link( LinkBase):
    def __init__( me, src_key):
        #src url
        me.src_key = src_key    # to address the target
        me.attr_name = None     # to address target's data

    def dereference( me, namespace):
        src_obj = namespace[ me.src_key]
        if isinstance( src_obj, LinkBase):
            src_obj = src_obj.dereference( namespace)

        if me.attr_name:
            res = get_attrib( src_obj, me.attr_name)
            if isinstance( res, LinkBase):
                return res.dereference( namespace)
            return res
        return src_obj

    def clone( me):
        c = me.__class__( me.src_key)
        c.attr_name = me.attr_name
        return c

    def __str__( me):
        return 'Link source name: %s  attribute: %s' % ( me.src_key, me.attr_name)


class LinkContainer( LinkBase):
    def __init__( me, attr_prefix =''):
        for k,v in me.__dict__.iteritems():
            if isinstance( v, Link):
                if attr_prefix: attr_prefix += '.'
                v.attr_name = attr_prefix + k

    def dereference( me, namespace):
        for name, attr in me.__dict__.iteritems():
            if isinstance( attr, LinkBase):
                setattr( me, name, attr.dereference( namespace))
        return me



# vim:ts=4:sw=4:expandtab
