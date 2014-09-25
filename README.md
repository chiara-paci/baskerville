#Baskerville

Application for private libraries

## .gitattributes

Definire questi due:

```
  *bskvctl filter=removeip
  *settings.py filter=cleansettings
```

E creare quattro script:

localbin/addip

```
    sed 's/%%SERVERIP%%/<IP>/g'
```

localbin/removeip

```
    sed 's/<IP>/%%SERVERIP%%/g'
```

localbin/cleansettings

```
    sed "s/SECRET_KEY = .*/SECRET_KEY = '%%SECRET_KEY%%'/g" | \
        sed "s/'PASSWORD': .*/'PASSWORD': '%%DB_PASSWORD%%'/g"
```

localbin/injectsettings

```
    sed "s/SECRET_KEY = '%%SECRET_KEY%%'/SECRET_KEY = '<SECRET_KEY>'/g" | \
        sed "s/'PASSWORD': '%%DB_PASSWORD%%'/'PASSWORD': '<DB_PASSWORD>'/g"
```

Sostituendo a <DB_PASSWORD>, <SECRET_KEY> e <IP> i valori opportuni
(per <SECRET_KEY> generare il progetto e copiare dal settings.py di
default).

Infine:
```
$ git config filter.cleansettings.smudge /home/chiara/baskerville/localbin/injectsettings
$ git config filter.cleansettings.clean /home/chiara/baskerville/localbin/cleansettings
$ git config filter.removeip.clean /home/chiara/baskerville/localbin/removeip
$ git config filter.removeip.smudge /home/chiara/baskerville/localbin/addip
```
