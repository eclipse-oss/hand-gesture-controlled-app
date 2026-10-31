# hand-gesture-controlled-app

A lightweight Python application that utilizes **MediaPipe** for hand tracking and **uinput** to emulate hardware mouse movement and keyboard shortcuts. It also features screen-zone automation to launch your favorite applications using simple left-hand gestures.

Highly optimized for Linux environments (tested on Arch Linux).

## ✨ Features

- **Smooth Mouse Tracking:** Move the cursor using your right hand's index finger.
- **Motion Safety Lock:** Tuck your right thumb in to instantly pause mouse movement.
- **Window Management:** Perform a full fist gesture with your right hand to send a `Win + C` macro to close active windows.
- **App Launching Zones:** Divide your monitor into 4 interactive quadrants. Close and open your left hand to spawn apps like Terminal, Browser, 

## 🛠️ System Requirements & Prerequisites
Since this project communicates directly with Linux kernel input devices via `/dev/uinput`, you need to allow your user account to access it without requiring root (`sudo`) permissions.

### 1. Configure udev Rules
Run the following commands to create a rule allowing the `input` group to access `uinput`:

```bash
sudo echo 'KERNEL=="uinput", MODE="0660", GROUP="input", OPTIONS+="static_node=uinput"' | sudo tee /etc/udev/rules.d/99-uinput.rules
```

### 2. Add User to the Input Group
```bash
sudo usermod -aG input \$USER
```


### 3. Reload Kernel Modules
```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
sudo modprobe uinput
```
*Note: You must log out and log back into your user session (or restart) for group changes to take effect.*

---

## 🚀 Installation & Setup

We have bundled a setup script that automates system dependencies installation, creates a Python 3.12 virtual environment, and installs pin-pointed dependencies.

1. Clone the repository and navigate into it:
   ```bash
   git clone https://github.com
   cd hand-gesture-mouse
   ```

2. Make the setup script executable and run it:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

---

## 💻 Usage

Always ensure your virtual environment is active before running the script:

```bash
source venv/bin/activate
python main.py
```

## 🎮 Controls & Gestures Layout

The application processes input from both hands independently. The **Right Hand** is dedicated to cursor navigation and window control, while the **Left Hand** acts as a multi-stage action trigger.

### 🫱 Right Hand: Mouse & Window Actions

*   **Mouse Movement:** Point and move your **Index Finger**. The cursor will mimic your tracking path with a speed multiplier for smooth desktop navigation.
*   **Motion Lock (Pause):** **Tuck your Thumb inward**. As long as the thumb is tucked, cursor tracking freezes entirely, allowing you to reposition your hand safely.
*   **Close Active Window:** Ball your right hand into a **Full Fist (with the thumb tucked)**. This immediately triggers a hardware macro executing `Win + C` (commonly used to close windows in modern Linux environments).
*   **Exit Application:** Extend only your **Index and Pinky fingers (Rock-on / Devil Horns gesture)** while keeping middle/ring fingers folded. This will break the webcam loop and safely shut down the virtual device.

---

### 🫲 Left Hand + Screen Zones: App Launching

By combining your cursor position with sequential left-hand actions, you can spawn terminal utilities and graphical applications based on **4 virtual screen quadrants**.

#### The Launch Sequence:
1. Move the cursor (using your right hand) into one of the four screen zones.
2. **Close your Left Hand** into a fist to prepare the system (triggers `Stage 1` stabilization).
3. **Open your Left Hand** completely. The mapped application launches instantly.

#### Screen Quadrants & Mapped Applications:

| Quadrant Zone | Screen Location | Launched Application |
| :--- | :--- | :--- |
| **Zone 1** | Top-Left | `kitty` (Terminal) |
| **Zone 2** | Top-Right | `firefox` (Web Browser) |
| **Zone 3** | Bottom-Left | `thunar` (File Manager) |
| **Zone 4** | Bottom-Right | `Telegram` (Messenger) |

---

### ⌨️ Physical Keyboard Fail-safe
*   **Emergency Quit:** Press the `Q` key on your physical keyboard at any time while focusing the webcam window to kill the script instantly.
