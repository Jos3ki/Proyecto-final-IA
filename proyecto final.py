import cv2
import mediapipe as mp
import numpy as np
import pyautogui
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- OPTIMIZACIÓN CRÍTICA DE PERIFÉRICOS ---
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0  

MARGIN = 10
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)

FINGER_TIPS  = [4,  8,  12, 16, 20]
FINGER_MID   = [3,  7,  11, 15, 19]
FINGER_BASES = [2,  6,  10, 14, 18]

THRESHOLD = 0.03           # BAJAMOS EL UMBRAL para que sea más fácil detectar el índice
THUMB_ANGLE_THRESHOLD = 150 

smooth_x, smooth_y = 0, 0
cooldown_click = 0
screen_width, screen_height = pyautogui.size()

# NUEVA VARIABLE: Bloqueo de Puño (Latch)
puno_bloqueado = False 

def calculate_angle(p1, p2, p3):
    v1 = p1 - p2
    v2 = p3 - p2
    dot = np.dot(v1, v2)
    mag = np.linalg.norm(v1) * np.linalg.norm(v2)
    if mag == 0: return 0.0
    cos_angle = np.clip(dot / mag, -1.0, 1.0)
    return np.degrees(np.arccos(cos_angle))

def is_finger_up(tip_y, mid_y, base_y):
    above_mid  = (mid_y  - tip_y) > THRESHOLD
    above_base = (base_y - tip_y) > THRESHOLD
    return above_mid and above_base

def is_thumb_up(hand_landmarks):
    p0 = np.array([hand_landmarks[0].x,  hand_landmarks[0].y])
    p2 = np.array([hand_landmarks[2].x,  hand_landmarks[2].y])
    p4 = np.array([hand_landmarks[4].x,  hand_landmarks[4].y])
    angle = calculate_angle(p0, p2, p4)
    return angle > THUMB_ANGLE_THRESHOLD

def count_fingers(hand_landmarks):
    dedos = [False, False, False, False, False]
    if is_thumb_up(hand_landmarks): dedos[0] = True
    for idx, (tip_idx, mid_idx, base_idx) in enumerate(zip(FINGER_TIPS[1:], FINGER_MID[1:], FINGER_BASES[1:]), start=1):
        tip_y  = hand_landmarks[tip_idx].y
        mid_y  = hand_landmarks[mid_idx].y
        base_y = hand_landmarks[base_idx].y
        if is_finger_up(tip_y, mid_y, base_y):
            dedos[idx] = True
    return dedos

def process_mouse_and_draw(bgr_frame, detection_result):
    global smooth_x, smooth_y, cooldown_click, puno_bloqueado
    annotated = np.copy(bgr_frame)
    h, w, _ = annotated.shape

    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list     = detection_result.handedness

    CONNECTIONS = [
        (0,1),(1,2),(2,3),(3,4), (0,5),(5,6),(6,7),(7,8),
        (0,9),(9,10),(10,11),(11,12), (0,13),(13,14),(14,15),(15,16),
        (0,17),(17,18),(18,19),(19,20), (5,9),(9,13),(13,17)
    ]

    total_fingers = 0
    accion_actual = "Ninguna"

    if cooldown_click > 0: cooldown_click -= 1

    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness     = handedness_list[idx]
        label          = handedness[0].category_name

        points = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]

        dedos_levantados = count_fingers(hand_landmarks)
        cantidad_dedos = sum(dedos_levantados)
        total_fingers += cantidad_dedos

        p_indice = hand_landmarks[8] 
        
        # --- DESBLOQUEO DEL PUÑO ---
        # Si tienes 2 o más dedos levantados, el sistema entiende que ya abriste la mano
        if cantidad_dedos >= 2:
            puno_bloqueado = False

        # --- SELECCIÓN DE ACCIONES ---
        
        # 1. Mover cursor: Índice arriba. Medio, Anular y Meñique ABAJO. (Ignoramos el pulgar)
        if dedos_levantados[1] and not dedos_levantados[2] and not dedos_levantados[3] and not dedos_levantados[4]:
            accion_actual = "MOVER CURSOR"
            target_x = np.interp(p_indice.x, (0.3, 0.7), (0, screen_width))
            target_y = np.interp(p_indice.y, (0.3, 0.7), (0, screen_height))
            smooth_x = smooth_x + (target_x - smooth_x) / 2
            smooth_y = smooth_y + (target_y - smooth_y) / 2
            pyautogui.moveTo(int(smooth_x), int(smooth_y))

        if cooldown_click == 0:
            # 2. Clic Izquierdo: Pulgar e Índice arriba, los demás abajo
            if dedos_levantados[0] and dedos_levantados[1] and not dedos_levantados[2]:
                pyautogui.click()
                cooldown_click = 10
                accion_actual = "CLIC IZQ"

            # 3. Clic Derecho: Pulgar, Índice y Medio arriba
            elif dedos_levantados[0] and dedos_levantados[1] and dedos_levantados[2] and not dedos_levantados[3]:
                pyautogui.rightClick()
                cooldown_click = 15
                accion_actual = "CLIC DER"

            # 4. Doble Clic: Índice y Medio arriba, pulgar abajo
            elif not dedos_levantados[0] and dedos_levantados[1] and dedos_levantados[2] and not dedos_levantados[3]:
                pyautogui.doubleClick()
                cooldown_click = 15
                accion_actual = "DOBLE CLIC"

            # 5. Minimizar Todo: Cero dedos Y el puño no está bloqueado
            elif cantidad_dedos == 0 and not puno_bloqueado:
                pyautogui.hotkey('win', 'd')
                puno_bloqueado = True  # ¡AQUÍ ESTÁ LA MAGIA! Se bloquea hasta que abras la mano
                cooldown_click = 20
                accion_actual = "MINIMIZAR TODO"

        # --- DIBUJAR EN PANTALLA ---
        for start, end in CONNECTIONS:
            cv2.line(annotated, points[start], points[end], (0, 200, 255), 2)
        for i, point in enumerate(points):
            color = (0, 255, 100) if i in FINGER_TIPS else (255, 255, 255)
            cv2.circle(annotated, point, 6, color, -1)
            
    # Panel de control
    overlay = annotated.copy()
    cv2.rectangle(overlay, (10, 10), (320, 90), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, annotated, 0.5, 0, annotated)
    cv2.putText(annotated, f"Dedos: {total_fingers}", (20, 45), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)
    cv2.putText(annotated, f"Accion: {accion_actual}", (20, 80), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)

    return annotated

# --- CONFIGURACIÓN ---
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options, num_hands=1, running_mode=vision.RunningMode.VIDEO
)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
frame_timestamp = 0

while True:
    ret, frame = cap.read()
    if not ret or frame is None or frame.size == 0: continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    detection_result = detector.detect_for_video(mp_image, frame_timestamp)
    frame_timestamp += 1

    output_frame = process_mouse_and_draw(frame, detection_result)
    cv2.imshow("Mouse Virtual Inteligente - FIMAZ", output_frame)

    if cv2.waitKey(5) & 0xFF in [ord('q'), 27]: break

cap.release()
detector.close()
cv2.destroyAllWindows()