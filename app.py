from distutils.log import debug
import math
import random
from turtle import color
import cvzone
import cv2
from django.shortcuts import redirect
from matplotlib import scale
import numpy as np
from cvzone.HandTrackingModule import HandDetector

from flask import Flask,render_template,Response,url_for

app=Flask(__name__)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

gameOve = False

detector = HandDetector(detectionCon=0.8, maxHands=1)


# @app.route('/stats')
# def stats():
#     return render_template('stats.html')

# with app.app_context(), app.test_request_context():
#     url = url_for('stats', page_number=2)
global k
k=1


 
class SnakeGameClass:
    def __init__(self, pathFood):
        self.points = []  # all points of the snake
        self.lengths = []  # distance between each point
        self.currentLength = 0  # total length of the snake
        self.allowedLength = 150  # total allowed Length
        self.previousHead = 0, 0  # previous head point
 
        self.imgFood = cv2.imread(pathFood, cv2.IMREAD_UNCHANGED)
        self.hFood, self.wFood, _ = self.imgFood.shape
        self.foodPoint = 0, 0
        self.randomFoodLocation()
 
        self.score = 0
        self.gameOver = False
 
    def randomFoodLocation(self):
        self.foodPoint = random.randint(100, 1000), random.randint(100, 600)
 
    def update(self, imgMain, currentHead):
 
        if self.gameOver:
            cvzone.putTextRect(imgMain, "Game Over", [300, 100],
                               scale=7, thickness=5, offset=20)
            cvzone.putTextRect(imgMain, f'Your Score: {self.score}', [300, 250],
                               scale=7, thickness=5, offset=20)
        
            cvzone.putTextRect(imgMain, f'To replay, press Ctrl+R', [300, 400],
                               scale=2, thickness=2, offset=20)
            # gameOve=True
            
            # l=[1,1,1]
            # return l

            # @app.route('/video')
            # def lose():
            #     return render_template('welcome.html')
        else:
            px, py = self.previousHead
            cx, cy = currentHead
 
            self.points.append([cx, cy])
            distance = math.hypot(cx - px, cy - py)
            self.lengths.append(distance)
            self.currentLength += distance
            self.previousHead = cx, cy
 
            # Length Reduction
            if self.currentLength > self.allowedLength:
                for i, length in enumerate(self.lengths):
                    self.currentLength -= length
                    self.lengths.pop(i)
                    self.points.pop(i)
                    if self.currentLength < self.allowedLength:
                        break
 
            # Check if snake ate the Food
            rx, ry = self.foodPoint
            if rx - self.wFood // 2 < cx < rx + self.wFood // 2 and \
                    ry - self.hFood // 2 < cy < ry + self.hFood // 2:
                self.randomFoodLocation()
                self.allowedLength += 50
                self.score += 1
                print(self.score)
 
            # Draw Snake
            if self.points:
                for i, point in enumerate(self.points):
                    if i != 0:
                        cv2.line(imgMain, self.points[i - 1], self.points[i], (0, 0, 255), 20)
                cv2.circle(imgMain, self.points[-1], 20, (0, 255, 0), cv2.FILLED)
 
            # Draw Food

            imgMain = cvzone.overlayPNG(imgMain, self.imgFood,
                                        (rx - self.wFood // 2, ry - self.hFood // 2))

 
            cvzone.putTextRect(imgMain, f'Score: {self.score}', [50, 80],
                               scale=3, thickness=3, offset=10)
            cvzone.putTextRect(imgMain,"Remember! if you decrease speed you lose",[20,20],scale=1,thickness=1,offset=15)
            global k
            # if(self.score>1*k):

            #     cvzone.putTextRect(imgMain,f"Congrats, you passed level {k}",[50,100],
            #                     scale=1,thickness=1,offset=100)
            #     k=k+1
            
            
            # Check for Collision
            pts = np.array(self.points[:-2], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(imgMain, [pts], False, (0, 255, 0), 3)
            minDist = cv2.pointPolygonTest(pts, (cx, cy), True)
 
            if -1 <= minDist <= 1:
                print("Hit")
                self.gameOver = True
                self.points = []  # all points of the snake
                self.lengths = []  # distance between each point
                self.currentLength = 0  # total length of the snake
                self.allowedLength = 150  # total allowed Length
                self.previousHead = 0, 0  # previous head point
                self.randomFoodLocation()
 
        return imgMain

def generate():
    game = SnakeGameClass("Donut.png")  #game is an object of class SnakeGameClass
    print(game)
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)  #0 for vertical
        hands, img = detector.findHands(img, flipType=False)
        # cv2.imshow("Image",img)
        # cv2.waitKey(1)

        if hands:
            lmList = hands[0]['lmList']
            pointIndex = lmList[8][0:2]
            cv2.circle(img,pointIndex,20, (200,0,200), cv2.FILLED)
            img = game.update(img, pointIndex)
        
        # l=[1,1,1]
        # if len(img)==3:
        #     print("out of class")
            # if gameOve==True:
            
            # return redirect(url_for('stats'))
            # break
        # else:
        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        # if key == ord('r'):
        #     game.gameOver = False
        ret,buffer=cv2.imencode('.jpg',img)
        img=buffer.tobytes()
        
        yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')

@app.route('/')
def homepage():
    return render_template('welcome.html')

#####################################################################

@app.route('/video')
def video():
    return Response(generate(),mimetype='multipart/x-mixed-replace; boundary=frame')

# if gameOve==True:
#     @app.route('/stats')
#     def stats():
#         return render_template('stats.html')


if __name__=="__main__":
    app.run(debug=True)