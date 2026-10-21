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

    is_david_goliath = any(k in prompt_text.lower() for k in ["david", "goliath", "shepherd", "elah", "bible"])

    # Generate animated video frames
    for i in range(num_frames):
        t = i / float(num_frames)
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        if is_david_goliath:
            # === BIBLICAL DESERT SUNSET & VALLEY OF ELAH ===
            for y in range(height):
                prog = y / float(height)
                # Golden desert sunset: deep orange at top to dusty amber in valley
                r = max(0, min(255, int(220 - prog * 110)))
                g = max(0, min(255, int(130 + prog * 40)))
                b = max(0, min(255, int(40 + prog * 60)))
                frame[y, :] = (b, g, r)

            # Distant mountain silhouettes (Philistine and Israelite hills)
            pts_left_hill = np.array([[0, 280], [120, 230], [240, 290], [240, height], [0, height]], np.int32)
            pts_right_hill = np.array([[220, 300], [380, 220], [width, 270], [width, height], [220, height]], np.int32)
            cv2.fillPoly(frame, [pts_left_hill], (40, 60, 110))
            cv2.fillPoly(frame, [pts_right_hill], (35, 55, 105))

            # Valley ground
            cv2.rectangle(frame, (0, 320), (width, height), (50, 80, 130), -1)
            # Sandy texture lines
            for gy in range(330, height - 70, 20):
                cv2.line(frame, (0, gy), (width, gy), (60, 95, 150), 1)

            # === GOLIATH (Right side, towering giant in bronze armor) ===
            gx, gy = int(width * 0.76), 330
            # Bronze body / armor
            cv2.rectangle(frame, (gx - 28, gy - 160), (gx + 28, gy), (30, 105, 180), -1) # Bronze armor
            cv2.rectangle(frame, (gx - 28, gy - 160), (gx + 28, gy), (40, 140, 220), 2)
            # Goliath Head & Helmet
            cv2.circle(frame, (gx, gy - 180), 22, (35, 115, 195), -1)
            # Red plume / crest on helmet
            cv2.ellipse(frame, (gx, gy - 200), (8, 16), 0, 0, 360, (40, 40, 220), -1)
            # Giant Spear
            spear_sway = int(np.sin(t * 2 * np.pi) * 6)
            cv2.line(frame, (gx + 35 + spear_sway, gy - 220), (gx + 30, gy + 15), (20, 50, 80), 4)
            # Spearhead
            cv2.drawMarker(frame, (gx + 35 + spear_sway, gy - 225), (180, 180, 180), cv2.MARKER_TRIANGLE_UP, 16, 3)
            # Large Bronze Shield
            cv2.rectangle(frame, (gx - 45, gy - 130), (gx - 20, gy - 20), (45, 130, 205), -1)
            cv2.rectangle(frame, (gx - 45, gy - 130), (gx - 20, gy - 20), (255, 230, 180), 2)
            cv2.putText(frame, "GOLIATH (9.7 ft)", (gx - 55, gy - 215), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2)
            cv2.putText(frame, "GOLIATH (9.7 ft)", (gx - 55, gy - 215), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 210, 255), 1)

            # === YOUNG DAVID (Left side, youthful shepherd) ===
            dx, dy = int(width * 0.22), 335
            # Simple shepherd's tunic (linen/brown)
            cv2.rectangle(frame, (dx - 14, dy - 80), (dx + 14, dy), (90, 120, 160), -1)
            cv2.circle(frame, (dx, dy - 95), 14, (120, 160, 210), -1) # Head
            # Shepherd's staff
            cv2.line(frame, (dx - 22, dy - 110), (dx - 22, dy + 10), (35, 60, 100), 3)

            # Animated swinging sling
            sling_angle = t * 10 * np.pi
            sling_len = 30
            sling_end_x = int(dx + 18 + sling_len * np.cos(sling_angle))
            sling_end_y = int(dy - 70 + sling_len * np.sin(sling_angle))
            cv2.line(frame, (dx + 10, dy - 60), (sling_end_x, sling_end_y), (40, 70, 120), 2)
            cv2.circle(frame, (sling_end_x, sling_end_y), 4, (200, 230, 255), -1) # Stone in pouch
            cv2.putText(frame, "DAVID", (dx - 18, dy - 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            cv2.putText(frame, "DAVID", (dx - 18, dy - 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # === FLYING SMOOTH STONE TRAJECTORY ===
            stone_progress = (t * 2.0) % 1.0 # 2 cycles
            stone_x = int(dx + 25 + stone_progress * (gx - dx - 35))
            stone_y = int((dy - 60) - 40 * np.sin(stone_progress * np.pi) - stone_progress * 115)
            # Glowing projectile trail
            cv2.circle(frame, (stone_x, stone_y), 6, (0, 240, 255), -1)
            cv2.circle(frame, (stone_x, stone_y), 10, (100, 255, 255), 1)

            # Header Banner
            cv2.rectangle(frame, (15, 15), (width - 15, 60), (20, 25, 45), -1)
            cv2.rectangle(frame, (15, 15), (width - 15, 60), (0, 200, 255), 1)
            cv2.putText(frame, "SCENE: DAVID & GOLIATH - THE CONFRONTATION", (25, 38),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 230, 255), 2)
            cv2.putText(frame, "Valley of Elah | 1 Samuel 17", (25, 54),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 220, 240), 1)

        else:
            # Fallback Cybernetic Animation
            bg_r = max(0, min(255, int(15 + 15 * np.sin(t * 2 * np.pi))))
            bg_g = max(0, min(255, int(10 + 20 * np.cos(t * 2 * np.pi))))
            bg_b = max(0, min(255, int(35 + 25 * np.sin(t * 2 * np.pi + np.pi/4))))
            frame[:] = (bg_b, bg_g, bg_r)

            grid_offset = int((t * 40) % 40)
            for y in range(height // 2, height, 25):
                y_pos = y + grid_offset
                if y_pos < height:
                    alpha = max(0.0, min(1.0, (y_pos - height // 2) / (height / 2.0)))
                    color = (int(255 * alpha), int(120 * alpha), int(200 * alpha))
                    cv2.line(frame, (0, y_pos), (width, y_pos), color, 1)

            center_x, horizon_y = width // 2, height // 2
            for x in range(0, width + 1, 40):
                cv2.line(frame, (center_x, horizon_y), (x, height), (180, 80, 140), 1)

            radius = int(45 + 15 * np.sin(t * 4 * np.pi))
            orb_color = (
                max(0, min(255, int(180 + 75 * np.cos(t * 2 * np.pi)))),
                max(0, min(255, int(100 + 80 * np.sin(t * 2 * np.pi)))),
                255
            )
            cv2.circle(frame, (center_x, horizon_y - 30), radius, orb_color, -1)
            cv2.circle(frame, (center_x, horizon_y - 30), radius + 12, (255, 200, 240), 2)

            cv2.rectangle(frame, (20, 20), (width - 20, 65), (20, 20, 40), -1)
            cv2.rectangle(frame, (20, 20), (width - 20, 65), (0, 220, 255), 1)
            cv2.putText(frame, "COMFYUI TEXT-TO-VIDEO AI ENGINE", (35, 48),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 240, 255), 2)

        # Prompt Subtitle
        display_prompt = prompt_text if len(prompt_text) < 48 else prompt_text[:45] + "..."
        cv2.putText(frame, f"Prompt: {display_prompt}", (25, height - 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (240, 240, 240), 1)

        # Progress bar
        bar_w = width - 50
        progress_w = int(bar_w * t)
        cv2.rectangle(frame, (25, height - 25), (25 + bar_w, height - 17), (40, 40, 60), -1)
        cv2.rectangle(frame, (25, height - 25), (25 + progress_w, height - 17), (0, 255, 180), -1)

        # Frame counter
        cv2.putText(frame, f"Frame {i+1}/{num_frames} ({fps} fps)", (width - 170, height - 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 220, 255), 1)

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
