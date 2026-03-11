# analysis_master.py - VERSION FINALE OPTIMISÉE (APA, H1/H2/H3, Fitts Regression & Be)
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

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

METRICS_MAP = {
    'IPe': ('Performance (IPe)', 'bits/s'),
    'Duration': ('MT/lap', 's'),
    'IDe': ('Difficulté (IDe)', 'bits'),
    'Be': ('Coeff Régression (Be)', 's/bit'),
    'Error_Rate': ('Taux d\'Erreur', '%'),
    'Te': ('Largeur Effective (Te)', 'px'),
    'LDLJ': ('Fluidité (LDLJ)', 'UA'),
    'Force_SD': ('Stabilité Force (SD)', 'Raw')
}

# ==========================================
# 1. OUTILS STATISTIQUES
# ==========================================
def cohen_d(x, y):
    nx, ny = len(x), len(y)
    dof = nx + ny - 2
    if dof <= 0: return 0
    pool_sd = np.sqrt(((nx-1)*np.std(x, ddof=1)**2 + (ny-1)*np.std(y, ddof=1)**2) / dof)
    return (np.mean(x) - np.mean(y)) / pool_sd if pool_sd > 0 else 0

def create_apa_table(df, condition_prefix, hypothesis_name, file_suffix):
    df_cond = df[df['Task_Type'] == condition_prefix]
    if df_cond.empty: return

    table_rows = []
    for col, (label, unit) in METRICS_MAP.items():
        if col not in df_cond.columns: continue
        if condition_prefix == "VP" and col == 'Force_SD': continue 
        
        nov = df_cond[df_cond['Group'] == 'Novice'][col].dropna()
        exp = df_cond[df_cond['Group'] == 'Expert'][col].dropna()
        if len(nov) < 2 or len(exp) < 2: continue
        
        m_n, s_n = np.mean(nov), np.std(nov, ddof=1)
        m_e, s_e = np.mean(exp), np.std(exp, ddof=1)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t_stat, p_val = stats.ttest_ind(nov, exp, equal_var=False)
        
        d_val = cohen_d(nov, exp)
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
        p_str = "< .001" if p_val < 0.001 else f"{p_val:.3f}"

        table_rows.append({
            "Métrique": label, "Unité": unit,
            "Novice (M±SD)": f"{m_n:.2f} ± {s_n:.2f}",
            "Expert (M±SD)": f"{m_e:.2f} ± {s_e:.2f}",
            "t-stat": f"{t_stat:.2f}", "p-value": f"{p_str} {sig}", "Cohen's d": f"{abs(d_val):.2f}"
        })

    df_table = pd.DataFrame(table_rows)
    df_table.to_excel(os.path.join(DOC_PATH, f"Tableau_APA_{file_suffix}.xlsx"), index=False)
    
    fig, ax = plt.subplots(figsize=(12, len(df_table)*0.8 + 2))
    ax.axis('off')
    tbl = ax.table(cellText=df_table.values, colLabels=df_table.columns, loc='center', cellLoc='center')
    tbl.auto_set_font_size(False); tbl.set_fontsize(11); tbl.scale(1.1, 2.2)
    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#2c3e50')
        elif row % 2 == 0: cell.set_facecolor('#ecf0f1')
    plt.title(f"{hypothesis_name} ({condition_prefix})", fontsize=15, weight='bold', pad=25)
    plt.savefig(os.path.join(DOC_PATH, f"Tableau_APA_{file_suffix}.png"), dpi=300, bbox_inches='tight')
    plt.close()

# ==========================================
# 2. GÉNÉRATION DES GRAPHIQUES
# ==========================================
def generate_graphs(df):
    print("\n=== GÉNÉRATION DES GRAPHIQUES SCIENTIFIQUES ===")

    # --- H1 : Performance ISO (Boxplot IPe & Be) ---
    df_vp = df[df['Task_Type'] == 'VP']
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    sns.boxplot(x="Group", y="IPe", data=df_vp, ax=axes[0], palette="Set2")
    axes[0].set_title("Efficience Motrice Global (IPe)")
    axes[0].set_ylabel("Throughput (bits/s)")
    
    sns.boxplot(x="Group", y="Be", data=df_vp, ax=axes[1], palette="Set2")
    axes[1].set_title("Coût du mouvement (Coefficient Be)")
    axes[1].set_ylabel("Pente (s/bit) - Plus bas = Meilleur")
    
    plt.tight_layout()
    plt.savefig(os.path.join(DOC_PATH, "Graph_H1_Fitts_Metrics.png"), dpi=300)
    plt.close()

    # --- NOUVEAU : La Droite de Fitts (MT vs IDe) ---
    plt.figure(figsize=(7, 6))
    sns.lmplot(x="IDe", y="Duration", hue="Group", data=df_vp, 
               palette={"Expert": "#2ecc71", "Novice": "#e74c3c"}, 
               markers=["s", "o"], scatter_kws={'alpha':0.4})
    plt.title("Loi de Fitts : MT = A + Be * IDe")
    plt.xlabel("Index de Difficulté Effectif (bits)")
    plt.ylabel("Temps par tour (MT/lap) [s]")
    plt.savefig(os.path.join(DOC_PATH, "Graph_H1_Fitts_Regression.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # --- H2 : Interaction & Résilience (IPe) ---
    plt.figure(figsize=(8, 6))
    sns.pointplot(x="Task_Type", y="IPe", hue="Group", data=df, markers=["o", "s"], capsize=.1, errorbar="sd")
    plt.title("H2 : Résilience à la contrainte de Force")
    plt.ylabel("Performance (IPe)")
    plt.savefig(os.path.join(DOC_PATH, "Graph_H2_Degradation_Interaction.png"), dpi=300)
    plt.close()

    # --- H3 : Fluidité LDLJ ---
    plt.figure(figsize=(6, 5))
    sns.boxplot(x="Group", y="LDLJ", data=df, palette="coolwarm")
    plt.title("H3 : Fluidité (Log Dimensionless Jerk)")
    plt.ylabel("LDLJ (Plus bas = Plus Fluide)")
    plt.savefig(os.path.join(DOC_PATH, "Graph_H3_Fluidity.png"), dpi=300)
    plt.close()

    # --- VALIDITÉ CLINIQUE (Ancienneté) ---
    df_subj = df.groupby('ID').mean(numeric_only=True).reset_index()
    if 'Experience_Years' in df_subj.columns:
        plt.figure(figsize=(6, 6))
        sns.regplot(x="Experience_Years", y="IPe", data=df_subj, color="#27ae60")
        r, p = stats.pearsonr(df_subj['Experience_Years'].dropna(), df_subj['IPe'].dropna())
        plt.title(f"Validation : Expérience vs Performance\nr = {r:.2f} (p={p:.3f})")
        plt.xlabel("Années de Pratique Chirurgicale")
        plt.ylabel("Performance Globale (IPe)")
        plt.savefig(os.path.join(DOC_PATH, "Graph_Correl_Experience_Perf.png"), dpi=300)
        plt.close()

# ==========================================
# EXÉCUTION
# ==========================================
if __name__ == "__main__":
    if not os.path.exists(FEATURES_FILE):
        print("ERREUR: dataset_features.csv introuvable.")
    else:
        df_all = pd.read_csv(FEATURES_FILE)
        df_all = df_all[df_all['Group'].isin(['Novice', 'Expert'])]
        
        # 1. Tableaux APA
        create_apa_table(df_all, "VP", "H1 : Discrimination Vitesse/Précision", "H1_VP")
        create_apa_table(df_all, "FVP", "H2 : Discrimination avec Force", "H2_FVP")
        
        # 2. Grand CSV Global avec P-values
        res_list = []
        for col in METRICS_MAP.keys():
            if col in df_all.columns:
                n = df_all[df_all['Group'] == 'Novice'][col].dropna()
                e = df_all[df_all['Group'] == 'Expert'][col].dropna()
                _, p = stats.ttest_ind(n, e, equal_var=False)
                res_list.append({'Metrique': col, 'P-Value': p, 'Cohen_d': cohen_d(n, e)})
        
        pd.DataFrame(res_list).to_csv(os.path.join(DOC_PATH, "Tableau_Significativite_Global.csv"), index=False)
        
        # 3. Graphiques
        generate_graphs(df_all)
        
        print(f"\n[SUCCÈS] Analyse terminée. Tous les documents sont dans {DOC_PATH}")