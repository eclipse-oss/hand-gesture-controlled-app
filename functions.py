import subprocess

# Screen corner zones mapped to target Linux applications
PROGRAMS = {
    1: ["kitty"],          
    2: ["firefox"],        
    3: ["thunar"],         
    4: ["Telegram"]             
}

def get_screen_zone(mouse_x, mouse_y, screen_width, screen_height):
    """Divides the screen into 4 equal quadrant zones based on cursor coordinates."""
    mid_x = screen_width // 2
    mid_y = screen_height // 2
    
    if mouse_x < mid_x and mouse_y < mid_y:
        return 1  # Top-Left (kitty)
    elif mouse_x >= mid_x and mouse_y < mid_y:
        return 2  # Top-Right (firefox)
    elif mouse_x < mid_x and mouse_y >= mid_y:
        return 3  # Bottom-Left (thunar)
    else:
        return 4  # Bottom-Right (telegram)

def gesture_triggered_func(zone):
    """Spawns the mapped application dynamically in a detached background process."""
    cmd = PROGRAMS.get(zone)
    if cmd:
        print(f"[INFO] Active zone {zone}. Start: {cmd[0]}")
        # Run process safely without locking up the main program flow
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def is_hand_closed(hand_landmarks, hand_label):
    """Returns True if the left hand is completely balled into a fist."""
    if not hand_landmarks or not hand_label:
        return False

    if hand_label != 'Left':
        return False

    # Check 4 main fingers: tip must be below the knuckle joint (Y-axis down)
    fingers = [(8, 6), (12, 10), (16, 14), (20, 18)]
    for tip, joint in fingers:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[joint].y:
            return False 

    # Check left thumb: tip tucked inwards to the right side (X-axis)
    thumb_tip = hand_landmarks.landmark[4].x
    thumb_joint = hand_landmarks.landmark[2].x
    if thumb_tip > thumb_joint:
        return False

    return True

def is_hand_open(hand_landmarks, hand_label):
    """Returns True if the left hand is wide open with all fingers extended."""
    if not hand_landmarks or not hand_label:
        return False

    if hand_label != 'Left':
        return False

    # Check 4 main fingers: tip must be above the joint (Y-axis up)
    fingers = [(8, 6), (12, 10), (16, 14), (20, 18)]
    for tip, joint in fingers:
        if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[joint].y:
            return False 

    # Check left thumb: tip extended outwards to the left side (X-axis)
    thumb_tip = hand_landmarks.landmark[4].x
    thumb_joint = hand_landmarks.landmark[2].x
    if thumb_tip < thumb_joint:
        return False

    return True

def is_the_thumb_tucked(hand_landmarks, hand_label):
    """Returns True if the right hand thumb is hidden/tucked inwards."""
    if not hand_landmarks or not hand_label: return False
    if hand_label != 'Right': return False

    # Right hand thumb moves left to tuck in, so tip X > joint X means it's tucked
    if hand_landmarks.landmark[4].x > hand_landmarks.landmark[2].x:
        return True
    
    return False

def close_window_move(hand_landmarks, hand_label):
    """Gesture: Fist with tucked thumb on the right hand."""
    if not hand_landmarks or not hand_label:
        return False

    if not is_the_thumb_tucked(hand_landmarks, hand_label):
        return False

    # All main fingers must be folded down
    fingers = [(8, 6), (12, 10), (16, 14), (20, 18)]
    for tip, joint in fingers:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[joint].y:
            return False 
    
    return True

def close_app_move(hand_landmarks, hand_label):
    """Gesture: Rock/Devil horns (Index and Pinky up, middle fingers down)."""
    if not hand_landmarks or not hand_label:
        return False

    if not is_the_thumb_tucked(hand_landmarks, hand_label):
        return False

    # Index (8) and Pinky (20) must be extended up
    fingers_raised = [(8, 6), (20, 18)]
    # Middle (12) and Ring (16) must be folded down
    fingers_lowered = [(12, 10), (16, 14)]

    for tip, joint in fingers_raised:
        if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[joint].y:
            return False
    
    for tip, joint in fingers_lowered:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[joint].y:
            return False

    return True