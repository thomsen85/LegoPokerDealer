import cv2

class Webcamera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)  
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            return (ret, frame)
        else:
            return None

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()