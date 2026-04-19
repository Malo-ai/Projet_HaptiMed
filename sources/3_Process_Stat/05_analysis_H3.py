# 10_h3_ellipse_interaction.py - ANALYSE DE L'ELLIPSE DE CONFIANCE (COUPLAGE FORCE-ESPACE)
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import signal, stats
from matplotlib.patches import Ellipse
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# --- CONFIGURATION DES CHEMINS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEAN_PATH = os.path.join(BASE_DIR, "data", "clean")
FEATURES_FILE = os.path.join(BASE_DIR, "data", "features", "dataset_features.csv")
OUT_DIR = os.path.join(BASE_DIR, "results")

if not os.path.exists(OUT_DIR): os.makedirs(OUT_DIR)
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

# --- PARAMÈTRES ---
TARGET_FORCE = 3200.0
CIRCLE_RADIUS = 350.0

def calculate_confidence_ellipse_area(force_err, spatial_err, confidence=0.95):
    """
    Calcule l'aire de l'ellipse de confiance à 95% pour un nuage de points 2D.
    Formule basée sur la distribution du Chi-deux (p=0.95, df=2) -> k^2 = 5.991
    """
    if len(force_err) < 5: return np.nan
    
    # Matrice de covariance
    x = np.stack((force_err, spatial_err), axis=0)
    cov = np.cov(x)
    
    # Calcul de l'aire via le déterminant : Area = pi * k^2 * sqrt(det(Cov))
    # k^2 pour 95% est approximativement 5.991
    det_cov = np.linalg.det(cov)
    if det_cov <= 0: return 0.0
    
    area = np.pi * 5.991 * np.sqrt(det_cov)
    return area

def analyze_ellipse_interaction():
    print("--- H3 : ANALYSE DE L'INTERACTION (ELLIPSE DE CONFIANCE 95%) ---\n")
    try:
        df_valid = pd.read_csv(FEATURES_FILE)
        df_valid = df_valid[df_valid['ID'] != 'P2VAFA']
        valid_keys = set(zip(df_valid['ID'].astype(str), df_valid['Condition'].astype(str), df_valid['Trial'].astype(int)))
    except Exception as e:
        print(f"⚠️ Erreur métadonnées : {e}")
        return

    clean_files = glob.glob(os.path.join(CLEAN_PATH, "*_CLEAN.csv"))
    results = []

    for f in clean_files:
        df_trial = pd.read_csv(f)
        if df_trial.empty: continue
        
        pid = str(df_trial['ID'].iloc[0]).strip().upper()
        if pid == 'P2VAFA': continue

        df_fvp = df_trial[df_trial['Bloc'].str.contains('FVP')].copy()
        for (bloc, tr), data in df_fvp.groupby(['Bloc', 'Trial_in_Bloc']):
            if (pid, str(bloc), int(tr)) not in valid_keys: continue

            fb_cond = "Sans Feedback" if "NoFB" in str(bloc) else "Avec Feedback"
            row_meta = df_valid[(df_valid['ID'] == pid) & (df_valid['Condition'] == bloc) & (df_valid['Trial'] == tr)].iloc[0]
            statut = str(row_meta['Statut_Principal']).lower()
            sous_statut = str(row_meta['Sous_Statut']).lower()
            
            if 'non domaine' in statut: group = 'Naïf'
            elif 'diplômé' in sous_statut: group = 'Expert'
            else: group = 'Novice'

            # Calcul des erreurs résiduelles (en valeur absolue)
            f_err = np.abs(data['P_Raw'].values - TARGET_FORCE)
            s_err = data['Err_Radiale'].values # Déjà en valeur absolue dans vos données
            
            # Rognage 5%
            trim = int(len(f_err) * 0.05)
            f_err, s_err = f_err[trim:-trim], s_err[trim:-trim]
            
            area = calculate_confidence_ellipse_area(f_err, s_err)
            
            if not np.isnan(area):
                results.append({'ID': pid, 'Group': group, 'Condition': fb_cond, 'Ellipse_Area': area})

    df_res = pd.DataFrame(results)
    if df_res.empty: return
    
    df_agg = df_res.groupby(['ID', 'Group', 'Condition']).mean(numeric_only=True).reset_index()
    order_groups = ['Naïf', 'Novice', 'Expert']
    df_plot = df_agg[df_agg['Group'].isin(order_groups)].copy()

    # --- EXPORT DU TABLEAU ---
    table_path = os.path.join(OUT_DIR, "Tableau3_Ellipse_Interaction.txt")
    with open(table_path, "w", encoding="utf-8") as f_out:
        def log(text):
            print(text); f_out.write(text + "\n")

        log("Tableau 3. Aire de l'Ellipse de Dispersion (Interaction Force x Espace)")
        log("=" * 110)
        log(f"{'Condition':<15} | {'Naïf':<20} | {'Novice':<20} | {'Expert':<20} | {'p (Nov vs Exp)':<15}")
        log("-" * 110)
        
        for cond in ["Avec Feedback", "Sans Feedback"]:
            df_c = df_plot[df_plot['Condition'] == cond]
            vals = {g: df_c[df_c['Group'] == g]['Ellipse_Area'].values for g in order_groups}
            
            res_str = [f"{np.mean(vals[g]):.0f} ± {np.std(vals[g]):.0f}" if len(vals[g]) > 0 else "N/A" for g in order_groups]
            
            p_val = "N/A"
            if len(vals['Novice']) > 0 and len(vals['Expert']) > 0:
                _, p = stats.mannwhitneyu(vals['Novice'], vals['Expert'])
                p_val = f"{str(round(p, 3)).lstrip('0') if p>=0.001 else '< .001'} {'ns' if p>=0.05 else '*'}"
            
            log(f"{cond:<15} | {res_str[0]:<20} | {res_str[1]:<20} | {res_str[2]:<20} | {p_val:<15}")
        log("=" * 110)

    # --- GRAPHIQUE ---
    plt.figure(figsize=(10, 7))
    palette = {'Avec Feedback': '#2ecc71', 'Sans Feedback': '#e74c3c'}
    
    sns.boxplot(x='Group', y='Ellipse_Area', hue='Condition', data=df_plot, order=order_groups, 
                palette=palette, showfliers=False, width=0.6)
    sns.stripplot(x='Group', y='Ellipse_Area', hue='Condition', data=df_plot, order=order_groups, 
                  palette=palette, dodge=True, alpha=0.5, jitter=True)
    
    plt.title("H3 : Stabilité Combinée (Aire de l'Ellipse de Dispersion)", weight='bold', pad=20)
    plt.ylabel("Surface de dispersion (Unités Force x pixels)")
    plt.xlabel("")
    
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "Fig10_Ellipse_Interaction.png"), dpi=300)
    print(f"\n✅ Analyse de l'interaction terminée. Fichiers dans {OUT_DIR}")

if __name__ == "__main__":
    analyze_ellipse_interaction()