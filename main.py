import cv2
import mediapipe as mp
import time
import uinput
import tkinter as tk
import functions 

class GestureController:
    def __init__(self):
        # Get dynamic screen layout and set a default window size
        self.screen_width, self.screen_height = self._get_screen_size()
        self.window_width = 600
        self.window_height = 400
        
        # Initialize MediaPipe Hands solution
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
        
        # State tracking variables for mouse and gesture progression
        self.prev_x, self.prev_y = None, None
        self.current_mouse_x = self.screen_width // 2
        self.current_mouse_y = self.screen_height // 2
        self.gesture_stage = 0
        self.window_close_triggered = False
        
        # Define virtual hardware input events (Linux uinput)
        self.events = (
            uinput.REL_X, uinput.REL_Y, 
            uinput.BTN_LEFT, uinput.BTN_RIGHT, 
            uinput.KEY_LEFTMETA, uinput.KEY_C
        )

    def _get_screen_size(self):
        """Quickly spins up a hidden Tkinter root to grab monitor resolution."""
        root = tk.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height

    def _setup_window(self, name):
        """Creates a resizable OpenCV window centered on the screen."""
        x = int((self.screen_width - self.window_width) / 2)
        y = int((self.screen_height - self.window_height) / 2)
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(name, self.window_width, self.window_height)
        cv2.moveWindow(name, x, y)

    def process_right_hand_mouse(self, landmark, w, h, device):
        """Tracks the index finger to emulate relative mouse movements."""
        index_finger = landmark.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        cx, cy = int(index_finger.x * w), int(index_finger.y * h)

        # Only move the mouse if we have a baseline frame and the thumb is out
        if (self.prev_x is not None and 
            self.prev_y is not None and 
            not functions.is_the_thumb_tucked(landmark, 'Right')):
            
            # Double the delta for a faster cursor speed feel
            dx = int((cx - self.prev_x) * 2)
            dy = int((cy - self.prev_y) * 2)
                    
            if dx != 0:
                device.emit(uinput.REL_X, dx, syn=False)
                self.current_mouse_x = max(0, min(self.screen_width, self.current_mouse_x + dx))
            if dy != 0:
                device.emit(uinput.REL_Y, dy, syn=False)
                self.current_mouse_y = max(0, min(self.screen_height, self.current_mouse_y + dy))
                    
            device.emit(uinput.REL_X, 0, syn=True) # Sync the events together

        self.prev_x, self.prev_y = cx, cy

    def process_window_close_shortcut(self, landmark, device):
        """Triggers a Win+C hotkey macro to close active app windows."""
        if functions.close_window_move(landmark, 'Right'):
            if not self.window_close_triggered:
                # Press down Win + C
                device.emit(uinput.KEY_LEFTMETA, 1, syn=False)
                device.emit(uinput.KEY_C, 1, syn=True)
                        
                # Release keys and wait a bit to avoid accidental spam loops
                device.emit(uinput.KEY_C, 0, syn=False)
                device.emit(uinput.KEY_LEFTMETA, 0, syn=True)
                time.sleep(1.0)
                        
                self.window_close_triggered = True 
                print("[SYSTEM] Win+C Sent. Window closed.")
            else:
                self.window_close_triggered = False
        else:
            self.window_close_triggered = False

    def process_two_handed_gesture(self, left_landmark, hand_label):
        """State machine for a two-hand action sequence (Close -> Open Left Hand)."""
        if self.gesture_stage == 0:
            if functions.is_hand_closed(left_landmark, 'Left'):
                self.gesture_stage = 1
                print("[DEBUG] Stage 1: Left hand closed. Ready to open.")
                    
        elif self.gesture_stage == 1:
            if functions.is_hand_open(left_landmark, 'Left'):
                # Locate cursor zone and trigger the targeted event callback
                zone = functions.get_screen_zone(
                    self.current_mouse_x, self.current_mouse_y, 
                    self.screen_width, self.screen_height
                )
                functions.gesture_triggered_func(zone)
                print(f"[MESSAGE] All done. Program triggered for zone {zone}")
                self.gesture_stage = 0
            
            elif not functions.is_hand_closed(left_landmark, 'Left'):
                # Reset state if the hand half-opened or tracking glitched
                self.gesture_stage = 0
                print("[ERROR] something went wrong! Gesture reset.")

    def run(self):
        """Launches the video pipeline and main processing loop."""
        cap = cv2.VideoCapture(0)
        window_name = 'Webcam'
        self._setup_window(window_name)

        # Context manager handles virtual device lifecycle safely
        with uinput.Device(self.events) as device:
            time.sleep(0.5) # Warm up time for uinput driver initialization

            while cap.isOpened():
                success, frame = cap.read()
                if not success: 
                    break

                # Flip horizontally for a natural mirror-like webcam look
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                
                # Convert BGR to RGB format required by MediaPipe
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(image_rgb)

                left_hand_landmarks = None
                right_hand_landmarks = None

                # Extract and sort landmarks into left and right slots
                if results.multi_hand_landmarks and results.multi_handedness:
                    for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                        self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                        
                        if handedness.classification[0].label == 'Right':
                            right_hand_landmarks = hand_landmarks
                        else:
                            left_hand_landmarks = hand_landmarks

                # Route data to specific managers if active hands are found
                if right_hand_landmarks is not None:
                    self.process_right_hand_mouse(right_hand_landmarks, w, h, device)
                else:
                    self.prev_x, self.prev_y = None, None

                self.process_window_close_shortcut(right_hand_landmarks, device)

                if left_hand_landmarks is not None and right_hand_landmarks is not None:
                    self.process_two_handed_gesture(left_hand_landmarks, 'Left')

                # Display the processed camera feed frame
                cv2.imshow(window_name, frame)
                
                # Check escape triggers: physical 'q' key or custom quit gesture
                if (cv2.waitKey(1) & 0xFF == ord('q') or 
                    functions.close_app_move(right_hand_landmarks, 'Right')): 
                    break

        # Explicitly clean up resources on exit
        cap.release()
        cv2.destroyAllWindows()

def main():
    controller = GestureController()
    controller.run()

if __name__ == "__main__":
    main()