from MusEEG import eegData

# -*- coding: utf8 -*-
#
# Cykit Example TCP - Client
# author: Icannos
# modified for MusEEG by: hugo flores garcia

import socket

class client:
    BUFFER_SIZE = eegData.chunkSize
    host = "127.0.0.1"
    port = 5555

    # Named fields according to Warren doc !
    FIELDS = {"COUNTER": 0, "DATA-TYPE": 1, "AF3": 4, "F7": 5, "F3": 2, "FC5": 3, "T7": 6, "P7": 7, "01": 8, "02": 9,
              "P8": 10, "T8": 11, "FC6": 14, "F4": 15, "F8": 12, "AF4": 13, "DATALINE_1": 16, "DATALINE_2": 17}

    def data2dic(self, data):
        field_list = data.split(b',')

        if len(field_list) > 17:
            return {field: float(field_list[index]) for field, index in self.FIELDS.items()}
        else:
            return -1

    def setup(self):

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
        self.s.send(b"\r\n")

        # To read the header msgs about cykit etc...
        self.s.recv(168, socket.MSG_WAITALL)

        # Local buffer to store parts of the messages
        self.buffer = b''

        # If when when split by \r, \r was the last character of the message, we know that we have to remove \n from
        # the begining of the next message
        self.remove_newline = False

    def stream(self):
        while True:
            # We read a chunk
            data = self.s.recv(self.BUFFER_SIZE, socket.MSG_WAITALL)

            # If we have to remove \n at the begining
            if self.remove_newline:
                data = data[1:]
                self.remove_newline = False

            # Splitting the chunk into the end of the previous message and the begining of the next message
            msg_parts = data.split(b'\r')

            # If the second part ends with nothing when splitted we will have to remove \n next time
            if msg_parts[-1] == b'':
                self.remove_newline = True
                # Therefore the buffer for the next step is empty
                self.n_buffer = b''
            else:
                # otherwise we store the begining of the next message as the next buffer
                self.n_buffer = msg_parts[-1][1:]

            # We interprete a whole message (begining from the previous step + the end
            fields = self.data2dic(buffer + msg_parts[0])

            # We setup the buffer for next step
            self.buffer = self.n_buffer

            # Print all channel
            print(fields)
            return fields


if __name__ == 'main':
    client = client()
    client.setup()
    client.stream()