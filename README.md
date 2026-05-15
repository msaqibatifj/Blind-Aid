# 👁️ Blind Aid — Vision Assist Technology

**Blind Aid** is an AI-powered real-time object detection web application designed to empower visually impaired users with greater independence. It uses a custom-trained YOLOv8 model to detect people, animals, and everyday objects through a live webcam feed, displaying bounding boxes and broadcasting detection events in real time.

---

## ✨ Features

- **Real-time Object Detection** — Detects objects every 5 frames using a custom YOLOv8 model (`best.pt`), with YOLOv8n as automatic fallback.
- **Live Video Streaming** — Streams the annotated webcam feed as MJPEG directly in the browser.
- **Server-Sent Events (SSE)** — Pushes newly detected object names to all connected clients instantly.
- **Detection Statistics** — REST endpoints expose frame counts and detection totals.
- **ngrok Tunnel** — Optionally exposes the local server publicly via ngrok for remote access or demos.
- **Vercel-ready** — Includes `vercel.json` for straightforward cloud deployment.

---

## 🗂️ Project Structure

```
Blind-Aid/
├── app.py              # Flask backend — video streaming, detection, API routes
├── best.pt             # Custom-trained YOLOv8 weights (primary model)
├── last.pt             # Checkpoint weights from last training epoch
├── yolov8n.pt          # YOLOv8 nano weights (fallback model)
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel deployment config
├── templates/
│   ├── intro.html      # Landing / intro page
│   └── app.html        # Live detection feed page
└── static/
    ├── css/
    │   └── style.css   # Application styles
    └── js/
        ├── intro.js    # Intro page scroll interactions
        └── app.js      # Detection feed logic (SSE, stats polling)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A webcam connected to the host machine
- *(Optional)* An [ngrok](https://ngrok.com/) account and auth token for remote access

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/msaqibatifj/Blind-Aid.git
   cd Blind-Aid
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

### Running the App

```bash
python app.py
```

Open your browser and navigate to `http://localhost:5000`.

> **Note:** If `best.pt` is not found, the app automatically downloads and uses `yolov8n.pt` as a fallback.

### Using ngrok (optional)

To expose the app publicly, paste your ngrok auth token into `app.py`:

```python
NGROK_AUTH_TOKEN = "your_ngrok_token_here"
```

When `python app.py` is run directly, ngrok will start automatically and print the public URL.

---

## 🌐 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/` | Intro / landing page |
| `GET` | `/app` | Live detection feed page |
| `GET` | `/video_feed` | MJPEG video stream with bounding boxes |
| `GET` | `/detections/stream` | SSE stream of newly detected object names |
| `GET` | `/detections/all` | JSON list of all object names seen in this session |
| `GET` | `/api/stats` | JSON stats: frames processed and detection count |
| `GET` | `/detector/status` | JSON detector running status |
| `POST` | `/detector/stop` | Stop the detector |

---

## ⚙️ Detection Settings

| Parameter | Value | Description |
|-----------|-------|-------------|
| Confidence threshold | `0.6` | Minimum confidence score to show a detection |
| Detection frequency | Every `5` frames | Runs inference once every 5 captured frames |
| Camera resolution | `1280 × 720` | Target webcam resolution |
| Camera FPS | `30` | Target webcam frame rate |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | [Flask](https://flask.palletsprojects.com/) |
| Object Detection | [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) |
| Computer Vision | [OpenCV](https://opencv.org/) |
| Deep Learning Runtime | [PyTorch](https://pytorch.org/) |
| Tunneling | [pyngrok](https://pyngrok.readthedocs.io/) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Deployment | [Vercel](https://vercel.com/) |

---

## ☁️ Deploying to Vercel

The repository includes a `vercel.json` that routes all traffic to `app.py`.

```bash
npm i -g vercel
vercel
```

> **Note:** Live webcam streaming and ngrok tunneling are not available in serverless environments. For full functionality, run the app locally or on a machine with a webcam.

---

## 📬 Contact

| | |
|---|---|
| **Email** | [msajanjua87@gmail.com](mailto:msajanjua87@gmail.com) |
| **GitHub** | [github.com/msaqibatifj](https://github.com/msaqibatifj) |
| **LinkedIn** | [Muhammad Saqib Atif](https://www.linkedin.com/in/muhammad-saqib-atif-a5a9662a8/) |

---

© 2026 Blind Aid. Built with ❤️ for accessibility.
