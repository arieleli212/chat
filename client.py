

import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter.scrolledtext import ScrolledText

HOST = '192.168.0.108'
PORT = 5000

class ChatClient:
    # self- refers to the instance of the class "ChatClient"
    # master- refers to the root window
    def __init__(self, master):
        self.master = master
        self.master.title("Python Chat Client")
        self.master.geometry("600x400")  # Sets the window size

        #defines the variables of ChatClient for the instance
        self.socket = None
        self.username = None
        self.user_list = []

        # Top frame: connection info + user dropdown
        
        self.frame_top = tk.Frame(master)
        self.frame_top.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.label_user = tk.Label(self.frame_top, text="Connecting...")
        self.label_user.pack(side=tk.LEFT, padx=5)

        self.label_to = tk.Label(self.frame_top, text="Recipient:")
        self.label_to.pack(side=tk.LEFT, padx=5)

        # Initialize a StringVar with a placeholder
        self.selected_user = tk.StringVar(master)
        self.selected_user.set("Select a user")

        # Create OptionMenu with at least one placeholder item
        self.dropdown_recipients = tk.OptionMenu(
            self.frame_top,
            self.selected_user,
            "Select a user"
        )
        self.dropdown_recipients.pack(side=tk.LEFT, padx=5)

        self.refresh_button = tk.Button(self.frame_top, text="Refresh", command=self.refresh_user_list)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        # Middle frame: chat display
 
        self.frame_middle = tk.Frame(master)
        self.frame_middle.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.text_area = ScrolledText(self.frame_middle, height=15, width=50, wrap=tk.WORD)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)

      
        # Bottom frame: message entry + send button

        self.frame_bottom = tk.Frame(master)
        self.frame_bottom.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.label_message = tk.Label(self.frame_bottom, text="Enter Message:")
        self.label_message.pack(side=tk.LEFT, padx=5)

        self.entry_message = tk.Entry(self.frame_bottom, width=40)
        self.entry_message.pack(side=tk.LEFT, padx=5)
        # binds the "Enter" key to send message
        self.entry_message.bind("<Return>", self.send_message_event)

        self.send_button = tk.Button(self.frame_bottom, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)

        # cleans up on close, activates the "WM_DELETE_WINDOW" protocol when closing the window
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # begins the connection between the client and the server via the "connect_to_server" function
        self.connect_to_server()

    def connect_to_server(self):
        # gets username from the user and connects to the server
        # allowe user to enter a username
        self.username = simpledialog.askstring("Username", "Enter a username:", parent=self.master)
        if not self.username: # if username is empty- displays error and closes the connection
            messagebox.showerror("Error", "Username cannot be empty.")
            self.master.destroy() # ends the connection
            return

        self.label_user.config(text=f"Connected as: {self.username}") #indicates that the user is connected

        try:
            # creates a new socket and connects to the server
            # AF_INET- address family, SOCK_STREAM- the sockets uses a TCP connection
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            
            # registers with the server via username and notifys the server
            register_msg = f"/register {self.username}"
            self.socket.sendall(register_msg.encode())
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
            self.master.destroy() # ends the connection
            return

        # starts a background thread to listen for messages
        listen_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        listen_thread.start()

    def listen_for_messages(self):
     # listens for messages from the server
        try:
            while True:
                data = self.socket.recv(4096) # recives the data in 4096 chuncks
                if not data: # if no data is recieved
                    break # breaks the loop
                #decodes the data and remove spaces from the start and end of the string
                message = data.decode().strip()
              
                # checks for a server shutdown message
                if message.startswith("/shutdown"): # is the message starts with '/shutdown' 
                    messagebox.showinfo("Server Shutdown", "The server has been shut down. Please try reconnecting later.")
                    break # breaks the loop
              
                # checks for special commands from the server
                if message.startswith("/userlist"):
                    # gets the cleint list from the server for example: "/userlist ['Valery', 'Ariel', 'Yam']"
                    try:
                        userlist_str = message.replace("/userlist ", "") # removes '/userlist' from the message                        
                        self.user_list = eval(userlist_str) # converts the message from string into a list
                        self.refresh_user_list() # updates the list of users this user can chat with according to the server's list
                 
                    except Exception as e: # if there is an error in converting the user list- prints message
                        print(f"[!] Error parsing user list: {e}")
                else:
                    self.append_text(message) # adds the message to the bottom of the chat window
       
        except Exception as e:
            print(f"[!] Error in listen_for_messages: {e}")
        finally: # closes the connection 
            self.socket.close() 
            self.master.quit()

    def refresh_user_list(self):
      # updates the dropdown menu of recipients with the current user list

        menu = self.dropdown_recipients["menu"]
        menu.delete(0, "end")

        # adds the users in user_list to the dropdown menu
        for user in self.user_list:
            if user != self.username:  # adds the user to the dropdown menu if it's not the current user 
                menu.add_command(
                    label=user,
                    command=lambda value=user: self.selected_user.set(value)
                )
      
      # sets default user/message to display in the dropdown menu- depending on if there are any other users in the user_list
        if self.user_list:
            possible_recipients = [u for u in self.user_list if u != self.username] # gets the first user who isnt the current user from the user list 
            if possible_recipients:
                self.selected_user.set(possible_recipients[0]) #sets him as the default user
            else:
                self.selected_user.set("Select a user") # if there are no other users- sets to "Select a user"
        else:
            self.selected_user.set("Select a user")

    def send_message_event(self, event):
        # Sends a message when the user presses the "Enter" key 
        self.send_message()

    def send_message(self):
       
        #sends a message to the selected recipient
       
        recipient = self.selected_user.get() # gets the selected user from the dropdown menu
        msg_body = self.entry_message.get().strip() # gets the message from the entry field 
       
        if not recipient or recipient == "Select a user": # as set in the function 'refresh_user_list' (when therr are no other users)
            messagebox.showwarning("Warning", "No recipient selected.")
            return
        if not msg_body: #if empty
            return

        msg = f"/msg {recipient} {msg_body}"
        try:
            self.socket.sendall(msg.encode()) # sends the message to the server
            # shows the message at the bottom of the local chat window
            self.append_text(f"[You -> {recipient}]: {msg_body}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not send message: {e}")

        # clears the entry field
        self.entry_message.delete(0, tk.END)

    def append_text(self, msg):
       
        # Appends a message (adds to the end of the chat) to the chat window and scrolls to the bottom.
       
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, msg + "\n")
        self.text_area.config(state=tk.DISABLED)
        # Automatically scroll to the end
        self.text_area.yview(tk.END)

    def on_closing(self):
     
       # cleans up when the user closes the window.
        try:
            self.socket.close() # closes the connection
        except:
            pass # checks if the connection is already closed and if so- passes
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk() # creates the main window and assigns it to root
    app = ChatClient(root) # creates an instance of the ChatClient class
    root.mainloop() # runs the main loop of the window
