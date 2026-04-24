import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import pygame  # tambahan

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.5,  # lebih toleran saat deteksi awal
    min_tracking_confidence=0.3,   # lebih toleran saat tracking
    model_complexity=1  
)
mp_draw = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.3)

# ── Init audio ──────────────────────────────────────────────────
pygame.mixer.init()
sound = pygame.mixer.Sound(r"C:\Gabut\kicau mania\cat_audio.mp3")  # 🔥 GANTI PATH DI SINI

cap = cv2.VideoCapture(0)
video_cat = cv2.VideoCapture(r"C:\Gabut\kicau mania\cat.mp4")

play_cat = False
gesture_count = 0
GESTURE_THRESHOLD = 8
# Taruh di atas, sebelum while loop — sejajar dengan gesture_count = 0
decay_counter = 0

WINDOW_SIZE = 20
x_history = deque(maxlen=WINDOW_SIZE)
MOVE_THRESHOLD = 0.008

def dist_to_mouth(hand_lm, face_lm):
    mouth_x = face_lm[13].x
    mouth_y = face_lm[13].y
    palm_x  = hand_lm[9].x
    palm_y  = hand_lm[9].y
    return np.sqrt((palm_x - mouth_x)**2 + (palm_y - mouth_y)**2)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_result = face_mesh.process(rgb)
    face_landmarks = None
    if face_result.multi_face_landmarks:
        face_landmarks = face_result.multi_face_landmarks[0].landmark

    hand_result = hands.process(rgb)

    hand_near_mouth = False
    hand_waving     = False

    if hand_result.multi_hand_landmarks and face_landmarks:
        all_hands = hand_result.multi_hand_landmarks

        if len(all_hands) == 1:
            lm = all_hands[0].landmark
            mp_draw.draw_landmarks(frame, all_hands[0], mp_hands.HAND_CONNECTIONS)
            if dist_to_mouth(lm, face_landmarks) < 0.15:
                hand_near_mouth = True

        elif len(all_hands) >= 2:
            lm0 = all_hands[0].landmark
            lm1 = all_hands[1].landmark

            d0 = dist_to_mouth(lm0, face_landmarks)
            d1 = dist_to_mouth(lm1, face_landmarks)

            mouth_hand = lm0 if d0 < d1 else lm1
            wave_hand  = lm1 if d0 < d1 else lm0

            mp_draw.draw_landmarks(frame, all_hands[0], mp_hands.HAND_CONNECTIONS)
            mp_draw.draw_landmarks(frame, all_hands[1], mp_hands.HAND_CONNECTIONS)

            if dist_to_mouth(mouth_hand, face_landmarks) < 0.15:
                hand_near_mouth = True

            curr_x = wave_hand[9].x
            x_history.append(curr_x)

            if len(x_history) == WINDOW_SIZE:
                total_movement = max(x_history) - min(x_history)
                if total_movement > MOVE_THRESHOLD:
                    hand_waving = True

                cv2.putText(frame, f"Move: {total_movement:.4f}", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)
                cv2.putText(frame, f"Wave palm X: {curr_x:.3f}", (10, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,0), 2)
    else:
        x_history.clear()

    gesture_detected = hand_near_mouth and hand_waving

    # Ganti bagian debounce di dalam loop:
    if gesture_detected:
        gesture_count = min(gesture_count + 2, GESTURE_THRESHOLD)
        decay_counter = 0  # reset timer saat gesture aktif
    else:
        decay_counter += 1
        if decay_counter >= 10:   # tunggu 3 frame dulu sebelum turun
            gesture_count = max(gesture_count - 1, 0)
            decay_counter = 0

    prev_play = play_cat
    play_cat = gesture_count >= GESTURE_THRESHOLD

    # ── Trigger audio saat mulai / berhenti ────────────────────
    if not prev_play and play_cat:
        # Baru mulai play → putar suara dari awal
        sound.play(loops=-1)  # loops=-1 = looping, ganti 0 kalau mau sekali saja

    elif prev_play and not play_cat:
        # Baru berhenti → stop suara & reset video
        sound.stop()
        video_cat.set(cv2.CAP_PROP_POS_FRAMES, 0)

    if play_cat:
        ret_cat, frame_cat = video_cat.read()
        if not ret_cat:
            video_cat.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret_cat, frame_cat = video_cat.read()
    else:
        frame_cat = None

    if frame_cat is not None:
        frame_cat = cv2.resize(frame_cat, (200, 150))
        x_offset = w - 210
        y_offset = 10
        frame[y_offset:y_offset+150, x_offset:x_offset+200] = frame_cat

    cv2.putText(frame, f"Mulut : {'YA' if hand_near_mouth else 'tidak'}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0) if hand_near_mouth else (0,0,200), 2)
    cv2.putText(frame, f"Gerak : {'YA' if hand_waving else 'tidak'}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0) if hand_waving else (0,0,200), 2)
    cv2.putText(frame, f"COUNT : {gesture_count} | {'PLAY' if play_cat else 'PAUSE'}", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,100) if play_cat else (100,100,100), 2)

    cv2.imshow("Gesture Overlay", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
video_cat.release()
pygame.mixer.quit()
cv2.destroyAllWindows()