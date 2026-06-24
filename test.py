import sys, os, traceback, threading, time

# Try to close the native PyInstaller splash screen if it exists
try:
    import pyi_splash
except ImportError:
    pyi_splash = None

# === Error Logging Setup ===
if getattr(sys, 'frozen', False):
    _app_dir = os.path.dirname(sys.executable)
else:
    _app_dir = os.path.dirname(os.path.abspath(__file__))
_log_path = os.path.join(_app_dir, 'error.log')

def _log_error():
    with open(_log_path, 'w') as f:
        traceback.print_exc(file=f)

# ============================================================
#  SPLASH SCREEN  —  shown instantly while heavy libs load
# ============================================================
import tkinter as tk
import math

class SplashScreen:
    """Modern dark-themed splash with animated arc loader."""

    # -- colour palette --
    BG           = "#0d0d1a"
    CARD_BG      = "#14142b"
    ACCENT       = "#6c63ff"
    ACCENT_GLOW  = "#8b83ff"
    TEXT_PRIMARY  = "#e8e6f0"
    TEXT_DIM      = "#7a7898"
    BORDER       = "#1e1e3a"

    WIDTH, HEIGHT = 480, 340

    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)          # frameless
        self.root.attributes("-topmost", True)
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        # centre on screen
        sx = self.root.winfo_screenwidth()
        sy = self.root.winfo_screenheight()
        x = (sx - self.WIDTH) // 2
        y = (sy - self.HEIGHT) // 2
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

        # rounded-card canvas
        self.canvas = tk.Canvas(
            self.root, width=self.WIDTH, height=self.HEIGHT,
            bg=self.BG, highlightthickness=0
        )
        self.canvas.pack()

        # draw card background with subtle border
        pad = 12
        self._round_rect(pad, pad, self.WIDTH - pad, self.HEIGHT - pad,
                         radius=24, fill=self.CARD_BG, outline=self.BORDER, width=1)

        # ── branding ──
        self.canvas.create_text(
            self.WIDTH // 2, 80,
            text="✦", font=("Segoe UI Emoji", 28),
            fill=self.ACCENT
        )
        self.canvas.create_text(
            self.WIDTH // 2, 130,
            text="AirType", font=("Segoe UI", 30, "bold"),
            fill=self.TEXT_PRIMARY
        )
        self.canvas.create_text(
            self.WIDTH // 2, 165,
            text="Virtual Air Keyboard", font=("Segoe UI", 11),
            fill=self.TEXT_DIM
        )

        # ── animated arc loader ──
        cx, cy, r = self.WIDTH // 2, 220, 18
        self.arc = self.canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=0, extent=90, style="arc",
            outline=self.ACCENT, width=3
        )
        self.arc_cx, self.arc_cy, self.arc_r = cx, cy, r
        self.arc_angle = 0

        # two small trailing dots for extra flair
        self.dot1 = self.canvas.create_oval(0, 0, 6, 6, fill=self.ACCENT_GLOW, outline="")
        self.dot2 = self.canvas.create_oval(0, 0, 4, 4, fill=self.ACCENT, outline="")

        # ── status label ──
        self.status_id = self.canvas.create_text(
            self.WIDTH // 2, 260,
            text="Initializing…", font=("Segoe UI", 10),
            fill=self.TEXT_DIM
        )

        # ── progress bar track + fill ──
        bar_w, bar_h = 240, 4
        bx = (self.WIDTH - bar_w) // 2
        by = 290
        self._round_rect(bx, by, bx + bar_w, by + bar_h, radius=2,
                         fill="#1e1e3a", outline="")
        self.bar_x = bx
        self.bar_y = by
        self.bar_w = bar_w
        self.bar_h = bar_h
        self.bar_fill = self._round_rect(bx, by, bx + 1, by + bar_h, radius=2,
                                          fill=self.ACCENT, outline="")

        # ── version tag ──
        self.canvas.create_text(
            self.WIDTH // 2, self.HEIGHT - 26,
            text="v1.0", font=("Segoe UI", 8),
            fill="#3a3860"
        )

        self._progress = 0.0
        self._status = "Initializing…"
        self._done = False
        self._after_id = None
        self._animate()
        
        # Close the bootloader splash now that our GUI is up
        if pyi_splash:
            try:
                pyi_splash.close()
            except Exception:
                pass

    # -- helpers --
    def _round_rect(self, x1, y1, x2, y2, radius=20, **kwargs):
        """Draw a rounded rectangle on the canvas."""
        points = [
            x1+radius, y1,   x2-radius, y1,   x2, y1,   x2, y1+radius,
            x2, y2-radius,   x2, y2,   x2-radius, y2,   x1+radius, y2,
            x1, y2,   x1, y2-radius,   x1, y1+radius,   x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def _animate(self):
        """Tick the arc loader ~30 fps."""
        if self._done:
            return
        self.arc_angle = (self.arc_angle + 8) % 360
        self.canvas.itemconfig(self.arc, start=self.arc_angle)

        # position trailing dots
        a1 = math.radians(self.arc_angle - 20)
        a2 = math.radians(self.arc_angle - 45)
        for dot, a, sz in [(self.dot1, a1, 3), (self.dot2, a2, 2)]:
            dx = self.arc_cx + self.arc_r * math.cos(a)
            dy = self.arc_cy - self.arc_r * math.sin(a)
            self.canvas.coords(dot, dx - sz, dy - sz, dx + sz, dy + sz)

        # update progress bar
        fill_w = max(1, int(self.bar_w * self._progress))
        self.canvas.coords(
            self.bar_fill,
            *self._round_rect_coords(self.bar_x, self.bar_y,
                                      self.bar_x + fill_w, self.bar_y + self.bar_h, 2)
        )
        self.canvas.itemconfig(self.status_id, text=self._status)

        self._after_id = self.root.after(33, self._animate)

    def _round_rect_coords(self, x1, y1, x2, y2, r):
        return [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1,
        ]

    def set_status(self, text, progress):
        self._status = text
        self._progress = min(1.0, progress)

    def close(self):
        self._done = True
        try:
            # Cancel pending animation callback to prevent Tcl errors
            if self._after_id is not None:
                self.root.after_cancel(self._after_id)
                self._after_id = None
            self.root.quit()     # exit mainloop
            self.root.destroy()  # destroy window
        except Exception:
            pass

    def mainloop(self):
        self.root.mainloop()


# ============================================================
#  BACKGROUND LOADER  —  imports + init while splash is alive
# ============================================================
load_error = None

def background_load(splash):
    """Run heavy imports & setup in a thread; update splash progress."""
    global load_error
    try:
        splash.set_status("Loading OpenCV…", 0.10)
        import cv2
        globals()['cv2'] = cv2

        splash.set_status("Loading PyAutoGUI…", 0.20)
        import pyautogui
        pyautogui.PAUSE = 0.01
        globals()['pyautogui'] = pyautogui

        splash.set_status("Loading MediaPipe…", 0.35)
        import mediapipe as mp
        globals()['mp'] = mp

        splash.set_status("Loading AI engine…", 0.50)
        import google.generativeai as genai
        globals()['genai'] = genai

        splash.set_status("Loading spell checker…", 0.60)
        from spellchecker import SpellChecker
        globals()['SpellChecker'] = SpellChecker

        splash.set_status("Loading hand tracker…", 0.70)
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision
        globals()['mp_python'] = mp_python
        globals()['vision'] = vision

        splash.set_status("Initializing models…", 0.85)
        # Pre-initialize everything that takes time
        globals()['spell'] = SpellChecker()
        genai.configure(api_key="your api key")
        globals()['model'] = genai.GenerativeModel("gemini-2.0-flash")

        splash.set_status("Starting camera…", 0.95)
        time.sleep(0.3)  # brief pause so user sees final status

        splash.set_status("Ready!", 1.0)
        time.sleep(0.4)

    except Exception as e:
        load_error = e
        _log_error()

    # Signal splash to close (schedule on main thread)
    splash.root.after(0, splash.close)


# === Helper for PyInstaller Resources ===
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ============================================================
#  LAUNCH SPLASH + LOAD
# ============================================================
splash = SplashScreen()
loader_thread = threading.Thread(target=background_load, args=(splash,), daemon=True)
loader_thread.start()
splash.mainloop()          # blocks until splash.close() is called
loader_thread.join()       # ensure thread finished

# Check for load errors
if load_error is not None:
    import tkinter.messagebox as mb
    root = tk.Tk()
    root.withdraw()
    mb.showerror("AirType — Startup Error", f"Failed to start:\n\n{load_error}\n\nCheck error.log for details.")
    root.destroy()
    sys.exit(1)


# ============================================================
#  MAIN APPLICATION  (all heavy modules are loaded at this point)
# ============================================================

# === Global AI Results ===
latest_results = None

def result_callback(result, output_image, timestamp_ms):
    global latest_results
    latest_results = result

# === Initialize MediaPipe Tasks API ===
base_options = mp_python.BaseOptions(
    model_asset_path=resource_path('hand_landmarker.task'),
    delegate=mp_python.BaseOptions.Delegate.CPU
)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback=result_callback,
    num_hands=2,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
)
detector = vision.HandLandmarker.create_from_options(options)

# === Keyboard Layout ===
keys = [
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';'],
    ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/'],
    ['Space', '<', 'Back', '>', 'Correct', '?', '!', '@']
]
key_width, key_height = 45, 50
special_width = 90
start_y, spacing, row_spacing = 80, 3, 6

# === Build Button Layout ===
def build_buttons():
    layout = []
    for row_idx, row in enumerate(keys):
        row_total_width = sum(special_width if key in ['Shift', 'Space', 'Back', 'Correct'] else key_width for key in row) + spacing * (len(row) - 1)
        offset_x = (640 - row_total_width) // 2
        for key in row:
            w = special_width if key in ['Shift', 'Space', 'Back', 'Correct'] else key_width
            layout.append([key, offset_x, start_y + row_idx * (key_height + row_spacing), w, key_height])
            offset_x += w + spacing
    return layout

button_layout = build_buttons()

# === State Variables ===
shift = False
typed_text = ""
click_delay = 0.15
last_key_pressed = None
correction_done_text = ""

hand_states = [
    {"last_click": 0, "pressed": False, "first_pinch_time": 0},
    {"last_click": 0, "pressed": False, "first_pinch_time": 0}
]

# === Drawing Utilities ===
def draw_button(frame, key, x, y, w, h, active=False):
    color = (0, 255, 255) if active else (0, 0, 0)
    overlay = frame.copy()
    cv2.rectangle(overlay, (x + 10, y), (x + w - 10, y + h), color, -1)
    cv2.rectangle(overlay, (x, y + 10), (x + w, y + h - 10), color, -1)
    cv2.circle(overlay, (x + 10, y + 10), 10, color, -1)
    cv2.circle(overlay, (x + w - 10, y + 10), 10, color, -1)
    cv2.circle(overlay, (x + 10, y + h - 10), 10, color, -1)
    cv2.circle(overlay, (x + w - 10, y + h - 10), 10, color, -1)
    frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
    label = key.upper() if (shift and key.isalpha()) else key
    size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    cv2.putText(frame, label, (x + (w - size[0]) // 2, y + (h + size[1]) // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    return frame

def draw_keyboard(frame):
    for key, x, y, w, h in button_layout:
        frame = draw_button(frame, key, x, y, w, h)
    return frame

# === Gemini Correction ===
def correct_last_word(text):
    words = text.strip().split()
    if not words:
        return text
    last = words[-1]
    try:
        prompt = f"Given the sentence context: '{text}', correct the spelling of the last word '{last}'. Only return the corrected word, nothing else."
        result = model.generate_content(prompt).text.strip()
        if result and result.lower() != last.lower():
            words[-1] = result
        return " ".join(words) + " "
    except Exception as e:
        corrected = spell.correction(last)
        if corrected and corrected.lower() != last.lower():
            words[-1] = corrected
        return " ".join(words) + " "

# === Virtual Typing Actions ===
def handle_keypress(key):
    global shift, typed_text, correction_done_text

    if key == 'Shift':
        shift = not shift
    elif key == 'Space':
        pyautogui.press('space')
        typed_text += ' '
    elif key == 'Back':
        pyautogui.press('backspace')
        typed_text = typed_text[:-1]
    elif key == '<':
        pyautogui.press('left')
    elif key == '>':
        pyautogui.press('right')
    elif key == 'Correct':
        def correct():
            global typed_text, correction_done_text
            words = typed_text.strip().split()
            if words:
                wrong = words[-1]
                typed_text = correct_last_word(typed_text)
                corrected = typed_text.strip().split()[-1]
                for _ in range(len(wrong)):
                    pyautogui.press('backspace')
                pyautogui.write(corrected, interval=0.05)
                correction_done_text = typed_text
        threading.Thread(target=correct).start()
    else:
        char = key.upper() if shift else key.lower()
        pyautogui.write(char)
        typed_text += char
        shift = False

# === Main Camera Loop ===
try:
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    if not cap.isOpened():
        import tkinter.messagebox as mb
        root = tk.Tk(); root.withdraw()
        mb.showerror("AirType", "Could not open camera!\nMake sure your webcam is connected.")
        root.destroy()
        sys.exit(1)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Downscale image 2x for much faster AI processing
        small_rgb = cv2.resize(rgb, (320, 240))
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=small_rgb)

        # Send image to background thread for zero lag
        timestamp_ms = int(time.time() * 1000)
        detector.detect_async(mp_image, timestamp_ms)

        # Drawing background for Typing text
        cv2.rectangle(frame, (0, 0), (640, 60), (200, 200, 200), -1)
        frame = draw_keyboard(frame)
        cv2.putText(frame, f"Typing: {typed_text}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)

        hands_pressed_this_frame = [False, False]

        if latest_results and latest_results.hand_landmarks:
            for idx, hand_landmarks in enumerate(latest_results.hand_landmarks):
                if idx >= 2: break

                h, w, _ = frame.shape
                lm = [(int(p.x * w), int(p.y * h)) for p in hand_landmarks]
                thumb_tip, index_tip = lm[4], lm[8]
                dist = ((thumb_tip[0]-index_tip[0])**2 + (thumb_tip[1]-index_tip[1])**2)**0.5

                if dist < 40:
                    for key, x, y, w_, h_ in button_layout:
                        if x < index_tip[0] < x + w_ and y < index_tip[1] < y + h_:
                            frame = draw_button(frame, key, x, y, w_, h_, active=True)

                            hands_pressed_this_frame[idx] = True
                            state = hand_states[idx]

                            if not state["pressed"]:
                                if time.time() - state["last_click"] > click_delay:
                                    state["last_click"] = time.time()
                                    state["first_pinch_time"] = time.time()
                                    handle_keypress(key)
                                    state["pressed"] = True
                            elif key == 'Back':
                                if time.time() - state.get("first_pinch_time", 0) > 3.0:
                                    if time.time() - state["last_click"] > 0.1:
                                        state["last_click"] = time.time()
                                        handle_keypress(key)
                            break

        for i in range(2):
            if not hands_pressed_this_frame[i]:
                hand_states[i]["pressed"] = False

        cv2.namedWindow("Virtual Keyboard")
        cv2.setWindowProperty("Virtual Keyboard", cv2.WND_PROP_TOPMOST, 1)
        cv2.imshow("Virtual Keyboard", frame)
        
        # Check if window was closed via 'X' button or Esc/Q key
        if cv2.getWindowProperty("Virtual Keyboard", cv2.WND_PROP_VISIBLE) < 1:
            break
        if cv2.waitKey(1) in [ord('q'), 27]:
            break

except Exception as e:
    _log_error()
    try:
        import tkinter.messagebox as mb
        root = tk.Tk(); root.withdraw()
        mb.showerror("AirType — Error", f"An error occurred:\n\n{e}\n\nCheck error.log for details.")
        root.destroy()
    except Exception:
        pass
finally:
    try:
        cap.release()
        cv2.destroyAllWindows()
    except Exception:
        pass