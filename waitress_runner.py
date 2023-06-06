import os

cmd = """waitress-serve --host 127.0.0.1 --port 8080 --ident "navak web server" app:app """

os.system(cmd)
