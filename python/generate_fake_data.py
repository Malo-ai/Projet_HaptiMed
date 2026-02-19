# generate_fake_data.py - GÉNÉRATEUR DE PARTICIPANTS VIRTUELS
import os
import pandas as pd
import numpy as np
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
META_PATH = os.path.join(BASE_DIR, "data", "metadata.csv")

def add_noise(df):
    """Ajoute un petit tremblement aléatoire pour que le clone ne soit pas parfait"""
    noise_level = 2.0 # 2 pixels de variation
    df['X'] = df['X'] + np.random.normal(0, noise_level, len(df))
    df['Y'] = df['Y'] + np.random.normal(0, noise_level, len(df))
    # On change un peu le temps aussi (vitesse différente)
    speed_factor = np.random.uniform(0.9, 1.1) 
    df['Time_Rel'] = df['Time_Rel'] * speed_factor
    return df

if __name__ == "__main__":
    print("--- GÉNÉRATION DE CLONES ---")
    
    # 1. On cherche les modèles (Vos pilotes actuels)
    try:
        # On suppose que PILOT_01 est Novice et PILOT_02 est Expert
        # (Adaptez les noms si vos fichiers s'appellent autrement)
        novice_src = pd.read_csv(os.path.join(RAW_PATH, "PILOT_01_RAW.csv"))
        expert_src = pd.read_csv(os.path.join(RAW_PATH, "PILOT_02_RAW.csv"))
    except:
        print("ERREUR : Il faut avoir PILOT_01_RAW.csv et PILOT_02_RAW.csv dans data/raw pour cloner.")
        exit()

    new_meta = []

    # 2. Création de 3 Novices Virtuels
    for i in range(1, 4):
        new_id = f"VIRTUAL_NOV_{i:02d}"
        df_clone = novice_src.copy()
        df_clone = add_noise(df_clone)
        df_clone['ID'] = new_id
        
        save_path = os.path.join(RAW_PATH, f"{new_id}_RAW.csv")
        df_clone.to_csv(save_path, index=False)
        new_meta.append({"ID": new_id, "Group": "Novice", "OSATS_Score": np.random.randint(8, 15)})
        print(f"Créé : {new_id}")

    # 3. Création de 3 Experts Virtuels
    for i in range(1, 4):
        new_id = f"VIRTUAL_EXP_{i:02d}"
        df_clone = expert_src.copy()
        df_clone = add_noise(df_clone) # Les experts tremblent aussi un peu
        df_clone['ID'] = new_id
        
        save_path = os.path.join(RAW_PATH, f"{new_id}_RAW.csv")
        df_clone.to_csv(save_path, index=False)
        new_meta.append({"ID": new_id, "Group": "Expert", "OSATS_Score": np.random.randint(22, 30)})
        print(f"Créé : {new_id}")

    # 4. Mise à jour Metadata
    # On lit l'existant
    try:
        current_meta = pd.read_csv(META_PATH, sep=None, engine='python', encoding='utf-8-sig')
    except:
        current_meta = pd.DataFrame(columns=["ID", "Group", "OSATS_Score"])
    
    # On ajoute les nouveaux
    df_new_meta = pd.DataFrame(new_meta)
    final_meta = pd.concat([current_meta, df_new_meta]).drop_duplicates(subset=['ID'], keep='last')
    
    final_meta.to_csv(META_PATH, index=False, encoding='utf-8-sig')
    print("--- TERMINE : Metadata mises à jour ---")