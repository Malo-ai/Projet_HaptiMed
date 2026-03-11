import os
import pandas as pd
import numpy as np
import random

# --- CONFIGURATION ---
BASE_DIR = os.getcwd()
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
META_FILE = os.path.join(BASE_DIR, "data", "metadata.csv")

if not os.path.exists(RAW_DIR): os.makedirs(RAW_DIR)

# 1. CRÉATION DES MÉTADONNÉES (14 Novices, 10 Experts)
participants = []
for i in range(1, 25):
    pid = f"P{i:02d}"
    if i <= 14:
        group, exp = "Novice", round(random.uniform(0.5, 3.0), 1)
    else:
        group, exp = "Expert", round(random.uniform(8.0, 25.0), 1)
    participants.append({"ID": pid, "Group": group, "Experience_Years": exp})

pd.DataFrame(participants).to_csv(META_FILE, index=False)

# 2. GÉNÉRATEUR DE DONNÉES BIOMÉCANIQUES RÉALISTES
def generate_human_data(pid, group):
    rows = []
    fs = 120.0  # On simule une tablette qui envoie 120 points par seconde
    
    for cond in ["VP_FB", "FVP_FB"]:
        if group == "Expert":
            mt_base = random.uniform(2.8, 4.2)
            noise_xy = random.uniform(1.2, 3.5)
            force_jitter = random.uniform(40, 110)
        else:
            mt_base = random.uniform(6.5, 11.0)
            noise_xy = random.uniform(9.0, 22.0)
            force_jitter = random.uniform(500, 1300)

        if "FVP" in cond:
            mt_base *= 1.4
            if group == "Novice": mt_base *= 1.3

        # CALCUL CRUCIAL : Nombre de points basé sur le temps à 120 Hz
        num_points = int(mt_base * fs) 
        t_points = np.linspace(0, mt_base, num_points)
        
        for t in t_points:
            angle = (t / mt_base) * 2 * np.pi
            drift = np.sin(t*2) * 5 if group == "Novice" else 0
            
            rows.append({
                "ID": pid, "Bloc": cond, "Trial_in_Bloc": 1,
                "Time_Abs": 1700000000 + t, "Time_Rel": t,
                "X": 500 + 300 * np.cos(angle) + random.uniform(-noise_xy, noise_xy) + drift,
                "Y": 500 + 300 * np.sin(angle) + random.uniform(-noise_xy, noise_xy) + drift,
                "P_Raw": 3000 + random.normalvariate(0, force_jitter),
                "Thickness": 6, "R": 300, "W": 50
            })
            
    pd.DataFrame(rows).to_csv(os.path.join(RAW_DIR, f"{pid}_RAW.csv"), index=False)

print("⏳ Simulation des 24 chirurgiens en cours...")
for p in participants:
    generate_human_data(p['ID'], p['Group'])
print(f"✅ Terminé ! 24 fichiers RAW 'humanisés' créés dans {RAW_DIR}")