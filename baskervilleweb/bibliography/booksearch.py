from bibliography.models import PublisherIsbn,Book,RepositoryFailedIsbn
from bibliography.webrepositories import repositories

class TemporaryAuthor(object):
    def __init__(self):
        pass

class TemporaryPublisher(object):
    def __init__(self,isbn_ced):
        self.isbn_ced=isbn_ced.upper()
        self.db_object=None
        self.name=""
        self.addresses=[]
        self.indb=False
        self.addresses_indb=False

    def set_db(self,db_object):
        self.db_object=db_object
        self.name=db_object.name
        self.addresses=db_object.addresses.all()
        self.addresses_indb=True
        self.indb=True

    def set_no_db(self,book):
        if not book.publisher: return
        self.name=book.publisher[0]
        if book.publisher[2]:
            self.addresses=book.publisher[2]
            self.addresses_indb=True
        else:
            self.addresses.append(book.publisher[1])

class TemporaryBook(object):
    def __init__(self,isbn_ced,isbn_book):
        self.isbn_ced=isbn_ced.upper()
        self.isbn_book=isbn_book.upper()
        self.authors=[]
        self.publisher=None
        self.title=""
        self.year=""
        self.indb=False

    def __str__(self): return self.isbn_ced+"-"+self.isbn_book
    def __repr__(self): return self.isbn_ced+"-"+self.isbn_book

    def crc10(self):
        if not str(self.isbn_book).isdigit(): return('Y')
        if not str(self.isbn_ced).isdigit(): return('Y')
        isbn=str(self.isbn_ced)+str(self.isbn_book)
        pesi=[10,9,8,7,6,5,4,3,2]
        cod_lista=list(map(int,list(isbn)))
        if len(cod_lista)<9:
            L=len(cod_lista)
            cod_lista+=[0 for x in range(L,9)]
        crc=11-(sum(map(lambda x,y: x*y,cod_lista,pesi))%11)
        if (crc==10): return('X')
        if (crc==11): return(0)
        return(crc)

    def crc13(self):
        if not str(self.isbn_book).isdigit(): return('Y')
        if not str(self.isbn_ced).isdigit(): return('Y')
        isbn=str(self.isbn_ced)+str(self.isbn_book)
        pesi=[1,3,1,3,1,3,1,3,1,3,1,3]
        cod_lista=[9,7,8]+list(map(int,list(isbn)))
        if len(cod_lista)<12:
            L=len(cod_lista)
            cod_lista+=[0 for x in range(L,12)]
        crc=10-(sum(map(lambda x,y: x*y,cod_lista,pesi))%10)
        if (crc==10): return(0)
        return(crc)

    def isbn_10(self):
        isbn_crc10=self.crc10()
        isbn10=self.isbn_ced+"-"+self.isbn_book+"-"+str(isbn_crc10)
        return isbn10

    def look_for(self,publisher_dict):
        objs=Book.objects.filter(isbn_ced__iexact=self.isbn_ced,isbn_book__iexact=self.isbn_book)
        if len(objs)>0:
            obj=objs[0]
            self.authors=obj.bookauthorrelation_set.all()
            self.title=obj.title
            self.year=obj.year
            self.publisher=obj.publisher
            self.indb=True
            #print obj.isbn_cache10,obj.isbn_cache13,"db"
            return

        if self.isbn_ced in publisher_dict:
            self.publisher=publisher_dict[self.isbn_ced][0]

        isbn_crc10=self.crc10()
        isbn_crc13=self.crc13()

        isbn10=self.isbn_ced+self.isbn_book+str(isbn_crc10)
        isbn13="978"+self.isbn_ced+self.isbn_book+str(isbn_crc13)

        for rep in repositories:
            data=rep.get_by_isbn(isbn10,isbn13)
            if data:
                #print isbn10,isbn13,rep.name
                if "title" in data:
                    self.title=data["title"]
                if "year" in data:
                    self.year=data["year"]
                if "authors" in data:
                    self.authors=data["authors"]
                if not self.publisher:
                    self.publisher=(data["publisher"],data["city"],data["addresses"])
                return
        RepositoryFailedIsbn.objects.get_or_create(isbn10=isbn10,isbn13=isbn13)

def look_for(isbn_list):
    separated=[]
    isbn_ced_list=[]
    unseparated=[]
    for isbn in isbn_list:
        isbn=isbn.upper()
        t=isbn.replace("-","")
        if len(t) in [12,13]:
            isbn=isbn[3:]
        if len(t) in [10,13]:
            isbn=isbn[:-1]
        isbn=isbn.strip("-")
        t=isbn.split("-")
        if len(t)==1:
            unseparated.append(isbn)
            continue
        isbn_book=t[-1]
        isbn_ced="".join(t[:-1])
        
        separated.append( (isbn_ced,isbn_book) )
        isbn_ced_list.append(isbn_ced)


    publisher_isbn_list=PublisherIsbn.objects.filter(isbn__in=isbn_ced_list)
    publisher_dict={}
    
    for isbn in publisher_isbn_list:
        publisher_dict[isbn.isbn.upper()]=list(isbn.publisher_set.all())

        
    book_list=[]
    for isbn_ced,isbn_book in separated:
        tmp_book=TemporaryBook(isbn_ced,isbn_book)
        book_list.append(tmp_book)

    isbn_ced_list=[]
    for isbn in unseparated:
        for n in range(1,9):
            isbn_ced_list.append(isbn[:n])
    publisher_isbn_list=PublisherIsbn.objects.filter(isbn__in=isbn_ced_list)
    for isbn in publisher_isbn_list:
        publisher_dict[isbn.isbn.upper()]=list(isbn.publisher_set.all())

    def find_ce(book_isbn,pub_dict):
        for n in range(1,9):
            if book_isbn[:n] in pub_dict:
                print(book_isbn,book_isbn[:n],"yes")
                isbn_ced=book_isbn[:n]
                isbn_book=book_isbn[n:]
                tmp_book=TemporaryBook(isbn_ced,isbn_book)
                return tmp_book
            print(book_isbn,book_isbn[:n],"no")
        return None

    for isbn in unseparated[:]:
        tmp_book=find_ce(isbn,publisher_dict)
        if not tmp_book: continue
        book_list.append(tmp_book)
        unseparated.remove(isbn)
        # for n in range(1,9):
        #     if publisher_dict.has_key(isbn[:n]):
        #         print isbn,isbn[:n],"yes"
        #         isbn_ced=isbn[:n]
        #         isbn_book=isbn[n:]
        #         tmp_book=TemporaryBook(isbn_ced,isbn_book)
        #         break
        #     print isbn[:n],"no"
            
    for uisbn in unseparated:
        ### solo per fargli calcolare crc10 e crc13
        tbook=TemporaryBook(uisbn[:3],uisbn[3:])
        uisbn10=uisbn+str(tbook.crc10())
        uisbn13="978"+uisbn+str(tbook.crc13())
        RepositoryFailedIsbn.objects.get_or_create(isbn10=uisbn10,isbn13=uisbn13)

        
    publisher_list=[]
    n=0
    for book in book_list:
        book.look_for(publisher_dict)
        tpub=TemporaryPublisher(book.isbn_ced)
        publisher_list.append(tpub)
        if tpub.isbn_ced.upper() in publisher_dict:
            tpub.set_db(publisher_dict[tpub.isbn_ced.upper()][0])
            continue
        tpub.set_no_db(book)

    return {
        'unseparable': unseparated,
        'isbn_list':isbn_list,
        'publisher_list':publisher_list,
        'book_list': book_list
        }
