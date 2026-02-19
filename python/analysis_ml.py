# analysis_ml.py - MACHINE LEARNING COMPLET (Sutton-Charagni)
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import LeaveOneOut
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEATURES_FILE = os.path.join(BASE_DIR, "data", "features", "dataset_features.csv")
DOC_PATH = os.path.join(BASE_DIR, "doc")

# Style seaborn
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

def run_ml_classification():
    print("\n--- ENTRAÎNEMENT DU MODÈLE IA (Random Forest) ---")
    if not os.path.exists(FEATURES_FILE): 
        print("Fichier features introuvable."); return
    
    df = pd.read_csv(FEATURES_FILE)
    df = df[df['Group'].isin(['Novice', 'Expert'])].dropna(subset=['Throughput_ISO', 'LDLJ', 'Te', 'Force_SD'])
    
    if len(df) < 4: 
        print("Pas assez de données pour l'IA."); return

    # Variables prédictives (Features)
    features = ['Throughput_ISO', 'LDLJ', 'Te', 'Force_SD']
    feature_names = ['Performance (ISO)', 'Fluidité (LDLJ)', 'Précision (Te)', 'Stabilité (Force)']
    
    X = df[features]
    y = df['Group']

    # Validation Croisée (Leave-One-Out)
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

    # 1. GRAPHIQUE : Matrice de Confusion
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Novice', 'Expert'], yticklabels=['Novice', 'Expert'], cbar=False)
    plt.title(f"Matrice de Confusion\n(Accuracy : {acc*100:.1f}%)", pad=15)
    plt.ylabel("Vérité Terrain")
    plt.xlabel("Prédiction de l'IA")
    plt.savefig(os.path.join(DOC_PATH, "Graph_ML_Confusion.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. GRAPHIQUE : Feature Importance (Nouveau !)
    # On ré-entraîne le modèle sur toutes les données pour avoir l'importance globale
    model.fit(X, y)
    importances = model.feature_importances_
    
    # Création d'un DataFrame pour faciliter l'affichage
    fi_df = pd.DataFrame({'Variable': feature_names, 'Importance': importances * 100})
    fi_df = fi_df.sort_values(by='Importance', ascending=False)
    
    plt.figure(figsize=(6, 4))
    sns.barplot(x='Importance', y='Variable', data=fi_df, palette="viridis")
    plt.title("Importance des Variables dans la Décision de l'IA", pad=15)
    plt.xlabel("Poids dans le modèle (%)")
    plt.ylabel("")
    plt.savefig(os.path.join(DOC_PATH, "Graph_ML_Features.png"), dpi=300, bbox_inches='tight')
    plt.close()

    print(f"[IA] Précision du modèle : {acc*100:.1f}%")
    print(f"[IA] Graphiques IA générés dans {DOC_PATH}")

if __name__ == "__main__":
    run_ml_classification()