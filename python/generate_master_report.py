import os

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_PATH = os.path.join(BASE_DIR, "doc")
REPORT_FILE = os.path.join(DOC_PATH, "Rapport_Master_HaptiMed.html")

# Liste des graphiques et interprétations scientifiques
# Liste des graphiques et interprétations scientifiques (Inclus IA)
GRAPH_DESC = {
    "Tableau_Publication.png": {
        "titre": "Statistiques Descriptives et Inférentielles (Norme APA)",
        "formule": "d = (\\mu_E - \\mu_N) / s_{pooled}",
        "detail": "Résumé complet des tailles d'effets (Cohen's d) et des p-values sur l'ensemble des essais.",
        "interpret": "Observer l'Intervalle de Confiance à 95% pour valider la robustesse de la différence."
    },
    "Graph_H1_Throughput_ISO.png": {
        "titre": "H1 : Performance Effective (ISO 9241-9)",
        "formule": "TP = ID_e / MT",
        "detail": "Le Throughput combine vitesse et précision via la Largeur Effective.",
        "interpret": "Si les boîtes sont disjointes (p < 0.05), l'expertise est validée sur le plan moteur global."
    },
    "Graph_H3_Fluidity.png": {
        "titre": "H3 : Fluidité Cinématique (LDLJ)",
        "formule": "LDLJ = \\ln \\left( \\frac{T^5}{PL^2} \\int |jerk|^2 dt \\right)",
        "detail": "Mesure la propreté du geste indépendamment de la vitesse et de la distance.",
        "interpret": "Un chirurgien expert montre une courbe plus basse, signe d'une pré-programmation motrice stable sans micro-corrections."
    },
    "Graph_ML_Confusion.png": {
        "titre": "Classification Automatique par IA (Random Forest)",
        "formule": "Accuracy = (TP + TN) / Total",
        "detail": "Modèle prédictif utilisant le Throughput, le LDLJ et la Stabilité de Force pour deviner le niveau du participant (Validation Leave-One-Out).",
        "interpret": "Une précision > 80% prouve que l'algorithme HaptiMed peut identifier un chirurgien expert de manière autonome."
    },
    "Graph_ML_Features.png": {
        "titre": "Explicabilité de l'IA (Feature Importance)",
        "formule": "Impureté de Gini (Mean Decrease Impurity)",
        "detail": "Identifie quelles métriques biomécaniques ont le plus aidé l'arbre de décision à classer le sujet.",
        "interpret": "Si la Fluidité (LDLJ) ou le Throughput dominent, cela confirme que l'expertise chirurgicale repose sur l'efficience globale et non sur une seule dimension (comme la vitesse pure)."
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
            .paper {{ background: white; padding: 50px; border-radius: 5px; box-shadow: 0 0 20px rgba(0,0,0,0.1); border-top: 8px solid #2980b9; }}
            h1 {{ color: #2c3e50; text-align: center; text-transform: uppercase; }}
            h2 {{ color: #2980b9; border-bottom: 2px solid #2980b9; padding-bottom: 5px; margin-top: 40px; }}
            .flowchart {{ background: #2d3436; color: #fab1a0; padding: 20px; border-radius: 5px; font-family: monospace; font-size: 0.9em; }}
            .analysis-block {{ margin-bottom: 50px; page-break-inside: avoid; }}
            .graph-box {{ text-align: center; margin: 20px 0; }}
            img {{ max-width: 80%; border: 1px solid #ddd; }}
            .info-panel {{ background: #e8f4fd; padding: 15px; border-left: 5px solid #3498db; margin: 10px 0; }}
            .math {{ font-weight: bold; color: #e67e22; text-align: center; display: block; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="paper">
            <h1>Rapport Technique & Interprétations</h1>
            <p style="text-align: center;"><em>Projet HaptiMed - Analyse de la Dextérité Chirurgicale</em></p>

            <h2>I. Architecture du Pipeline (Dialogue Inter-Scripts)</h2>
            <div class="flowchart">
[Acquisition] steering_task.py -> data/raw/P01_RAW.csv (Pixels, Force Brute)<br>
      |<br>
[Calcul]      process_data.py  -> data/features/dataset_features.csv (Métriques ISO & LDLJ)<br>
      |<br>
[Visuels]    analysis_global.py -> doc/*.png (Graphiques Statistiques)<br>
      |<br>
[Synthèse]   generate_master_report.py -> Ce fichier HTML (Interprétation finale)
            </div>

            <h2>II. Résultats Expérimentaux et Discussion</h2>
    """

    for filename, info in GRAPH_DESC.items():
        img_path = os.path.join(DOC_PATH, filename)
        
        html += f"""
        <div class="analysis-block">
            <h3>{info['titre']}</h3>
            <span class="math">$$ {info['formule']} $$</span>
            <p>{info['detail']}</p>
        """
        
        if os.path.exists(img_path):
            html += f'<div class="graph-box"><img src="{filename}"></div>'
        else:
            html += f'<p style="color:red;">[ERREUR] Graphique {filename} absent. Lancez d\'abord analysis_global.py.</p>'
            
        html += f"""
            <div class="info-panel">
                <strong>Interprétation suggérée :</strong> {info['interpret']}<br><br>
                <strong>Observations Personnalisées :</strong><br>
                <div style="min-height: 60px; border: 1px dashed #3498db; padding: 10px; background: white;">
                    [Cliquez ici pour rédiger votre analyse spécifique à ce graphique...]
                </div>
            </div>
        </div>
        """

    html += """
            <h2>III. Conclusion Générale</h2>
            <p>Ce rapport permet de valider les hypothèses H1 (Performance), H2 (Force) et H3 (Fluidité). Les données traitées à 120Hz après filtrage de Butterworth (10Hz) garantissent la précision des calculs de dérivées (Jerk).</p>
        </div>
    </body>
    </html>
    """

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Rapport HTML généré : {REPORT_FILE}")

if __name__ == "__main__":
    generate_report()