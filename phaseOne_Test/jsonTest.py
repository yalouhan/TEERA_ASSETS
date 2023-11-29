import socket
import threading
import struct
import json

conn = None
file_lock = threading.Lock()
received_data = []

def tcp_server():
    global conn
    global server_sock
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('0.0.0.0', 12345))
    server_sock.listen(1)
    conn, addr = server_sock.accept()

    print("begin sent to ESP32")

    with open('received_data.json', 'a') as json_file:
        while True:
            data = conn.recv(10000)
            if not data:
                break
            with file_lock:
                received_data.extend(struct.unpack(f'{len(data)//4}i', data))
        json.dump(received_data, json_file)

    conn.close()
    server_sock.close()

def keyboard_input():
    global conn
    preset_key = "Han935779084!?"
    user_input = input("Please input your password: ")

    label = 'True' if user_input == preset_key else 'False'
   
    with file_lock:
        received_data.append(label)

    # conn.sendall(b'end')
    # print("end sent to ESP32")
    conn.close()
    server_sock.close()

# 创建并启动线程
thread_server = threading.Thread(target=tcp_server)
thread_input = threading.Thread(target=keyboard_input)

thread_server.start()
thread_input.start()

thread_server.join()
thread_input.join()
