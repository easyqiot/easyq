# easyq

A simple and plain text tcp message broker 

[![PyPI](http://img.shields.io/pypi/v/easyq.svg)](https://pypi.python.org/pypi/easyq)
[![Build Status](https://travis-ci.org/pylover/easyq.svg?branch=master)](https://travis-ci.org/pylover/easyq)
[![Coverage Status](https://coveralls.io/repos/github/pylover/easyq/badge.svg?branch=master)](https://coveralls.io/github/pylover/easyq?branch=master)


## Instalation

```bash
pip install easyq
```

Or

```bash
pip install git+https://github.com/pylover/easyq
```


### Development

```bash
clone git@github.com:pylover/easyq.git
cd easyq
pip install -r requirements-dev.txt
pip install -e .

```

### CLI auto completion

```bash
easyq autocompletion install [-s]
```

Uninstall

```bash
easyq autocompletion uninstall [-s]
```

If you are inside a virtualenv it will add the bash completion in `$VIRTUAL_ENV/bin/postactivate`.
if not, the `$HOME/.bashrc` will be used. 

The `-s` flag tells the installer to add the `# PYTHON_ARGCOMPLETE_OK` after the shebang line of
`$(which easyq)`.

For more info see: [argcomplete](https://github.com/kislyuk/argcomplete)

## Starting the server

```bash
easyq server start [-h] [-b [HOST:]PORT] [-C DIRECTORY] [-c FILE] [-o key1.key2=value]
```

example

```bash
easyq server start
easyq server start -o dispatchers=3
easyq server start -o logging.level=warning
```

More:

```bash

usage: easyq server start [-h] [-b {HOST:}PORT] [-C DIRECTORY] [-c FILE]
                          [-o key1.key2=value]

optional arguments:
  -h, --help            show this help message and exit
  -b {HOST:}PORT, --bind {HOST:}PORT
                        Bind Address. if ommited the value from the config
                        file will be usedThe default config value is:
                        localhost:1085
  -C DIRECTORY, --directory DIRECTORY
                        Change to this path before starting the server
  -c FILE, --config-file FILE
  -o key1.key2=value, --option key1.key2=value
                        Configuration value to override. this option could be
                        passed multiple times.
```

### Server Configuration

The builtin configuration is same as the bellow:

```yaml
bind: localhost:1085 

authentication:
  method: trust

logging:
  level: debug

queues:
  default:
    maxsize: 100

dispatchers: 1
dispatcher:
  messages_per_queue: 5
  intervals: .3
```

But can oveeride it by `-o/--option key.subkey=value` or specifying a `yaml` config file with 
the `-c/--config-file myfile.yaml`.


## Client

### Console

Feel free to use any regular tcp text client such as `telnet` and or `nc`.

Start a server in another terminal to handle our connections.

```bash
easyq server start
```

#### Netcat

```bash
$ nc localhost 1085
LOGIN username;
HI username;
PULL FROM q;
PUSH Hello INTO q;
MESSAGE Hello FROM q;
IGNORE q;
^C
```

#### Telnet

```bash
$ telnet localhost 1085
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
LOGIN username;
HI username;
PULL FROM q;
PUSH Hello INTO q;
MESSAGE Hello FROM q;
IGNORE q;
^]
telnet> close
Connection closed.
```

The server's log should be something like this:

```bash

2018-05-22 23:50:27 DEBUG PROTO Data received: b'LOGIN username;'
2018-05-22 23:50:27 INFO PROTO Authenticating: ('127.0.0.1', 33826)
2018-05-22 23:50:27 INFO PROTO Login success: username from ('127.0.0.1', 33826)
2018-05-22 23:50:41 DEBUG PROTO Data received: b'PULL FROM q;'
2018-05-22 23:50:41 INFO QM Queue q just created.
2018-05-22 23:50:41 INFO QM Queue q was subscribed by username
2018-05-22 23:50:57 DEBUG WORKER 0 Cycle: 600
2018-05-22 23:51:00 DEBUG PROTO Data received: b'PUSH Hello INTO q;'
2018-05-22 23:51:00 DEBUG WORKER 0 Dispatching b'Hello'
2018-05-22 23:51:00 DEBUG QM Dispatching message b'Hello' from queue q to username
2018-05-22 23:51:09 DEBUG PROTO Data received: b'IGNORE q;'
2018-05-22 23:51:09 INFO QM Queue q was ignored by username
2018-05-22 23:51:17 DEBUG PROTO EOF Received: ('127.0.0.1', 33826)
2018-05-22 23:51:17 INFO PROTO Connection lost: ('127.0.0.1', 33826)
```

### Python AsyncIO API


```python
import asyncio

from easyq.client import connect


async def message_received(queue, message):
    print(f'Messsage received from {queue.decode()}: {message.decode()}')


async def main():
    client = await connect('Username', 'localhost', 1085)
    await client.pull(b'q', message_received)
    await client.push(b'q', b'Hello')
    await asyncio.sleep(2)
    await client.ignore(b'q', message_received)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
```

