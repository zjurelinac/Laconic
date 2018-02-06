from . import *

app = Laconic()

def f(x=1): return 'Hello, x=%d' % x

app.add_route('/f', f)
