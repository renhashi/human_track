from collections import defaultdict
import signal
import serial
import time
import datetime
import cv2
import numpy as np
import serialcount
from ultralytics import YOLO
from ultralytics.trackers import basetrack
import setlog

# Load the YOLOv8 model
model = YOLO("yolo11n.pt")
logger = setlog.set_logfile()

# Open the video file
video_path = "sample2.mp4"
#cap = cv2.VideoCapture(video_path)
cap = cv2.VideoCapture(0)

serial_port = None
SAVE_DATA = False                       #動画ファイルの出力をするかいなか
INTERVAL = 60                           #シグナルを起動させるインターバル(秒)
timeup = False
ID_RESET = True

#定期的にシリアル通信させるトリガー
def task(signum, frame):
	global timeup
	timeup = True

def reset_id(tracker, track_history):
	tracker.reset_id()
	track_history.clear()
	print("ID Reset")
		
def main():
    global cap
    global timeup
    
    logger.info("PROGRAM START")

    startday = datetime.datetime.now()
    reset_time = startday.day
    reset_check = reset_time

    #フレームの幅
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    # フレームの高さ
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    #create lines
    print(width)
    print(height)
    set_linex1 = int(width/3)
    set_linex2 = int(width/3*2)
    set_liney1 = int(height/3)
    set_liney2 = int(height/3*2)
    
    #send numbers
    to_right = 0
    to_left = 0
    to_upper = 0
    to_lower = 0
    stay_num_Ri = 0
    stay_num_Up = 0
    reset_count_lr = 0
    reset_count_ud = 0

    serialcount.serial_open()
    signal.signal(signal.SIGALRM, task)     #指定時間にtaskを実行する
    signal.setitimer(signal.ITIMER_REAL, 10, INTERVAL)  #signal.setitimer(signal.ITIMER_REAL, 1回目の実行までの時間, 2回目以降の実行間隔)
    tracker = basetrack.BaseTrack()

    # Store the track history
    track_history = defaultdict(lambda: [])
    count_checer_lr = defaultdict(lambda: [])
    count_checer_ud = defaultdict(lambda: [])

    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()

        if success:
            # Run YOLOv8 tracking on the frame, persisting tracks between frames
            results = model.track(frame, persist=True, classes=[0],verbose=False)

            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            #画面になにも写ってなかったら処理を飛ばす
            ids = results[0].boxes.id
            if ids != None:
                # Get the boxes and track IDs
                boxes = results[0].boxes.xywh.cpu()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                # Plot the tracks
                for box, track_id in zip(boxes, track_ids):
                    x, y, w, h = box
                    track = track_history[track_id]
                    count_lr = count_checer_lr[track_id]
                    count_ud = count_checer_ud[track_id]
                    if len(track) == 0:
                        x_b, y_b = x, y
                    else:
                        x_b, y_b = track[-1]
                    track.append((float(x), float(y)))  # x, y center point
                    if len(track) > 30:  # retain 90 tracks for 90 frames
                        track.pop(0)

                    #横のライン通過判定
                    if x < set_linex2 and set_linex2 < x_b:
                        count_lr.append('le')
                    elif x < set_linex1 and set_linex1 < x_b:
                        count_lr.append('ft')
                    elif x > set_linex1 and set_linex1 > x_b:
                        count_lr.append('ri')
                    elif x > set_linex2 and set_linex2 > x_b:
                        count_lr.append('ght')

                    #2ラインの関係性確認
                    if len(count_lr) > 1:  # retain 90 tracks for 90 frames
                        print(count_lr[0]+count_lr[1])
                        dir = str(count_lr[0]+count_lr[1])
                        if dir == 'right':
                            to_right += 1
                            stay_num_Ri -= 1
                        elif dir == 'left':
                            to_left += 1
                            stay_num_Ri += 1
                        count_lr.pop(0)

                    #縦のライン通過判定
                    if y < set_liney2 and set_liney2 < y_b:
                        count_ud.append('u')
                    elif y < set_liney1 and set_liney1 < y_b:
                        count_ud.append('pp')
                    elif y > set_liney1 and set_liney1 > y_b:
                        count_ud.append('do')
                    elif y > set_liney2 and set_liney2 > y_b:
                        count_ud.append('wn')

                    #2ラインの関係性確認
                    if len(count_ud) > 1:  # retain 90 tracks for 90 frames
                        print(count_ud[0]+count_ud[1])
                        dir = str(count_ud[0]+count_ud[1])
                        if dir == 'upp':
                            to_upper += 1
                            stay_num_Up += 1
                        elif dir == 'down':
                            to_lower += 1
                            stay_num_Up -= 1
                        count_ud.pop(0)

                    # Draw the tracking lines
                    points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                    cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

            #N秒毎に人数を送信する
            if timeup:
                timeup = False
                now = datetime.datetime.now()
                print(now)
                reset_check = now.day
                print("Right-flow is {}".format(to_right))
                print("Left-flow is {}".format(to_left))
                print("Up-flow is {}".format(to_upper))
                print("Down-flow is {}".format(to_lower))
	
		#kari no minus taisaku
                if stay_num_Ri < 0 :
                    stay_num_Ri = 0
                    reset_count_lr += 1
                    print("!!!!!!!!!!!1RESET STAY NUM!!!!!!!!!!1!!!")

                if stay_num_Up < 0 :
                    stay_num_Up = 0
                    reset_count_ud += 1
                    print("!!!!!!!!!!!1RESET STAY NUM!!!!!!!!!!1!!!")
                    
                logger.info("Right:" + str(to_right) + ", Left:" + str(to_left) + ", Up:" + str(to_upper) + ", Down:" + str(to_lower))

                serialcount.serial_send_4data(to_right, to_left, to_upper, to_lower)
                to_right = 0
                to_left = 0
                to_upper = 0
                to_lower = 0

            if ID_RESET and reset_check != reset_time:
                reset_id(tracker, track_history)
                reset_time = reset_check
                logger.info("ID Reset")

            #print("------------------------------------------------------")

            #ラインの描写
            cv2.line(annotated_frame,(set_linex1, 0),(set_linex1, int(height)),(255,0, 0),5)
            cv2.line(annotated_frame,(set_linex2, 0),(set_linex2, int(height)),(255,0, 0),5)
            cv2.line(annotated_frame,(0, set_liney1),(int(width), set_liney1),(0,255, 0),5)
            cv2.line(annotated_frame,(0, set_liney2),(int(width), set_liney2),(0,255, 0),5)
            #通過人数の描写
            cv2.putText(annotated_frame, 'right:'+str(to_right), (0, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(annotated_frame, 'left:'+str(to_left), (0, 60), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(annotated_frame, 'stay RL:'+str(stay_num_Ri), (0, 90), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(annotated_frame, 'up:'+str(to_upper), (0, 120), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(annotated_frame, 'down:'+str(to_lower), (0, 150), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(annotated_frame, 'stay UL:'+str(stay_num_Up), (0, 180), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2, cv2.LINE_AA)
            
            # Display the annotated frame
            cv2.imshow("YOLO11 Tracking", annotated_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            print("not opend")
            logger.warning("do not get camera")
            #break
            
    logger.info("PROGRAM END")

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
