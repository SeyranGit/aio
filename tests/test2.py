import aio
from socket import AF_INET, SOCK_STREAM


async def handler(sock: aio.Socket):
    while True:
        data: bytes = await sock.recv()
        print(data.decode())
        await sock.send("Hello".encode())

async def server():
    sock = aio.socket(AF_INET, SOCK_STREAM)
    sock.bind(('localhost', 8000))
    sock.listen()

    while True:
        client, addres = await sock.accept()
        aio.to_plan(client)


if __name__ == '__main__':
    aio.run(server())
