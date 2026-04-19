# process_data.py - VERSION ABSOLUE (Zéro Erreur + Jerk Haptique + Double Erreur)
import os
import glob
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
from scipy import stats 

# ==========================================
# 1. CONFIGURATION DES CHEMINS ET SEUILS
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
CLEAN_PATH = os.path.join(BASE_DIR, "data", "clean")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "features")

# Seuils de Qualité Biomécanique
CONTACT_THRESHOLD = 100   # Seuil de pression brute
MAX_LOSS_RATIO = 0.10     # Rejet si > 10% de perte de contact
MAX_BACKTRACK_RATIO = 0.15 # Rejet si > 15% de backtracking
FORCE_TOLERANCE = 0.15    # Tolérance d'erreur haptique (+/- 15%)

for p in [CLEAN_PATH, OUTPUT_PATH]:
    if not os.path.exists(p): 
        os.makedirs(p)

# ==========================================
# 2. FONCTIONS MATHÉMATIQUES ET FILTRAGE
# ==========================================
def butter_lowpass_filter(data, cutoff, fs, order=2):
    if len(data) < 15: return data 
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

def get_kinematics(x, y, dt):
    vx = np.gradient(x, dt); vy = np.gradient(y, dt)
    ax = np.gradient(vx, dt); ay = np.gradient(vy, dt)
    jx = np.gradient(ax, dt); jy = np.gradient(ay, dt)
    velocity = np.sqrt(vx**2 + vy**2)
    jerk = np.sqrt(jx**2 + jy**2)
    return velocity, jerk

def calculate_f95(data, fs):
    n = len(data)
    if n < 2: return 0
    fft_vals = np.fft.fft(data)
    psd = np.abs(fft_vals)**2
    freqs = np.fft.fftfreq(n, d=1/fs)
    pos = freqs > 0
    f, p = freqs[pos], psd[pos]
    if len(p) == 0: return 0
    cum = np.cumsum(p)
    idx = np.searchsorted(cum, 0.95 * cum[-1])
    return f[idx] if idx < len(f) else f[-1]

# ==========================================
# 3. TRAITEMENT D'UN ESSAI UNIQUE
# ==========================================
def process_single_trial(df_trial, info_dict, pid):
    time = df_trial['Time_Abs'].values
    if len(time) < 15: return None
        
    dt = np.mean(np.diff(time))
    fs = 1 / dt if dt > 0 else 125.0

    # --- A. VERROUS DE SÉCURITÉ ---
    p_raw = df_trial['P_Raw'].values if 'P_Raw' in df_trial.columns else np.zeros(len(time))
    mask_contact = p_raw > CONTACT_THRESHOLD
    if (1 - (np.sum(mask_contact) / len(p_raw))) > MAX_LOSS_RATIO:
        return None

    if 'Angle' in df_trial.columns:
        diffs = np.diff(df_trial['Angle'].values)
        diffs = (diffs + np.pi) % (2 * np.pi) - np.pi
        main_dir = 1 if np.mean(diffs) > 0 else -1
        if np.mean((diffs * main_dir) < 0) > MAX_BACKTRACK_RATIO:
            return None

    # --- B. CALCULS CINÉMATIQUES ---
    x_clean = df_trial['X'].values
    y_clean = df_trial['Y'].values
    vel, jerk = get_kinematics(x_clean, y_clean, dt)
    
    duration = time[-1] - time[0]
    path_length = np.sum(np.sqrt(np.diff(x_clean)**2 + np.diff(y_clean)**2))
    
    # Fluidité (LDLJ) Inversé
    integral_jerk_sq = np.sum(jerk**2) * dt
    ldlj = -np.log((duration**5 / path_length**2) * integral_jerk_sq) if path_length > 0 else 0
        
    # ISO 9241-9
    cx, cy = (x_clean.max() + x_clean.min()) / 2, (y_clean.max() + y_clean.min()) / 2
    Ri = np.sqrt((x_clean - cx)**2 + (y_clean - cy)**2)
    Re, sigma_R = np.mean(Ri), np.std(Ri)
    Te = 4.133 * sigma_R
    IDe = np.log2((2 * np.pi * Re) / Te) if Te > 0 else 0
    IPe = IDe / duration if duration > 0 else 0
    
    # --- C. CALCULS HAPTIQUES ET ERREURS (DOUBLE TÂCHE) ---
    p_valid = p_raw[mask_contact]
    condition = str(df_trial['Bloc'].iloc[0])
    
    error_pos = np.mean(np.abs(Ri - df_trial['R'].iloc[0]) > (df_trial['W'].iloc[0]/2)) * 100
    
    if 'FVP' in condition and len(p_valid) > 2:
        force_mean = np.mean(p_valid)
        force_sd = np.std(p_valid)
        
        # Jerk Haptique (Dérivée seconde de la pression)
        force_velocity = np.gradient(p_valid, dt)
        force_jerk_arr = np.gradient(force_velocity, dt)
        force_jerk = np.sqrt(np.mean(force_jerk_arr**2)) # Valeur RMS
        
        # Erreur Haptique (% du temps en dehors d'une zone de tolérance)
        if 'P_Target' in df_trial.columns:
            target = df_trial['P_Target'].iloc[0]
            error_force = np.mean(np.abs(p_valid - target) > (FORCE_TOLERANCE * target)) * 100
        else:
            # Si pas de cible absolue, on évalue l'incapacité à maintenir SA propre moyenne stable
            error_force = np.mean(np.abs(p_valid - force_mean) > (FORCE_TOLERANCE * force_mean)) * 100
    else:
        force_mean = 0
        force_sd = 0
        force_jerk = 0
        error_force = 0

    # --- D. DICTIONNAIRE COMPLET ---
    return {
        'ID': pid, 'Condition': condition, 'Task_Type': condition,
        'Trial': df_trial['Trial_in_Bloc'].iloc[0] if 'Trial_in_Bloc' in df_trial.columns else 0,
        'Age': info_dict.get('age', np.nan),
        'Lateralite': info_dict.get('lateralite', 'Unknown'),
        'Statut_Principal': info_dict.get('statut_principal', 'Unknown'),
        'Sous_Statut': info_dict.get('sous_statut', 'na'),
        'Annee_Apprentissage': info_dict.get('annee_apprentissage', 'na'),
        'Annees_Pratique': info_dict.get('annees_pratique', 'na'),
        'Specialite': info_dict.get('specialite', 'na'),
        'Sommeil_h': info_dict.get('sommeil_h', np.nan),
        'Fatigue_EVA': info_dict.get('fatigue_eva', np.nan),
        'Cafe_24h': info_dict.get('cafe_24h', np.nan),
        'Jeux_Video': info_dict.get('jeux_video', 'Unknown'),
        'IPe': IPe, 'Duration': duration, 'LDLJ': ldlj,
        'Force_Mean': force_mean, 'Force_SD': force_sd, 'Force_Jerk': force_jerk,
        'Error_Pos': error_pos, 'Error_Force': error_force,
        'Path_Length': path_length, 'Mean_Velocity': np.mean(vel), 'F95': calculate_f95(Ri, fs), 'IDe': IDe, 'Te': Te
    }

# ==========================================
# 4. BOUCLE PRINCIPALE
# ==========================================
if __name__ == "__main__":
    print("--- DÉMARRAGE DU TRAITEMENT SCIENTIFIQUE ---")
    raw_files = glob.glob(os.path.join(RAW_PATH, "*_RAW.csv"))
    all_features = []
    rejection_log = []

    for f in raw_files:
        try:
            df = pd.read_csv(f)
            pid = str(df['ID'].iloc[0]).strip().upper()
            info_file = os.path.join(RAW_PATH, f"{pid}_INFO.csv")
            info_dict = pd.read_csv(info_file).iloc[0].to_dict() if os.path.exists(info_file) else {}

            dt_avg = np.mean(np.diff(df['Time_Abs'].values))
            fs = 1/dt_avg if dt_avg > 0 else 125.0
            df_clean = df.copy()
            
            # Application du filtre Butterworth
            for c in ['X', 'Y', 'P_Raw']:
                if c in df.columns: df_clean[c] = butter_lowpass_filter(df[c].values, 10, fs)
            
            df_clean.to_csv(os.path.join(CLEAN_PATH, f"{pid}_CLEAN.csv"), index=False)

            for (bloc, tr), data_essai in df_clean.groupby(['Bloc', 'Trial_in_Bloc']):
                feat = process_single_trial(data_essai, info_dict, pid)
                if feat is not None:
                    all_features.append(feat)
                else:
                    p_raw = data_essai['P_Raw'].values
                    loss = 1 - (np.sum(p_raw > 100) / len(p_raw))
                    reason = "Backtracking" if loss <= 0.10 else f"Perte Contact ({loss:.1%})"
                    rejection_log.append({'ID': pid, 'Condition': bloc, 'Trial': tr, 'Raison': reason})
            
            print(f"-> Sujet {pid} : Terminé")
        except Exception as e: print(f"!! Erreur {f}: {e}")

    # --- CALCUL DE FITTS (Be) ET SAUVEGARDE ---
    if all_features:
        df_res = pd.DataFrame(all_features)
        df_res['Be'] = 0.0
        for (pid, task), sub in df_res.groupby(['ID', 'Task_Type']):
            if len(sub) > 2 and sub['IDe'].nunique() > 1:
                slope, _, _, _, _ = stats.linregress(sub['IDe'], sub['Duration'])
                df_res.loc[(df_res['ID']==pid) & (df_res['Task_Type']==task), 'Be'] = slope
        
        # SAUVEGARDE DATASET
        df_res.to_csv(os.path.join(OUTPUT_PATH, "dataset_features.csv"), index=False)
        print(f"\nFINI ! {len(df_res)} essais compilés avec Double Erreur et Force Jerk.")
        
    # --- SAUVEGARDE LOG ---
    if rejection_log:
        pd.DataFrame(rejection_log).to_csv(os.path.join(OUTPUT_PATH, "rejection_log.csv"), index=False)
        print(f"RAPPORT : {len(rejection_log)} rejets notés.")