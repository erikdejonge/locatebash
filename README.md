# locate
Bash locate combines mdfind and locate

Output is sorted 
Optional show the folders

##usage
``` bash
Call mdfind to do a quick search

Usage:
  locate.py [options] <query>...

Options:
  -h --help       Show this screen.
  -f --folders    Show folders seperately
```

## example output
```bash
$ locate pycrypto.py -f

[pycrypto.py](1):
/Users/rabshakeh/workspace/cryptobox/cryptobox_app/pyinstaller/tests/libraries/test_pycrypto.py
/usr/local/lib/python3.4/site-packages/jwt/contrib/algorithms/pycrypto.py

[pycrypto.py] Folders:
/Users/rabshakeh/workspace/cryptobox/cryptobox_app/pyinstaller/tests/libraries
/usr/local/lib/python3.4/site-packages/jwt/contrib/algorithms

```
