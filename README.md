Simple socket chatroom:
-Uses RSA encryption and key swaps after every message.
-Uses tkinter and customtkinter to make a user friendly GUI.

Client.py:
-Takes ip/port and username then attempts to connect to the server
-Has a message entry field and send button.
-Center of the application is a chat log.

Server.py:
-Takes ip/port and then hosts with the host button.
-Accepts all incoming connections and starts encryption handshake and username retrieval.
-Waits for messages and sends the new message to all connected users.
