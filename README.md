# FastAPI Distributed Websockets

A library to implement websockets for distibuted system based on FastAPI


## Problems of scaling websockets among multiple servers in production

Websocket is a relatively new protocol for real time communication over HTTP.
It establish a druable, stateful, full-duplex connection between clients and the server.
It can be used to implement chats, real time notifications, broadcasting and
pub/sub models.

### Connections from clients

HTTP request/response mechanism fits very well to scale among multiple server
instances in production. Any time a client make a request, it can connect
to any server instance and it's going to receive the same response. After
the response has been returned to the client, it went disconnected and it can
make another request without the need to hit the same instace as before.
This thanks to the stateless nature of HTTP.

However, Websocket establish stateful connection between the client and the
server and, if some error occurs and the connection went lost, we have to
ensure that clients are going to hit the same server instance they were connected
before, since that instance was managing the connection state.

***Stateful means that there is a state that can be manipulated. In particular,
a stateful connection is a connection that heavily relies on its state in
order to work***

### Broadcasting and group messages

Another problem of scaling Websockets occurs when we need to send messages to
multiple connect clients (i.e. broadcasting a message or sending a message to
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
defined recently. Its name is [asyncapi](https://www.asyncapi.com/) and
we can use it for this porpouse.

### Other problems

When I came first to think about this library, I started making a lot of research
of common problems related to Websocket on stackoverflow, reddit, github issues and
so on. I found some interesting resource that are howevere related to the implementation
itself. I picked up best solutions and elaborated my owns convergin all of that in
this library.

## The design
