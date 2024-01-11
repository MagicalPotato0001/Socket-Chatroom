import socket
import threading
import pyaudio
import noisereduce as nr
import numpy as np


class AudioClient:
    def __init__(self, 
                 server = ('127.0.0.1', 12345), 
                 timeout = 0.5,
                 buffer = 2,
                 local = False,
                 send_chunk = 1024,
                 receive_chunk = 1024,
                 input_channels = 1,
                 output_channels = 1,
                 rate = 44100,
                 input_device = None,
                 output_device = None):
        self.p = pyaudio.PyAudio()
        self.info = self.p.get_host_api_info_by_index(0)
        if input_device is None:
            self.input_device = int(self.info.get('defaultInputDevice'))
        else:
            self.input_device = input_device
        if output_device is None:
            self.output_device = int(self.info.get('defaultOutputDevice'))
        else:
            self.output_device = output_device
        self.AFORMAT = pyaudio.paInt16
        self.SCHUNK = send_chunk
        self.RCHUNK = receive_chunk
        self.INPUT_CHANNELS = input_channels
        self.OUTPUT_CHANNELS = output_channels
        self.RATE = rate
        self.BUFFER = buffer
        self.connected = False
        self.recording = False
        self.listening = False
        self.server = server

        self.s_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.r_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if local:
            self.r_client.bind(('localhost', 5004))
        else:
            self.r_client.bind(server)

        self.s_thread = None
        self.r_thread = None
        self.r_client.settimeout(timeout)

        self.error_log = []

        self.stream = self.p.open(format = self.AFORMAT,
                            channels = self.INPUT_CHANNELS,
                            rate = self.RATE,
                            input = True,
                            output = True,
                            frames_per_buffer= self.SCHUNK,
                            input_device_index=self.input_device)

    def send_audio(self):
        while self.recording:
            try:
                data = self.stream.read(self.SCHUNK)
                audio_data_int = np.frombuffer(data, dtype=np.int16)

                final_audio = nr.reduce_noise(y=audio_data_int, sr=self.RATE, chunk_size=self.SCHUNK)

                # Send the denoised audio
                self.s_client.sendto(final_audio, self.server)
            except Exception as e:
                self.error_log.append(f"[Error sending audio] {e}")
                self.recording = False
                return
    
    def receive_audio(self):
        while self.listening:
            try:
                data, _ = self.r_client.recvfrom(self.RCHUNK * self.BUFFER)
                if not data:
                    self.error_log.append("[No audio data received]")
                    break
                self.stream.write(data)
            except Exception as e:
                self.error_log.append(f"[Error receiving audio] {e}")
                self.listening = False
                return

    def start_streaming(self):
        try:
            self.recording = True
            self.listening = True
            self.s_thread = threading.Thread(target = self.send_audio, daemon=True).start()
            self.r_thread = threading.Thread(target = self.receive_audio, daemon=True).start()
        except Exception as e:
            self.error_log.append(f"[Error starting audio stream] {e}")

    def terminate(self):
        self.recording = False
        self.listening = False
        self.stream.stop_stream()
        self.p.terminate()
        self.s_client.close()
        self.r_client.close()

#Client = AudioClient(local = False)
#Client.start_streaming()
#Client.terminate()