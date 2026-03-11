# generate_master_report.py - GÉNÉRATION DU RAPPORT HTML FINAL
import os

# 1. CONFIGURATION DES CHEMINS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOC_PATH = os.path.join(BASE_DIR, "doc")
REPORT_FILE = os.path.join(BASE_DIR, "Rapport_Master_HaptiMed.html")

# 2. LISTE ENRICHIE DES GRAPHIQUES (Preuves Scientifiques)
GRAPH_DESC = {
    "Tableau_APA_H1_VP.png": {
        "titre": "Statistiques Descriptives (Loi de Fitts Classique)",
        "formule": "d = (\\mu_E - \\mu_N) / s_{pooled}",
        "detail": "Résumé des performances sur la tâche classique sans force.",
        "interpret": "Valide la séparation initiale des groupes sur les métriques standard."
    },
    "Graph_H1_Fitts_Metrics.png": {
        "titre": "H1 : Efficience vs Coût Moteur",
        "formule": "IP_e \\text{ vs } B_e",
        "detail": "Comparaison directe de l'indice de performance et de la pente de difficulté.",
        "interpret": "Un expert doit avoir un IPe haut ET un Be bas (moindre sensibilité à la difficulté)."
    },
    "Graph_H1_Fitts_Regression.png": {
        "titre": "H1 : Modélisation de la Loi de Fitts",
        "formule": "MT = a + b \\cdot ID_e",
        "detail": "Régression linéaire du Temps de Mouvement en fonction de la Difficulté.",
        "interpret": "La pente (b) plus faible chez les experts démontre une meilleure gestion de l'incertitude spatiale."
    },
    "Graph_H2_Degradation_Interaction.png": {
        "titre": "H2 : Résilience à la charge Haptique",
        "formule": "\\Delta IP_e = IP_{e(VP)} - IP_{e(FVP)}",
        "detail": "Analyse de l'interaction entre l'expertise et la contrainte de force.",
        "interpret": "L'écart croissant entre les courbes prouve que la force est un 'stress test' qui révèle l'expertise."
    },
    "Graph_H2_ForceSD.png": {
        "titre": "H2 : Stabilité du Contrôle Haptique",
        "formule": "Force\\_{SD} = \\sqrt{\\frac{1}{N} \\sum (P_i - \\bar{P})^2}",
        "detail": "Variabilité de la pression axiale exercée sur la tablette.",
        "interpret": "Une faible variance (SD) est la signature d'un contrôle sensorimoteur expert."
    },
    "Graph_H3_Fluidity.png": {
        "titre": "H3 : Qualité du Geste (Fluidité)",
        "formule": "LDLJ = \\ln \\left( \\frac{Duration^5}{PathLength^2} \\int |jerk|^2 dt \\right)",
        "detail": "Mesure de la propreté cinématique (Log Dimensionless Jerk).",
        "interpret": "Les valeurs plus basses chez les experts confirment un mouvement programmé et non saccadé."
    },
    "Graph_Correl_Experience_Perf.png": {
        "titre": "Validité Clinique : Courbe d'Apprentissage",
        "formule": "r_{Pearson} (\\text{Expérience}, IP_e)",
        "detail": "Lien entre la pratique réelle (années) et la performance virtuelle.",
        "interpret": "Prouve que le simulateur HaptiMed mesure une compétence chirurgicale réelle."
    },
    "Graph_ML_Comparaison_Accuracy.png": {
        "titre": "Intelligence Artificielle : Valeur Ajoutée de la Force",
        "formule": "\\text{Gain Acc.} = Acc_{FVP} - Acc_{VP}",
        "detail": "Comparaison de la précision de classification des modèles Random Forest.",
        "interpret": "Si le gain est significatif, la force est validée comme biomarqueur de l'expertise."
    },
    "Graph_ML_Features_FVP.png": {
        "titre": "Explicabilité de l'IA (Feature Importance)",
        "formule": "\\text{Mean Decrease Impurity (Gini)}",
        "detail": "Poids de chaque métrique biomécanique dans la décision de l'algorithme Random Forest.",
        "interpret": "Si la 'Stabilité Force' ou le 'Be' dominent, cela confirme que ces métriques sont les vrais marqueurs de l'expertise."
    }
}

def generate_report():
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Rapport d'Analyse Master - HaptiMed</title>
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/dist/all-site.js"></script>
        <style>
            body {{ font-family: 'Helvetica', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1100px; margin: 0 auto; padding: 40px; background: #f4f7f6; }}
            .paper {{ background: white; padding: 50px; border-radius: 5px; box-shadow: 0 0 20px rgba(0,0,0,0.1); border-top: 8px solid #2c3e50; }}
            h1 {{ color: #2c3e50; text-align: center; text-transform: uppercase; }}
            h2 {{ color: #2980b9; border-bottom: 2px solid #2980b9; padding-bottom: 5px; margin-top: 40px; }}
            .flowchart {{ background: #2d3436; color: #a29bfe; padding: 20px; border-radius: 5px; font-family: monospace; font-size: 0.95em; line-height: 1.5; }}
            .analysis-block {{ margin-bottom: 50px; page-break-inside: avoid; border: 1px solid #eee; padding: 20px; border-radius: 8px; }}
            .graph-box {{ text-align: center; margin: 20px 0; }}
            
            /* --- EFFET ZOOM SUR LES IMAGES --- */
            img {{ 
                max-width: 85%; 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                box-shadow: 0 4px 8px rgba(0,0,0,0.05);
                transition: transform 0.3s ease; 
            }}
            img:hover {{
                transform: scale(1.05);
                cursor: zoom-in;
            }}
            /* ---------------------------------- */

            .info-panel {{ background: #e8f4fd; padding: 15px; border-left: 5px solid #3498db; margin: 10px 0; border-radius: 0 5px 5px 0; }}
            .math {{ font-weight: bold; color: #e67e22; text-align: center; display: block; margin: 15px 0; font-size: 1.1em; }}
        </style>
    </head>
    <body>
        <div class="paper">
            <h1>Rapport Technique & Interprétations</h1>
            <p style="text-align: center; font-size: 1.2em; color: #7f8c8d;"><em>Projet HaptiMed - Évaluation Biomécanique de l'Expertise Chirurgicale</em></p>

            <h2>I. Architecture du Pipeline (Dialogue Inter-Scripts)</h2>
            <div class="flowchart">
[1. Passation_Test] steering_task.py   -> data/raw/ (Coordonnées X,Y, Pression)<br>
      |<br>
[2. Clean_Data]     process_data.py    -> data/features/ (Calcul de IPe, IDe, Be, LDLJ)<br>
      |<br>
[3. Process_Stat]   analysis_master.py -> doc/*.png (Stats APA & Visuels H1/H2/H3)<br>
                    analysis_ml.py     -> doc/*.png (Modèles IA Random Forest)<br>
      |<br>
[4. Paper]          generate_master_report.py -> Ce fichier HTML
            </div>

            <h2>II. Résultats Expérimentaux et Discussion</h2>
    """

    for filename, info in GRAPH_DESC.items():
        img_path = os.path.join(DOC_PATH, filename)
        relative_img_src = f"doc/{filename}"
        
        html += f"""
        <div class="analysis-block">
            <h3 style="color: #2c3e50;">{info['titre']}</h3>
            <span class="math">$$ {info['formule']} $$</span>
            <p>{info['detail']}</p>
        """
        
        if os.path.exists(img_path):
            html += f'<div class="graph-box"><img src="{relative_img_src}" alt="Graphique {filename}"></div>'
        else:
            html += f'<p style="color:#e74c3c; font-weight:bold;">[ATTENTE] Graphique {filename} absent dans doc/.</p>'
            
        html += f"""
            <div class="info-panel">
                <strong>Interprétation suggérée :</strong> {info['interpret']}<br><br>
                <strong>Observations Personnalisées :</strong><br>
                <div style="min-height: 80px; border: 1px dashed #bdc3c7; padding: 10px; background: white; margin-top: 10px; color: #95a5a6;">
                    [Cliquez ici ou imprimez ce document pour rédiger votre analyse spécifique...]
                </div>
            </div>
        </div>
        """

    html += """
            <h2>III. Conclusion Générale</h2>
            <p>Ce rapport permet de valider de manière reproductible les hypothèses H1 (Performance), H2 (Force haptique) et H3 (Fluidité). Les données traitées à 120Hz après filtrage de Butterworth garantissent la précision des calculs cinématiques dérivés, validant l'intégration de la variable force ($Force\\_SD$) au sein de la norme ISO 9241-9 ($IP_e$).</p>
        </div>
    </body>
    </html>
    """

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Rapport HTML généré avec succès : {REPORT_FILE}")

if __name__ == "__main__":
    generate_report()