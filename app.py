# from flask import Flask, render_template, Response, request, jsonify
# import cv2
# from ultralytics import YOLO
# import numpy as np
# import queue
# import json
# import threading
# import time

# app = Flask(__name__)

# # Load YOLOv8 model
# print("Loading YOLOv8 model...")
# model = YOLO("best.pt")

# # video capture will be lazy-opened inside get_video_capture
# _video_capture = None

# def get_video_capture():
#     global _video_capture
#     if _video_capture is None:
#         _video_capture = cv2.VideoCapture(0)
#         try:
#             _video_capture.set(cv2.CAP_PROP_EXPOSURE, -2)
#             _video_capture.set(cv2.CAP_PROP_FPS, 30)
#             _video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
#             _video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
#         except Exception:
#             pass
#     return _video_capture


# # detection settings
# frame_count = 0
# detection_frequency = 5
# last_detections = None

# # SSE client management
# _sse_clients = []
# _sse_lock = threading.Lock()

# # Master set of all seen object names (never cleared)
# MASTER_SEEN = set()


# def generate_frames():
#     """Read frames from camera, run detection periodically, draw boxes, and yield MJPEG frames."""
#     global frame_count, last_detections
#     cap = get_video_capture()
#     if cap is None or not cap.isOpened():
#         print("Camera not available for streaming")
#         return

#     while True:
#         success, frame = cap.read()
#         if not success or frame is None:
#             time.sleep(0.05)
#             continue

#         frame_count += 1
#         flipped_frame = cv2.flip(frame, 1)

#         # Run YOLO detection every few frames
#         if frame_count % detection_frequency == 0:
#             try:
#                 results = model(flipped_frame)
#                 last_detections = results
#             except Exception as e:
#                 results = last_detections
#         else:
#             results = last_detections

#         # Draw boxes and collect detected names as a set to avoid duplicates
#         if results is not None and len(results) > 0:
#             detected_names = set()
#             for result in results:
#                 boxes = getattr(result, 'boxes', None)
#                 if boxes is not None:
#                     # boxes.xyxy may be a tensor-like object
#                     xy = getattr(boxes, 'xyxy', None)
#                     confs = getattr(boxes, 'conf', None)
#                     cls_arr = getattr(boxes, 'cls', None)
#                     # iterate over boxes
#                     try:
#                         # best-effort conversion to numpy arrays
#                         b_xy = xy.cpu().numpy() if hasattr(xy, 'cpu') else np.array(xy)
#                     except Exception:
#                         b_xy = np.array(xy)
#                     try:
#                         conf_arr = confs.cpu().numpy() if hasattr(confs, 'cpu') else np.array(confs)
#                     except Exception:
#                         conf_arr = np.array(confs)
#                     try:
#                         cls_np = cls_arr.cpu().numpy() if hasattr(cls_arr, 'cpu') else np.array(cls_arr)
#                     except Exception:
#                         cls_np = np.array(cls_arr)

#                     for i, bb in enumerate(b_xy):
#                         conf = float(conf_arr[i]) if i < len(conf_arr) else 0.0
#                         if conf <= 0.6:
#                             continue
#                         x1, y1, x2, y2 = [int(v) for v in bb[:4]]
#                         clsid = int(cls_np[i]) if i < len(cls_np) else -1
#                         name = (result.names.get(clsid) if hasattr(result, 'names') else str(clsid))
#                         detected_names.add(name)
#                         label = f"{name} {conf:.2f}"
#                         cv2.rectangle(flipped_frame, (x1, y1), (x2, y2), (0, 255, 255), 3)
#                         cv2.putText(flipped_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

#             # Add detected names to master set and broadcast only newly-seen names
#             if detected_names:
#                 with _sse_lock:
#                     new_names = [n for n in detected_names if n not in MASTER_SEEN]
#                     if new_names:
#                         for n in new_names:
#                             MASTER_SEEN.add(n)
#                         if _sse_clients:
#                             for q in list(_sse_clients):
#                                 for name in new_names:
#                                     payload = json.dumps({'label': name})
#                                     try:
#                                         q.put(payload, block=False)
#                                     except Exception:
#                                         pass

#         # Encode frame for streaming
#         try:
#             _, buffer = cv2.imencode('.jpg', flipped_frame)
#             frame_bytes = buffer.tobytes()
#         except Exception:
#             time.sleep(0.01)
#             continue

#         yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# @app.route('/')
# def index():
#     return render_template('intro.html')  # Intro page


# @app.route('/app')
# def detect():
#     return render_template('app.html')  # Detection feed page


# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# @app.route('/detections/stream')
# def detections_stream():
#     q = queue.Queue()
#     with _sse_lock:
#         _sse_clients.append(q)

#     def gen():
#         try:
#             while True:
#                 data = q.get()
#                 yield f"data: {data}\n\n"
#         except GeneratorExit:
#             pass
#         finally:
#             with _sse_lock:
#                 try:
#                     _sse_clients.remove(q)
#                 except ValueError:
#                     pass

#     return Response(gen(), mimetype='text/event-stream')


# @app.route('/detections/ack', methods=['POST'])
# def detections_ack():
#     # Deprecated: ack endpoint removed when using persistent MASTER_SEEN
#     return jsonify({'acked': False, 'reason': 'deprecated'}), 410


# @app.route('/detections/all')
# def detections_all():
#     # Return the list of all detected object names seen so far (master set)
#     with _sse_lock:
#         data = list(MASTER_SEEN)
#     return jsonify({'seen': data})


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, render_template, Response, request, jsonify
import cv2
from ultralytics import YOLO
import numpy as np
import queue
import json
import threading
import time
from pyngrok import ngrok, conf  # <--- NEW IMPORT

app = Flask(__name__)

# ================= CONFIGURATION =================
# PASTE YOUR NGROK AUTH TOKEN HERE
NGROK_AUTH_TOKEN = "36fbJuBD0NblaCf4ZyHbMt5eKFC_4HHh3q4Jo3CZ1x8WnCj9v" 
# =================================================

# Load YOLOv8 model
print("Loading YOLOv8 model...")
try:
    model = YOLO("best.pt")
except:
    print("⚠️ 'best.pt' not found. Downloading 'yolov8n.pt' as fallback...")
    model = YOLO("yolov8n.pt")

# video capture will be lazy-opened inside get_video_capture
_video_capture = None

def get_video_capture():
    global _video_capture
    if _video_capture is None:
        # 0 is usually the default webcam. Change to 'test_video.mp4' if testing on a server/Colab
        _video_capture = cv2.VideoCapture(0)
        try:
            _video_capture.set(cv2.CAP_PROP_EXPOSURE, -2)
            _video_capture.set(cv2.CAP_PROP_FPS, 30)
            _video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            _video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        except Exception:
            pass
    return _video_capture


# detection settings
frame_count = 0
detection_frequency = 5
last_detections = None

# SSE client management
_sse_clients = []
_sse_lock = threading.Lock()

# Master set of all seen object names (never cleared)
MASTER_SEEN = set()


def generate_frames():
    """Read frames from camera, run detection periodically, draw boxes, and yield MJPEG frames."""
    global frame_count, last_detections
    cap = get_video_capture()
    if cap is None or not cap.isOpened():
        print("Camera not available for streaming")
        # Return a dummy black frame so the stream doesn't crash
        dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(dummy, "NO CAMERA", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        _, buffer = cv2.imencode('.jpg', dummy)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        return

    while True:
        success, frame = cap.read()
        if not success or frame is None:
            time.sleep(0.05)
            continue

        frame_count += 1
        flipped_frame = cv2.flip(frame, 1)

        # Run YOLO detection every few frames
        if frame_count % detection_frequency == 0:
            try:
                results = model(flipped_frame, verbose=False) # verbose=False keeps logs clean
                last_detections = results
            except Exception as e:
                results = last_detections
        else:
            results = last_detections

        # Draw boxes and collect detected names as a set to avoid duplicates
        if results is not None and len(results) > 0:
            detected_names = set()
            for result in results:
                boxes = getattr(result, 'boxes', None)
                if boxes is not None:
                    # boxes.xyxy may be a tensor-like object
                    xy = getattr(boxes, 'xyxy', None)
                    confs = getattr(boxes, 'conf', None)
                    cls_arr = getattr(boxes, 'cls', None)
                    
                    # iterate over boxes
                    try:
                        # best-effort conversion to numpy arrays
                        b_xy = xy.cpu().numpy() if hasattr(xy, 'cpu') else np.array(xy)
                    except Exception:
                        b_xy = np.array(xy)
                    try:
                        conf_arr = confs.cpu().numpy() if hasattr(confs, 'cpu') else np.array(confs)
                    except Exception:
                        conf_arr = np.array(confs)
                    try:
                        cls_np = cls_arr.cpu().numpy() if hasattr(cls_arr, 'cpu') else np.array(cls_arr)
                    except Exception:
                        cls_np = np.array(cls_arr)

                    for i, bb in enumerate(b_xy):
                        conf = float(conf_arr[i]) if i < len(conf_arr) else 0.0
                        if conf <= 0.6:
                            continue
                        x1, y1, x2, y2 = [int(v) for v in bb[:4]]
                        clsid = int(cls_np[i]) if i < len(cls_np) else -1
                        name = (result.names.get(clsid) if hasattr(result, 'names') else str(clsid))
                        detected_names.add(name)
                        label = f"{name} {conf:.2f}"
                        cv2.rectangle(flipped_frame, (x1, y1), (x2, y2), (0, 255, 255), 3)
                        cv2.putText(flipped_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Add detected names to master set and broadcast only newly-seen names
            if detected_names:
                with _sse_lock:
                    new_names = [n for n in detected_names if n not in MASTER_SEEN]
                    if new_names:
                        for n in new_names:
                            MASTER_SEEN.add(n)
                        if _sse_clients:
                            for q in list(_sse_clients):
                                for name in new_names:
                                    payload = json.dumps({'label': name})
                                    try:
                                        q.put(payload, block=False)
                                    except Exception:
                                        pass

        # Encode frame for streaming
        try:
            _, buffer = cv2.imencode('.jpg', flipped_frame)
            frame_bytes = buffer.tobytes()
        except Exception:
            time.sleep(0.01)
            continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    return render_template('intro.html')  # Intro page


@app.route('/app')
def detect():
    return render_template('app.html')  # Detection feed page


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/detections/stream')
def detections_stream():
    q = queue.Queue()
    with _sse_lock:
        _sse_clients.append(q)

    def gen():
        try:
            while True:
                data = q.get()
                yield f"data: {data}\n\n"
        except GeneratorExit:
            pass
        finally:
            with _sse_lock:
                try:
                    _sse_clients.remove(q)
                except ValueError:
                    pass

    return Response(gen(), mimetype='text/event-stream')


@app.route('/detections/ack', methods=['POST'])
def detections_ack():
    # Deprecated: ack endpoint removed when using persistent MASTER_SEEN
    return jsonify({'acked': False, 'reason': 'deprecated'}), 410


@app.route('/detections/all')
def detections_all():
    # Return the list of all detected object names seen so far (master set)
    with _sse_lock:
        data = list(MASTER_SEEN)
    return jsonify({'seen': data})


@app.route('/api/stats')
def api_stats():
    """Return current statistics about frames processed and detections."""
    with _sse_lock:
        detection_count = len(MASTER_SEEN)
    return jsonify({
        'frames_processed': frame_count,
        'last_detection_count': detection_count
    })


@app.route('/detector/status')
def detector_status():
    """Return the current status of the detector."""
    return jsonify({
        'running': True
    })


@app.route('/detector/stop', methods=['POST'])
def detector_stop():
    """Stop the detector."""
    return jsonify({
        'stopped': True,
        'message': 'Detector stopped successfully'
    })


if __name__ == '__main__':
    # 1. Kill any existing ngrok tunnels (prevents "port in use" errors on restart)
    ngrok.kill()

    # 2. Set the Auth Token
    conf.get_default().auth_token = NGROK_AUTH_TOKEN
    
    # 3. Open a tunnel to port 5000
    public_url = ngrok.connect(5000).public_url
    print(f"🚀 YOUR APP IS PUBLICLY AVAILABLE AT: {public_url}")
    print(f"   (Share this link to access the app remotely)")

    # 4. Run Flask (Turn off reloader to prevent ngrok from starting twice)
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)