import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import os

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Choisis un fichier RAW de test qui existe encore
FILE_PATH = os.path.join(BASE_DIR, "data", "raw", "PILOT_01_RAW.csv") 

def butter_lowpass_filter(data, cutoff, fs, order=2):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

if __name__ == "__main__":
    if not os.path.exists(FILE_PATH):
        print(f"Erreur : Le fichier {FILE_PATH} n'existe pas. Utilise un nom de fichier présent dans data/raw.")
    else:
        df = pd.read_csv(FILE_PATH)
        # On prend un segment de 5 secondes pour bien voir
        segment = df.head(500) 
        
        raw_x = segment['X'].values
        time = segment['Time_Rel'].values
        fs = 1 / np.mean(np.diff(time))
        
        # Test de deux fréquences de coupure (Cutoff)
        # 10Hz est le standard pour le mouvement humain
        filtered_10 = butter_lowpass_filter(raw_x, 10, fs)
        filtered_5 = butter_lowpass_filter(raw_x, 5, fs)

        plt.figure(figsize=(12, 6))
        plt.plot(time, raw_x, label="Brut (Bruité)", alpha=0.3, color='grey')
        plt.plot(time, filtered_10, label="Filtré 10Hz (Standard)", color='blue', linewidth=2)
        plt.plot(time, filtered_5, label="Filtré 5Hz (Trop lissé ?)", color='red', linestyle='--')
        
        plt.title("Vérification du filtre passe-bas (Signal X)")
        plt.xlabel("Temps (s)")
        plt.ylabel("Position X (px)")
        plt.legend()
        plt.grid(True)
        
        print(f"Graphique généré. Fréquence d'échantillonnage détectée : {fs:.1f} Hz")
        plt.show()