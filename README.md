# FastAPI Distributed Websocket

A library to implement websocket for distibuted systems based on FastAPI.

**N.B.: This library is still under development and is not ready for production yet.**


## Problems of scaling websocket among multiple servers in production

Websocket is a relatively new protocol for real time communication over HTTP.
It establishes a druable, stateful, full-duplex connection between clients and the server.
It can be used to implement chats, real time notifications, broadcasting and
pub/sub models.

### Connections from clients

HTTP request/response mechanism fits very well to scale among multiple server
instances in production. Any time a client makes a request, it can connect
to any server instance and it's going to receive the same response. After
the response has been returned to the client, it went disconnected and it can
make another request without the need to hit the same instace as before.
This thanks to the stateless nature of HTTP.

However, Websocket establishes a stateful connection between the client and the
server and, if some error occurs and the connection went lost, we have to
ensure that clients are going to hit the same server instance they were connected
before, since that instance was managing the connection state.

***Stateful means that there is a state that can be manipulated. In particular,
a stateful connection is a connection that heavily relies on its state in
order to work***

### Broadcasting and group messages

Another problem of scaling Websocket occurs when we need to send messages to
multiple connected clients (i.e. broadcasting a message or sending a message to
all clients subscribed to a specific topic).

Imagine that we have a chat server, and that when an user send a message in a
specific chat room, we broadcast it to all users subscribed to that room.
If we have a single server instance, all connection are managed by this instance
so we can safely trust that the message will be delivered to all recipents.
On the other hand, with multiple server instances, users subscribing to a chat
room will probably connect to different instances. This way, if an user send a
message to the chat room *'xyz'* at the server *A*, users subscribed to the same
chat room at the server *B* are not receiving it.

### Documenting Websocket interfaces

Another common problem with Websocket, that's not even related to scaling, is
about documentation. Due to the event driven nature of the Websocket protocol
it does not fit well to be documented with [openapi](https://swagger.io/specification/).
However a new specification for asynchronous, event driven interfaces has been
defined recently. The spec name is [asyncapi](https://www.asyncapi.com/) and I'm
currently studying it. I don't know if this has to be implemented here or it's
better having a separate library for that, however this is surely something
we have to look at.

### Other problems

When I came first to think about this library, I started making a lot of research
of common problems related to Websocket on stackoverflow, reddit, github issues and
so on. I found some interesting resource that are however related to the implementation
itself. I picked up best solutions and elaborated my owns converging all of that in
this library.

## Example

This is a basic example using an in memory broker with a single server instance.

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from distributed_websocket import Connection, WebSocketManager

app = FastAPI()
manager = WebSocketManager('channel:1', broker_url='memory://')
...


app.on_event('startup')
async def startup() -> None:
    ...
    await manager.startup()


app.on_event('shutdown')
async def shutdown() -> None:
    ...
    await manager.shutdown()


@app.websocket('/ws/{conn_id}')
async def websocket_endpoint(
    ws: WebSocket,
    conn_id: str,
    *,
    topic: Optional[Any] = None,
) -> None:
    connection: Connection = await manager.new_connection(ws, conn_id)
    try:
        async for msg in connection.iter_json():
            await manager.broadcast(msg)
    except WebSocketDisconnect:
        await manager.raw_remove_connection(connection)
```

The `manger.new_connection` method create a new Connection object and add it to
the `manager.active_connections` list. Note that after a WebSocketDisconnect
is raised, we call `raw_remove_connection`: this method only remove the connection
object from the `manager.active_connections` list, without calling `connection.close`.
If you need to close a connection at any other time, you can use `manager.remove_connection`.

Note that here we are using `manager.broadcast` to send the message to all connections managed
by the WebSocketManager instance. However, this method only work if we have a single server
instance. If we have multiple server instances, we have to use `manager.receive`, to properly
send the message to the broker.

```python
@app.websocket('/ws/{conn_id}')
async def websocket_endpoint(
    ws: WebSocket,
    conn_id: str,
    *,
    topic: Optional[Any] = None,
) -> None:
    connection: Connection = await manager.new_connection(ws, conn_id)
    try:
        async for msg in connection.iter_json():
            await manager.receive(msg)
    except WebSocketDisconnect:
        await manager.raw_remove_connection(connection)
```
