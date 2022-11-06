import asyncio
import logging

from asyncua import Server, ua
from asyncua.common.methods import uamethod


@uamethod
def func(parent, value):
    return value * 2


async def main():
    _logger = logging.getLogger("asyncua")
    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    server.set_server_name("opcua-chat-server")

    # setup our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    myobj = await server.nodes.objects.add_object(idx, "MyChatObjects")
    myvar_input = await myobj.add_variable(idx, "MyChatVar_Input", "")
    myvar_display = await myobj.add_variable(idx, "MyChatVar_Display", "Starting Chat")
    # Set MyVariable to be writable by clients
    await myvar_input.set_writable()
    await server.nodes.objects.add_method(
        ua.NodeId("ServerMethod", idx),
        ua.QualifiedName("ServerMethod", idx),
        func,
        [ua.VariantType.Int64],
        [ua.VariantType.Int64],
    )
    _logger.info("Starting server!")
    print("running..")
    async with server:
        while True:
            
            # short pause to give the server some breathingroom
            await asyncio.sleep(0.1)

            # if there is something in the input variable, copy to display var and set input to empty string
            if await myvar_input.get_value() != '':
                new_input = await myvar_input.get_value()
                await myvar_display.write_value(new_input)
                await myvar_input.write_value('')
                print(f"## {new_input}")



if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.CRITICAL)
    asyncio.run(main(), debug=True)
