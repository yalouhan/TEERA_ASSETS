import socket
import threading
import struct

conn = None
file_lock = threading.Lock()

def tcp_server():
    global conn
    global server_sock
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('0.0.0.0', 12345))
    server_sock.listen(1)
    conn, addr = server_sock.accept()

    # conn.sendall(b'begin')
    print("begin sent to ESP32") 

    with open('data_file_HYL.txt', 'w') as file:
        while True:
            data = conn.recv(10000)
            if not data:
                break
            # print(f"Received data size: {len(data)}")  
            # print(f"Received data content: {data}")    
            with file_lock:
                for i in range(0, len(data), 4):
                    if i + 4 <= len(data):
                        unpacked_data = struct.unpack('i', data[i:i+4])[0]
                        file.write(f"{unpacked_data}, ")
                file.flush()
                # print("Data written to file")
    conn.close()
    server_sock.close()


def keyboard_input():
    global conn
    preset_key = "Han935779084!?"
    user_input = input("Please input your password: ")

    with open('data_file_HYL.txt', 'a') as file:
        with file_lock:
            if user_input == preset_key:
                file.write('True\n')
                conn.sendall(b'end')
                print("end sent to ESP32")
            else:
                file.write('False\n')
                conn.sendall(b'end')
                print("end sent to ESP32")
    conn.close()
    server_sock.close()

# 创建并启动线程
thread_server = threading.Thread(target=tcp_server)
thread_input = threading.Thread(target=keyboard_input)

thread_server.start()
thread_input.start()

thread_server.join()
thread_input.join()
