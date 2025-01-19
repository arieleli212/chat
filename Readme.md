# Introduction to Chat Project 💬
Our project demonstrates using the TCP Protocol for communication between multipule clients and a main server to rule them all [insert evil laughter here😈].

The packages used for the **Server**:
- socket package - handles the TCP connections
- threading package - handles multiple clients connections
- signal package - siganls to the clients for catching errors in the server  
- json package - reads/writes from files 
- sys package -  uses system command

The packages used for the **Client**:
- socket package - handles the TCP connections
- threading package - handles obtaining the socket and GUI
- tkinter package - handles the graphics

## How Does It Work? 🤔

When you run the server it opens a socket and binds it to your localhost (`127.0.0.1`) and port `5000`.

After the bind, the server starts the socket and waits for the clients to connect. meanwhile, the server always checks if the socket is alive in order to let the clients know if there's anything wrong and shutdown unexpectedlly.

### 🎉New Client in Town

 We made a nice GUI using the [tkinter](https://docs.python.org/3/library/tkinter.html) package to make the client experience more joyfull 😊

The GUI is a basic chat that allows you to write your message and send it to the recipient of your choosing. 

you can receive other messages and they will be listed in the nice text board in the middle of the chat GUI.

In the begining you will receive a messageBox to insert your name so the server knows who you are and will let the other users know you're here (We can all see you👀)

### So how does the server respond to a new client?
When the server receive a connection it gets the connection details (port,address) and opens a new thread for it to live in. This allows it to connect to multiple clients simultaneously (it's ok there is enough server for everyone 😉). After that the server waits for the client to insert his name so he will be identifed and known to the other users. 

### Chat Room
In the chat room you can choose who you'd like to text and everyone can text you too.

## History (DB)

We save all the history in a file called messages.json.
(very original as you can tell)

The file contains a json object for each client connected, and all the messages sent to him with the senders name.

If you reconnect using the same name, all your messages will be recoverd with a `[History]` prefix.

So think carefully before sending a message, (WE KNOW EVERYTHING🧿).

# How To Start?

## Prerequisites
- [python](https://www.python.org/downloads/)
- Run `linux: python --version, windows: python.exe --version` to check if you have python installed  

## Run the server
Run from this directory `linux: python server.py, windows: python.exe server.py` , check for your command (may be py.exe, python3.exe, python39.exe, etc)

## Run a Client
Run from this directory `linux: python client.py, windows: python.exe client.py` , check for your command (may be py.exe, python3.exe, python39.exe, etc) 

# Pay Attention
If you try to run the client without the server, the client will fail because there is no server to connect to.
([#lonely🥲](https://youtu.be/6EEW-9NDM5k?si=9sShE3m9xdGqFBKS&t=13))

# Handling Errors

- Run A Client without a Server: Client wont be able to run.
- Client crushes in a middle of a session: The server will disconnect him from the connected clients list
- Server crushes in a middle of a session: The server will notify all the clients it's entering shutdown mode. After the specific client approves the pop-up message he will be disconnected. 
