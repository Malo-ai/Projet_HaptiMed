# 05_hypothesis_H2_Expert_Novice.py - VÉRIFICATION H2 (Asymétrie Force)
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

sns.set_theme(style="white", context="paper", font_scale=1.2)

# ==============================================================================
# 1. PRÉPARATION DES DONNÉES (Ciblage strict Novice vs Expert)
# ==============================================================================
def get_target_h2(row):
    """Filtre pour isoler uniquement les chirurgiens selon leur expertise"""
    statut = str(row['Statut_Principal']).lower()
    sous_statut = str(row['Sous_Statut']).lower()
    
    # On exclut totalement les sujets non médicaux (Naïfs)
    if 'non domaine' in statut: 
        return np.nan 
        
    if 'diplômé' in sous_statut: 
        return 'Expert'
    if 'apprentissage' in sous_statut: 
        return 'Novice'
        
    return np.nan

def classify_condition(cond):
    cond_str = str(cond)
    if cond_str.startswith('FVP'): return 'Avec Force (FVP)'
    if cond_str.startswith('VP'): return 'Sans Force (VP)'
    return 'Autre'

def test_hypothesis_H2():
    print("--- VÉRIFICATION H2 : CHUTE DE PERFORMANCE (NOVICE vs EXPERT) ---")
    
    try:
        df_raw = pd.read_csv(FILE_PATH)
    except FileNotFoundError:
        print(f"⚠️ Fichier introuvable : {FILE_PATH}")
        return

    # --- EXCLUSION SPÉCIFIQUE ---
    # On retire le sujet P2VAFA du dataset avant toute analyse
    df_raw = df_raw[df_raw['ID'] != 'P2VAFA']

    df = df_raw.copy()
    df['Group'] = df.apply(get_target_h2, axis=1)
    df['Cond_Type'] = df['Condition'].apply(classify_condition)
    
    # On garde uniquement VP et FVP
    df = df[df['Cond_Type'].isin(['Sans Force (VP)', 'Avec Force (FVP)'])]
    df = df.dropna(subset=['Group', 'IPe', 'Cond_Type'])

    # --- AGRÉGATION PAR SUJET ET PAR CONDITION ---
    df_agg = df.groupby(['ID', 'Group', 'Cond_Type'])['IPe'].mean().reset_index()

    # --- PIVOT POUR CALCULER LE DELTA (Coût de la Force) ---
    df_pivot = df_agg.pivot(index=['ID', 'Group'], columns='Cond_Type', values='IPe').reset_index()
    df_pivot = df_pivot.dropna() # Garde les sujets qui ont fait VP ET FVP
    
    # Calcul de la chute d'IPe
    df_pivot['Chute_IPe'] = df_pivot['Sans Force (VP)'] - df_pivot['Avec Force (FVP)']
    
    # --- STATISTIQUES ---
    group_novice = df_pivot[df_pivot['Group'] == 'Novice']['Chute_IPe'].values
    group_expert = df_pivot[df_pivot['Group'] == 'Expert']['Chute_IPe'].values
    
    if len(group_novice) == 0 or len(group_expert) == 0:
        print("⚠️ Pas assez de données pour comparer Novices et Experts sur ces conditions.")
        return

    mean_novice, std_novice = np.mean(group_novice), np.std(group_novice)
    mean_expert, std_expert = np.mean(group_expert), np.std(group_expert)
    
    # Test non-paramétrique de Mann-Whitney U (bilatéral)
    stat, p_val_delta = stats.mannwhitneyu(group_novice, group_expert, alternative='two-sided')

    # Formatage APA
    p_val_str = str(round(p_val_delta, 3)).lstrip('0') if p_val_delta >= 0.001 else "< .001"
    signif = "***" if p_val_delta < 0.001 else "**" if p_val_delta < 0.01 else "*" if p_val_delta < 0.05 else "ns"

    print("\n[RÉSULTATS DE L'ASYMÉTRIE DU COÛT DE LA FORCE]")
    print(f"  Novices : Chute moyenne de M = {mean_novice:.2f}, SD = {std_novice:.2f} bits/s (n={len(group_novice)})")
    print(f"  Experts : Chute moyenne de M = {mean_expert:.2f}, SD = {std_expert:.2f} bits/s (n={len(group_expert)})")
    print(f"  Test d'Interaction (H2) : U = {stat}, p = {p_val_str} [{signif}]")

    # ==============================================================================
    # 2. GÉNÉRATION DU GRAPHIQUE À DEUX PANNEAUX
    # ==============================================================================
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("H2 : Impact de la Force Axiale selon l'Expertise", weight='bold', fontsize=16, y=0.98)

    palette_clinique = ['#3498db', '#e74c3c'] # Bleu pour Novice, Rouge pour Expert
    order_clinique = ['Novice', 'Expert']

    # PANNEAU 1 : Le pointplot d'Interaction
    sns.pointplot(x='Cond_Type', y='IPe', hue='Group', data=df_agg, 
                  order=['Sans Force (VP)', 'Avec Force (FVP)'], hue_order=order_clinique,
                  palette=palette_clinique, markers=['o', 's'], capsize=.1, err_kws={'linewidth': 1.5}, ax=axes[0])
    axes[0].set_title("Évolution de l'IPe (VP vs FVP)", pad=15)
    axes[0].set_ylabel("IPe (bits/s)")
    axes[0].set_xlabel("")
    axes[0].grid(axis='y', linestyle='--', alpha=0.6)

    # PANNEAU 2 : Le Boxplot de la Chute (Delta)
    sns.boxplot(x='Group', y='Chute_IPe', data=df_pivot, order=order_clinique, 
                palette=palette_clinique, width=0.4, showfliers=False, ax=axes[1])
    sns.stripplot(x='Group', y='Chute_IPe', data=df_pivot, order=order_clinique, 
                  color='black', alpha=0.5, jitter=True, size=6, ax=axes[1])
    
    axes[1].set_title("Chute de Performance (Coût Cognitif/Moteur)", pad=15)
    axes[1].set_ylabel("Delta IPe (VP - FVP)")
    axes[1].set_xlabel("")
    
    # Ajout de la p-value aux normes APA
    y_max = df_pivot['Chute_IPe'].max()
    y_loc = y_max + (y_max * 0.05)
    axes[1].plot([0, 1], [y_loc, y_loc], lw=1.5, c='k')
    axes[1].text(0.5, y_loc, f'Asymétrie $p$ {p_val_str} ({signif})', ha='center', va='bottom', color='k', weight='bold')

    sns.despine()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    file_out = os.path.join(OUT_DIR, "Fig5_Hypothese_H2_Novice_vs_Expert.png")
    plt.savefig(file_out, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n✅ Graphique d'interaction sauvegardé dans : {file_out}")

if __name__ == "__main__":
    test_hypothesis_H2()