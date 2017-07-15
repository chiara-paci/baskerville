# -*- coding: utf-8 -*-

#from config import *
import urllib.request, urllib.error, urllib.parse
import re

from bibliography.models import PublisherAddress,RepositoryCacheBook,RepositoryCacheAuthor,Author

URL_CONVERSION = [
    ( ["+"]                 , " " ),
    ( ["%21"]               , "!" ),
    ( ["%23"]               , "#" ),
    ( ["%26"]               , "&" ),
    ( ["%27"]               , "'" ),
    ( ["%28"]               , "(" ),
    ( ["%29"]               , ")" ),
    ( ["%80"]               , "€" ),
    ( ["%2F","%2f"]         , "/" ),
    ( ["%5B","%5b"]         , "[" ),
    ( ["%5D","%5d"]         , "]" ),
    ( ["%CC","%cc"]         , "Ì" ),
    ( [" %3A","%3A"," %3a","%3a"], ":" ),
    ( [" %2C","%2C"," %2c","%2c"], "," ),

]

def url_ripulisci(stringa):
    for (lista,val) in URL_CONVERSION:
        for l in lista:
            stringa=stringa.replace(l,val)
    stringa=stringa.strip()
    print("===>",stringa)
    return(stringa)

class BookRepository(object):
    def __init__(self,name): 
        self.name=name

    def get_addresses(self,city):
        #objs=PublisherAddress.objects.filter(city=city)
        #if objs: return objs
        return None

    def get_by_isbn(self,isbn10,isbn13): return({})

    def get_authors(self,data): 
        ret=[]
        n=0
        for aut in data:
            # qset=Author.objects.filter_by_name(aut)
            # if qset.count():
            #     ret.append( ("author",n,qset.first()) )
            # else:
            #     ret.append( ("author",n,aut) )
            ret.append( ("author",n,aut) )
            n+=1
        return ret

    def save_cache(self,isbn,R):
        for k in ["city","publisher","year"]:
            if k not in R: R[k]=""
        if "authors" not in R: R["authors"]=[]
        book_obj,created=RepositoryCacheBook.objects.get_or_create(isbn=isbn,
                                                                   defaults={ "title": R["title"],
                                                                              "city": R["city"],
                                                                              "publisher": R["publisher"],
                                                                              "year": R["year"],
                                                                              "indb": False
                                                                              })
        for role,ind,aut in R["authors"]:
            aut_obj,created=RepositoryCacheAuthor.objects.get_or_create(book=book_obj,
                                                                        name=aut,
                                                                        defaults={ "pos": ind,"role": role })
        

class CacheRepository(BookRepository):
    def __init__(self):
        BookRepository.__init__(self,"cache")

    def get_by_isbn(self,isbn10,isbn13):
        objs=RepositoryCacheBook.objects.filter(isbn__in=[isbn10,isbn13])
        if not objs: return {}
        obj=objs[0]
        R={}
        R["title"]=obj.title
        R["city"]=obj.city
        R["addresses"]=self.get_addresses(R["city"])
        R["publisher"]=obj.publisher
        R["year"]=obj.year
        authors=[]
        for aut in obj.repositorycacheauthor_set.order_by("pos"):
            t=[x for x in [x.strip() for x in aut.name.strip().split(" ")] if bool(x)]
            autname=" ".join(t)
            # qset=Author.objects.filter_by_name(autname)
            # if qset.count():
            #     authors.append( (aut.role,aut.pos,qset.first()) )
            # else:
            #     authors.append( (aut.role,aut.pos,autname) )
            authors.append( (aut.role,aut.pos,autname) )


        R["authors"]=authors
        return R

class WebRepository(BookRepository):
    def __init__(self,urlbase):
        self.urlbase=urlbase
        BookRepository.__init__(self,urlbase)

    def mk_url(self,isbn10,isbn13): return(self.urlbase+isbn10)

    def get_page_by_isbn(self,isbn10,isbn13):
        url=self.mk_url(isbn10,isbn13)
        req=urllib.request.Request(url=url)
        f=urllib.request.urlopen(req)
        html=f.read()
        f.close()
        return(html)

    def parse_html(self,html): return R

    def get_by_isbn(self,isbn10,isbn13):
        html=self.get_page_by_isbn(isbn10,isbn13)
        R=self.parse_html(html)
        if R:
            self.save_cache(isbn13,R)
            if R["city"]:
                R["addresses"]=self.get_addresses(R["city"])
            else:
                R["addresses"]=None
        return R

class WebRepository13(WebRepository):
    def __init__(self,urlbase):
        WebRepository.__init__(self,urlbase)

    def mk_url(self,isbn10,isbn13): return(self.urlbase+isbn13)
        
class WRWorldCat(WebRepository):
    def __init__(self):
        WebRepository.__init__(self,"http://worldcatlibraries.org/isbn/")

    def parse_html(self,html):
        if type(html)==bytes:
            html=html.decode("utf-8")
        L=re.compile('<span class="Z3988".*</span></div>').findall(html)
        if not L: return({})
        S=L[0]
        S=S.replace("></span></div>","")
        S=S.replace('<span class="Z3988" title="',"")
        if not S: return({})
        tokens={}
        for t in S.split("&"):
            x=t.split("=")
            tokens[x[0]]=x[1]
        R={}

        if "rft.btitle" in tokens:
            R["title"]=url_ripulisci(tokens["rft.btitle"])
        elif "rft.title" in tokens:
            R["title"]=url_ripulisci(tokens["rft.title"])
        else:
            R["title"]=""
        if "rft.place" in tokens:
            R["city"]=url_ripulisci(tokens["rft.place"])
        else:
            R["city"]=""

        if "rft.pub" in tokens:
            R["publisher"]=url_ripulisci(tokens["rft.pub"])
        else:
            R["publisher"]=""

        R["year"]=url_ripulisci(tokens["rft.date"])

        if "rft.aulast" in tokens:
            cognome=tokens["rft.aulast"]
        else:
            cognome=""
        if "rft.aufirst" in tokens:
            nome=tokens["rft.aufirst"]
        else:
            nome=""
            
        if "rft.auinitm" in tokens:
            nome+=" "+tokens["rft.auinitm"]
        cognome=url_ripulisci(cognome)
        nome=url_ripulisci(nome)
        if not cognome: cognome="-"
        if not nome: nome="-"
        
        R["authors"]=self.get_authors([nome.strip()+" "+cognome.strip()])
        print(R)
        return(R)
    
    
#http://copac.ac.uk/search?isn=8878182690&rn=1&format=Tagged+(Short)
class WRCopac(WebRepository):
    def __init__(self):
        urlbase="http://copac.ac.uk/search?rn=1&format=Tagged+(Short)&isn="
        WebRepository.__init__(self,urlbase)

    def parse_html(self,html):
        R={}
        if not html: return(R)
        authors=[]
        righe=html.split("\n")
        for riga in righe:
            if not riga: continue
            t=riga.split("-")
            key=t[0].strip()
            val="-".join(t[1:]).strip()
            if key=="AU":
                val=val.replace(".","")
                t=val.split(",")
                cognome=t[0].strip()
                if len(t)>1:
                    nome=t[1].strip()
                else:
                    nome=""
                authors.append(nome+" "+cognome)
                continue
            if key=="TI":
                t=val.split(":")
                val=":".join(t[:-1]).strip()
                R["title"]=val
                continue
            if key=="PU":
                t=val.split(":")
                city=t[0].strip()
                publisher=t[1].strip()
                R["city"]=city
                R["publisher"]=publisher
                continue
            if key=="PY":
                R["year"]=val.replace(".","").strip()
        if authors:
            R["authors"]=self.get_authors(authors)
        return(R)

class WRAbeBooks(WebRepository):
    def __init__(self):
        WebRepository.__init__(self,"http://www.abebooks.com/products/")

    def parse_html(self,html):
        R={}
        righe=[x.strip() for x in html.split("\n")]
        retitle=re.compile("<h2 id=\"plp-sub-heading\" property=\"name\" class=\"nopadding plptitle\">.*</h2>")
        reauthor_split=re.compile("^.*>(.*)</span.*$")
        reauthor=re.compile(".*<span .*property=\"author\">.*</span>.*</h3>.*")
        republisher=re.compile("Publisher: <strong>.*</strong><br />")
        for riga in righe:
            if retitle.match(riga):
                R["title"]=riga.replace("<h2 id=\"plp-sub-heading\" property=\"name\" class=\"nopadding plptitle\">","").replace("</h2>","")
                continue
            if reauthor.match(riga):
                aut=reauthor_split.split(riga)
                R["authors"]=self.get_authors([aut[1]])
                continue
            if republisher.match(riga):
                R["publisher"]=riga.replace("Publisher: <strong>","").replace("</strong><br />","").replace('<span id="publisher" property="publisher">',"").replace('</span>',"")
                continue
        if not R: return(R)
        R["city"]=""
        R["year"]=""
        return(R)

class WRGulliverTown(WebRepository13):
    def __init__(self):
        WebRepository.__init__(self,"http://www.gullivertown.com/cerca?search_query=")

    def parse_html(self,html):
        R={}
        righe=[x.strip() for x in html.split("\n")]
        retitle=re.compile(".*<strong>Titolo:</strong>.*")
        reauthor=re.compile("<strong>Autore:</strong>")
        reyear=re.compile(".*<strong>Anno:</strong>.*")
        republisher=re.compile("<strong>Editore:</strong>")
        for riga in righe:
            if retitle.match(riga):
                R["title"]=riga.replace("<td width=\"84%\" valign=\"top\"><p><strong>Titolo:</strong> <span class=azr><strong>","").replace("</strong></span><br>","")
            if reauthor.match(riga):
                saut=riga.replace("/","").split("<strong>")
                raut=saut[3]
                if not raut:
                    R["authors"]=[]
                    continue
                R["authors"]=self.get_authors([ raut[0]+" "+raut[1]])
            if republisher.match(riga):
                sced=riga.replace("/","").split("<strong>")
                R["publisher"]=sced[3]
            if reyear.match(riga):
                syear=riga.replace("/","").split("<strong>")
                R["year"]=syear[4].replace("<br>","").strip()
        if not R: return(R)
        R["city"]=""
        return(R)

repositories=[ 
    CacheRepository(),
    WRWorldCat(),
    #WRCopac(),
    #WRGulliverTown(),
    #WRAbeBooks(),
    ]
