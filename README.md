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

In order to solve this issue, ***fastapi-distributed-websockets*** implements a
way to share Websocket connections information between instances.

### 
