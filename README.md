# rop-rpc

A sophisticated and enterprise-ready method to run arbitrary complex ROP payloads on Nintendo Switch.

## Installation

Copy `config.py.sample` to `config.py` and edit it to select your target.

## Running

Run `./server.py YOUR_IP_FROM_SWITCH`. This script will start the web server and socket (rpc) server.

`YOUR_IP_FROM_SWITCH` is what IP the Switch can use to access your PC over the network.

- Web server is used to serve the JS exploit and stage1 rop.js, by default it runs on port 6969 so you need a nginx or similar to forward conntest.nintendowifi.net to it (but depends on the target you use), I use this config:

```
server {
    listen YOUR_IP_FROM_SWITCH:80;
    server_name conntest.nintendowifi.net;
    root /var/www/conntest.nintendowifi.net;
    location / {
        proxy_pass       http://YOUR_IP_FROM_SWITCH:6969;
        proxy_set_header Host      $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

```

- Socket server is the one used for actual RPC, it runs on port 6970 by default and you don't need to configure anything for it to work

Once that's done, navigate from Switch to the usual web page (captive portal or puyo-puyo, depending on your target) and run the exploit.

The server should tell you to run `./client.py` in a terminal once everything is ready.

`client.py` uses localhost sockets to communicate with `server.py` so you can edit and restart `client.py` without disconnecting from Switch.

## Writing commands

In `client.py`, every time you do `self.execute()` what happens is it "sends" a payload to Switch and retrieves the result buffer.

The payload is 0x8000 bytes of rop script and the result is 0x8000 bytes of data.

The data you get is from `data_base`, so basically if you do in your rop script:

```
rop.write64(0xDEADBEEF, data_base)
data = self.execute(rop)
```

`data` will start like `"\xEF\xBE\xAD\xDE"`.

Note that the buffer you get is fixed size, also make sure NOT to use last 0x1000 bytes of data; basically don't write to `data_base + 0x7000` and expect to read back what you wrote!

## Function helper

Function helper is a wrapper over `client.execute()`, it runs a single function and gives you return value (and optionally all registers).

This means you can write payloads like this:

```
def some_cmd(self, args):
    handle = self.fh.fopen(args[0], "rb")
    for x in range(123):
        self.fh.fread(...)
    self.fh.fclose(handle)
```

Every function handler invocation invokes a single ropchain roundtrip, so it might be slow if you are executing a lot of stuff, but is fast enough for most.

In addition, after function helper is invoked, it sets `self.mem` to the `data` returned so you can write e.g. a memory dumper like this:

```
def examine_mem(self, args):
    addr, length = int(args[0], 0), int(args[1], 0)
    self.fh.memcpy(data_base, addr, length)
    data = self.mem[0:length]
    print hexdump(data, start=addr)
```

Don't forget about size limitation: don't expect more than 0x7000 bytes to be available (if you need more, tough titties).

## Interactive shell

`client.py` provides a python-like interactive shell and there's a lot of commands available (see the source) for you to play with!

## Credits

Originally created by @xyzz, a LOT of improvements by @plutooo and @yellows8.

## License

MIT license, see COPYING.
