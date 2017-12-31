Files starting with `base`: these are used to mix and match gadgets/functions, for example, `base_210_wk.py` would contain gadgets and functions from webkit 210.

Files starting with `target`: these are final targets that provide Rop, Gadgets, Functions, specific to a combination of version and binary (aka target).

So `target` can be created by mixing multiple `base` classes, for example, a `target_210_webauth.py` would have a gadget class like this:

```
class Gadgets(Gadgets210Wk, Gadgets210Webauth):
    pass
```

so it has gadgets from both 210 webkit and 210 webauth

And a `target_210_shopn` would have a:

```
class Gadgets(Gadgets210Wk, Gadgets210Shopn):
    pass
```

Every target also provides a `Functions` class and a `Rop` class (and maybe `DataPtrs`?)

Most important part of every target is `Rop` class (but it also can be derived yadda yadda). It should provide the following functions for everything to work:

* write64
* store_ret
* load_ret
* dump_regs

and two callfuncs:
* call_v8 - for normal calls via functionhelper - note - there's also x8 support might be required
* call_rv4 - for network calls in rpc
