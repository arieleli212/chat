# Introduction to Chat Project
Our project demonstrate using the TCP Protocol for communication between multipule clients and a main server to rule them all.

The packages used for the **Server**:
- socket package - handle the TCP connections
- threading package - handle multiple clients connections
- signal package - siganls to the clients for catching errors in the server  
- json package - read/write from files 
- sys package -  using system command

The packages used for the **Client**:
- socket package - handle the TCP connections
- threading package - handle obtaining the socket and GUI
- tkinter package - handle the graphics

## How It Works?

When you run the server it opens a socket and bind it to your localhost (`127.0.0.1`) and port `5000`.

After the bind the server start the socket and wait for clients to connect. meanwhile the server always checks if the socket is alive for letting the clients to know if there is something wrong and he shutdown unexpectedlly.

### 🎉New Client in Town

When you run the client we made a nice GUI using the [tkinter](https://docs.python.org/3/library/tkinter.html) package to make the client experience to be more joyfull.

The GUI is a basic chat so you can write your message and send it to the recipient as you choose. you can receive other messages and they will be listed in the nice texting board in the middle of the chat box.

In the begging you will receive a messageBox to insert your name so the server will know who you are and will let the other users know you're here (We can all see you👀)

### So how is the server responds to a new client?
When the server receive a connection he gets the connection details (port,address) and opens a new thread for it to live in so it won't stuck the server on one connection only (its ok there is enough server for everyone). After that the server waits for the client to insert his name so he will be identify and be known to all the other users 

### Chat Room
In the chat room you can choose who you'd like to text and everyone can text you to.

## History (DB)

We save all the history in a file called messages.json.

The file contain a json object for each client connected and all the messages sent to him with the sender name.

If you reconnect using the same name, all your messages will be recoverd with a `[History]` prefix.

So think carefully before sending a message, (WE KNOW ALL🧿).

# How To Start?

## Prerequisites
- [python](https://www.python.org/downloads/)
- Run `linux: python --version, windows: python.exe --version` to check if you have python installed  

## Run the server
Run from this directory `linux: python server.py, windows: python.exe server.py` , check for your command (may be py.exe, python3.exe, python39.exe, etc)

## Run a Client
Run from this directory `linux: python client.py, windows: python.exe client.py` , check for your command (may be py.exe, python3.exe, python39.exe, etc) 

# Notice
If you try to run the client without the server, the client will fail because there is no server to connect to.

# Handle Error

- Run A Client without a Server: Client wont be able to run.
- Client crushes in a middle of a session: the server will disconnect him from the connected clients list
- Server crushes in a middle of a session: the server will notify all the clients that he is in shutdown mode and after client acknoledge the client will disconnected. 
