# analysis_master.py - SCRIPT COMPLET (TABLEAUX APA + GRAPHIQUES H1/H2/H3)
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import warnings

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FEATURES_FILE = os.path.join(BASE_DIR, "data", "features", "dataset_features.csv")
DOC_PATH = os.path.join(BASE_DIR, "doc")

if not os.path.exists(DOC_PATH): os.makedirs(DOC_PATH)

# Style Publication
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

# Dictionnaire des métriques pour les tableaux
METRICS_MAP = {
    'Throughput_ISO': ('Throughput (ISO)', 'bits/s'),
    'Mean_Velocity': ('Vitesse Moyenne', 'px/s'),
    'Error_Rate': ('Taux d\'Erreur', '%'),
    'Te': ('Largeur Effective (Te)', 'px'),
    'LDLJ': ('Fluidité (LDLJ)', 'UA'),
    'Force_SD': ('Stabilité Force (SD)', 'Raw')
}

# ==========================================
# 1. OUTILS STATISTIQUES POUR TABLEAUX APA
# ==========================================
def get_stats_string(data):
    if len(data) < 2: return 0, 0, (0, 0)
    mean, sd = np.mean(data), np.std(data, ddof=1)
    se = stats.sem(data)
    ci = se * stats.t.ppf((1 + 0.95) / 2., len(data)-1)
    return mean, sd, (mean-ci, mean+ci)

def cohen_d(x, y):
    nx, ny = len(x), len(y)
    dof = nx + ny - 2
    if dof <= 0: return 0
    pool_sd = np.sqrt(((nx-1)*np.std(x, ddof=1)**2 + (ny-1)*np.std(y, ddof=1)**2) / dof)
    return (np.mean(x) - np.mean(y)) / pool_sd if pool_sd > 0 else 0

def create_apa_table(df, condition_prefix, hypothesis_name, file_suffix):
    df_cond = df[df['Condition'].str.startswith(condition_prefix, na=False)]
    if df_cond.empty: return

    table_rows = []
    for col, (label, unit) in METRICS_MAP.items():
        if col not in df_cond.columns: continue
        if condition_prefix == "VP" and col == 'Force_SD': continue # Pas de force en VP
        
        nov = df_cond[df_cond['Group'] == 'Novice'][col].dropna()
        exp = df_cond[df_cond['Group'] == 'Expert'][col].dropna()
        if len(nov) < 2 or len(exp) < 2: continue
        
        m_n, s_n, _ = get_stats_string(nov)
        m_e, s_e, _ = get_stats_string(exp)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t_stat, p_val = stats.ttest_ind(nov, exp, equal_var=False)
        
        d_val = cohen_d(nov, exp)
        
        if np.isnan(p_val): sig, p_str, t_str = "ns", "N/A", "N/A"
        else:
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
            p_str = "< .001" if p_val < 0.001 else f"{p_val:.3f}"
            t_str = f"t={t_stat:.2f}"
            
        d_str = f"{abs(d_val):.2f}" if not np.isnan(d_val) else "N/A"

        table_rows.append({
            "Métrique": label, "Unité": unit,
            "Novice": f"{m_n:.2f} ± {s_n:.2f}",
            "Expert": f"{m_e:.2f} ± {s_e:.2f}",
            "t-test": t_str, "p-value": f"{p_str} {sig}", "Cohen's d": d_str
        })

    df_table = pd.DataFrame(table_rows)
    df_table.to_excel(os.path.join(DOC_PATH, f"Tableau_APA_{file_suffix}.xlsx"), index=False)
    
    fig, ax = plt.subplots(figsize=(12, len(df_table)*0.8 + 2))
    ax.axis('off')
    table_data = [[str(item) for item in row] for idx, row in df_table.iterrows()]
    tbl = ax.table(cellText=table_data, colLabels=df_table.columns, loc='center', cellLoc='center')
    tbl.auto_set_font_size(False); tbl.set_fontsize(11); tbl.scale(1.2, 2.0)
    
    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#2c3e50'); cell.set_linewidth(0)
        else:
            cell.set_linewidth(0.5); cell.set_edgecolor('#bdc3c7')
            if row % 2 == 0: cell.set_facecolor('#ecf0f1')
            
    plt.title(f"{hypothesis_name} (Condition {condition_prefix})", fontsize=16, weight='bold', pad=20)
    plt.savefig(os.path.join(DOC_PATH, f"Tableau_APA_{file_suffix}.png"), dpi=300, bbox_inches='tight')
    plt.close()

# ==========================================
# 2. GRAND TABLEAU RÉCAPITULATIF CSV
# ==========================================
def generate_summary_csv(df):
    print("\n=== GRAND TABLEAU CSV GLOBAL (NOVICE vs EXPERT) ===")
    summary_list = []
    
    print(f"{'MÉTRIQUE':<35} | {'NOVICE (Moy±SD)':<20} | {'EXPERT (Moy±SD)':<20} | {'P-VALUE':<10}")
    print("-" * 95)

    for col, (label, _) in METRICS_MAP.items():
        if col not in df.columns: continue
        nov = df[df['Group'] == 'Novice'][col].dropna()
        exp = df[df['Group'] == 'Expert'][col].dropna()
        if len(nov) < 2 or len(exp) < 2: continue
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            _, p_val = stats.ttest_ind(nov, exp, equal_var=False)
        
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
        mean_n, sd_n = np.mean(nov), np.std(nov)
        mean_e, sd_e = np.mean(exp), np.std(exp)
        
        print(f"{label:<35} | {mean_n:.2f} ± {sd_n:.2f}      | {mean_e:.2f} ± {sd_e:.2f}      | {p_val:.4f} {sig}")
        
        summary_list.append({
            "Metrique": label, "Novice_Mean": mean_n, "Novice_SD": sd_n,
            "Expert_Mean": mean_e, "Expert_SD": sd_e, "P-Value": p_val, "Significatif": sig
        })
        
    pd.DataFrame(summary_list).to_csv(os.path.join(DOC_PATH, "Tableau_Statistiques_Global.csv"), index=False, encoding='utf-8-sig')

# ==========================================
# 3. GÉNÉRATION DES GRAPHIQUES (H1, H2, H3)
# ==========================================
def generate_graphs(df):
    print("\n=== GÉNÉRATION DES GRAPHIQUES ===")
    df['Tache_Type'] = df['Condition'].apply(lambda x: 'FVP' if str(x).startswith('FVP') else 'VP')
    df_vp = df[df['Tache_Type'] == 'VP']
    df_fvp = df[df['Tache_Type'] == 'FVP']

    # --- H1 : Vitesse / Précision (Sur condition VP) ---
    plt.figure(figsize=(6, 5))
    sns.boxplot(x="Group", y="Throughput_ISO", data=df_vp, hue="Group", palette="Set2", legend=False)
    plt.title("H1 : Performance Effective (ISO 9241-9) en VP")
    plt.ylabel("Throughput (bits/s)")
    plt.savefig(os.path.join(DOC_PATH, "Graph_H1_Throughput.png"), dpi=300)
    plt.close()

    plt.figure(figsize=(6, 5))
    sns.boxplot(x="Group", y="Te", data=df_vp, hue="Group", palette="viridis", legend=False)
    plt.title("H1 : Dispersion Spatiale (Largeur Effective Te) en VP")
    plt.ylabel("Te (pixels)")
    plt.savefig(os.path.join(DOC_PATH, "Graph_H1_Precision_Te.png"), dpi=300)
    plt.close()

    # --- H2 : Ajout de la Force (Sur condition FVP & Interaction) ---
    if 'Force_SD' in df_fvp.columns:
        plt.figure(figsize=(6, 5))
        sns.boxplot(x="Group", y="Force_SD", data=df_fvp, hue="Group", palette="magma", legend=False)
        plt.title("H2 : Stabilité de la Force en FVP")
        plt.ylabel("Force SD (Écart-type)")
        plt.savefig(os.path.join(DOC_PATH, "Graph_H2_ForceSD.png"), dpi=300)
        plt.close()

    plt.figure(figsize=(8, 6))
    sns.pointplot(x="Tache_Type", y="Throughput_ISO", hue="Group", data=df, markers=["o", "s"], capsize=.1, errorbar="sd")
    plt.title("H2 : Dégradation de la Performance Effective (VP vs FVP)")
    plt.ylabel("Throughput ISO (bits/s)")
    plt.xlabel("Condition")
    plt.savefig(os.path.join(DOC_PATH, "Graph_H2_Degradation_Interaction.png"), dpi=300)
    plt.close()

    # --- H3 : Fluidité (Global) ---
    if 'LDLJ' in df.columns:
        plt.figure(figsize=(6, 5))
        sns.boxplot(x="Group", y="LDLJ", data=df, hue="Group", palette="coolwarm", legend=False)
        plt.title("H3 : Fluidité (Log Dimensionless Jerk)")
        plt.ylabel("LDLJ (Valeur négative = Fluide)")
        plt.savefig(os.path.join(DOC_PATH, "Graph_H3_Fluidity.png"), dpi=300)
        plt.close()

    # --- 4. VALIDITÉ CONCOURANTE (Corrélations OSATS) ---
    df_osats = df.dropna(subset=['OSATS'])
    if not df_osats.empty:
        df_subj = df_osats.groupby('ID')[['OSATS', 'Throughput_ISO', 'LDLJ']].mean().reset_index()
        
        plt.figure(figsize=(6, 6))
        sns.regplot(x="OSATS", y="Throughput_ISO", data=df_subj, color="g")
        r, p = stats.pearsonr(df_subj['OSATS'], df_subj['Throughput_ISO'])
        plt.title(f"OSATS vs Performance ISO\nR={r:.2f}, p={p:.3f}")
        plt.xlabel("Score OSATS (Expert)")
        plt.ylabel("Throughput Effectif (bits/s)")
        plt.savefig(os.path.join(DOC_PATH, "Graph_Correl_OSATS_Perf.png"), dpi=300)
        plt.close()

        if 'LDLJ' in df_subj.columns:
            plt.figure(figsize=(6, 6))
            sns.regplot(x="OSATS", y="LDLJ", data=df_subj, color="r")
            r2, p2 = stats.pearsonr(df_subj['OSATS'], df_subj['LDLJ'])
            plt.title(f"OSATS vs Fluidité (LDLJ)\nR={r2:.2f}, p={p2:.3f}")
            plt.xlabel("Score OSATS (Expert)")
            plt.ylabel("LDLJ (Plus petit = meilleur)")
            plt.savefig(os.path.join(DOC_PATH, "Graph_Correl_OSATS_Fluidity.png"), dpi=300)
            plt.close()

# ==========================================
# EXÉCUTION PRINCIPALE
# ==========================================
if __name__ == "__main__":
    if not os.path.exists(FEATURES_FILE):
        print("ERREUR: Données introuvables. Lancez process_data.py d'abord.")
    else:
        df_all = pd.read_csv(FEATURES_FILE)
        df_all = df_all[df_all['Group'].isin(['Novice', 'Expert'])]
        
        # 1. Générer les Tableaux APA (Images PNG + Excel)
        create_apa_table(df_all, "VP", "H1 : Discrimination par Vitesse/Précision", "H1_VP")
        create_apa_table(df_all, "FVP", "H2 : Discrimination avec Force", "H2_FVP")
        
        # 2. Générer le CSV Global (Dans le terminal et fichier)
        generate_summary_csv(df_all)
        
        # 3. Générer tous les graphiques
        generate_graphs(df_all)
        
        print(f"\n[SUCCÈS] Tous les tableaux et graphiques ont été générés dans le dossier {DOC_PATH}")