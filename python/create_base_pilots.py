import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
if not os.path.exists(RAW_PATH): os.makedirs(RAW_PATH)

def create_dummy_pilot(filename, p_id, noise_level):
    fs = 120 # 120 Hz
    t = np.linspace(0, 5, 5 * fs) # 5 secondes de mouvement
    
    # Simulation d'un mouvement circulaire avec plus ou moins de tremblement (bruit)
    x = 400 + 150 * np.sin(2 * np.pi * 0.5 * t) + np.random.normal(0, noise_level, len(t))
    y = 300 + 150 * np.cos(2 * np.pi * 0.5 * t) + np.random.normal(0, noise_level, len(t))
    p = 3000 + np.random.normal(0, 100, len(t)) # Pression simulée
    
    df = pd.DataFrame({
        'ID': [p_id]*len(t),
        'Time_Abs': t + 1600000000,
        'Time_Rel': t,
        'X': x,
        'Y': y,
        'P_Raw': p,
        'Thickness': [4]*len(t),
        'Bloc': ['VP']*len(t),
        'Trial_in_Bloc': [1]*len(t),
        'R': [250]*len(t),
        'W': [100]*len(t)
    })
    
    filepath = os.path.join(RAW_PATH, filename)
    df.to_csv(filepath, index=False)
    print(f"[OK] Fichier de base généré : {filename}")

if __name__ == "__main__":
    print("--- CRÉATION DES PILOTES DE BASE ---")
    # PILOT 01 : Bruit fort (Novice)
    create_dummy_pilot("PILOT_01_RAW.csv", "PILOT_01", noise_level=8.0)
    # PILOT 02 : Bruit faible (Expert)
    create_dummy_pilot("PILOT_02_RAW.csv", "PILOT_02", noise_level=1.5)
    print("\nParfait ! Vous pouvez maintenant lancer la génération des clones.")