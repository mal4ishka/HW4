import socket


def echo_server(host, port):
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                print(f'From client: {data}')
                if not data:
                    break
                conn.send(data.upper())


if __name__ == '__main__':
    main()
