#$Id$


############################################################################
###Tova ne se polzva zasega ####
table_data = [
 ['\xc8\xec\xe5', '\xc2\xfa\xe7\xf0\xe0\xf1\xf2', '\xc0\xe4\xf0\xe5\xf1'],
 ['a', 'one', 'la'],
 ['aggr', 'one', 'ba'],
 ['\xc3\xf0\xf3\xfe', 'one', 'xa'],
 ['\xcc\xfe\xec\xfe\xed', 'Nne', 'df '],
 ['\xcb\xf3\xea\xf0\xe5\xf6\xe8\xe9', 'None', '  '],
 ['\xed\xee\xe2\xe0\xea', 'None', ''],
 ['\xe4\xee\xed \xea\xe8\xf5\xee\xf2', 'None', '  '],
 ['\xf2\xe5\xf0\xec\xe8\xed\xe0\xf2\xee\xf02', 'None', '  '],
 ['\xf0\xe0\xec\xe1\xee', 'None', '  '],
 ['\xf1\xf2\xe0\xe6\xe0\xed\xf21', 'None', '  '],
 ['\xf1\xf2\xe0\xe6\xe0\xed\xf22', 'None', '  '],
 ]
#        r  c    r  c    r  c    r  c    r  c   r  c     r  c
cell = [(0, 0), (1, 0), (4, 0), (0, 1), (1, 1),(0, 2), (1, 2)]
zcell = [(0, 0), (0, 1), (0, 2)]
def cell_parse(cell):

    c = cell
    col = []
    row = []
    table = []

    g = cell[0][1]
    for x in c:
        if x[1] == g:
            col.append(x)
        else:
            g = x[1]
            table.append(col)
            col =[]
            col.append(x)

    table.append(col)
    return table
aggr_idx = []
zaggr_idxs =[]
def table_data_parse(table_data, cell, aggr_idxs =aggr_idx ):
    l = zip( *table_data)
    col = []
    data_cols = []
    data = []
    null= cell[0][0]
    l1= []
    aggr = aggr_idxs
    p=0
    for df in l:
        l1.append(list (tm for tm in df ))

    l=l
    agregirasht = False
    for c in cell:
        for xy in c:
            x = xy[0]
            y = xy[1]

            div = abs(null[0] - x)

            while p!=div:
                r = l[cell.index(c)][p]
                for a in aggr:
                    print p, a
                    if p == a:
                        agregirasht = True
                if not agregirasht:
                    col.append(r)
                else:
                    agregirasht = False

                p+=1

            if div!=0:
                data_cols.append(col)
                col= []

        for pl in range(p, len(l[cell.index(c)])):
                for a in aggr:
                    if pl == a:
                        agregirasht = True
                if not agregirasht:
                    col.append(l[cell.index(c)][pl])
                else:
                    agregirasht = False


        data_cols.append(col)
        col=[]
        p=0
        data.append(data_cols)
        data_cols = []
    return data
#################################################################################3

############## Tova se polzva, za izvajdaneto na agregirashtite redove ot dannite
def aggreg( data, aggr_idxs):
    l1 = []
    agregirasht = False
    for df in data:
        l1.append(list (tm for tm in df ))

    data=l1
    col = []
    aggr_col = []
    aggr_data = []
    aggr_row=[]
    data_row = []
    i=0
    aggr = aggr_idxs
    for colomn in range(0, len(data)):
        for row in range(0, len(data[colomn])):
            for a in aggr:
                if row == (a-1):
                    agregirasht = True
            if not agregirasht:
                col.append(data[colomn][row])
            elif agregirasht:
                aggr_row.append(data[colomn][row])
                print aggr_row
                agregirasht = False

        aggr_data.append(aggr_row)
        data_row.append(col)
        col= []
        aggr_row =[]

    return data_row, aggr_data

#Run
def data_parse( table_data, aggr_idxs ): #cell= cell, ):
    d =zip(*table_data)
    data, aggr = aggreg(d, aggr_idxs)
    return data, aggr
if __name__=='__main__':
    print cell_parse( cell)
# vim:ts=4:sw=4:expandtab

