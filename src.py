import numpy as np
import cv2
import tensorflow as tf
from ultralytics import YOLO

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_EXPOSURE, -2)
cap.set(cv2.CAP_PROP_FPS, 120)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


if not cap.isOpened():
    print("err in cam")
    exit()

# SETTING UP YOLOV8 MODE (MY GPU CANT TAKE THIS SHI BUT IDCCCCC LESGOOOOOOOOOOOO)

print("yolo loading")
model = YOLO('yolov8n.pt') # yolov8n is nano pre-trained model of yolo 
if not model:
    print('model not loaded')

frame_count = 0
detection_frequency = 5
last_detections = None

print("press q to exit")

while True:
    # TO READ THE FRAMES

    ret, frame = cap.read()

    if not ret:
        print("err in frame reading")
        break
    
    ##############################

    # TO SHOW CAM FEED

    frame_count += 1

    flipped_frame = cv2.flip(frame, 1)

    if frame_count % detection_frequency == 0:
        results = model(flipped_frame)
        last_detections = results

        #degub
        if results and len(results) > 0:
            print(f"Frame {frame_count}: Detected {len(results[0].boxes) if results[0].boxes is not None else 0} objects")
            if results[0].boxes is not None:
                for i, box in enumerate(results[0].boxes):
                    cls = box.cls[0]
                    conf = box.conf[0]
                    print(f"Object {i}: {results[0].names[int(cls)]} (confidence: {conf:.2f})")
        
        else:
            print(f"Frame {frame_count}: No results")

    else:
        results = last_detections

    if results is not None and len(results) > 0:
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    conf = float(box.conf[0])

                    if (conf > 0.6):
                        
                        coords = box.xyxy[0].cpu().numpy()
                        x1,y1,x2,y2 = map(int, coords)
                        conf = float(box.conf[0])
                        cls = int (box.cls[0])
                        label = f"{result.names[int(cls)]}{conf:.2f}"

                        #degub
                        if frame_count % detection_frequency == 0:
                            print(f"Drawing box ({x1}, {x2}) to ({y1}, {y2}) - {label}")

                        cv2.rectangle(flipped_frame, (x1, y1), (x2,y2), (0,255,255), 3)

                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.7
                        thickness = 2
                        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)

                        cv2.rectangle(flipped_frame,
                                      (x1, y1 - text_height - 10),
                                      (x1 + text_width, y1),
                                      (0, 0, 0), -1)
                        
                        cv2.putText(flipped_frame, label,
                                    (x1, y1 - 5),
                                    font, font_scale, (255, 255, 255), thickness)

    cv2.imshow('cam feed', flipped_frame)
    ##############################

    # TO CHECK FOR INPUTS

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # CHECK IF CROSS BUTTON IS PRESSED ON WINDOW
    if cv2.getWindowProperty('cam feed', cv2.WND_PROP_VISIBLE) < 1:
        break

    ##############################

# CLEAN RESOURCES

cap.release()
cv2.destroyAllWindows()

##############################
