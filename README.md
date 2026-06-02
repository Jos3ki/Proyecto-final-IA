# 🖱️ Mouse Virtual Inteligente basado en Visión Artificial (NUI)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=for-the-badge&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Tasks-orange?style=for-the-badge)

## 🏛️ Información Académica

**Universidad Autónoma de Sinaloa (UAS) - Facultad de Informática Mazatlán (FIMAZ)**

- **Materia:** Introducción a la Inteligencia Artificial
- **Docente:** Dra. Alma Yadira Quiñones
- **Ciclo Escolar:** 2025 - 2026

### 👨‍💻 Equipo de Desarrollo

- José Carlos Castillo Padilla
- José Gerardo Sánchez Rodríguez
- Carlos Said Sánchez Domínguez
- Salvador Reynoso Villaverde
- Abdel Karim Gonzales Álvarez

---

## 📖 Descripción del Proyecto

Este proyecto implementa una **Interfaz Natural de Usuario (NUI)** que permite controlar el sistema operativo mediante gestos manuales capturados en tiempo real a través de una cámara web. Su objetivo principal es reducir la brecha digital y ofrecer una alternativa de accesibilidad "touchless" para personas con discapacidades motrices menores o para expositores en entornos educativos.

Utilizando técnicas de **Visión Artificial y Aprendizaje por Transferencia (Transfer Learning)**, el sistema extrae una malla tridimensional de 21 puntos clave (landmarks) de la mano y procesa su geometría espacial para traducir movimientos físicos en llamadas a la API del sistema operativo.

## ✨ Características Principales y Gestos

El algoritmo cuenta con una máquina de estados optimizada para evitar fluctuaciones (_jitter_) e incorpora detección de flancos para los eventos de clic.

| Gesto Físico                       | Acción en Pantalla | Lógica de Control                                                    |
| :--------------------------------- | :----------------- | :------------------------------------------------------------------- |
| **Índice arriba, Pulgar relajado** | Mover Cursor       | Mapeo mediante _Virtual Bounding Box_ al 65% del FOV para ergonomía. |
| **Pellizco (Índice y Pulgar)**     | Clic Izquierdo     | Cálculo de distancia Euclidiana escalada al tamaño de la palma.      |
| **Doble Pellizco Rápido**          | Doble Clic         | Ventana de tiempo (Edge Detection) < 0.5s entre flancos de subida.   |
| **Pulgar, Índice y Medio arriba**  | Clic Derecho       | Reconocimiento por elevación sobre el eje Y superando el umbral.     |
| **Gesto de "L" / Pistola**         | Congelar Cursor    | Activación de zona muerta (Histéresis) para precisión de puntería.   |
| **Puño Cerrado**                   | Minimizar Todo     | Atajo nativo de Windows. Cuenta con bloqueo (Latch) anti-spam.       |

## 🛠️ Arquitectura y Tecnologías

1. **Google MediaPipe (Tasks API):** Extractor de características basado en Redes Neuronales Convolucionales (CNN) ligeras.
2. **OpenCV (cv2):** Captura, procesamiento matricial de cuadros de video y renderizado de la interfaz visual en pantalla.
3. **PyAutoGUI:** Integración de bajo nivel para inyectar eventos de teclado y mouse directamente en el SO.
4. **NumPy:** Procesamiento vectorial acelerado para calcular distancias, normas euclidianas e interpolación de coordenadas.
5. **Tkinter:** Renderizado de un _Overlay_ de sistema (Widget Flotante persistente) que no se minimiza, garantizando UX continua.

## 🚀 Instalación y Uso

### Requisitos previos

Se recomienda crear un entorno virtual (`venv` o `conda`) antes de instalar las dependencias.

```bash
# Clonar el repositorio
git clone [https://github.com/Jos3ki/Proyecto-final-IA](https://github.com/Jos3ki/Proyecto-final-IA)
cd TU_REPOSITORIO

# Instalar librerías requeridas
pip install opencv-python mediapipe numpy pyautogui

Ejecución
Para iniciar el sistema de IA, ejecuta el script principal desde la terminal:

Bash
python main.py
(Nota: Asegúrate de tener una cámara web conectada y funcional, y de contar con buena iluminación frontal para optimizar la inferencia del modelo).
```

"Por optimización de recursos en la arquitectura NUI, se optó por un enfoque de Hard-Coded Heuristic Classification (Clasificación Heurística Rígida). Las fronteras de decisión y los umbrales geométricos que se observan en el código final (THRESHOLD = 0.015, ancho_palma * 0.85) no fueron puestos al azar; fueron los hiperparámetros óptimos resultantes de nuestro entrenamiento previo local."

## 📈 Limitaciones y Trabajo Futuro

Sensibilidad a la luz: El modelo pre-entrenado presenta una ligera caída en la exactitud en entornos con bajo contraste o retroiluminación extrema.

Futuras implementaciones: Se planea expandir la matriz de gestos para incluir funciones complejas de navegación (Scroll vertical, arrastrar y soltar) y habilitar la calibración paramétrica directamente desde el widget flotante.

Desarrollado en Mazatlán, Sinaloa. Proyecto de la materia de Introducción a la Inteligencia Artificial.
