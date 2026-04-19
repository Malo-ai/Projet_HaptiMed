# 11_h3_3d_master_signature.py - VOLUME D'INTERFÉRENCE ET SUPERPOSITION CHRONO
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy import stats
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEAN_PATH = os.path.join(BASE_DIR, "data", "clean")
FEATURES_FILE = os.path.join(BASE_DIR, "data", "features", "dataset_features.csv")
OUT_DIR = os.path.join(BASE_DIR, "results")

if not os.path.exists(OUT_DIR): os.makedirs(OUT_DIR)

TARGET_FORCE = 3200.0
CX, CY = 960.0, 540.0 

def calculate_ellipsoid_volume(x_err, y_err, z_err):
    """Calcule le volume de l'ellipsoïde de confiance à 95% (k^2 = 7.81 pour 3 DF)."""
    if len(x_err) < 10: return np.nan
    data = np.stack((x_err, y_err, z_err), axis=0)
    cov = np.cov(data)
    det_cov = np.linalg.det(cov)
    if det_cov <= 0: return 0.0
    # Formule : (4/3) * pi * sqrt( (k^2)^3 * det(Cov) )
    volume = (4/3) * np.pi * np.sqrt((7.81**3) * det_cov)
    return volume

def run_master_3d():
    print("--- H3 : ANALYSE MASTER SIGNATURE 3D (VOLUME & TEMPS) ---")
    df_meta = pd.read_csv(FEATURES_FILE)
    df_meta = df_meta[df_meta['ID'] != 'P2VAFA']

    results = []
    clean_files = glob.glob(os.path.join(CLEAN_PATH, "*_CLEAN.csv"))

    # Préparation de la figure pour la visualisation
    fig = plt.figure(figsize=(22, 12))
    groups = ['Naïf', 'Novice', 'Expert']
    
    # Dictionnaire pour stocker un sujet représentatif par groupe pour le plot
    plot_samples = {g: None for g in groups}

    # 1. BOUCLE DE CALCUL DES VOLUMES (SUR TOUS LES SUJETS)
    for f in clean_files:
        df = pd.read_csv(f)
        if df.empty: continue
        pid = str(df['ID'].iloc[0]).strip().upper()
        if pid == 'P2VAFA': continue

        df_fvp = df[df['Bloc'].str.contains('FVP')].copy()
        for (bloc, tr), data in df_fvp.groupby(['Bloc', 'Trial_in_Bloc']):
            # Identification du groupe
            meta = df_meta[(df_meta['ID'] == pid) & (df_meta['Condition'] == bloc) & (df_meta['Trial'] == tr)]
            if meta.empty: continue
            
            group = 'Naïf' if 'non domaine' in str(meta['Statut_Principal'].iloc[0]).lower() else \
                    ('Expert' if 'diplômé' in str(meta['Sous_Statut'].iloc[0]).lower() else 'Novice')
            
            fb_cond = "Sans Feedback" if "NoFB" in str(bloc) else "Avec Feedback"

            # Calcul des erreurs
            z_err = data['P_Raw'].values - TARGET_FORCE
            x_err = data['Err_Radiale'].values * np.cos(data['Angle'].values)
            y_err = data['Err_Radiale'].values * np.sin(data['Angle'].values)
            
            vol = calculate_ellipsoid_volume(x_err, y_err, z_err)
            results.append({'ID': pid, 'Group': group, 'Condition': fb_cond, 'Volume': vol})
            
            # Garder un sujet de chaque groupe pour la démo visuelle
            if plot_samples[group] is None and fb_cond == "Avec Feedback":
                plot_samples[group] = pid

    # 2. GÉNÉRATION DES GRAPHIQUES (SUPERPOSITION DES 10 ESSAIS)
    for i, group in enumerate(groups):
        pid = plot_samples[group]
        if not pid: continue
        
        ax = fig.add_subplot(1, 3, i+1, projection='3d')
        df_subj = pd.read_csv(glob.glob(os.path.join(CLEAN_PATH, f"{pid}*_CLEAN.csv"))[0])
        df_fvp = df_subj[df_subj['Bloc'].str.contains('FVP')]

        for tr_no in range(1, 11):
            trial = df_fvp[df_fvp['Trial_in_Bloc'] == tr_no]
            if trial.empty: continue
            
            z_err = trial['P_Raw'].values - TARGET_FORCE
            x_err = trial['Err_Radiale'].values * np.cos(trial['Angle'].values)
            y_err = trial['Err_Radiale'].values * np.sin(trial['Angle'].values)
            
            # Gradient de temps pour chaque essai
            time_colors = plt.cm.viridis(np.linspace(0, 1, len(trial)))
            ax.scatter(x_err, y_err, z_err, c=time_colors, s=1, alpha=0.15)

        ax.scatter(0, 0, 0, color='red', s=100, marker='*', label="Cible")
        ax.set_title(f"Signature : {group} (10 essais superposés)\nID: {pid}", weight='bold')
        ax.set_xlim(-15, 15); ax.set_ylim(-15, 15); ax.set_zlim(-1500, 1500)
        ax.view_init(elev=20, azim=45)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "Fig11_Master_3D_Superposition.png"), dpi=300)

    # 3. EXPORT DU TABLEAU APA
    df_res = pd.DataFrame(results)
    df_agg = df_res.groupby(['ID', 'Group', 'Condition']).mean(numeric_only=True).reset_index()
    
    table_path = os.path.join(OUT_DIR, "Tableau4_Volume_Interference_APA.txt")
    with open(table_path, "w", encoding="utf-8") as f_out:
        f_out.write("Tableau 4. Volume d'Interférence 3D (Espace x Force)\n")
        f_out.write("="*100 + "\n")
        f_out.write(f"{'Condition':<15} | {'Naïf':<20} | {'Novice':<20} | {'Expert':<20}\n")
        f_out.write("-"*100 + "\n")
        for cond in ["Avec Feedback", "Sans Feedback"]:
            row = [cond]
            for g in groups:
                vals = df_agg[(df_agg['Group'] == g) & (df_agg['Condition'] == cond)]['Volume']
                row.append(f"{vals.mean():.0f} ± {vals.std():.0f}")
            f_out.write(f"{row[0]:<15} | {row[1]:<20} | {row[2]:<20} | {row[3]:<20}\n")
        f_out.write("="*100 + "\n")
    
    print(f"✅ Analyse Master terminée. Fichiers dans : {OUT_DIR}")

if __name__ == "__main__":
    run_master_3d()