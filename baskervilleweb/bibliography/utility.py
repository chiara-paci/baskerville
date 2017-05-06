def crcissn(issn):
    if not str(issn).isdigit(): return('Y')
    pesi=[8,7,6,5,4,3,2]
    cod_lista=list(map(int,list(issn)))
    if len(cod_lista)<7:
        L=len(cod_lista)
        cod_lista+=[0 for x in range(L,7)]
    crc=11-(sum(map(lambda x,y: x*y,cod_lista,pesi))%11)
    if (crc==10): return('X')
    if (crc==11): return(0)
    return(crc)

def crcisbn(isbn):
    if not str(isbn).isdigit(): return('Y')
    pesi=[10,9,8,7,6,5,4,3,2]
    cod_lista=list(map(int,list(isbn)))
    if len(cod_lista)<9:
        L=len(cod_lista)
        cod_lista+=[0 for x in range(L,9)]
    crc=11-(sum(map(lambda x,y: x*y,cod_lista,pesi))%11)
    if (crc==10): return('X')
    if (crc==11): return(0)
    return(crc)

def crcisbn13(isbn):
    if not str(isbn).isdigit(): return('Y')
    pesi=[1,3,1,3,1,3,1,3,1,3,1,3]
    cod_lista=[9,7,8]+list(map(int,list(isbn)))
    if len(cod_lista)<12:
        L=len(cod_lista)
        cod_lista+=[0 for x in range(L,12)]
    crc=10-(sum(map(lambda x,y: x*y,cod_lista,pesi))%10)
    if (crc==10): return(0)
    return(crc)
