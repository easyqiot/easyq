import asyncio


async def server_handler(reader, writer):
    while True:
        try:
            chunk = await reader.readuntil(b'\n')
            writer.write(chunk)
        except asyncio.IncompleteReadError:
            writer.close()
            break
        except asyncio.LimitOverrunError:
            # If the data cannot be read because of over limit, a LimitOverrunError exception will
            # be raised, and the data will be left in the internal buffer, so it can be read
            # again.
            pass

