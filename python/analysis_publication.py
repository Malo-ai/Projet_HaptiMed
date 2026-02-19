# analysis_publication.py - TABLEAU APA CLEAN
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_FILE = os.path.join(BASE_DIR, "data", "features", "dataset_features.csv")
DOC_PATH = os.path.join(BASE_DIR, "doc")

METRICS_MAP = {
    'LDLJ': ('Log Dimensionless Jerk', 'UA'),
    'Mean_Jerk': ('Mean Tooltip Jerk', '10³ px/s³'), # On divise par 1000 pour la lisibilité
    'F95': ('95% Motion Freq', 'Hz'),
    'Throughput_ISO': ('Throughput (ISO)', 'bits/s'),
    'Error_Rate': ('Taux d\'Erreur', '%'),
    'Te': ('Largeur Effective (Te)', 'px'),
    'Force_SD': ('Stabilité Force (SD)', 'Raw'),
    'Mean_Velocity': ('Vitesse Moyenne', 'px/s')
}

def get_stats_string(data):
    mean, sd = np.mean(data), np.std(data, ddof=1)
    if len(data) > 1:
        se = stats.sem(data)
        ci = se * stats.t.ppf((1 + 0.95) / 2., len(data)-1)
        return mean, sd, (mean-ci, mean+ci)
    return mean, sd, (0, 0)

def cohen_d(x, y):
    nx, ny = len(x), len(y)
    dof = nx + ny - 2
    if dof <= 0: return 0
    pool_sd = np.sqrt(((nx-1)*np.std(x, ddof=1)**2 + (ny-1)*np.std(y, ddof=1)**2) / dof)
    return (np.mean(x) - np.mean(y)) / pool_sd if pool_sd > 0 else 0

def generate_scientific_table():
    if not os.path.exists(FEATURES_FILE): return
    df = pd.read_csv(FEATURES_FILE)
    df = df[df['Group'].isin(['Novice', 'Expert'])]
    
    # Division du Mean Jerk par 1000 pour éviter les nombres géants
    if 'Mean_Jerk' in df.columns: df['Mean_Jerk'] = df['Mean_Jerk'] / 1000.0
    
    table_rows = []
    for col, (label, unit) in METRICS_MAP.items():
        if col not in df.columns: continue
        
        nov = df[df['Group'] == 'Novice'][col].dropna()
        exp = df[df['Group'] == 'Expert'][col].dropna()
        if len(nov) < 2 or len(exp) < 2: continue
        
        m_n, s_n, ci_n = get_stats_string(nov)
        m_e, s_e, ci_e = get_stats_string(exp)
        
        # Gestion propre des stats
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t_stat, p_val = stats.ttest_ind(nov, exp, equal_var=False)
        
        d_val = cohen_d(nov, exp)
        
        # Formatage STRICT à 2 décimales (Norme APA)
        if np.isnan(p_val): sig, p_str, t_str = "ns", "N/A", "N/A"
        else:
            sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
            p_str = "< .001" if p_val < 0.001 else f"{p_val:.3f}"
            t_str = f"t={t_stat:.2f}"
            
        d_str = f"{abs(d_val):.2f}" if not np.isnan(d_val) else "N/A"

        table_rows.append({
            "Métrique": label, "Unité": unit,
            "Novice": f"{m_n:.2f} ± {s_n:.2f}\n[{ci_n[0]:.2f}, {ci_n[1]:.2f}]",
            "Expert": f"{m_e:.2f} ± {s_e:.2f}\n[{ci_e[0]:.2f}, {ci_e[1]:.2f}]",
            "t-test": t_str, "p-value": p_str + " " + sig, "Cohen's d": d_str
        })

    df_table = pd.DataFrame(table_rows)
    df_table.to_excel(os.path.join(DOC_PATH, "Tableau_Publication.xlsx"), index=False)
    
    # Rendu Image élargi
    fig, ax = plt.subplots(figsize=(16, len(df_table)*1.2 + 2)) # Plus large
    ax.axis('off')
    table_data = [[str(item) for item in row] for idx, row in df_table.iterrows()]
    tbl = ax.table(cellText=table_data, colLabels=df_table.columns, loc='center', cellLoc='center')
    tbl.auto_set_font_size(False); tbl.set_fontsize(11); tbl.scale(1.2, 2.5) # Cellules plus grandes
    
    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#40466e'); cell.set_linewidth(0)
        else:
            cell.set_linewidth(0.5); cell.set_edgecolor('#dddddd')
            if row % 2 == 0: cell.set_facecolor('#f5f5f5')
            
    plt.title("Métriques de Fluidité et Performance", fontsize=16, weight='bold', pad=20)
    plt.savefig(os.path.join(DOC_PATH, "Tableau_Publication.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("[IMAGE] Tableau APA généré proprement.")

if __name__ == "__main__":
    generate_scientific_table()