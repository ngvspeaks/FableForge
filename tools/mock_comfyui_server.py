import http.server
import socketserver
import json
import urllib.parse
import uuid
import time
import threading
import os
import cv2
import numpy as np

PORT = 8188
OUTPUT_DIR = os.path.join(os.getcwd(), "storage", "temp", "comfyui_mock_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

jobs = {}

def render_demo_video(prompt_id, prompt_text, width=512, height=512, num_frames=60, fps=20):
    filename = f"comfy_render_{prompt_id}.mp4"
    filepath = os.path.join(OUTPUT_DIR, filename)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filepath, fourcc, float(fps), (width, height))

    # Generate animated futuristic cyberpunk demo video
    for i in range(num_frames):
        t = i / float(num_frames)
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Dynamic cybernetic gradient background
        bg_r = max(0, min(255, int(15 + 15 * np.sin(t * 2 * np.pi))))
        bg_g = max(0, min(255, int(10 + 20 * np.cos(t * 2 * np.pi))))
        bg_b = max(0, min(255, int(35 + 25 * np.sin(t * 2 * np.pi + np.pi/4))))
        frame[:] = (bg_b, bg_g, bg_r)

        # Draw glowing animated perspective grid lines
        grid_offset = int((t * 40) % 40)
        for y in range(height // 2, height, 25):
            y_pos = y + grid_offset
            if y_pos < height:
                alpha = max(0.0, min(1.0, (y_pos - height // 2) / (height / 2.0)))
                color = (int(255 * alpha), int(120 * alpha), int(200 * alpha))
                cv2.line(frame, (0, y_pos), (width, y_pos), color, 1)

        # Draw vanishing perspective lines
        center_x = width // 2
        horizon_y = height // 2
        for x in range(0, width + 1, 40):
            cv2.line(frame, (center_x, horizon_y), (x, height), (180, 80, 140), 1)

        # Glowing pulsating cyber orb in center
        radius = int(45 + 15 * np.sin(t * 4 * np.pi))
        orb_color = (
            max(0, min(255, int(180 + 75 * np.cos(t * 2 * np.pi)))),
            max(0, min(255, int(100 + 80 * np.sin(t * 2 * np.pi)))),
            255
        )
        cv2.circle(frame, (center_x, horizon_y - 30), radius, orb_color, -1)
        cv2.circle(frame, (center_x, horizon_y - 30), radius + 12, (255, 200, 240), 2)

        # Header Badge
        cv2.rectangle(frame, (20, 20), (width - 20, 65), (20, 20, 40), -1)
        cv2.rectangle(frame, (20, 20), (width - 20, 65), (0, 220, 255), 1)
        cv2.putText(frame, "COMFYUI TEXT-TO-VIDEO AI ENGINE", (35, 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 240, 255), 2)

        # Prompt Subtitle
        display_prompt = prompt_text if len(prompt_text) < 40 else prompt_text[:37] + "..."
        cv2.putText(frame, f"Prompt: {display_prompt}", (30, height - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 230, 230), 1)

        # Progress bar
        bar_w = width - 60
        progress_w = int(bar_w * t)
        cv2.rectangle(frame, (30, height - 35), (30 + bar_w, height - 25), (40, 40, 60), -1)
        cv2.rectangle(frame, (30, height - 35), (30 + progress_w, height - 25), (0, 255, 180), -1)

        # Frame counter
        cv2.putText(frame, f"Frame {i+1}/{num_frames} ({fps} fps)", (width - 190, height - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 220, 255), 1)

        out.write(frame)

    out.release()
    print(f"[Render Engine] Video rendered successfully: {filepath} ({os.path.getsize(filepath)} bytes)")
    return filename

class ComfyUIHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        print(f"[ComfyUI Mock] {args[0]} - {args[1]}")

    def do_POST(self):
        if self.path == "/prompt":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8')) if body else {}

            prompt_id = f"demo-prompt-{uuid.uuid4().hex[:8]}"

            prompt_text = "Futuristic Cybernetic City"
            workflow = data.get("prompt", {})
            for node_id, node in workflow.items():
                if isinstance(node, dict) and "inputs" in node:
                    if "text" in node["inputs"]:
                        prompt_text = str(node["inputs"]["text"])
                        break

            jobs[prompt_id] = {
                "status": "QUEUED",
                "ready_time": time.time() + 1.2,
                "prompt_text": prompt_text,
                "filename": None
            }

            def background_render():
                time.sleep(0.4)
                jobs[prompt_id]["status"] = "RENDERING"
                fn = render_demo_video(prompt_id, prompt_text)
                jobs[prompt_id]["filename"] = fn
                jobs[prompt_id]["status"] = "COMPLETED"

            threading.Thread(target=background_render, daemon=True).start()

            response = {
                "prompt_id": prompt_id,
                "number": len(jobs),
                "node_errors": {}
            }
            resp_bytes = json.dumps(response).encode('utf-8')
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(resp_bytes)
        else:
            self.send_error(404)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/history/"):
            prompt_id = path.replace("/history/", "").strip()
            job = jobs.get(prompt_id)

            if job and job["status"] == "COMPLETED" and time.time() >= job["ready_time"]:
                response = {
                    prompt_id: {
                        "outputs": {
                            "7": {
                                "videos": [
                                    {
                                        "filename": job["filename"],
                                        "subfolder": "",
                                        "type": "output"
                                    }
                                ]
                            }
                        }
                    }
                }
            else:
                response = {}

            resp_bytes = json.dumps(response).encode('utf-8')
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(resp_bytes)

        elif path == "/view":
            params = urllib.parse.parse_qs(parsed.query)
            filename = params.get("filename", [""])[0]
            filepath = os.path.join(OUTPUT_DIR, filename)

            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(file_size))
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")

        elif path == "/queue":
            response = {"queue_running": [], "queue_pending": []}
            resp_bytes = json.dumps(response).encode('utf-8')
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(resp_bytes)

        elif path == "/system_stats":
            response = {"system": {"os": "windows"}}
            resp_bytes = json.dumps(response).encode('utf-8')
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(resp_bytes)

        else:
            self.send_error(404)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == "__main__":
    server = ThreadedTCPServer(("127.0.0.1", PORT), ComfyUIHandler)
    print(f"Mock ComfyUI Server running on http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
