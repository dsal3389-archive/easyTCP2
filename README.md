[Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/easyTCP2.svg?logo=python&logoColor=yellow)
![GitHub](https://img.shields.io/github/license/dsal3389/easyTCP2.svg?style=popout)

# easyTCP2

# install 🤩
`pip install easyTCP2`

## what is easyTCP2?
it is the same concept like easyTCP (first version) but more stable, understandable, flexable, readable and more features
(and also because i was too layz to update the last one)
this gives you full controll on your server and make it easy and stable

### inspiration 
I have inspired by [discord.py][discordpy] package because this
help you build bots so easily and they are useful so I wanted an easy way to build
asyncronus server so I have did many tests and took inspiration from the [discord.py][discordpy] code
(no I dont copy code accept this [function][coppiedfunc]) I dont take cradit for things I didnt think/did
all by myself 

[coppiedfunc]: https://github.com/dsal3389/easyTCP2/blob/master/easyTCP2/Core/Protocol.py#L82
[discordpy]: https://github.com/Rapptz/discord.py

## what I get from that package? 🤔
|             | easyTCP  | easyTCP2 |
|:-----------:|----------|----------|
| user levels |    yes   |    yes   |
| groups      |    no    |    yes   |
| events      |    no    |    yes   |
| stable      | not much |    yes   |
| logging     |    no    |    yes   |
| encryption  |    yes   |    soon  |
| logging     |    no    |    yes   |

# when to use 
if you creating a small project that needs a server
or an app that module can be very useful

### examples
example files [here][examples].
I add there examples in any update
if there is a missing version in the example it is because
it is not a big change or even only bug fixing

[examples]: https://github.com/dsal3389/easyTCP2/tree/master/examples

# quick start 🤯
```py
import asyncio
from easyTCP2.Core.Settings import Settings
from easyTCP2.Server import Server

Settings.use_default() # using default


@Server.ready()
async def foo(server):
    print("Server running (ip: %s | port: %d)" %(server.ip, server.port))

@Server.Event(5)
async def oof():
    print("oof event called :)")


async def main(loop):
    server = Server(loop=loop)
    await server

if __name__=="__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete()

    try:
        loop.run_forever()
    finally:
        loop.close()
```

if you like or wanna try, install it! 🏅
it is not hard
