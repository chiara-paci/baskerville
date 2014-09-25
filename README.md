#Baskerville

Application for private libraries

## .gitattributes

Definire questi due:

```
  *bskvctl filter=removeip
  *settings.py filter=cleansettings
```

E creare quattro script:

addip

```
    sed 's/%%SERVERIP%%/<IP>/g'
```

removeip

cleansettings

injectsettings
