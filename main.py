# main.py - POINT D'ENTRÉE UNIQUE DU PROJET HAPTIMED
import os
import subprocess
import sys

def run_script(script_path):
    """Lance un script Python et vérifie s'il s'est bien exécuté."""
    print(f"\n" + "="*50)
    print(f"RUNNING: {script_path}")
    print("="*50)
    
    try:
        # On utilise subprocess pour garantir l'isolation et la gestion des erreurs
        result = subprocess.run([sys.executable, script_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERREUR fatale dans {script_path}")
        print(f"Code d'erreur : {e.returncode}")
        return False

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DU PIPELINE HAPTIMED (Master HMS)")
    
    # Liste des scripts dans l'ordre logique de la thèse
    # Attention : Vérifie que tes dossiers sont bien renommés en 'sources'
    pipeline = [
        "sources/Clean_Data/process_data.py",    # 1. Traitement & Filtrage
        "sources/Process_Stat/analysis_master.py", # 2. Stats & Graphiques
        "sources/Process_Stat/analysis_ml.py",     # 3. Machine Learning
        "sources/Paper/generate_master_report.py"  # 4. Rapport HTML final
    ]
    
    success_count = 0
    for script in pipeline:
        if not os.path.exists(script):
            print(f"⚠️ FICHIER INTROUVABLE : {script}")
            print("Vérifiez l'organisation de vos dossiers (sources/...)")
            break
            
        if run_script(script):
            success_count += 1
        else:
            print("\n⛔ Arrêt du pipeline suite à une erreur.")
            break

    if success_count == len(pipeline):
        print("\n" + "!"*50)
        print("✅ TOUT EST PRÊT ! Le rapport HTML est disponible.")
        print("!"*50)