# analysis_ml.py - MACHINE LEARNING COMPLET (Version IPe / Be)
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import LeaveOneOut
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FEATURES_FILE = os.path.join(BASE_DIR, "data", "features", "dataset_features.csv")
DOC_PATH = os.path.join(BASE_DIR, "doc")

# Style seaborn
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

def train_and_evaluate(df, features, feature_names, model_name):
    # Nettoyage des NaNs pour les variables sélectionnées
    df_clean = df.dropna(subset=features)
    if len(df_clean) < 4:
        print(f"⚠️ Pas assez de données pour le modèle {model_name}.")
        return 0, np.zeros((2,2)), pd.DataFrame()
        
    X = df_clean[features]
    y = df_clean['Group']

    loo = LeaveOneOut()
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    y_true, y_pred = [], []
    for train_index, test_index in loo.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        model.fit(X_train, y_train)
        y_pred.append(model.predict(X_test)[0])
        y_true.append(y_test.values[0])

    acc = accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=['Novice', 'Expert'])
    
    model.fit(X, y)
    fi_df = pd.DataFrame({'Variable': feature_names, 'Importance': model.feature_importances_ * 100})
    fi_df = fi_df.sort_values(by='Importance', ascending=False)
    
    return acc, cm, fi_df

def run_ml_classification():
    print("\n--- ENTRAÎNEMENT DES MODÈLES IA (Random Forest) ---")
    if not os.path.exists(FEATURES_FILE): 
        print("Fichier features introuvable."); return
    
    df = pd.read_csv(FEATURES_FILE)
    df = df[df['Group'].isin(['Novice', 'Expert'])]
    
    df['Tache_Type'] = df['Condition'].apply(lambda x: 'FVP' if str(x).startswith('FVP') else 'VP')
    df_vp = df[df['Tache_Type'] == 'VP']
    df_fvp = df[df['Tache_Type'] == 'FVP']

    # --- MODÈLE 1 : VP (Avec IPe et Be) ---
    features_vp = ['IPe', 'Be', 'LDLJ', 'Te']
    names_vp = ['Performance (IPe)', 'Pente (Be)', 'Fluidité (LDLJ)', 'Précision (Te)']
    print("Entraînement Modèle 1 (VP - Sans Force)...")
    acc_vp, cm_vp, fi_vp = train_and_evaluate(df_vp, features_vp, names_vp, "VP")

    # --- MODÈLE 2 : FVP (Ajout Force_SD) ---
    features_fvp = ['IPe', 'Be', 'LDLJ', 'Te', 'Force_SD']
    names_fvp = ['Performance (IPe)', 'Pente (Be)', 'Fluidité (LDLJ)', 'Précision (Te)', 'Stabilité Force']
    print("Entraînement Modèle 2 (FVP - Avec Force)...")
    acc_fvp, cm_fvp, fi_fvp = train_and_evaluate(df_fvp, features_fvp, names_fvp, "FVP")

    # --- GRAPHIQUES ---
    if acc_vp > 0 or acc_fvp > 0:
        # 1. Comparaison Accuracy
        plt.figure(figsize=(6, 5))
        sns.barplot(x=['Modèle VP', 'Modèle FVP'], y=[acc_vp*100, acc_fvp*100], palette=['#3498db', '#e74c3c'])
        plt.title("H2 : Précision de l'IA (Validation LOO)", pad=15, weight='bold')
        plt.ylabel("Accuracy (%)")
        plt.ylim(0, 105)
        plt.savefig(os.path.join(DOC_PATH, "Graph_ML_Comparaison_Accuracy.png"), dpi=300)
        plt.close()

        # 2. Importance des variables (Modèle complet FVP)
        plt.figure(figsize=(7, 4))
        sns.barplot(x='Importance', y='Variable', data=fi_fvp, palette="magma")
        plt.title("Importance des marqueurs biomécaniques", pad=15)
        plt.xlabel("Poids dans la décision (%)")
        plt.savefig(os.path.join(DOC_PATH, "Graph_ML_Features_FVP.png"), dpi=300, bbox_inches='tight')
        plt.close()

    print(f"\n[RÉSULTATS]")
    print(f"Accuracy VP  : {acc_vp*100:.1f}%")
    print(f"Accuracy FVP : {acc_fvp*100:.1f}%")
    print(f"✅ Graphiques IA générés dans {DOC_PATH}")

if __name__ == "__main__":
    run_ml_classification()