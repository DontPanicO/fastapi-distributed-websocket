[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/) 
[![License: MIT](https://img.shields.io/badge/License-MIT-success.svg)](https://mit-license.org/) 
[![pypi 0.2.0](https://img.shields.io/badge/pypi-0.2.0-ff69b4.svg)](https://pypi.org/project/fastapi-distributed-websocket/)

# FastAPI Distributed Websocket

A library to implement websocket for distibuted systems based on FastAPI.

**N.B.: This library is still at an early stage, use it in production at your own risk.**


## What it does

The main features of this libarary are:

* Easly implementing broadcasting, pub/sub, chat rooms, etc...
* Proxy websocket connections to other servers (e.g. from an api gateway)
* Authentication
* Clean exception handling
* An in memory broker for fast development


## Problems of scaling websocket among multiple servers in production

Websocket is a relatively new protocol for real time communication over HTTP.
It establishes a durable, stateful, full-duplex connection between clients and the server.
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

**Stateful means that there is a state that can be manipulated. In particular,
a stateful connection is a connection that heavily relies on its state in
order to work**

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

## Examples

### Installation

`$ pip install fastapi-distributed-websocket`

### Basic usage

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
        while True:
            msg = await connection.receive_json()
            await manager.broadcast(msg)
    except WebSocketDisconnect:
        await manager.remove_connection(connection)
```

The `manger.new_connection` method create a new Connection object and add it to
the `manager.active_connections` list. Note that after a `WebSocketDisconnect`
is raised, we call `remove_connection`: this method only remove the connection
object from the `manager.active_connections` list, without calling `connection.close`, since
the connection is already closed.
If you need to close a connection at any other time, you can use `manager.close_connection`.
If you use `connection.iter_json`, it already handles the `WebSocketDisconnect` exception, so
you can simply call `manager.remove_connection` just after the loop (see next code block).

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
    # This is the preferred way of handling WebSocketDisconnect
    async for msg in connection.iter_json():
        await manager.receive(connection, msg)
    await manager.remove_connection(connection)
```

### Proxy from an API gateway

Let's say we are developing a chat service and that all our services are behind
an API gateway. If we want to keep our websocket service behind it too, then
fastapi-distributed-websocket provides us with `WebSocketProxy`.

```python
from distributed_websocket import WebSocketProxy
# skipped other imports for brevity

app = FastAPI()


WS_TARGET_ENDPOINT = 'ws://websocket_service:8000/wshandler'

@app.websocket('/ws')
async def websocket_proxy(websocket: WebSocket):
    await websocket.accept()
    ws_proxy = WebSocketProxy(websocket, WS_TARGET_ENDPOINT)
    await ws_proxy()
```

This will forward all messages from the client to the target endpoint and
all messages from the target endpoint to the client.

Now let's assume that our websocket service code is the code of our previous
example. Our API Gateway code will be:

```python
from distributed_websocket import WebSocketProxy
# skipped other imports for brevity

app = FastAPI()


WS_TARGET_ENDPOINT = 'ws://websocket_service:8000/ws/{}'

@app.websocket('/ws/{conn_id}')
async def websocket_endpoint(
    ws: WebSocket,
    conn_id: str,
) -> None:
    await websocket.accept()
    ws_proxy = WebSocketProxy(websocket, WS_TARGET_ENDPOINT.format(conn_id))
    await ws_proxy()
```

## API Reference

### Connection

Connection objects wrap the websocket connection and provide a simple interface
to send and receive messages. They have a `topics` attribute to store subscriptions
patterns and implement pub/sub models.

* **`async`**` accept(self) -> None` \
  Accept the connection.
* **`async`**` close(self, code: int = 1000) -> None` \
  Close the connection with the specified status.
* **`async`**` receive_json(self) -> Any` \
  Receive a JSON message.
* **`async`**` send_json(self, data: Any) -> None` \
  Send a JSON message over the connection.
* **`async`**` iter_json(self) -> AsyncIterator[Any]` \
  Iterate over the messages received over the connection.


### Messages

Message objects store the message type, the topic and the data. They provides
an easy serialization/deserialization mechanism.
Remeber that messages returned by `connection.iter_json` are already deserialized
into `dict` objects, so here we call *deserialization* the process of converting
a `dict` object into a `Message` object.

* `type: str` \
  The message type.
* `topic: str` \
  The message topic.
* `conn_id: str | list[str]` \
  The connection id or list of connection ids that the message should be sent to.
* `data: Any` \
  The message data.

* **`classmethod`**`from_client_message(cls, *, data: Any) -> Message` \
  Create a message from a client message.
* `__serialize__(self) -> dict` \
  Serialize the message into a `dict` object.


### Subscriptions

You can bind topics to connection objects to implement pub/sub models, notification and so on.
The `topics` attribute is a set of strings that follows the pattern matching syntax of MQTT.
This library share connection objects state between server instances, so you may find
references to terms like `channel`, `publish`, `subscribe` and `unsubscribe` referring to
the same concepts but applied to the underlying server/broker communication. \
This may be confusing, but remember to keep separated the communication between the server
and the clients, that you are developing and the communication between the server and the broker,
that you usually don't deal with.

* `subscribe(connection: Connection, message: Message) -> None` \
  Subscribe a connection to `message.topic`.
* `unsubscribe(connection: Connection, message: Message) -> None` \
  Unsubscribe a connection from `message.topic`.
* `hanlde_subscription_message(connection: Connection, message: Message) -> None` \
  Calls `subscribe` or `unsubscribe` depending on the message type.
* `matches(topic: str, patterns: set[str]) -> bool` \
  Check if `topic` matches any of the patterns in `patterns`.


### Authentication

Authentication is provided with the `WebSocketOAuth2PasswordBearer` class.
It inherits from *FastAPI* `OAuth2PasswordBearer` and overrides `__call__` method to accept
a `WebSocket` object.

* **`async`**` __call__(self, websocket: WebSocket) -> str | None` \
  Authenticate the websocket connection and return the *Authorization* header value. \
  If the authentication fails, return `None` if the objects has been initialized with `auto_error=False` \
  or close the connection with the `WS_1008_POLICY_VIOLATION` code.


### Exceptions and Exception Handling

`fastapi-distributed-websocket` provides exception handling via decorators. You can use the
apposite decorators passing an exception class and a handler callable. Exception handlers
should accept only the exception object as argument.\
**Why this is useful?**\
Because sometimes the same type of exception can be raised by different parts of the application,
this way you can decorate the higer level function in the call stack to handle the exception at
any level.\
A base `WebSocketException` class is provided to bind connection objects to the exception, so
your handler function can easily access it.
If you need to access connection objects from the exception handler, your custom exceptions
should inherit from `WebSocketException`, no matter if they are really network related or not.

* `WebSocketException(self, message: str, *, connection: Connection) -> None`
* `InvalidSubscription(self, message: str, *, connection: Connection) -> None` \
  Raised when a subscription pattern use an invalid syntax. Inherits from `WebSocketException`.
* `InvalidSubscriptionMessage(self, message: str, *, connection: Connection) -> None` \
  Like `InvalidSubscription` it could be raised for bad syntax, but it could also be raised \
  when the message type is not *subscribe* or *unsubscribe*. Inherits from `WebSocketException`.

* `handle(exc: BaseException, handler: Callable[..., Any]) -> Callable[..., Any]` \
  Decorator to handle exceptions. If you decorate a function with this decorator, at any time \
  an exception of type `exc` is raised or propagated to the function, it will be handled by `handler`. \
  Use this decorator only if both your handler and the function are not async.
* **`async`**` ahandle(
    exc: BaseException, handler: Callable[..., Coroutine[Any, Any, Any]]
) -> Callable[..., Any]` \
  Decorator to handle exceptions, same ad `handle`, but the handler is a coroutine function. \
  Use this if your handler is a coroutine function, while the decorated function could be \
  either a sync or an async function.


### Broker Interfaces

Connections' state is shared between server instances using a pub/sub broker. By default,
the broker is a `reids.asyncio.Redis` instance (ex `aioredis.Redis`), but you can use any
other implementation. `fastapi-distributed-websocket` provides an `InMemoryBroker` class
for development purposes.
You can inherit from `BrokerInterface` and override the methods to implement your own broker.

* **`async`**` connect(self) -> Coroutine[Any, Any, None]` \
  Connect to the broker.
* **`async`**` disconnect(self) -> Coroutine[Any, Any, None]` \
  Disconnect from the broker.
* **`async`**` subscribe(self, channel: str) -> Coroutine[Any, Any, None]` \
  Subscribe to a channel.
* **`async`**` unsubscribe(self, channel: str) -> Coroutine[Any, Any, None]` \
  Unsubscribe from a channel.
* **`async`**` publish(self, channel: str, message: Any) -> Coroutine[Any, Any, None]` \
  Publish a message to a channel.
* **`async`**` get_message(self, **kwargs) -> Coroutine[Any, Any, Message | None]` \
  Get a message from the broker.

### WebSocketManager

The `WebSocketManager` class is where the main logic of the library is implemented. \
It keeps track of the connection objects and starts the broker connection.
It spawn a main task, a listener that wait (non-blocking) for messages from the broker,
and send them to the connection objects (broadcasting or checking for subscriptions)
spawning a new task for each send. \
The broker initialisation is done in the constructor while calls to `broker.connect` and
`broker.disconnect` are handled in the `startup` and `shutdown` methods.

* **`async`**` new_connection(
        self, websocket: WebSocket, conn_id: str, topic: str | None = None
    ) -> Coroutine[Any, Any, Connection]` \
  Create a new connection object, add it to `self.active_connections` and return it.
* **`async`**` close_connection(
        self, connection: Connection, code: int = status.WS_1000_NORMAL_CLOSURE
    ) -> Coroutine[Any, Any, None]` \
  Close a connection object and remove it from `self.active_connections`.
* ` remove_connection(self, connection: Connection) -> None` \
  Remove a connection object from `self.active_connections`.
* `set_conn_id(self, connection: Connection, conn_id: str) -> None` \
  Set the connection id and notify the client.
* `send(self, message: Message) -> None` \
  Send a message to all the connection objects subscribed to `message.topic`. \
  It spawns a new task wrapping the coroutine resulting from `self._send`.
* `broadcast(self, message: Message) -> None` \
  Send a message to all the connection objects. \
  It spawns a new task wrapping the coroutine resulting from `self._broadcast`.
* `send_by_conn_id(self, message: Message) -> None` \
  Send a message to all the connection objects with `id` equals to `message.conn_id`. \
  It spawns a new task wrapping the coroutine resulting from `self._send_by_conn_id` \
  if `conn_id` is a string or from `_send_multi_by_conn_id` if it is a list.
* `send_msg(self, message: Message) -> None` \
  Based on the message type, it calls `send`, `send_by_conn_id` or `broadcast`.
* **`async`**` receive(
        self, connection: Connection, message: Any
    ) -> Coroutine[Any, Any, None]` \
  Receive a message from a connection object. It passes the message down to \
  a private method that handle eventual subscriptions and then publish the message \
  to the broker.
* **`async`**` startup(self) -> Coroutine[Any, Any, None]` \
  Start the broker connection and the listener task.
* **`async`**` shutdown(self) -> Coroutine[Any, Any, None]` \
  Close the broker connection and the listener task. \
  It also takes care to cancel all the tasks spawned by `send_msg` and \
  close all the connection objects before.


### WebSocketProxy

The `WebSocketProxy` class initialise callable objects that can be
used to start proxyng websocket messages from client to a server and viceversa.
It's initialised with a two parameters:

* **client**: a `WebSocket` object
* **server_endpoint**: a `str` containing the endpoint of the server

Notice that the target server could be a remote server or the same server that starts the proxy.

* **`async`**` __call__(self) -> Coroutine[Any, Any, None]` \
  Start a websocket connection to **server_endpoint** and spawn two tasks: \
  one that forwards the messages from the client to the target and the other that \
  forwards the messages from the target to the client.
