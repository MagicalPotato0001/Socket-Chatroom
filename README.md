# Socket Chatroom
#### Video Demo:  https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley
#### Description:
## Introduction
This README provides an overview of a TCP messaging and UDP voice chat server and client application. The application is designed for text-based messaging and real-time voice communication between clients over a network. It includes both server and client components written in Python.

## Basic Overview
- Python TCP and UDP socket chatroom with GUI, RSA and Fernet encryption.
- Server and client based files.
- Connection authorized via Fernet key and then updated to RSA encryption after handshake.
- All TCP messages are encrypted.
- Voice over UDP.
- Usernames.
- Active user list for connected users and voice chat users.
- Noise Reduction for audio stream.
- Audio stream is not encrypted yet.

## Features
- **TCP Messaging: Clients can connect to the server using TCP/IP and exchange text messages in real-time.
- **UDP Voice Chat: Clients can participate in voice chat using UDP/IP, allowing for low-latency voice communication.
- **Encryption: All messages are encrypted using RSA and Fernet encryption for secure communication.
- **Active User List: The server maintains a list of active users and updates it in real-time.
- **Graphical User Interface (GUI): The client application includes a graphical user interface for easy interaction.

## Prerequisites
Before using this application, ensure you have the following prerequisites installed:

- Python 3.x
- Required Python packages: rsa, cryptography, pyaudio, noisereduce, numpy, socket, threading, json, tkinter, customtkinter


You can install these packages using 'pip':
- pip install rsa cryptography pyaudio noisereduce numpy

## Getting Started
To use the messaging and voice chat application, follow these steps:

# Server
1. Open the server.py script in a text editor.
2. Customize the server settings, such as IP address, ports, and encryption key, if needed.
3. Run the server script using Python:
```bash
python server.py
```

# Client
1. Open the client.py script in a text editor.
2. Customize the client settings, such as the server IP address, ports, username, and password, if needed.
3. Run the client script using Python:
```bash
python client.py
```

## Class Descriptions
Overview of each class and it's purpose:

# MessagingClient
- This class represents the messaging client.
- It is responsible for establishing a TCP connection to the server, sending and receiving encrypted text messages, and handling various messaging-related tasks.
- The class provides methods for encryption, decryption, connection, message sending, and disconnection.

# AudioClient
- This class represents the audio client for voice chat.
- It uses PyAudio to capture and play audio data in real-time.
- Voice data is transmitted over UDP for low-latency voice communication.
- The class provides methods for sending and receiving audio data, starting and terminating the audio stream, and handling audio-related tasks.

# Client
- This class serves as the main client application, combining both messaging and audio capabilities.
- It provides a graphical user interface (GUI) for user interaction and allows users to connect to the server, send messages, and participate in voice chat.
- The class includes methods for connecting, disconnecting, sending messages, and managing the GUI.

# Server
- This class represents the server component of the application.
- It handles incoming TCP connections for messaging and UDP communication for voice chat.
- The server maintains active user lists and ensures secure messaging through encryption.
- The class includes methods for starting and stopping the messaging and voice servers, as well as handling client connections.

# Client GUI
- If you want to use the graphical user interface (GUI) for the client, set use_gui to True in the client script (client.py).
- The GUI provides a user-friendly interface for connecting to the server, sending messages, and managing voice chat.

## Usage
Once the server and client(s) are running, you can perform the following actions:

# Messaging
- Connect to the server by providing the server's IP address, messaging port (TCP), username, and password (optional).
- Send text messages in the chat window by typing in the message input box and pressing Enter or clicking the "Send" button.
- The chat log displays incoming and outgoing messages.

# Voice Chat
- To enable voice chat, click the "Connect Voice" button in the client GUI.
- Participants in voice chat can speak into their microphones, and the voice data is sent over UDP to other connected clients.
- Click the "Disconnect Voice" button to stop voice chat.

# Active User List
- The client displays a list of active users in both messaging and voice chat modes.
- The list is updated in real-time to reflect connected users.

# Disconnect
- You can disconnect from the server by clicking the "Disconnect" button in the client GUI or by sending the "!DISCONNECT" message.

# Generating a New Encryption Key
- To generate a new encryption key, click the "Generate Key" button in the server GUI. This will create a new Fernet encryption key.

# Troubleshooting and Error Handling
- Any errors or issues encountered during server or client operation are logged and displayed in the console if verbose is set to True
- Refer to the error logs for troubleshooting and debugging purposes.

# Security Considerations
- This application uses RSA and Fernet encryption for message security. However, it is recommended to use strong and unique passwords and encryption keys.
- Ensure that the server is hosted on a secure network to prevent unauthorized access.

# Limitations
This application is a basic example of messaging and voice chat and may not be suitable for production use without further development and security enhancements.
- The voice chat feature relies on UDP and does not provide error correction or packet loss recovery.


