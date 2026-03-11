# generate_tech_doc.py - DOCUMENTATION TECHNIQUE ET SCIENTIFIQUE COMPLÈTE
import os

# --- CONFIGURATION DES CHEMINS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOC_PATH = os.path.join(BASE_DIR, "doc")
if not os.path.exists(DOC_PATH): 
    os.makedirs(DOC_PATH)

# --- GÉNÉRATION DU CONTENU HTML (Utilisation de r""" pour le LaTeX et le formis) ---
html_content = r"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Documentation Haute Fidélité - HaptiMed</title>
    
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" 
        onload="renderMathInElement(document.body, {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false}
            ]
        });">
    </script>
    
    <style>
        :root { --bg: #ffffff; --text: #333; --primary: #2c3e50; --secondary: #2980b9; --accent: #e74c3c; --box-bg: #f8f9fa; --border: #dee2e6; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; line-height: 1.6; color: var(--text); max-width: 1100px; margin: 0 auto; padding: 40px; background: var(--bg); }
        h1 { color: var(--primary); text-align: center; border-bottom: 3px solid var(--secondary); padding-bottom: 15px; margin-bottom: 30px; }
        h2 { color: var(--secondary); margin-top: 50px; border-left: 5px solid var(--secondary); padding-left: 15px; background: var(--box-bg); padding: 12px; }
        h3 { color: var(--primary); border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 35px;}
        
        /* Grille des Hypothèses */
        .hypotheses-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 25px 0; }
        .hyp-card { padding: 20px; border-radius: 8px; border-top: 5px solid; background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        .hyp-card h4 { margin: 0 0 10px 0; color: var(--primary); }
        .hyp-tag { display: inline-block; margin-top: 10px; font-size: 0.8em; font-weight: bold; text-transform: uppercase; color: var(--secondary); }

        /* Sommaire */
        .toc { background: var(--box-bg); padding: 25px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 40px; }
        .toc ul { list-style: none; padding-left: 0; }
        .toc li { margin-bottom: 10px; font-weight: 600; }
        .toc a { text-decoration: none; color: var(--secondary); }
        .toc .file-desc { font-weight: normal; font-size: 0.85em; color: #666; display: block; margin-left: 20px; }
        
        /* Boîtes Entrées/Sorties */
        .io-container { display: flex; gap: 20px; margin: 20px 0; }
        .io-box { flex: 1; padding: 15px; border-radius: 6px; border-left: 5px solid; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.05); font-size: 0.9em; }
        .io-in { border-color: #27ae60; }
        .io-out { border-color: #e67e22; }
        
        /* Détails Code */
        details { background: var(--box-bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px 18px; margin: 20px 0; }
        summary { font-weight: bold; cursor: pointer; color: var(--secondary); }
        .var-name { font-family: 'Consolas', monospace; color: #c0392b; background: #fef5f5; padding: 2px 6px; border-radius: 4px; border: 1px solid #fadbd8; }
        .lib-link { color: #2980b9; font-weight: bold; text-decoration: none; }
        
        .math-box { background: #fff; border: 1px dashed #bdc3c7; padding: 20px; text-align: center; margin: 25px 0; border-radius: 8px; font-size: 1.2em; }
        .transition-phrase { font-style: italic; color: #7f8c8d; text-align: right; margin-top: 30px; border-right: 3px solid var(--border); padding-right: 10px; }
    </style>
</head>
<body>

    <h1>Documentation Technique & Scientifique HaptiMed</h1>

    <div class="toc">
        <h2>Sommaire des Processus</h2>
        <ul>
            <li><a href="#partie1">1. Protocole Expérimental et Setup</a>
                <span class="file-desc">Définition de la cohorte (Experts/Novices) et des hypothèses H1, H2, H3.</span></li>
            <li><a href="#partie2">2. Calibration de Force (<code>calibration_mvc.py</code>)</a>
                <span class="file-desc">Normalisation via la Contraction Volontaire Maximale (MVC).</span></li>
            <li><a href="#partie3">3. Acquisition Haute Fréquence (<code>steering_task.py</code>)</a>
                <span class="file-desc">Capture sub-pixel 120Hz des trajectoires et pressions axiales.</span></li>
            <li><a href="#partie4">4. Traitement Cinématique (<code>process_data.py</code>)</a>
                <span class="file-desc">Filtrage Butterworth et calcul des métriques ISO (IPe, IDe, Be) et Smoothness (LDLJ).</span></li>
            <li><a href="#partie5">5. Analyse Inférentielle (<code>analysis_master.py</code>)</a>
                <span class="file-desc">Validation statistique (T-test, Cohen's d) et tableaux APA.</span></li>
            <li><a href="#partie6">6. Machine Learning (<code>analysis_ml.py</code>)</a>
                <span class="file-desc">Classification prédictive par Random Forest (Comparaison VP vs FVP).</span></li>
        </ul>
    </div>

    <h2 id="partie1">1. Protocole Expérimental et Hypothèses</h2>
    <p>Cette étude vise à quantifier l'expertise chirurgicale par l'intégration d'une contrainte de force axiale dans une tâche de pilotage (Steering Task).</p>

    <div class="hypotheses-grid">
        <div class="hyp-card" style="border-top-color: #3498db;">
            <h4>H1 : Performance ISO</h4>
            <p>Le Throughput effectif ($IP_e$) suffit à discriminer les groupes en condition classique.</p>
            <span class="hyp-tag">Indice de performance</span>
        </div>
        <div class="hyp-card" style="border-top-color: #9b59b6;">
            <h4>H2 : Interaction Haptique</h4>
            <p>L'ajout de force (FVP) dégrade la performance des novices mais pas celle des experts.</p>
            <span class="hyp-tag">Résilience motrice</span>
        </div>
        <div class="hyp-card" style="border-top-color: #27ae60;">
            <h4>H3 : Fluidité (LDLJ)</h4>
            <p>Les experts présentent un geste plus fluide (moindre Jerk) que les novices.</p>
            <span class="hyp-tag">Qualité cinématique</span>
        </div>
        <div class="hyp-card" style="border-top-color: #e67e22;">
            <h4>Validité Clinique</h4>
            <p>Forte corrélation entre les scores de la tablette et l'ancienneté réelle du praticien.</p>
            <span class="hyp-tag">Ancienneté (Années)</span>
        </div>
    </div>

    <h2 id="partie2">2. Calibration de Force (<code>calibration_mvc.py</code>)</h2>
    <p>Normalise l'effort requis durant la tâche FVP en fonction de la force maximale du sujet.</p>
    
    <div class="io-container">
        <div class="io-box io-in"><b>Entrée :</b> Événements de pression brute via le driver Wacom.</div>
        <div class="io-box io-out"><b>Sortie :</b> Fichier <code>last_mvc.txt</code> (Valeur 0-8192).</div>
    </div>

    <details>
        <summary>Détails Techniques & Bibliothèques</summary>
        <ul>
            <li><a class="lib-link" href="https://doc.qt.io/qtforpython-6/">PyQt6</a> : Utilisation de <span class="var-name">QTabletEvent</span> pour une capture haute précision.</li>
            <li><span class="var-name">event.pressure()</span> : Récupère la pression normalisée (0.0 à 1.0).</li>
        </ul>
    </details>

    <h2 id="partie3">3. Acquisition (<code>steering_task.py</code>)</h2>
    <p>Interface interactive simulant un tunnel chirurgical circulaire.</p>

    <div class="math-box">
        $$ f_s = 120 \text{ Hz} \quad \text{(Respect du critère de Nyquist-Shannon)} $$
    </div>

    <div class="io-container">
        <div class="io-box io-in"><b>Entrée :</b> Rayon $R$ et Largeur $W$ du tunnel.</div>
        <div class="io-box io-out"><b>Sortie :</b> Fichier CSV <code>ID_RAW.csv</code> (X, Y, Pression, Temps).</div>
    </div>

    <details>
        <summary>Variables du Code</summary>
        <ul>
            <li><span class="var-name">QPainter</span> : Rendu vectoriel du tunnel et du feedback de force (épaisseur du trait).</li>
            <li><span class="var-name">Time_Abs</span> : Horodatage précis pour le calcul des dérivées ultérieures.</li>
        </ul>
    </details>

    <h2 id="partie4">4. Traitement Cinématique (<code>process_data.py</code>)</h2>
    <p>Nettoyage des signaux et calcul des métriques biomécaniques avancées.</p>

    <div class="math-box">
        $$ LDLJ = \ln \left( \frac{MT^5}{L^2} \int |jerk|^2 dt \right) $$
        $$ IP_e = \frac{ID_e}{MT} \quad ; \quad MT = a + b \cdot ID_e $$
    </div>

    <details>
        <summary>Algorithmes & Filtres</summary>
        <ul>
            <li><a class="lib-link" href="https://scipy.org/">SciPy</a> : Filtre de Butterworth d'ordre 2 (Coupure 10Hz) via <span class="var-name">filtfilt</span>.</li>
            <li><span class="var-name">np.gradient</span> : Calcul des vecteurs Vitesse, Accélération et Jerk.</li>
            <li><span class="var-name">stats.linregress</span> : Extraction du coefficient <span class="var-name">Be</span> (pente de Fitts).</li>
        </ul>
    </details>

    <h2 id="partie5">5. Analyse Inférentielle (<code>analysis_master.py</code>)</h2>
    <p>Génération de preuves statistiques pour valider les hypothèses H1, H2 et H3.</p>

    <div class="math-box">
        $$ d = \frac{\bar{x}_E - \bar{x}_N}{s_{pooled}} \quad \text{(Taille de l'effet de Cohen)} $$
    </div>

    <div class="io-container">
        <div class="io-box io-in"><b>Entrée :</b> <code>dataset_features.csv</code>.</div>
        <div class="io-box io-out"><b>Sortie :</b> Tableaux APA (.xlsx) et Boxplots (.png).</div>
    </div>

    <h2 id="partie6">6. Modélisation par IA (<code>analysis_ml.py</code>)</h2>
    <p>Utilisation d'un classifieur pour automatiser le diagnostic du niveau d'expertise.</p>

    <details>
        <summary>Architecture du Modèle</summary>
        <ul>
            <li><a class="lib-link" href="https://scikit-learn.org/">Scikit-Learn</a> : Algorithme <b>Random Forest</b> (100 arbres).</li>
            <li><b>Validation :</b> Leave-One-Out Cross-Validation (LOO CV).</li>
            <li><b>Métriques :</b> Accuracy et Matrice de Confusion.</li>
        </ul>
    </details>

    <div class="math-box">
        $$ \text{Gain de performance de l'IA} = Acc_{FVP} - Acc_{VP} $$
    </div>

</body>
</html>
"""

# --- SAUVEGARDE ---
output_file = os.path.join(BASE_DIR, "Documentation_Technique_Globale.html")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[SUCCÈS] Documentation technique INTÉGRALE générée à la racine : {output_file}")