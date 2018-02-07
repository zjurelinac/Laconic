import os

from laconic import util

BASE_PATH = os.path.dirname(__file__)


def test_config_loading():
    class O: pass

    obj = O()
    setattr(obj, 'HELLO', 123)
    setattr(obj, 'hello', 456)

    cfg = util.Config()
    cfg.from_object(obj)

    assert('HELLO' in cfg)
    assert('hello' not in cfg)
    assert(cfg['HELLO'] == 123)

    cfg = util.Config(BASE_PATH)
    cfg.from_pyfile('_cfgutil.py')

    assert('STUFF' in cfg)
    assert('other_stuff' not in cfg)
    assert(cfg['STUFF'] == 'abcdef')


def test_namespace():
    ns1, ns2 = util.Namespace(a=1), util.Namespace(b=2)
    assert(ns1 != ns2)
    ns1.b = 2
    ns2.a = 1
    assert(ns1 == ns2)


def test_attrscope():
    as1 = util.AttributeScope(a=1, b=1)
    as2 = util.AttributeScope(as1, a=2, c=2, d=2)
    as3 = util.AttributeScope(as2, a=3, d=3, e=3, f=3)

    assert(as1['a'] == 1)
    assert(as2['a'] == 2)
    assert(as2['c'] == 2)
    assert(as3['a'] == 3)
    assert(as3['b'] == 1)
    assert(as3['c'] == 2)
    assert(as3['d'] == 3)
    assert(as3['e'] == 3)

    assert(len(as1) == 2)
    assert(len(as2) == 4)
    assert(len(as3) == 6)

    for k, v in as3.items():
        assert(as3[k] == v)