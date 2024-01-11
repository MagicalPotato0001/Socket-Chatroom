import socket
import threading
import rsa
import json
from cryptography.fernet import Fernet

class MessagingClient:
    def __init__(self,
                 server = ('localhost', 9999),
                 server_pass = None,
                 verbose = True,
                 parent = None,
                 key_size = 2048,
                 message_size = 4096,
                 disconnect_message = "!DISCONNECT",
                 voice_join_message = "!VOICEJOIN",
                 voice_leave_message = "!VOICELEAVE",
                 update_active_message = "!UPDATE_LIST",
                 username = "ANON"):
        self.client = None
        self.server = server
        self.parent = parent
        self.passw = server_pass
        self.cipher = Fernet(self.passw)

        self.verbose = verbose

        self.user = username
        self.format = 'utf-8'

        self.msg_size = message_size
        self.d_msg = disconnect_message
        self.vj_msg = voice_join_message
        self.vl_msg = voice_leave_message
        self.update_msg = update_active_message

        #Encryption
        self.public_key, self.private_key = rsa.newkeys(key_size)
        self.public_partner = None

        self.error_log = []
        self.message_log = []
        self.connected = False

    def encrypt(self, msg):
        return rsa.encrypt(msg.encode(self.format), self.public_partner)
    
    def decrypt(self, msg):
        return rsa.decrypt(msg, self.private_key).decode(self.format)

    def connect(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(self.server)
            self.public_partner = rsa.PublicKey.load_pkcs1(self.cipher.decrypt(self.client.recv(self.msg_size)))
            self.client.send(self.public_key.save_pkcs1("PEM"))
            self.client.send(self.encrypt(self.user))
            self.connected = True
            threading.Thread(target=self.receive, daemon=True).start()
        except Exception as e:
            self.error_log.append(f"[Error connecting to server] {e}")
            if self.verbose:
                print(self.error_log[-1])
    
    def receive(self):
        while self.connected:
            try:
                msg = self.decrypt(self.client.recv(self.msg_size))
                if msg:
                    msg_split = msg.split('\n')
                    if msg.split('\n', 1)[0] == self.update_msg:
                        try:
                            data = '\n'.join(msg_split[1:])
                            json_data = json.loads(data)
                            self.parent.update_list(json_data)
                        except json.JSONDecodeError as e:
                            self.error_log.append(f"[Error updating active users] {e}")
                            if self.verbose:
                                print(self.error_log[-1])
                        continue
                    elif msg == self.d_msg:
                        self.parent.disconnect()
                    else:
                        self.message_log.append(msg)
                        self.parent.update_chat(msg)
            except Exception as e:
                self.error_log.append(f"[Error receiving from server] {e}")
                if self.verbose:
                    print(self.error_log[-1])
    
    def send(self, msg):
        try:
            self.client.send(self.encrypt(msg))
        except Exception as e:
            self.error_log.append(f"[Error sending message to server] {e}")
            if self.verbose:
                print(self.error_log[-1])

    def disconnect(self):
        try:
            self.send(self.d_msg)
            self.connected = False
            self.client.close()
        except Exception as e:
            self.error_log.append(f"[Error disconnecting from server] {e}")
            if self.verbose:
                print(self.error_log[-1])
