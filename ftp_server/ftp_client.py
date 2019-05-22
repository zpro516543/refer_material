"""
    协议
    L 表示请求文件列表
    Q 表示退出
    G 表示下载
"""
from socket import *
import sys
from time import sleep


# 具体功能
class FtpClient:
    def __init__(self, sockfd):
        self.sockfd = sockfd

    def do_list(self):
        self.sockfd.send(b"L")  # 发送请求
        # 等待回复
        data = self.sockfd.recv(128).decode()
        # OK表示请求成功
        if data == "OK":
            # 接收文件列表
            data = self.sockfd.recv(4096)
            print(data.decode())
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b"Q")
        self.sockfd.close()
        sys.exit("谢谢使用")

    def do_get(self, filename):
        # 发送请求
        self.sockfd.send(("G " + filename).encode())
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            fd = open(filename, "wb")
            # 接收内容写入文件
            while True:
                message = self.sockfd.recv(1024)
                if message == b"##":
                    break
                fd.write(message)
            fd.close()
        else:
            print(data)

    def do_put(self, filename):
        try:
            fd = open(filename, "rb")
        except Exception:
            print("没有该文件")
            return
        filename = filename.split("/")[-1]
        self.sockfd.send(("P " + filename).encode())
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            while True:
                content = fd.read(1024)
                if not content:
                    sleep(0.1)
                    self.sockfd.send(b"##")
                    break
                self.sockfd.send(content)
            fd.close()
        else:
            print(data)


def request(sockfd):
    """
        发起请求
    """
    ftp = FtpClient(sockfd)

    while True:
        print("\n===========命令选项===========")
        print("*********** list ***********")
        print("*********** get file ***********")
        print("*********** put file ***********")
        print("*********** quit ***********")
        print("==============================")

        cmd = input("输入命令:")
        if cmd.strip() == "list":
            ftp.do_list()
        elif cmd.strip() == "quit":
            ftp.do_quit()
        elif cmd[:3] == "get":
            filename = cmd.strip().split(" ")[-1]
            ftp.do_get(filename)
        elif cmd[:3] == "put":
            filename = cmd.strip().split(" ")[-1]
            ftp.do_put(filename)


# 网络连接
def main():
    # 服务器地址
    ADDR = ("127.0.0.1", 8080)
    # ADDR = ("176.122.17.94", 8080)
    sockfd = socket()
    try:
        sockfd.connect(ADDR)
    except Exception:
        print("连接服务器失败")
        return
    else:
        print("""
                ********************
                Data    File    Image
                ********************
        """)
        cls = input("请选择文件种类:")
        if cls not in ["Data", "File", "Image"]:
            print("Sorry input Error!")
            return
        else:
            sockfd.send(cls.encode())
            request(sockfd)  # 发送具体请求

if __name__== "__main__":
    main()
