# opcua_concept_chat_server

This project is about building a basic concept of a chat-server and client. The server will run the Freeopcua python library 'opcua-asyncio'. On the clientside there will be a WinCC SCADA project connected to the server and serving as the interface for the user.

### Software used

This project uses:

- Serverside: [opcua-asyncio](https://github.com/FreeOpcUa/opcua-asyncio)
- Clientside: WinCC SCADA version 7.4 + SP1 + Upd11

The server or client can be exchanged for any other opcua compatible software.

### The Plan

Setting up the server to serve two variables. The first variable (**MyChatVar_Input**) is used as the users input, it is writeable and will be set to empy string once the server read it's content. The second variable (**MyChatVar_Display**) will contain the value of the first variable after it has been read and set to empy string. The second variable is not writeable by the users.

The client will offer an inputfield for a string, which will be connected with the **MyChatVar_Input** of the server. Before inserting the text in the server's input variable the client will add the username to the beginning of the string. The server's **MyChatVar_Display** need to be archived with 'Log Tags' in acyclic mode. This way it can be shown as a 'WinCC OnlineTable' and will behave like a chat history.


### Preparing Server


Install python3
`sudo apt install python3 python3-venv python3-pip`

Open new virtual python environment to isolate the libraries from your systems library
```
python3 -m venv new_opcua_env
source new_opcua_env/bin/activate
```

Install opcua-asyncio
`sudo pip install asyncua`

The server script consist of a modified version of the ['minimal-server'-example](https://github.com/FreeOpcUa/opcua-asyncio/blob/master/examples/server-minimal.py) provided by the opcua-asyncio project.
Copy and paste in a new file _opcua-server.py_

```
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
```


You can modify the server name as you like.

You might need to modify the ip adress from 0.0.0.0 to the actual ip of your servers network interface you intend to use.

The log-level can be set to logging.DEBUG if you want more information.

Start the Server
`python3 opcua-server.py`


### Preparing Client

Setup a new WinCC SCADA project.

In the variablemanagement insert a new driver "OPC UA WinCC Channel".

Create a new connection in that channel and set it up to connect to your server ip
`opc.tcp://<yourserverip>:4840`
    
Right mouse click on the connection and 'search server', to get to know what the server is offering.

Under 'MyChatObjects' there should now be two variables, tick the 'access' box on the left for both of them.

Add two additional intern variable (e.g. _Var_Chat_Intern_Input_ and _Var_Chat_Name_) in the variablemanager. It will be used to combine the username with the written input text.

Create a new screen in the graphicsmanager.

To that screen you add one IO-Field connect to the _Var_Chat_Name_ and one IO-Field connected to the _Var_Chat_Intern_Input_.

This visualbasic script will be added to the IO-Field of the _Var_Chat_Intern_Input_, on the 'Inputvalue got changed'-event. It's purpose is to add the username in front of the chat text.

```
Dim chat_server_input
Dim chat_namefield
Dim chat_intern_input


Set chat_server_input = HMIRuntime.Tags("MyChatVar_Input")
Set chat_namefield = HMIRuntime.Tags("Var_Chat_Name")
Set chat_intern_input = HMIRuntime.Tags("Var_Chat_Intern_Input")

' add name in front of message and put it in the opc-ua server variable
chat_server_input.Value = chat_namefield.Read & ": " & chat_intern_input.Read
chat_server_input.Write

' delete content of the input field
chat_intern_input.Value = ""
chat_intern_input.Write
```

Go to 'Tag Logging' and add a new processarchiv for the _MyChatVar_Display_ of the OPC UA server variable. Set it to acyclic mode, this way it only get updated if the values changes. The acyclic mode introduce heavy load on the server but in this scenario it is ok.

Insert a 'WinCC OnlineTable' on your screen and add the logged archive variable _MyChatVar_Display_ to it.

After starting the runtime and confirming that the connection to the server is established, you can add a name in the appropriate field and your message in the other input field. Voilà
