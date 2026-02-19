# analysis_global.py - ANALYSE SCIENTIFIQUE ISO 9241-9 & FLUIDITÉ
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_FILE = os.path.join(BASE_DIR, "data", "features", "dataset_features.csv")
DOC_PATH = os.path.join(BASE_DIR, "doc")

if not os.path.exists(DOC_PATH): os.makedirs(DOC_PATH)

# Style Publication
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

def load_data():
    if not os.path.exists(FEATURES_FILE):
        print("ERREUR: Données introuvables. Lancez process_data.py d'abord.")
        return None
    df = pd.read_csv(FEATURES_FILE)
    return df[df['Group'].isin(['Novice', 'Expert'])]

# --- 1. LE GRAND TABLEAU (METRIQUES ISO) ---
def generate_summary_table(df):
    print("\n=== GRAND TABLEAU RÉCAPITULATIF (NOVICE vs EXPERT) ===")
    
    # Nouvelles métriques officielles
    metrics = {
        'Throughput_ISO': 'H1: Throughput Effectif (bits/s)',
        'Error_Rate': 'Précision (% Sortie Tunnel)',
        'Te': 'Largeur Effective (Dispersion px)',
        'LDLJ': 'H3: Fluidité (Log Jerk)',          # <--- CORRIGÉ ICI
        'Force_SD': 'H2: Stabilité Force (SD)',
        'Mean_Velocity': 'Vitesse Moyenne (px/s)'
    }
    
    summary_list = []
    
    print(f"{'MÉTRIQUE':<35} | {'NOVICE (Moy±SD)':<20} | {'EXPERT (Moy±SD)':<20} | {'P-VALUE':<10}")
    print("-" * 95)

    for col, label in metrics.items():
        if col not in df.columns: continue

        nov = df[df['Group'] == 'Novice'][col].dropna()
        exp = df[df['Group'] == 'Expert'][col].dropna()
        
        if len(nov) < 2 or len(exp) < 2: continue
        
        # Test T de Student
        # On ignore les warnings temporaires (dues aux fausses données)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            t_stat, p_val = stats.ttest_ind(nov, exp, equal_var=False)
        
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
        mean_n, sd_n = np.mean(nov), np.std(nov)
        mean_e, sd_e = np.mean(exp), np.std(exp)
        
        print(f"{label:<35} | {mean_n:.2f} ± {sd_n:.2f}      | {mean_e:.2f} ± {sd_e:.2f}      | {p_val:.4f} {sig}")
        
        summary_list.append({
            "Metrique": label,
            "Novice_Mean": mean_n, "Novice_SD": sd_n,
            "Expert_Mean": mean_e, "Expert_SD": sd_e,
            "P-Value": p_val, "Significatif": sig
        })
        
    pd.DataFrame(summary_list).to_csv(os.path.join(DOC_PATH, "Tableau_Statistiques.csv"), index=False, encoding='utf-8-sig')
    print(f"\n[TABLEAU] Sauvegardé : {DOC_PATH}/Tableau_Statistiques.csv")

# --- 2. LES GRAPHIQUES ---
def generate_graphs(df):
    print("\n=== GÉNÉRATION DES GRAPHIQUES ===")
    
    # 1. H1 : PERFORMANCE EFFECTIVE (ISO)
    plt.figure(figsize=(6, 5))
    sns.boxplot(x="Group", y="Throughput_ISO", data=df, hue="Group", palette="Set2", legend=False)
    plt.title("H1 : Performance Effective (ISO 9241-9)")
    plt.ylabel("Throughput (bits/s)")
    plt.savefig(os.path.join(DOC_PATH, "Graph_H1_Throughput_ISO.png"), dpi=300)
    plt.close()
    
    # 2. H3 : FLUIDITÉ (LDLJ au lieu de RMS_Jerk)  # <--- CORRIGÉ ICI
    plt.figure(figsize=(6, 5))
    if 'LDLJ' in df.columns:
        sns.boxplot(x="Group", y="LDLJ", data=df, hue="Group", palette="coolwarm", legend=False)
        plt.title("H3 : Fluidité (Log Dimensionless Jerk)")
        plt.ylabel("LDLJ (Valeur négative = Fluide)")
        plt.savefig(os.path.join(DOC_PATH, "Graph_H3_Fluidity.png"), dpi=300)
    plt.close()

    # 3. PRÉCISION (Te - Largeur Effective)
    plt.figure(figsize=(6, 5))
    sns.boxplot(x="Group", y="Te", data=df, hue="Group", palette="viridis", legend=False)
    plt.title("Dispersion Spatiale (Largeur Effective Te)")
    plt.ylabel("Te (pixels)")
    plt.savefig(os.path.join(DOC_PATH, "Graph_Precision_Te.png"), dpi=300)
    plt.close()

    # 4. INTERACTION DÉGRADATION (VP vs FVP)
    df['Tache_Type'] = df['Condition'].apply(lambda x: 'FVP' if 'FVP' in x else 'VP')
    plt.figure(figsize=(8, 6))
    sns.pointplot(x="Tache_Type", y="Throughput_ISO", hue="Group", data=df, 
                  markers=["o", "s"], capsize=.1, errorbar="sd")
    plt.title("Dégradation de la Performance Effective (VP vs FVP)")
    plt.ylabel("Throughput ISO (bits/s)")
    plt.xlabel("Condition")
    plt.savefig(os.path.join(DOC_PATH, "Graph_Degradation_Interaction.png"), dpi=300)
    plt.close()

    # 5. VALIDITÉ CONCOURANTE (OSATS vs ISO & LDLJ)
    df_osats = df.dropna(subset=['OSATS'])
    if not df_osats.empty:
        df_subj = df_osats.groupby('ID')[['OSATS', 'Throughput_ISO', 'LDLJ']].mean().reset_index()
        
        # Graphique A : OSATS vs Performance
        plt.figure(figsize=(6, 6))
        sns.regplot(x="OSATS", y="Throughput_ISO", data=df_subj, color="g")
        r, p = stats.pearsonr(df_subj['OSATS'], df_subj['Throughput_ISO'])
        plt.title(f"OSATS vs Performance ISO\nR={r:.2f}, p={p:.3f}")
        plt.xlabel("Score OSATS (Expert)")
        plt.ylabel("Throughput Effectif (bits/s)")
        plt.savefig(os.path.join(DOC_PATH, "Graph_Correlation_OSATS_Perf.png"), dpi=300)
        plt.close()

        # Graphique B : OSATS vs Fluidité (LDLJ)
        if 'LDLJ' in df_subj.columns:
            plt.figure(figsize=(6, 6))
            sns.regplot(x="OSATS", y="LDLJ", data=df_subj, color="r")
            r2, p2 = stats.pearsonr(df_subj['OSATS'], df_subj['LDLJ'])
            plt.title(f"OSATS vs Fluidité (LDLJ)\nR={r2:.2f}, p={p2:.3f}")
            plt.xlabel("Score OSATS (Expert)")
            plt.ylabel("LDLJ (Plus petit = meilleur)")
            plt.savefig(os.path.join(DOC_PATH, "Graph_Correlation_OSATS_Jerk.png"), dpi=300)
            plt.close()

    print(f"[GRAPHIQUES] Générés dans {DOC_PATH}")

if __name__ == "__main__":
    df = load_data()
    if df is not None:
        generate_summary_table(df)
        generate_graphs(df)
        print("\n--- ANALYSE TERMINÉE ---")