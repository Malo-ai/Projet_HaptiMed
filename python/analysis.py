# ==============================================================================
# PROJET HAPTIMED - ANALYSE AUTOMATISÉE
# Ce script lit tous les fichiers SCORES, les fusionne et génère les figures.
# ==============================================================================

import os
import glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# 1. CONFIGURATION DES CHEMINS (Relatifs !)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
DOC_PATH = os.path.join(BASE_DIR, "doc")

def load_all_data():
    """Lit tous les fichiers CSV se terminant par _SCORES.csv"""
    all_files = glob.glob(os.path.join(DATA_PATH, "*_SCORES.csv"))
    
    if not all_files:
        print("ERREUR: Aucun fichier de données trouvé dans data/raw !")
        return None

    df_list = []
    for filename in all_files:
        df = pd.read_csv(filename)
        df_list.append(df)
    
    # Fusionne tout en un seul grand tableau
    full_df = pd.concat(df_list, axis=0, ignore_index=True)
    return full_df

def process_data(df):
    """Ajoute les colonnes nécessaires (IDc, Condition)"""
    # 1. Calcul de l'Indice de Difficulté de Steering (IDc = A / W)
    # A = Longueur du tunnel = Circonférence = 2 * pi * R
    df['IDc'] = (2 * np.pi * df['R']) / df['W']
    
    # 2. Création d'une colonne "Condition" lisible
    # Ex: "FVP-FB" ou "VP-NoFB"
    df['Condition'] = df['Task'] + "-" + df['FB'].apply(lambda x: "FB" if x == 1 else "NoFB")
    
    return df

def plot_steering_law(df):
    """Génère le graphique de la Loi de Steering (MT vs IDc)"""
    plt.figure(figsize=(10, 6))
    
    # Régression linéaire avec Seaborn
    sns.lmplot(x="IDc", y="MT", hue="Condition", data=df, aspect=1.5, height=6)
    
    plt.title("Loi de Steering (Loi d'Accot-Zhai)", fontsize=16)
    plt.xlabel("Indice de Difficulté (IDc)", fontsize=12)
    plt.ylabel("Temps de Mouvement (s)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # Sauvegarde
    save_path = os.path.join(DOC_PATH, "Resultat_Loi_Steering.png")
    plt.savefig(save_path, dpi=300)
    print(f"[OK] Graphique sauvegardé : {save_path}")
    plt.close() # Ferme la figure pour libérer la mémoire

def plot_rmse_boxplot(df):
    """Génère le Boxplot de l'erreur (RMSE)"""
    plt.figure(figsize=(10, 6))
    
    sns.boxplot(x="Condition", y="RMSE", data=df, palette="Set2")
    
    plt.title("Précision (RMSE) selon les conditions", fontsize=16)
    plt.ylabel("Erreur Moyenne (pixels)", fontsize=12)
    plt.xlabel("Condition", fontsize=12)
    
    save_path = os.path.join(DOC_PATH, "Resultat_RMSE.png")
    plt.savefig(save_path, dpi=300)
    print(f"[OK] Graphique sauvegardé : {save_path}")
    plt.close()

if __name__ == "__main__":
    print("--- DÉBUT DE L'ANALYSE ---")
    
    # 1. Chargement
    data = load_all_data()
    
    if data is not None:
        print(f"Données chargées : {len(data)} essais trouvés.")
        
        # 2. Traitement
        data = process_data(data)
        
        # 3. Génération des graphiques
        plot_steering_law(data)
        plot_rmse_boxplot(data)
        
        # 4. Petit résumé statistique dans la console
        print("\n--- RÉSUMÉ STATISTIQUE (Moyennes par Condition) ---")
        print(data.groupby("Condition")[["MT", "RMSE", "Mean_Force"]].mean())
        
        print("\n--- ANALYSE TERMINÉE AVEC SUCCÈS ---")