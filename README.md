🎯 HaptiMed : Évaluation de l'Expertise Chirurgicale
Ce projet de recherche vise à discriminer le niveau d'expertise (Novices vs Experts) en comparant l'ancienneté clinique aux performances biomécaniques quantitatives. Nous utilisons une tâche de pilotage circulaire (Steering Task) modélisée selon la loi d'Accot et Zhai (dérivée de la loi de Fitts), en y intégrant des contraintes haptiques.

Auteur : Malo Bertrand--Goarin

Cours : Engineering and Ergonomics of Physical Activity

Lien GitHub : [Lien vers ton repository public]

📂 Structure du Projet (Safe Logic)
Le dépôt est organisé selon la structure imposée pour garantir la portabilité et la clarté de l'analyse :

Bertrand--Goarin.Malo.html : Rapport de projet auto-suffisant présentant la question scientifique, les méthodes et les résultats.

main.py : Point d'entrée unique permettant d'exécuter l'intégralité du pipeline d'analyse.

environment.yml : Fichier de configuration pour recréer l'environnement Conda et installer les dépendances (Scipy, Scikit-Learn, FPDF, etc.).

readme.md : Ce fichier de documentation.

LICENCE : Licence de distribution du code.

📁 sources/ : Répertoire contenant les scripts et fonctions modulaires.

🧪 Passation_Test/ : Acquisition sub-pixel à 120 Hz et calibration MVC.

🧹 Clean_Data/ : Filtrage de Butterworth d'ordre 2 et calcul des métriques ISO 9241-9.

📊 Process_Stat/ : Analyse statistique inférentielle et classification par Random Forest.

📄 Paper/ : Scripts de génération des rapports et kits administratifs.

📁 data/ : Données brutes (raw/) et traitées (clean/).

📁 results/ : Sorties graphiques, tableaux APA et documentation technique.

📁 notebooks/ : Analyses exploratoires complémentaires.

🚀 Installation et Exécution
Le projet est conçu pour fonctionner sur n'importe quel système (Win, Mac, Unix).

Recréer l'environnement :

Bash
conda env create -f environment.yml
conda activate env_haptimed
Lancer le pipeline complet :
Exécutez la commande suivante à la racine pour traiter les données, générer les statistiques et produire le rapport final :

Bash
python main.py

🧪 Maîtrise Scientifique et TechniqueCe projet démontre l'acquisition des compétences suivantes :Traitement du signal : Échantillonnage à 120 Hz pour respecter le critère de Nyquist-Shannon vis-à-vis du tremblement physiologique et filtrage passe-bas de Butterworth à 10 Hz pour éliminer le bruit électronique.Analyse Statistique : Modélisation par régression linéaire de la Loi de Fitts ($MT = a + b \cdot ID_e$), tests de Welch pour les comparaisons de groupes et calcul de la taille d'effet (Cohen's d).Machine Learning : Utilisation de l'algorithme Random Forest avec validation croisée (LOO) pour quantifier la valeur ajoutée de la force haptique dans la discrimination de l'expertise.

🗺️ Détail des pôles (sources/)1. 🧪 Passation_Test/Gère l'interaction temps-réel avec la tablette graphique via PyQt6. Il enregistre les coordonnées et la pression axiale, cruciale pour l'hypothèse H2 sur la charge haptique.2. 🧹 Clean_Data/Transforme les séries temporelles brutes en variables descriptives. Il calcule notamment le Throughput ($IP_e$) et la fluidité gestuelle via le Log Dimensionless Jerk ($LDLJ$).3. 📊 Process_Stat/Répond aux questions de recherche en produisant des tableaux de résultats conformes aux normes APA et des visualisations (boxplots, scatter plots) pour l'interprétation scientifique.4. 📄 Paper/Automatise la production de la documentation. Le script generate_master_report.py compile les résultats dans le rapport HTML final déposé sur Moodle.Note : Ce projet a été réalisé avec l'assistance de l'IA (Gemini 3 Flash) pour l'optimisation de la structure modulaire et la génération automatisée des rapports.