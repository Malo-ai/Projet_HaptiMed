# 04_statistical_analysis.py - ANALYSE STATISTIQUE CLASSIQUE (H1 : IPe Baseline)
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILE_PATH = os.path.join(BASE_DIR, "data", "features", "dataset_features.csv")
OUT_DIR = os.path.join(BASE_DIR, "results")

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)

# Style APA : Fond blanc, épuré
sns.set_theme(style="white", context="paper", font_scale=1.2)

def analyze_and_plot():
    print("--- VALIDATION DE L'HYPOTHÈSE H1 (Normes APA & Nettoyage) ---")
    
    try:
        df_raw = pd.read_csv(FILE_PATH)
    except FileNotFoundError:
        print(f"⚠️ Fichier introuvable : {FILE_PATH}")
        return

    # --- EXCLUSION SPÉCIFIQUE ---
    # Retrait du sujet P2VAFA avant analyse
    df_raw = df_raw[df_raw['ID'] != 'P2VAFA']

    # Isolement de la baseline (VP uniquement)
    df_base = df_raw[~df_raw['Condition'].str.contains('FVP')].copy()

    # Création de la figure
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle("Comparaison de l'Indice de Performance (IPe) par Niveau d'Expertise", 
                 weight='bold', fontsize=14, y=0.98)

    # Fonctions de ciblage des groupes
    def get_target_task1(row):
        statut = str(row['Statut_Principal']).lower()
        return 'Naïf' if 'non domaine' in statut else 'Chirurgien'

    def get_target_task2(row):
        statut = str(row['Statut_Principal']).lower()
        sous_statut = str(row['Sous_Statut']).lower()
        if 'non domaine' in statut: return np.nan
        if 'diplômé' in sous_statut: return 'Expert'
        if 'apprentissage' in sous_statut: return 'Interne'
        return np.nan

    tasks = [
        ("TÂCHE 1 : Naïf vs Chirurgien", get_target_task1, ['Naïf', 'Chirurgien'], axes[0], "T1"),
        ("TÂCHE 2 : Interne vs Expert", get_target_task2, ['Interne', 'Expert'], axes[1], "T2")
    ]

    for title, target_func, order, ax, task_id in tasks:
        df_task = df_base.copy()
        df_task['Group'] = df_task.apply(target_func, axis=1)
        df_task = df_task.dropna(subset=['Group'])
        
        # Agrégation par sujet
        df_agg = df_task.groupby(['ID', 'Group'])['IPe'].mean().reset_index()

        group_A_data = df_agg[df_agg['Group'] == order[0]]['IPe'].values
        group_B_data = df_agg[df_agg['Group'] == order[1]]['IPe'].values

        if len(group_A_data) == 0 or len(group_B_data) == 0:
            continue

        # Test de Mann-Whitney U
        stat, p_value = stats.mannwhitneyu(group_A_data, group_B_data, alternative='two-sided')

        # Formatage p-value APA (pas de zéro initial)
        p_val_str = str(round(p_value, 3)).lstrip('0') if p_value >= 0.001 else "< .001"
        signif = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"

        print(f"\n{title}")
        print(f"  {order[0]} (n={len(group_A_data)}): M = {np.mean(group_A_data):.2f}, SD = {np.std(group_A_data):.2f}")
        print(f"  {order[1]} (n={len(group_B_data)}): M = {np.mean(group_B_data):.2f}, SD = {np.std(group_B_data):.2f}")
        print(f"  U = {stat}, p = {p_val_str}")

        # Graphisme
        palette = ['#95a5a6', '#2ecc71'] if task_id == "T1" else ['#3498db', '#e74c3c']
        sns.boxplot(x='Group', y='IPe', data=df_agg, order=order, ax=ax, palette=palette, width=0.4, showfliers=False)
        sns.stripplot(x='Group', y='IPe', data=df_agg, order=order, ax=ax, color='black', alpha=0.5, jitter=True)
        
        ax.set_title(title, fontsize=11, pad=10)
        ax.set_ylabel("IPe (bits/s)" if task_id == "T1" else "")
        ax.set_xlabel("")
        
        # Barre de signification APA
        y_max = df_agg['IPe'].max()
        y_loc = y_max * 1.05
        ax.plot([0, 1], [y_loc, y_loc], lw=1, c='k')
        ax.text(0.5, y_loc, f'$p$ {p_val_str} ({signif})', ha='center', va='bottom', weight='bold')
        ax.set_ylim(df_agg['IPe'].min() * 0.9, y_loc * 1.15)

    sns.despine()
    
    # Ajustement pour ne pas couper le titre (rect=[gauche, bas, droite, haut])
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    file_out = os.path.join(OUT_DIR, "Fig4_Analyse_Statistique_IPe_Baseline_Clean.png")
    plt.savefig(file_out, dpi=300)
    plt.close()
    print(f"\n✅ Analyse H1 terminée. Graphique sauvegardé : {file_out}")

if __name__ == "__main__":
    analyze_and_plot()