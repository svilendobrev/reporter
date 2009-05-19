#$Id$
from pyXLWriter import *
''' Funkciq za Slagane na Granica na 'Tablica' definirana chrez gorna-lqva i
    dolna-dqsna kletka!

'''
#dirEx = 'D:\\Proba\\'
w = Writer('BorderProba.xls')#+dirEx)#, big = True)

ws = w.add_worksheet()



top_br = 5
bottom_br = 5
left_br = 5
right_br = 5


def border(types):
        if types == 0:
                style = w.add_format()
                return style

        if types == 1: 
                #TOP LEFT CORNER
                t= [('top',top_br), ('left',left_br,), ('size', 12)]
                ts = dict(t)        
                style1 = w.add_format(**ts)
                return style1

        if types == 3:
                #TOP RIGHT CORNER
                style3 = w.add_format(top = top_br, right= right_br, )
                return style3
        
        if types == 2:
                #TOP MIDDLE
                style2 = w.add_format(top = top_br,)
                return style2 

        if types == 4:
                #MIDLE LEFT
                style4 = w.add_format(left= left_br)
                return style4

        if types == 5:
                #MIDLE RIGHT
                style5 = w.add_format(right= right_br,)
                return style5

        if types == 6:
                #BOTTOM LEFT
                style6 = w.add_format(left= left_br, bottom= bottom_br)
                return style6

        if types == 7:
                #BOTTOM MIDLE
                style7 = w.add_format(bottom= bottom_br)
                return style7

        if types == 8:
                #BOTTOM RIGHT
                style8 = w.add_format(right= right_br, bottom= bottom_br)
                return style8


cell1 = (1,1)
cell2 = (10,10)


def table(cell1, cell2):
        #Kletka Gore-Lqvo
        r1 = cell1[0]
        c1 = cell1[1]
        #Kletka Dolu-Dqsno
        r2 = cell2[0]
        c2 = cell2[1]

        ws.write([r1,c1], '',border(0))



        #Goren Liav agal na tablicata
        ws.write([r1, c1], 'Cell '+str(1+r1)+' '+str(1+c1), border(1))
        #Goren Red na Tablicata
        for c in range(c1+1,c2):
               ws.write([r1,c],'Cell '+str(1+r1)+' '+str(1+c),border(2))
        #tmp1=[('Cell '+str(1+r1)+' '+str(1+c)) for c in range(c1+1,c2)]
        #ws.write_row([r1,c1+1], tmp1, border(2))

        #Goren Desen agal na tablicata
        ws.write([r1,c2], 'Cell '+str(1+r1)+' '+str(1+c2), border(3))

        #Sredni Koloni

        tmp=[[('Cell '+str(1+r)+' '+str(1+x)) for x in range(c1+1,c2)] for r in range(r1+1, r2)]
        ws.write_col([r1+1,c1+1],tmp,border(0))

        #Lqva kolona
        tmp2=[('Cell '+str(1+r)+' '+str(1+c1)) for r in range(r1+1,r2)]
        ws.write_col([r1+1,c1],tmp2, border(4))

        #Dqsna Kolona
        tmp3=[('Cell '+str(1+r)+' '+str(1+c2)) for r in range(r1+1,r2)]
        ws.write_col([r1+1,c2],tmp3, border(5))
                     
         #   ws.write([r, c1], 'Cell '+str(1+r)+' '+str(1+c), border(4))
        #ws.write([r,c2],'Cell '+str(1+r)+' '+str(1+c2), border(5))
       
        #for c in range(c1,c2):
        #Dolen Red
        ws.write([r2, c1], 'Cell '+str(1+r2)+' '+str(1+c1), border(6))

        tmp4=[('Cell '+str(1+r2)+' '+str(1+c)) for c in range(c1+1,c2)]
        ws.write_row([r2,c1+1], tmp4, border(7))
                     
        ws.write([r2, c2], 'Cell '+str(1+r2)+' '+str(1+c), border(8))

        f = w.add_format()
        
ws.set_row( 1,20,  1 )


table(cell1,cell2)
w.close()

# vim:ts=4:sw=4:expandtab
