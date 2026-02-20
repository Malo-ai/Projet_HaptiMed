import os

# --- CONFIGURATION DES CHEMINS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_PATH = os.path.join(BASE_DIR, "doc")
if not os.path.exists(DOC_PATH): 
    os.makedirs(DOC_PATH)

# --- GÉNÉRATION DU CONTENU HTML (Utilisation de r""" pour le LaTeX) ---
html_content = r"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Documentation Scientifique - HaptiMed</title>
    
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
        body { font-family: 'Segoe UI', system-ui, sans-serif; line-height: 1.6; color: var(--text); max-width: 1000px; margin: 0 auto; padding: 40px; background: var(--bg); }
        h1 { color: var(--primary); text-align: center; border-bottom: 3px solid var(--secondary); padding-bottom: 15px; margin-bottom: 30px; }
        h2 { color: var(--secondary); margin-top: 50px; border-left: 5px solid var(--secondary); padding-left: 15px; background: var(--box-bg); padding: 12px; }
        h3 { color: var(--primary); border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 35px;}
        
        /* Sommaire */
        .toc { background: var(--box-bg); padding: 25px; border-radius: 8px; border: 1px solid var(--border); margin-bottom: 40px; }
        .toc h2 { background: transparent; border: none; padding: 0; margin-top: 0; }
        .toc ul { list-style: none; padding-left: 0; }
        .toc li { margin-bottom: 15px; font-weight: 600; }
        .toc a { text-decoration: none; color: var(--secondary); transition: color 0.2s; }
        .toc a:hover { color: var(--accent); }
        .toc .file-desc { font-weight: normal; font-size: 0.9em; color: #666; display: block; margin-left: 22px; }
        
        /* Boîtes Entrées/Sorties */
        .io-container { display: flex; gap: 20px; margin: 20px 0; }
        .io-box { flex: 1; padding: 15px; border-radius: 6px; border-left: 5px solid; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.05); font-size: 0.9em; }
        .io-in { border-color: #27ae60; }
        .io-out { border-color: #e67e22; }
        
        /* Accordéon Détails Code */
        details { background: var(--box-bg); border: 1px solid var(--border); border-radius: 6px; padding: 12px 18px; margin: 20px 0; }
        summary { font-weight: bold; cursor: pointer; color: var(--secondary); outline: none; }
        .var-name { font-family: 'Consolas', monospace; color: #c0392b; background: #fef5f5; padding: 2px 6px; border-radius: 4px; border: 1px solid #fadbd8; }
        
        /* Math & Transition */
        .math-box { background: #fff; border: 1px dashed #bdc3c7; padding: 20px; text-align: center; margin: 25px 0; border-radius: 8px; overflow-x: auto; font-size: 1.1em; }
        .transition-phrase { font-style: italic; color: #7f8c8d; text-align: right; margin-top: 40px; padding-right: 10px; border-right: 3px solid var(--border); }
        .lib-link { color: #2980b9; font-weight: bold; text-decoration: none; border-bottom: 1px solid transparent; }
        .lib-link:hover { border-bottom-color: var(--secondary); }
    </style>
</head>
<body>

    <h1>Documentation Technique HaptiMed<br><small>Pipeline de traitement et analyse de l'expertise chirurgicale</small></h1>

    <div class="toc">
        <h2>Sommaire des Processus</h2>
        <ul>
            <li><a href="#partie1">1. Protocole Expérimental et Setup</a>
                <span class="file-desc">Définition scientifique de la cohorte et du dispositif haptique.</span>
            </li>
            <li><a href="#partie2">2. Calibration de Force (<code>calibration_mvc.py</code>)</a>
                <span class="file-desc">Détermination de la Contraction Volontaire Maximale (MVC).</span>
            </li>
            <li><a href="#partie3">3. Acquisition Haute Fréquence (<code>steering_task.py</code>)</a>
                <span class="file-desc">Capture temps-réel des trajectoires et de la pression (120 Hz).</span>
            </li>
            <li><a href="#partie4">4. Prétraitement Cinématique (<code>process_data.py</code>)</a>
                <span class="file-desc">Filtrage Butterworth et extraction des features (ISO/LDLJ).</span>
            </li>
            <li><a href="#partie5">5. Analyse Inférentielle (<code>analysis_publication.py</code>)</a>
                <span class="file-desc">Tests statistiques de Welch, Cohen's d et formatage APA.</span>
            </li>
            <li><a href="#partie6">6. Modélisation Prédictive (<code>analysis_ml.py</code>)</a>
                <span class="file-desc">Classification Expert/Novice par Intelligence Artificielle.</span>
            </li>
        </ul>
    </div>

    <h2 id="partie1">1. Protocole Expérimental et Setup</h2>
    <p>Ce protocole vise à comparer la signature motrice d'experts et de novices lors d'une tâche de navigation guidée sous contrainte de force.</p>
    
    

    <h3>Consignes et Schéma de l'expérience</h3>
    <ul>
        <li><b>Cohorte :</b> Sujets Experts (Chirurgiens) vs Novices (Étudiants).</li>
        <li><b>Tâche :</b> Effectuer un tour complet dans un tunnel circulaire de rayon $R$ et largeur $W$.</li>
        <li><b>Conditions :</b> VP (Vitesse-Précision) et FVP (Force-Vitesse-Précision).</li>
    </ul>

    <p class="transition-phrase">➔ Une fois le sujet installé, nous procédons à la calibration physique de son profil de force.</p>

    <hr>

    <h2 id="partie2">2. Calibration de Force (<code>calibration_mvc.py</code>)</h2>
    <h3>Objectif et Justification</h3>
    <p>Normaliser l'effort haptique en fonction des capacités physiques intrinsèques de chaque individu pour garantir une comparaison inter-sujets équitable.</p>
    
    <div class="io-container">
        <div class="io-box io-in"><b>Entrée :</b> Signal continu de pression $P \in [0.0, 1.0]$.</div>
        <div class="io-box io-out"><b>Sortie :</b> Valeur maximale $MVC \in [0, 8192]$ enregistrée dans <code>last_mvc.txt</code>.</div>
    </div>

    <h3>Bibliothèques</h3>
    <ul>
        <li><a class="lib-link" href="https://doc.qt.io/qtforpython-6/">PyQt6</a> : Gestion de l'interface et du matériel (QTabletEvent).</li>
    </ul>

    <details>
        <summary>Détail de l'architecture et variables</summary>
        <p>Le script utilise une boucle d'écoute événementielle. Si la pression actuelle dépasse le maximum stocké, la valeur est mise à jour.</p>
        <ul>
            <li><span class="var-name">event.pressure()</span> : Pression normalisée par le driver.</li>
            <li><span class="var-name">RAW_MAX</span> : 8192 (Résolution Wacom Pro Pen 3).</li>
        </ul>
    </details>

    <p class="transition-phrase">➔ Le profil de force étant établi, le sujet peut lancer la tâche d'acquisition.</p>

    <hr>

    <h2 id="partie3">3. Acquisition (<code>steering_task.py</code>)</h2>
    <h3>Objectif et Justification</h3>
    <p>Capturer la performance motrice brute. La fréquence d'échantillonnage de 120 Hz est choisie pour respecter le critère de Nyquist vis-à-vis du tremblement physiologique (8-12 Hz).</p>

    <div class="math-box">
        $$ f_s \ge 2 \cdot f_{max} $$
    </div>

    <h3>Bibliothèques</h3>
    <ul>
        <li><a class="lib-link" href="https://doc.qt.io/qtforpython-6/">PyQt6</a> : Rendu graphique (QPainter) et capture sub-pixel.</li>
        <li><a class="lib-link" href="https://numpy.org/">NumPy</a> : Calculs géométriques en temps réel.</li>
    </ul>

    <details>
        <summary>Détail de l'architecture et variables</summary>
        <ul>
            <li><span class="var-name">Time_Abs</span> : Temps Unix (s).</li>
            <li><span class="var-name">QPointF</span> : Coordonnées X, Y en précision flottante.</li>
        </ul>
    </details>

    <p class="transition-phrase">➔ Les données brutes (RAW) sont ensuite transmises au moteur de traitement post-hoc.</p>

    <hr>

    <h2 id="partie4">4. Traitement (<code>process_data.py</code>)</h2>
    <h3>Objectif et Justification</h3>
    <p>Filtrer le bruit haute fréquence et extraire les métriques de la Loi de Steering (ISO 9241-9) et de fluidité (LDLJ).</p>
    
    

    <div class="math-box">
        $$ LDLJ = \ln \left( \frac{MT^5}{L^2} \int_{0}^{MT} |jerk(t)|^2 dt \right) $$
        $$ T_e = 4.133 \cdot \sigma_R $$
    </div>

    <h3>Bibliothèques</h3>
    <ul>
        <li><a class="lib-link" href="https://scipy.org/">SciPy</a> : Filtre de Butterworth (filtfilt) pour un lissage sans déphasage.</li>
        <li><a class="lib-link" href="https://pandas.pydata.org/">Pandas</a> : Structuration du dataset final.</li>
    </ul>

    <details>
        <summary>Détail de l'architecture et variables</summary>
        <ul>
            <li><span class="var-name">np.gradient()</span> : Dérivées numériques pour la vitesse et le jerk.</li>
            <li><span class="var-name">Throughput_ISO</span> : Indice de performance effectif.</li>
        </ul>
    </details>

    <p class="transition-phrase">➔ Le dataset de "features" est prêt pour la validation statistique.</p>

    <hr>

    <h2 id="partie5">5. Analyse Inférentielle (<code>analysis_publication.py</code>)</h2>
    <h3>Objectif et Justification</h3>
    <p>Valider les hypothèses de recherche par des tests statistiques rigoureux (Welch t-test) et mesurer la force de la différence par le d de Cohen.</p>

    <div class="math-box">
        $$ d = \frac{\bar{x}_1 - \bar{x}_2}{s_{pooled}} $$
    </div>

    <h3>Bibliothèques</h3>
    <ul>
        <li><a class="lib-link" href="https://scipy.org/">SciPy Stats</a> : Calcul des p-values et intervalles de confiance.</li>
    </ul>

    <details>
        <summary>Détail de l'architecture et variables</summary>
        <ul>
            <li><span class="var-name">p-value</span> : Seuil de significativité (souvent 0.05).</li>
            <li><span class="var-name">Cohen's d</span> : Taille de l'effet biomécanique.</li>
        </ul>
    </details>

    <p class="transition-phrase">➔ La dernière étape consiste à entraîner une IA pour automatiser le diagnostic de l'expertise.</p>

    <hr>

    <h2 id="partie6">6. Machine Learning (<code>analysis_ml.py</code>)</h2>
    <h3>Objectif et Justification</h3>
    <p>Prédire l'appartenance à un groupe (Expert vs Novice). La validation croisée Leave-One-Out est utilisée pour garantir la robustesse sur des échantillons cliniques réduits.</p>

    <div class="math-box">
        $$ \text{Précision} = \frac{VP + VN}{Total} $$
    </div>

    <h3>Bibliothèques</h3>
    <ul>
        <li><a class="lib-link" href="https://scikit-learn.org/">Scikit-Learn</a> : Random Forest Classifier et métriques de validation.</li>
        <li><a class="lib-link" href="https://seaborn.pydata.org/">Seaborn</a> : Visualisation des matrices de confusion.</li>
    </ul>

    <details>
        <summary>Détail de l'architecture et variables</summary>
        <ul>
            <li><span class="var-name">Feature Importance</span> : Poids des variables biomécaniques dans la décision de l'IA.</li>
            <li><span class="var-name">Confusion Matrix</span> : Tableau de contingence des erreurs.</li>
        </ul>
    </details>

</body>
</html>
"""

# --- SAUVEGARDE DU FICHIER ---
output_file = os.path.join(BASE_DIR, "Documentation_Technique_Globale.html")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[SUCCÈS] Documentation complète générée : {output_file}")