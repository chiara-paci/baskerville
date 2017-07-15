from bibliography.models import PublisherIsbn,Book,RepositoryFailedIsbn,Publisher,Author
from bibliography.webrepositories import repositories

class TemporaryAuthor(object):
    def __init__(self):
        pass

class TemporaryPublisher(object):
    def __init__(self,book):
        self.isbn_ced=book.isbn_ced.upper()
        self.name=""
        self.addresses=[]
        self.addresses_indb=False
        self.set_no_db(book)

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
        # objs=Book.objects.filter(isbn_ced__iexact=self.isbn_ced,isbn_book__iexact=self.isbn_book)
        # if len(objs)>0:
        #     obj=objs[0]
        #     self.authors=obj.bookauthorrelation_set.all()
        #     self.title=obj.title
        #     self.year=obj.year
        #     self.publisher=obj.publisher
        #     self.indb=True
        #     self.db_object=obj
        #     #print obj.isbn_cache10,obj.isbn_cache13,"db"
        #     return

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

    def set_old_authors(self,old_author_dict):
        if not self.authors: return
        new_authors=[]
        for role,ind,name in self.authors:
            if name in old_author_dict:
                new_authors.append( (role,ind,old_author_dict[name]) )
            else:
                new_authors.append( (role,ind,name) )
        self.authors=new_authors

    def suspended(self):
        if not isinstance(self.publisher,Publisher): return True
        for role,ind,aut in self.authors:
            if not isinstance(aut,Author): return True
        return False

# def look_for(isbn_list):
#     separated=[]
#     isbn_ced_list=[]
#     unseparated=[]

#     for isbn in isbn_list:
#         isbn=isbn.upper()
#         t=isbn.replace("-","")
#         if len(t) in [12,13]:
#             isbn=isbn[3:]
#         if len(t) in [10,13]:
#             isbn=isbn[:-1]
#         isbn=isbn.strip("-")
#         t=isbn.split("-")
#         if len(t)==1:
#             unseparated.append(isbn)
#             continue
#         isbn_book=t[-1]
#         isbn_ced="".join(t[:-1])
        
#         separated.append( (isbn_ced,isbn_book) )
#         isbn_ced_list.append(isbn_ced)

#     publisher_isbn_list=PublisherIsbn.objects.filter(isbn__in=isbn_ced_list)
#     publisher_dict={}
    
#     for isbn in publisher_isbn_list:
#         publisher_dict[isbn.isbn.upper()]=list(isbn.publisher_set.all())
        
#     book_list=[]
#     for isbn_ced,isbn_book in separated:
#         tmp_book=TemporaryBook(isbn_ced,isbn_book)
#         book_list.append(tmp_book)

#     isbn_ced_list=[]
#     for isbn in unseparated:
#         for n in range(1,9):
#             isbn_ced_list.append(isbn[:n])
#     publisher_isbn_list=PublisherIsbn.objects.filter(isbn__in=isbn_ced_list)
#     for isbn in publisher_isbn_list:
#         publisher_dict[isbn.isbn.upper()]=list(isbn.publisher_set.all())

#     def find_ce(book_isbn,pub_dict):
#         for n in range(1,9):
#             if book_isbn[:n] in pub_dict:
#                 print(book_isbn,book_isbn[:n],"yes")
#                 isbn_ced=book_isbn[:n]
#                 isbn_book=book_isbn[n:]
#                 tmp_book=TemporaryBook(isbn_ced,isbn_book)
#                 return tmp_book
#             print(book_isbn,book_isbn[:n],"no")
#         return None

#     for isbn in unseparated[:]:
#         tmp_book=find_ce(isbn,publisher_dict)
#         if not tmp_book: continue
#         book_list.append(tmp_book)
#         unseparated.remove(isbn)
#         # for n in range(1,9):
#         #     if publisher_dict.has_key(isbn[:n]):
#         #         print isbn,isbn[:n],"yes"
#         #         isbn_ced=isbn[:n]
#         #         isbn_book=isbn[n:]
#         #         tmp_book=TemporaryBook(isbn_ced,isbn_book)
#         #         break
#         #     print isbn[:n],"no"
            
#     for uisbn in unseparated:
#         ### solo per fargli calcolare crc10 e crc13
#         tbook=TemporaryBook(uisbn[:3],uisbn[3:])
#         uisbn10=uisbn+str(tbook.crc10())
#         uisbn13="978"+uisbn+str(tbook.crc13())
#         RepositoryFailedIsbn.objects.get_or_create(isbn10=uisbn10,isbn13=uisbn13)
        
#     publisher_list=[]
#     n=0
#     for book in book_list:
#         book.look_for(publisher_dict)
#         tpub=TemporaryPublisher(book.isbn_ced)
#         publisher_list.append(tpub)
#         if tpub.isbn_ced.upper() in publisher_dict:
#             tpub.set_db(publisher_dict[tpub.isbn_ced.upper()][0])
#             continue
#         tpub.set_no_db(book)


#     return {
#         'unseparable': unseparated,
#         'isbn_list':isbn_list,
#         'publisher_list': publisher_list,
#         'book_list': book_list
#         }

# def split_isbn(unseparated):
#     if not unseparated: return [],[]
#     isbn_list=[]
#     for isbn in unseparated:
#         for n in range(1,9):
#             isbn_list.append(isbn[:n])
#     L=[ v.isbn for v in PublisherIsbn.objects.filter(isbn__in=isbn_list) ]
#     if not L:
#         return [],unseparated
#     uns=[]
#     sep=[]
#     for isbn in unseparated:
#         trovato=False
#         for db_isbn in L:
#             if isbn.startswith(db_isbn):
#                 trovato=True
#                 isbn_book=isbn[len(db_isbn):]
#                 sep.append( (db_isbn,isbn_book) )
#                 break
#         if not trovato:
#             uns.append(isbn)
#     return sep,uns

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

    sep,unseparated=PublisherIsbn.objects.split_isbn(unseparated)
    separated+=sep
    
    for uisbn in unseparated:
        ### solo per fargli calcolare crc10 e crc13
        tbook=TemporaryBook(uisbn[:3],uisbn[3:])
        uisbn10=uisbn+str(tbook.crc10())
        uisbn13="978"+uisbn+str(tbook.crc13())
        RepositoryFailedIsbn.objects.get_or_create(isbn10=uisbn10,isbn13=uisbn13)

    old_books,new_book_isbn_list=Book.objects.look_for(separated)

    isbn_ced_list=[ x[0] for x in new_book_isbn_list ]

    old_publishers,new_publisher_isbn_list=Publisher.objects.look_for(isbn_ced_list)

    #publisher_isbn_list=PublisherIsbn.objects.filter(isbn__in=isbn_ced_list)

    publisher_dict={}
    for pub in old_publishers:
        for pisbn in pub.isbn_list:
            key=pisbn.upper()
            if key not in publisher_dict:
                publisher_dict[key]=[]
            publisher_dict[key].append(pub)
        
    book_list=[]
    author_list=[]
    publisher_list={}
    address_list=[]

    for isbn_ced,isbn_book in new_book_isbn_list:
        book=TemporaryBook(isbn_ced,isbn_book)
        book_list.append(book)
        book.look_for(publisher_dict)
        author_list+=book.authors
        if isinstance(book.publisher,Publisher): continue
        if book.isbn_ced in publisher_list: continue
        tpub=TemporaryPublisher(book)
        publisher_list[book.isbn_ced]=tpub
        address_list.append(tpub.addresses)

    author_list=[ a[2] for a in author_list ]
    old_author_dict,new_author_list=Author.objects.look_for(author_list)

    for book in book_list:
        book.set_old_authors(old_author_dict)

    print(address_list)

    publisher_list=publisher_list.values()
    old_author_list=old_author_dict.values()

    return {
        'unseparable': unseparated,
        'isbn_list':isbn_list,
        'publisher_list': publisher_list,
        'book_list': book_list,
        'author_list': new_author_list,
        'old_book_list': old_books,
        'old_publisher_list': old_publishers,
        'old_author_list': old_author_list
        }
