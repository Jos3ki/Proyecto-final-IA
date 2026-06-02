import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- OPTIMIZACIÓN CRÍTICA ---
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.0  

MARGIN = 10
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)

FINGER_TIPS  = [4,  8,  12, 16, 20]
FINGER_MID   = [3,  7,  11, 15, 19]
FINGER_BASES = [2,  6,  10, 14, 18]
THRESHOLD = 0.015           

smooth_x, smooth_y = 0, 0
cooldown_click = 0
screen_width, screen_height = pyautogui.size()
puno_bloqueado = False 

# NUEVAS VARIABLES PARA EL DOBLE CLIC Y CLICS FANTASMAS
estado_pellizco_anterior = False
tiempo_ultimo_clic = 0.0

def is_finger_up(tip_y, mid_y, base_y):
    above_mid  = (mid_y  - tip_y) > THRESHOLD
    above_base = (base_y - tip_y) > THRESHOLD
    return above_mid and above_base

def count_fingers(hand_landmarks):
    dedos = [False, False, False, False, False]
    ancho_palma = np.hypot(hand_landmarks[5].x - hand_landmarks[17].x, hand_landmarks[5].y - hand_landmarks[17].y)
    distancia_pulgar = np.hypot(hand_landmarks[4].x - hand_landmarks[17].x, hand_landmarks[4].y - hand_landmarks[17].y)
    
    # UMBRAL MÁS ESTRICTO PARA CONGELAR EL CURSOR (Evita que se trabe por accidente)
    pulgar_muy_extendido = distancia_pulgar > (ancho_palma * 1.5)
    if pulgar_muy_extendido:
        dedos[0] = True

    for idx, (tip_idx, mid_idx, base_idx) in enumerate(zip(FINGER_TIPS[1:], FINGER_MID[1:], FINGER_BASES[1:]), start=1):
        tip_y  = hand_landmarks[tip_idx].y
        mid_y  = hand_landmarks[mid_idx].y
        base_y = hand_landmarks[base_idx].y
        if is_finger_up(tip_y, mid_y, base_y):
            dedos[idx] = True
            
    return dedos, ancho_palma

def process_mouse_and_draw(bgr_frame, detection_result):
    global smooth_x, smooth_y, cooldown_click, puno_bloqueado
    global estado_pellizco_anterior, tiempo_ultimo_clic
    
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

        dedos_levantados, ancho_palma = count_fingers(hand_landmarks)
        cantidad_dedos = sum(dedos_levantados)
        total_fingers += cantidad_dedos

        p_pulgar = hand_landmarks[4]
        p_indice = hand_landmarks[8] 
        
        # LÓGICA DE PELLIZCO
        distancia_pinza = np.hypot(p_indice.x - p_pulgar.x, p_indice.y - p_pulgar.y)
        es_pellizco = distancia_pinza < (ancho_palma * 0.35)
        
        if cantidad_dedos >= 2: puno_bloqueado = False

        # --- 1. MOVER CURSOR (Fluido y sin trabas) ---
        # Solo se detiene si realmente estiras el pulgar hacia afuera (dedos_levantados[0] = True)
        if dedos_levantados[1] and not dedos_levantados[0] and not es_pellizco and not dedos_levantados[2]:
            accion_actual = "MOVER CURSOR"
            # Ampliamos la sensibilidad para llegar a las esquinas fácil (0.2 a 0.8)
            target_x = np.interp(p_indice.x, (0.2, 0.8), (0, screen_width))
            target_y = np.interp(p_indice.y, (0.2, 0.8), (0, screen_height))
            
            smooth_x = smooth_x + (target_x - smooth_x) / 5
            smooth_y = smooth_y + (target_y - smooth_y) / 5
            pyautogui.moveTo(int(smooth_x), int(smooth_y))

        # --- 2. LÓGICA DE CLICS CON MEMORIA (Adiós clics fantasmas y hola Doble Clic) ---
        if es_pellizco and not estado_pellizco_anterior and not dedos_levantados[2]:
            tiempo_actual = time.time()
            
            # Si pasaron menos de 0.5 segundos desde el último clic, es un DOBLE CLIC
            if (tiempo_actual - tiempo_ultimo_clic) < 0.5:
                pyautogui.doubleClick()
                accion_actual = "DOBLE CLIC!"
                tiempo_ultimo_clic = 0.0  # Reseteamos el contador
            else:
                # Si es el primer pellizco, es un CLIC SENCILLO
                pyautogui.click()
                accion_actual = "CLIC IZQUIERDO"
                tiempo_ultimo_clic = tiempo_actual
                
        # Guardamos el estado para el siguiente frame (Flanco de subida)
        estado_pellizco_anterior = es_pellizco

        if cooldown_click == 0:
            # 3. CONGELADO (APUNTA): Índice arriba y Pulgar ESTIRADO (pistola)
            if dedos_levantados[1] and dedos_levantados[0] and not es_pellizco and not dedos_levantados[2]:
                accion_actual = "CONGELADO (Apunta)"

            # 4. CLIC DERECHO: Pulgar, Índice y Medio arriba
            elif dedos_levantados[0] and dedos_levantados[1] and dedos_levantados[2]:
                pyautogui.rightClick()
                cooldown_click = 15
                accion_actual = "CLIC DERECHO"

            # 5. MINIMIZAR TODO (Puño cerrado)
            elif cantidad_dedos == 0 and not puno_bloqueado and not es_pellizco:
                pyautogui.hotkey('win', 'd')
                puno_bloqueado = True  
                cooldown_click = 20
                accion_actual = "MINIMIZAR TODO"

        # --- DIBUJAR EN PANTALLA ---
        for start, end in CONNECTIONS:
            cv2.line(annotated, points[start], points[end], (0, 200, 255), 2)
        for i, point in enumerate(points):
            color = (0, 255, 100) if i in FINGER_TIPS else (255, 255, 255)
            if es_pellizco and i in [4, 8]: color = (0, 0, 255) # Rojo al pellizcar
            cv2.circle(annotated, point, 6, color, -1)
            
    # Panel de control
    overlay = annotated.copy()
    cv2.rectangle(overlay, (10, 10), (380, 90), (0, 0, 0), -1)
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
    cv2.imshow("Mouse Virtual Inteligente - Proyecto Final", output_frame)

    if cv2.waitKey(5) & 0xFF in [ord('q'), 27]: break

cap.release()
detector.close()
cv2.destroyAllWindows()