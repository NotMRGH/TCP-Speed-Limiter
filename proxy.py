import asyncio
import time
import contextlib

IN_PORT = int(input("Enter input port: "))
OUT_PORT = int(input("Enter output port: "))
RATE_LIMIT = int(input("Enter speed limit in Mbps: ")) * 1024 * 1024 // 8

clients = {}

class ClientSession:
    def __init__(self, ip):
        self.ip = ip
        self.tokens = RATE_LIMIT
        self.last_check = time.time()
        self.connections = 0

    def update_tokens(self):
        now = time.time()
        elapsed = now - self.last_check
        self.last_check = now
        self.tokens = min(RATE_LIMIT, self.tokens + elapsed * RATE_LIMIT)

    async def limit_speed(self, data):
        self.update_tokens()

        while len(data) > self.tokens:
            await asyncio.sleep(0.01)
            self.update_tokens()

        self.tokens -= len(data)
        return data

async def handle_client(reader, writer):
    peer_ip = writer.get_extra_info('peername')[0]

    if peer_ip not in clients:
        clients[peer_ip] = ClientSession(peer_ip)

    session = clients[peer_ip]
    session.connections += 1

    try:
        remote_reader, remote_writer = await asyncio.open_connection('127.0.0.1', OUT_PORT)
    except:
        writer.close()
        with contextlib.suppress(ConnectionResetError, BrokenPipeError):
            await writer.wait_closed()
        return

    async def forward(src_reader, dst_writer):
        try:
            while True:
                data = await src_reader.read(4096)
                if not data:
                    break
                data = await session.limit_speed(data)
                dst_writer.write(data)
                await dst_writer.drain()
        except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
            pass
        finally:
            dst_writer.close()
            with contextlib.suppress(ConnectionResetError, BrokenPipeError):
                await dst_writer.wait_closed()

    task1 = asyncio.create_task(forward(reader, remote_writer))
    task2 = asyncio.create_task(forward(remote_reader, writer))

    try:
        await asyncio.gather(task1, task2)
    except:
        pass
    finally:
        writer.close()
        with contextlib.suppress(ConnectionResetError, BrokenPipeError):
            await writer.wait_closed()
        
        session.connections -= 1
        if session.connections == 0:
            del clients[peer_ip]

async def main():
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(lambda *args: None)

    server = await asyncio.start_server(handle_client, "0.0.0.0", IN_PORT)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}, Speed Limit: {RATE_LIMIT * 8 // (1024 * 1024)} Mbps')

    async with server:
        await server.serve_forever()

asyncio.run(main())
