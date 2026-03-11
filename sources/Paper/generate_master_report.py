import os

# --- 1. CONFIGURATION UTILISATEUR & CHEMINS ---
NOM_PRENOM = "Bertrand--Goarin Malo"
ID_ETUDIANT = "2026-XXXX" 
COURSE_NAME = "Engineering and Ergonomics of Physical Activity"
GITHUB_URL = "https://github.com/Malo-ai/Projet_HaptiMed.git"

# Ajustement des chemins pour la structure 'sources/Paper/'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOC_PATH = os.path.join(BASE_DIR, "results")
REPORT_FILE = os.path.join(BASE_DIR, "Bertrand--Goarin.Malo.html")

# --- 2. LISTE DES GRAPHIQUES & CONTEXTE TECHNIQUE ---
GRAPH_DESC = {
    "Tableau_APA_H1_VP.png": {
        "titre": "4.1 Statistiques Descriptives (Loi de Fitts Classique)",
        "formule": "d = (\\mu_E - \\mu_N) / s_{pooled}",
        "detail": "Comparaison du Throughput effectif entre experts et novices en condition standard.",
        "interpret": "Valide la séparation initiale des groupes via le Throughput (ISO 9241-9)."
    },
    "Graph_H1_Fitts_Regression.png": {
        "titre": "4.2 Modélisation de la Loi d'Accot-Zhai",
        "formule": "MT = a + b \\cdot \\int \\frac{1}{W(s)} ds",
        "detail": "Régression linéaire du Temps de Mouvement (MT) selon l'Indice de Difficulté (IDe).",
        "interpret": "La pente b quantifie la sensibilité au rétrécissement du tunnel (coût moteur)."
    },
    "Graph_H2_Degradation_Interaction.png": {
        "titre": "4.3 Résilience à la charge Haptique (Interaction)",
        "formule": "\\Delta IP_e = IP_{e(VP)} - IP_{e(FVP)}",
        "detail": "Analyse de la dégradation de performance sous contrainte de force axiale.",
        "interpret": "L'expertise se manifeste par une moindre dégradation de l'IPe en condition FVP."
    },
    "Graph_H3_Fluidity.png": {
        "titre": "4.4 Qualité du Geste (Smoothness)",
        "formule": "LDLJ = \\ln \\left( \\frac{Duration^5}{PathLength^2} \\int |jerk|^2 dt \\right)",
        "detail": "Mesure de la fluidité via le Log Dimensionless Jerk.",
        "interpret": "Un LDLJ plus bas chez les experts reflète une motricité pré-programmée (Feedforward)."
    },
    "Graph_ML_Comparaison_Accuracy.png": {
        "titre": "4.5 Classification par IA : Apport des données de Force",
        "formule": "\\text{Gain Acc.} = Acc_{FVP} - Acc_{VP}",
        "detail": "Précision de classification des modèles Random Forest.",
        "interpret": "Le gain de précision valide la force comme biomarqueur critique de l'expertise."
    }
}

def generate_report():
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Rapport {NOM_PRENOM} - HMS</title>
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/dist/all-site.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1000px; margin: 0 auto; padding: 40px; background: #f0f2f5; }}
            .paper {{ background: white; padding: 50px; border-radius: 10px; box-shadow: 0 4px 25px rgba(0,0,0,0.1); }}
            .header-info {{ text-align: right; border-bottom: 3px solid #2c3e50; padding-bottom: 20px; margin-bottom: 40px; }}
            h1 {{ color: #2c3e50; text-align: center; text-transform: uppercase; letter-spacing: 2px; }}
            h2 {{ color: #2980b9; border-bottom: 2px solid #2980b9; padding-bottom: 8px; margin-top: 45px; }}
            h3 {{ color: #2c3e50; margin-top: 30px; }}
            .github-link {{ text-align: center; margin: 30px 0; }}
            .github-link a {{ color: #d35400; text-decoration: none; font-weight: bold; border: 2px solid #d35400; padding: 10px 25px; border-radius: 30px; transition: 0.3s; }}
            .github-link a:hover {{ background: #d35400; color: white; }}
            .flowchart {{ background: #2d3436; color: #fab1a0; padding: 25px; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 0.9em; }}
            .analysis-block {{ border: 1px solid #e1e8ed; padding: 30px; margin-bottom: 40px; border-radius: 12px; background: #fff; }}
            .math {{ font-weight: bold; color: #d35400; text-align: center; display: block; margin: 20px 0; font-size: 1.2em; }}
            img {{ max-width: 95%; border-radius: 8px; box-shadow: 0 6px 12px rgba(0,0,0,0.1); transition: 0.3s; cursor: zoom-in; }}
            img:hover {{ transform: scale(1.03); }}
            .highlight-box {{ background: #e8f4fd; padding: 20px; border-left: 6px solid #3498db; margin: 20px 0; border-radius: 4px; }}
            ul {{ padding-left: 20px; }}
        </style>
    </head>
    <body>
        <div class="paper">
            <div class="header-info">
                <strong>{NOM_PRENOM}</strong><br>
                Étudiant Master HMS - EuroMov DHM<br>
                Cours : <em>{COURSE_NAME}</em><br>
                Enseignant : Denis Mottet
            </div>

            <h1>Rapport de Projet : HaptiMed</h1>
            
            <div class="github-link">
                Lien du dépôt GitHub : <a href="{GITHUB_URL}" target="_blank">{GITHUB_URL}</a>
            </div>

            <h2>1. Introduction et Objectifs</h2>
            <p>Ce projet vise à discriminer le niveau d'expertise chirurgicale en comparant l'expérience clinique aux performances biomécaniques quantitatives sur une tâche de pilotage (Steering Task).</p>
            <div class="highlight-box">
                <strong>Paradigme Expérimental :</strong> Navigation dans un tunnel circulaire sous 4 conditions croisant la Difficulté (Loi d'Accot-Zhai) et la Charge Haptique (Force axiale constante basée sur la MVC du sujet).
            </div>

            <h2>2. Architecture du Système (Pipeline)</h2>
            <p>Le projet est structuré de manière modulaire pour garantir la reproductibilité :</p>
            <div class="flowchart">
                [ACQUISITION] (120 Hz) -> data/raw/ (PyQt6)<br>
                [TRAITEMENT] (Butterworth 10Hz) -> sources/Clean_Data/process_data.py<br>
                [STATISTIQUES] (APA & Inférentiel) -> sources/Process_Stat/analysis_master.py<br>
                [IA] (Random Forest Classifier) -> sources/Process_Stat/analysis_ml.py<br>
                [RAPPORT] (Génération dynamique) -> sources/Paper/generate_master_report.py
            </div>

            <h2>3. Méthodologie Technique</h2>
            <h3>3.1 Échantillonnage et Filtrage</h3>
            <p>Conformément au critère de Nyquist-Shannon pour le mouvement humain, les données sont acquises à 120 Hz. Un filtre passe-bas de Butterworth d'ordre 2 à 10 Hz est appliqué pour supprimer le bruit sans déphaser les trajectoires.</p>
            <h3>3.2 Métriques de Performance</h3>
            <p>Nous utilisons le <strong>Throughput ($IP_e$)</strong> comme mesure d'efficience motrice (ISO 9241-9) et le <strong>Log Dimensionless Jerk ($LDLJ$)</strong> pour quantifier la fluidité gestuelle.</p>

            <h2>4. Résultats et Analyses</h2>
    """

    for filename, info in GRAPH_DESC.items():
        img_path = os.path.join(DOC_PATH, filename)
        relative_img_src = f"results/{filename}"
        
        html += f"""
        <div class="analysis-block">
            <h3>{info['titre']}</h3>
            <span class="math">$$ {info['formule']} $$</span>
            <p>{info['detail']}</p>
        """
        
        if os.path.exists(img_path):
            html += f'<div style="text-align:center;"><img src="{relative_img_src}" alt="{filename}"></div>'
        else:
            html += f'<p style="color:#e74c3c; font-weight:bold;">[ERREUR] Graphique {filename} manquant.</p>'
            
        html += f"""
            <div class="highlight-box" style="margin-top:20px;">
                <strong>Interprétation :</strong> {info['interpret']}
            </div>
        </div>
        """

    html += f"""
            <h2>5. Discussion et Conclusion</h2>
            <p>Les résultats valident l'hypothèse selon laquelle l'ajout d'une contrainte de force agit comme un révélateur d'expertise. La stabilité haptique, mesurée par la variabilité de la force, apparaît comme le paramètre le plus discriminant dans nos modèles de classification.</p>

            <hr style="margin-top: 50px;">
            <p style="font-size: 0.85em; color: #7f8c8d; font-style: italic;">
                <strong>Déclaration d'intégrité :</strong> Ce projet a été développé avec l'assistance de l'IA (Gemini 3 Flash) pour l'optimisation des scripts de traitement, la structure du pipeline Python et la mise en forme de ce rapport HTML.
            </p>
        </div>
    </body>
    </html>
    """

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Rapport final complet généré : {REPORT_FILE}")

if __name__ == "__main__":
    generate_report()