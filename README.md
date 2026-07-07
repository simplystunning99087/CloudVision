Cloud-to-Edge AI Safety System (ESP32(Microcontroller&CAM + YOLOv8)
📌 Overview
This project is a distributed Internet of Things (IoT) architecture designed to monitor safety compliance (e.g., helmet/seatbelt detection) in real-time. It bridges physical edge microcontrollers with a cloud-based AI inference engine using secure tunneling protocols. 

Instead of running heavy AI models on weak microcontrollers, this architecture leverages a **Python Flask "Brain Server"** running YOLO object detection in the cloud, while decentralized **ESP32 Edge Nodes** handle data collection and physical alarm triggering.

🏗️ System Architecture
The system is divided into three distinct functional nodes:

1. The Vision Node (ESP32-CAM):Captures physical environment data and streams raw frames via `POST` requests to the cloud server.
2. The Brain Server (Python/Flask + YOLOv8): A cloud-hosted environment (Google Colab/Kaggle Notebook) that processes incoming frames, runs AI inference to detect safety violations, uploads photographic evidence to Cloudinary, and updates a global state machine.
3. The Control Node (ESP32-S3): A decentralized alarm node that continuously polls the Brain Server's API via `GET` requests to fetch the current system state, triggering physical hardware alarms when a violation is detected.
🚀 Setup & Deployment
1. Cloud Environment: Run the Python script in Google Colab or a local environment with a GPU. Ensure `flask`, `ultralytics`, and `cloudinary` are installed.
2. Network Tunnel: Use Ngrok or Cloudflare to expose local port `5000` to the public web.
3. Hardware Config: Update the `ssid`, `password`, and dynamic `serverName` URL in the `.ino` files before flashing to the ESP32 boards.
4. API Keys: You will need to provide your own Cloudinary API credentials in the server code to handle image storage.

Further Improvements:
Automated Cloud Workspace Management: Engineered a custom Google Colab initialization script that actively manages the cloud file system, preventing phantom memory issues by wiping legacy weights before new model injections.
Frictionless Model Swapping: Developed a smart upload utility that intercepts user-uploaded YOLO .pt files, automatically standardizing the naming convention (best.pt) required by the Flask server, removing the need for manual file manipulation.
Built-in Integrity Checks: The script automatically calculates and verifies the final file size post-upload, providing immediate terminal feedback to ensure the model wasn't corrupted or truncated during the cloud transfer.

 🔮 Future Improvements
* Implement logic-level shifters (5V to 3.3V) on the hardware integration layer to prevent future over-voltage casualties.
* Migrate the YOLO inference directly to an Edge TPU (like a Coral Accelerator) to reduce cloud latency.
