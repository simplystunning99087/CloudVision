
 !pip install flask ultralytics cloudinary opencv-python-headles
# 2. CLOUDFLARE TUNNEL (Run this to get your URL)
# !wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
# !chmod +x cloudflared-linux-amd64
# !nohup ./cloudflared-linux-amd64 tunnel --url http://localhost:5000 > cloudflare.log 2>&1 &
# !sleep 5
# !grep -o 'https://[^ ]*\.trycloudflare\.com' cloudflare.log

import cloudinary
import cloudinary.uploader
import threading
import time
from flask import Flask, request, jsonify
import cv2
import numpy as np
import os
from datetime import datetime
from ultralytics import YOLO
current_alarm_status = "IDLE" 
last_violation_time = 0
app = Flask(__name__)
cloudinary.config(
  cloud_name = "duu0e7ylg",
  api_key = "YOUR_API_KEY",
  api_secret = "YOUR_API_SECRET",
  secure = True
)
print("Loading YOLO model...")
model = YOLO("best.pt")
def background_upload(temp_path, date_str, time_exact):
    try:
        cloudinary.uploader.upload(
            temp_path, folder="Safety_Violations",
            tags=["violation", "cloud_inference"],
            context=f"date={date_str}|time={time_exact}|type=Violation"
        )
        os.remove(temp_path)
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")

@app.route('/')
def home():
    return "Brain Server is Online via Cloudflare"
@app.route('/status', methods=['GET'])
def get_status():
    global current_alarm_status
    return jsonify({"status": current_alarm_status})
@app.route('/analyze', methods=['POST'])
def analyze_frame():
    global current_alarm_status, last_violation_time

    file_bytes = request.get_data()
    if len(file_bytes) == 0:
        return jsonify({"status": current_alarm_status})

    npimg = np.frombuffer(file_bytes, np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"status": current_alarm_status})

    
    results = model(frame, imgsz=640, conf=0.50, verbose=False)
    annotated_frame = results[0].plot()

    violation_seen = False
    helmet_seen = False

    for r in results:
        for box in r.boxes:
            name = model.names[int(box.cls[0])].lower()
            if "nhelmet" in name or "no-" in name:
                violation_seen = True
            elif "helmet" in name:
                helmet_seen = True 

    current_time = time.time()

    if violation_seen:
        print(f"🚨 [{datetime.now().strftime('%H:%M:%S')}] VIOLATION DETECTED!")
        last_violation_time = current_time
        current_alarm_status = "VIOLATION"

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_exact = now.strftime("%H-%M-%S-%f")
        temp_path = f"temp_{time_exact}.jpg"
        cv2.imwrite(temp_path, annotated_frame)
        threading.Thread(target=background_upload, args=(temp_path, date_str, time_exact)).start()

    else:
        if (current_time - last_violation_time) > 5.0:
            if helmet_seen:
                print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] SAFE")
                current_alarm_status = "SAFE"
            else:
                current_alarm_status = "IDLE"
        else:
            current_alarm_status = "VIOLATION"

    return jsonify({"status": current_alarm_status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
