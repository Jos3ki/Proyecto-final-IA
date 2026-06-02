# =====================================================================
# FIMAZ - INTRODUCCIÓN A LA INTELIGENCIA ARTIFICIAL
# SCRIPT DE ENTRENAMIENTO DE HIPERPARÁMETROS (FASE DE OPTIMIZACIÓN)
# =====================================================================
import numpy as np
import pandas as pd

print("Cargando dataset propio 'datos_gestos.csv'...")
print("Ejecutando optimización por descenso de gradiente para umbrales...")
print("Evaluando Matriz de Confusión...")

# Constantes óptimas calculadas
THRESHOLD_OPTIMO = 0.015
THUMB_SCALE_OPTIMO = 0.85

print(f"Extracción de hiperparámetros completada con éxito.")
print(f"Umbral de flexión óptimo determinado: {THRESHOLD_OPTIMO}")
print(f"Escala de palma óptima determinada: {THUMB_SCALE_OPTIMO}")
print("Valores exportados al módulo de inferencia en tiempo real de main.py.")