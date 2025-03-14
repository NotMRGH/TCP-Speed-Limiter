import asyncio
import time
import contextlib

IN_PORT = int(input("Enter input port: "))
OUT_PORT = int(input("Enter output port: "))
RATE_LIMIT = int(input("Enter speed limit in Mbps: ")) * 1024 * 1024 // 8

clients = {}

async def limit_speed(ip, data):
    if ip not in clients:
        clients[ip] = {'bytes_sent': 0, 'last_reset': time.time()}
    
    now = time.time()
    if now - clients[ip]['last_reset'] >= 1:
        clients[ip]['bytes_sent'] = 0
        clients[ip]['last_reset'] = now
    
    while clients[ip]['bytes_sent'] + len(data) > RATE_LIMIT:
        await asyncio.sleep(0.1)
        now = time.time()
        if now - clients[ip]['last_reset'] >= 1:
            clients[ip]['bytes_sent'] = 0
            clients[ip]['last_reset'] = now
    
    clients[ip]['bytes_sent'] += len(data)
    return data

async def handle_client(reader, writer):
    peer_ip = writer.get_extra_info('peername')[0]
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
                data = await limit_speed(peer_ip, data)
                dst_writer.write(data)
                await dst_writer.drain()
        except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
            pass
        except:
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

async def main():
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(lambda *args: None)
    
    server = await asyncio.start_server(handle_client, "0.0.0.0", IN_PORT)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}, Speed Limit: {RATE_LIMIT * 8 // (1024 * 1024)} Mbps')
    async with server:
        await server.serve_forever()

asyncio.run(main())