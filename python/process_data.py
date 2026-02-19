# process_data.py - VERSION FINALE (Sauvegarde CLEAN + Toutes Métriques LDLJ/F95/ISO)
import os
import glob
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
CLEAN_PATH = os.path.join(BASE_DIR, "data", "clean")
META_PATH = os.path.join(BASE_DIR, "data", "metadata.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "features")

for p in [CLEAN_PATH, OUTPUT_PATH]:
    if not os.path.exists(p): os.makedirs(p)

TUNNEL_LEVELS_REF = [
    {"R": 250, "W": 100}, {"R": 400, "W": 100},
    {"R": 250, "W": 50},  {"R": 400, "W": 50},
    {"R": 400, "W": 30}
]

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
    acceleration = np.sqrt(ax**2 + ay**2)
    jerk = np.sqrt(jx**2 + jy**2)
    return velocity, acceleration, jerk

def calculate_f95(data, fs):
    n = len(data)
    if n < 2: return 0
    fft_vals = np.fft.fft(data)
    psd = np.abs(fft_vals)**2
    freqs = np.fft.fftfreq(n, d=1/fs)
    pos_mask = freqs > 0
    freqs = freqs[pos_mask]
    psd = psd[pos_mask]
    if len(psd) == 0: return 0
    cum_power = np.cumsum(psd)
    total_power = cum_power[-1]
    idx_95 = np.searchsorted(cum_power, 0.95 * total_power)
    return freqs[idx_95] if idx_95 < len(freqs) else freqs[-1]

def process_single_trial(df_trial, metadata, pid):
    time = df_trial['Time_Abs'].values
    if len(time) < 5: return None
    dt = np.mean(np.diff(time))
    fs = 1 / dt if dt > 0 else 120.0

    # Les données sont DÉJÀ filtrées par le bloc principal avant d'arriver ici
    x_clean = df_trial['X'].values
    y_clean = df_trial['Y'].values
    p_clean = df_trial['P_Raw'].values if 'P_Raw' in df_trial.columns else np.zeros(len(time))

    if 'R' in df_trial.columns:
        R_target = df_trial['R'].iloc[0]; W_target = df_trial['W'].iloc[0]
    else:
        try:
            lvl = int(df_trial['IDc_Lvl'].iloc[0]) - 1
            idx = max(0, min(lvl, 4))
            R_target = TUNNEL_LEVELS_REF[idx]["R"]; W_target = TUNNEL_LEVELS_REF[idx]["W"]
        except: R_target = 250; W_target = 100
    
    thickness = df_trial['Thickness'].mean() if 'Thickness' in df_trial.columns else 4.0

    # 2. CALCULS CINÉMATIQUES (Vitesse, Accel, Jerk)
    vel, acc, jerk = get_kinematics(x_clean, y_clean, dt)
    
    # 3. CALCULS METRIQUES IMAGE (Smoothness)
    duration = df_trial['Time_Rel'].max() - df_trial['Time_Rel'].min()
    path_length = np.sum(np.sqrt(np.diff(x_clean)**2 + np.diff(y_clean)**2))
    
    mean_jerk = np.mean(jerk)
    
    integral_jerk_squared = np.sum(jerk**2) * dt
    if path_length > 0 and duration > 0:
        arg_log = (duration**5 / path_length**2) * integral_jerk_squared
        ldlj = np.log(arg_log) if arg_log > 1e-9 else 0
    else:
        ldlj = 0
        
    cx = (df_trial['X'].max() + df_trial['X'].min()) / 2
    cy = (df_trial['Y'].max() + df_trial['Y'].min()) / 2
    radial_pos = np.sqrt((x_clean - cx)**2 + (y_clean - cy)**2)
    f95 = calculate_f95(radial_pos, fs)

    # 4. CALCULS ISO 9241-9 (Précision)
    Ri = np.sqrt((x_clean - cx)**2 + (y_clean - cy)**2)
    Re = np.mean(Ri)
    sigma_R = np.std(Ri)
    Te = 4.133 * sigma_R
    IDe = np.log2((2 * np.pi * Re) / Te) if Te > 0 else 0
    IPe = IDe / duration if duration > 0 else 0
    
    error_radial = np.abs(Ri - R_target)
    is_out = (error_radial + thickness/2) > (W_target / 2)
    error_rate = np.mean(is_out) * 100

    # 5. METADATA
    try:
        subject_row = metadata[metadata['ID'].str.upper() == pid.upper()]
        group = subject_row.iloc[0]['Group'] if not subject_row.empty else "Unknown"
        osats = subject_row.iloc[0]['OSATS_Score'] if not subject_row.empty and 'OSATS_Score' in subject_row.columns else np.nan
    except: group = "Unknown"; osats = np.nan

    return {
        'ID': pid, 'Group': group, 'OSATS': osats,
        'Condition': str(df_trial['Bloc'].iloc[0]) if 'Bloc' in df_trial.columns else "VP",
        'Trial': df_trial['Trial_in_Bloc'].iloc[0] if 'Trial_in_Bloc' in df_trial.columns else 0,
        
        # TOUTES VOS MÉTRIQUES SONT LÀ :
        'Mean_Jerk': mean_jerk,
        'LDLJ': ldlj,
        'F95': f95,
        'Throughput_ISO': IPe,
        'Error_Rate': error_rate,
        'Te': Te,
        'Duration': duration,
        'Path_Length': path_length,
        'Mean_Velocity': np.mean(vel),
        'Force_SD': np.std(p_clean)
    }

if __name__ == "__main__":
    print("--- TRAITEMENT, SAUVEGARDE CLEAN ET MÉTRIQUES COMPLÈTES ---")
    try:
        meta_df = pd.read_csv(META_PATH, sep=None, engine='python', encoding='utf-8-sig')
        meta_df.columns = meta_df.columns.str.strip()
        meta_df['ID'] = meta_df['ID'].astype(str).str.strip().str.upper()
    except: meta_df = pd.DataFrame(columns=['ID', 'Group'])

    raw_files = glob.glob(os.path.join(RAW_PATH, "*_RAW.csv"))
    all_features = []

    for f in raw_files:
        try:
            df = pd.read_csv(f)
            pid = str(df['ID'].iloc[0]).strip().upper()
            
            # --- ÉTAPE A : FILTRAGE GLOBAL ET SAUVEGARDE ---
            time_arr = df['Time_Abs'].values
            fs = 120.0
            if len(time_arr) > 2:
                dt = np.mean(np.diff(time_arr))
                if dt > 0: fs = 1/dt
                
            df_clean = df.copy()
            df_clean['X'] = butter_lowpass_filter(df['X'].values, 10, fs)
            df_clean['Y'] = butter_lowpass_filter(df['Y'].values, 10, fs)
            if 'P_Raw' in df.columns:
                df_clean['P_Raw'] = butter_lowpass_filter(df['P_Raw'].values, 10, fs)
            
            clean_file_path = os.path.join(CLEAN_PATH, f"{pid}_CLEAN.csv")
            df_clean.to_csv(clean_file_path, index=False)
            
            # --- ÉTAPE B : DÉCOUPAGE ET CALCUL DES MÉTRIQUES ---
            if 'Trial_in_Bloc' not in df_clean.columns:
                df_clean['New_Trial'] = (df_clean['Time_Rel'].diff() < -0.5) | (df_clean['Time_Rel'].shift(1).isna())
                df_clean['Trial_Auto'] = df_clean['New_Trial'].cumsum()
                group_col = 'Trial_Auto'
            else: group_col = 'Trial_in_Bloc'
            
            group_keys = [group_col]
            if 'Bloc' in df_clean.columns: group_keys.append('Bloc')

            for name, data_essai in df_clean.groupby(group_keys):
                feat = process_single_trial(data_essai, meta_df, pid)
                if feat: all_features.append(feat)
            
            print(f"-> Traité et Sauvegardé (Clean) : {pid}")

        except Exception as e: print(f"Erreur {os.path.basename(f)}: {e}")

    if all_features:
        pd.DataFrame(all_features).to_csv(os.path.join(OUTPUT_PATH, "dataset_features.csv"), index=False)
        print(f"\nSUCCÈS ! Fichiers Clean générés et toutes les features (LDLJ, F95, ISO) extraites.")