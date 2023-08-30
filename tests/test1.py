import aio


async def counter(msg):
    while True:
        print(msg)
        await aio.sleep(1)


async def main():
    aio.to_plan(counter("Hello"))
    await counter("world")


if __name__ == '__main__':
    aio.run(main())
