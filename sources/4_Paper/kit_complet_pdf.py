from fpdf import FPDF
import os

# --- CONFIGURATION DES CHEMINS DYNAMIQUES ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_FILE = os.path.join(SCRIPT_DIR, "image_d9e00a.png") 

OUTPUT_DIR = r"C:\Projet_HaptiMed\Paper_intervention" 

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

class HaptiMedPDF(FPDF):
    def header(self):
        # Affiche l'en-tête UNIQUEMENT sur la page 1
        if self.page_no() == 1:
            if os.path.exists(LOGO_FILE):
                self.image(LOGO_FILE, 10, 8, 40)
            
            self.set_y(15)
            self.set_font('Arial', 'B', 10)
            self.set_text_color(0, 0, 0)
            self.cell(45) 
            self.cell(0, 10, 'Laboratoire EuroMov Digital Health in Motion - Univ. Montpellier', 0, 0, 'L')
            
            # On descend à 40mm pour laisser la place au logo sur la page 1
            self.set_y(40)
        else:
            # Pour la page 2 et les suivantes, on commence plus haut (pas de logo)
            self.set_y(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150) 
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def clean_text(txt):
    """Nettoie le texte pour éviter les erreurs d'encodage avec FPDF (Latin-1)"""
    txt = txt.replace("’", "'").replace("…", "...").replace("•", "-")
    txt = txt.replace("«", '"').replace("»", '"').replace("œ", "oe")
    return txt.encode('latin-1', 'replace').decode('latin-1')

def create_fiche_info():
    pdf = HaptiMedPDF()
    # Marge par défaut pour toutes les pages (le header modifiera la page 1)
    pdf.set_margins(left=10, top=20, right=10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, clean_text("FICHE D'INFORMATION PARTICIPANT"), 0, 1, 'C')
    pdf.ln(5)

    sections = [
        ("Titre du projet", "Caractérisation de l'expertise gestuelle clinique : Étude de la régulation de force et de l'adaptation motrice face à l'incertitude tissulaire simulée."),
        ("Responsable scientifique", "Sutton-Charani Nicolas"),
        ("Objectifs du projet", "L'objectif principal de cette étude est de quantifier le \"Coût de la Vitesse\" sur la stabilité de la force et du mouvement dans un contexte de chirurgie endonasale."),
        ("Déroulement et Méthodologie", "L'expérience consiste à suivre un couloir circulaire sur une tablette avec un stylet. Vous réaliserez 4 conditions d'environ 5 minutes chacune, présentées aléatoirement :\n"
                                        "- Vitesse-Précision (VP) avec et sans feedback visuel.\n"
                                        "- Force-Vitesse-Précision (FVP) avec et sans feedback visuel.\n"
                                        "Dans les conditions impliquant la Force (FVP), vous devrez maintenir une pression constante (mémorisée au départ) tout au long du tracé.\n"
                                        "Il n'y a aucune priorité entre la force, la vitesse et la précision : vous devez tenter d'optimiser ces trois composantes de manière équivalente. Lors des conditions avec feedback pour la force, l'épaisseur du trait variera en temps réel pour refléter la pression que vous appliquez."),
        ("Ce que l'on attend de vous", "Les positions de la pointe du stylet seront enregistrées (système de capture de mouvement), ainsi que les vitesses, accélérations, jerk et données de force.\n"
                                       "Vous serez invité(e) à réaliser la tâche en respectant scrupuleusement les 3 consignes (Force, Vitesse, Précision) de façon simultanée."),
        ("Bénéfices et Risques", "Vous ne tirerez aucun bénéfice personnel direct, si ce n'est votre contribution à l'avancée des connaissances scientifiques. Cette recherche ne présente pas de risques plus grands que ceux encourus lorsque vous écrivez quotidiennement."),
        ("Droits, Confidentialité et Retrait", "Votre participation est volontaire. Vous pouvez la refuser ou l'arrêter à tout moment sans vous justifier, et demander la destruction de vos données. Toutes les données récoltées (excepté le consentement) sont identifiées par un numéro de code pour être anonymes."),
        ("Archivage et Stockage des données", "Type de données : Les formulaires de consentement papier et les données expérimentales (.csv).\n"
                                              "Lieu : Les données seront stockées en France, à Montpellier (34000). Les formulaires papier seront dans un local fermé à clef au laboratoire EuroMov DHM. Les données numériques sur un serveur sécurisé.\n"
                                              "Durée : L'ensemble des données (papier et .csv) sera archivé pendant 10 ans.\n"
                                              "Responsable : Le porteur du projet est responsable de l'archivage et de la sécurité des données.")
    ]

    for title, text in sections:
        # L'espace forcé a été retiré ici pour garder une mise en page fluide
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(41, 128, 185) 
        pdf.cell(0, 8, clean_text(title), 0, 1)
        
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 5, clean_text(text))
        pdf.ln(3)

    pdf.output(os.path.join(OUTPUT_DIR, "01_Fiche_Information.pdf"))

def create_consentement():
    pdf = HaptiMedPDF()
    pdf.set_margins(left=10, top=20, right=10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 10, clean_text("FORMULAIRE DE CONSENTEMENT"), 0, 1, 'C')
    pdf.ln(5)

    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, clean_text("Titre : Caractérisation de l'expertise gestuelle clinique : Étude de la régulation de force et de l'adaptation motrice face à l'incertitude tissulaire simulée."))
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, clean_text("Je soussigné(e) : __________________________________________"), 0, 1)
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 10)
    items = [
        "J'atteste être affilié(e) ou bénéficiaire d'un régime d'assurance maladie.",
        "Le chercheur responsable m'a informé(e) de la nature et des buts de cette recherche, ainsi que de son déroulement et des risques éventuels.",
        "J'ai en ma possession la note d'information que j'ai lue et comprise. J'ai pu poser toutes les questions voulues et j'ai obtenu des réponses satisfaisantes.",
        "Je comprends que ma participation est volontaire. Je suis LIBRE À TOUT MOMENT D'ARRÊTER sans avoir à me justifier (par écrit à l'adresse du laboratoire).",
        "J'ai bien noté qu'aucune information personnelle nominative ne sera traitée de manière informatisée en lien avec mes résultats.",
        "Je m'engage à observer les contraintes spécifiées pour la bonne fin du protocole et j'atteste avoir répondu de façon sincère aux questions sur mon profil.",
        "J'autorise la consultation de mes données (strictement confidentielles) par l'équipe de recherche. Je suis informé(e) que ces données, une fois anonymes, pourront être rendues publiques dans une logique de science ouverte."
    ]
    
    for item in items:
        pdf.cell(8, 6, "[  ]", 0, 0)
        pdf.multi_cell(0, 6, clean_text(item))
        pdf.ln(2)
        
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, clean_text("J'accepte de manière libre et éclairée de participer à ce projet de recherche."), 0, 1)
    
    pdf.ln(10)
    pdf.set_font('Arial', '', 10)
    pdf.cell(100, 10, clean_text("Date, Nom, Prénom, Signature du participant :"), 0, 0)
    pdf.cell(0, 10, clean_text("Date, Signature du chercheur responsable :"), 0, 1)

    pdf.output(os.path.join(OUTPUT_DIR, "02_Consentement_Eclaire.pdf"))

def create_guide_utilisateur():
    pdf = HaptiMedPDF()
    pdf.set_margins(left=10, top=20, right=10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.ln(10) # Fait descendre le titre du guide utilisateur
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, clean_text("GUIDE UTILISATEUR - PROTOCOLE EXPÉRIMENTAL"), 0, 1, 'C')
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(41, 128, 185) 
    pdf.cell(0, 8, clean_text("PHASE 1 : Accueil et Administratif"), 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, clean_text("1. Information : Remettre la Fiche d'information au participant.\n"
                                    "2. Consentement : Faire signer le Formulaire de Consentement papier.\n"
                                    "3. Archivage : Ranger immédiatement le consentement dans le meuble sous clef."))
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 8, clean_text("PHASE 2 : Passation Expérimentale"), 0, 1)
    pdf.set_text_color(0, 0, 0)

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 6, clean_text("Étape 2.1 : Préparation de l'environnement et posture"), 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, clean_text("- Lumière : S'assurer que l'éclairage de la salle est strictement identique à chaque passation.\n"
                                    "- Posture : Le participant doit se tenir debout, face à l'écran.\n"
                                    "- Tablette : Positionner la tablette de manière à ce que le participant soit à l'aise, avec un angle d'ouverture des coudes supérieur à 90°.\n"
                                    "- Consignes : Avant le début, informez le participant qu'il devra lire et suivre attentivement les consignes qui s'afficheront à l'écran à chaque changement de condition. Rappelez-lui qu'il n'y a pas de priorité entre Force, Vitesse et Précision."))
    pdf.ln(3)
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 6, clean_text("Étape 2.2 : Calibration de la Force (MVC)"), 0, 1)
    pdf.set_font('Courier', '', 10)
    pdf.set_fill_color(240, 240, 240) 
    pdf.cell(0, 6, "python Passation_Test\\calibration_mvc.py", 0, 1, fill=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, clean_text("Action : Le sujet appuie avec le stylet. Appuyez sur ESPACE pour sauver la MVC."))
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 6, clean_text("Étape 2.3 : Tâche de Navigation (Steering Task)"), 0, 1)
    pdf.set_font('Courier', '', 10)
    pdf.cell(0, 6, "python Passation_Test\\steering_task.py", 0, 1, fill=True)
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 5, clean_text("Action 1 : Remplir l'ID et les paramètres de la tâche.\n"
                                    "Action 2 : Remplir le questionnaire dynamique (Âge, Sommeil, Statut médical...).\n"
                                    "Action 3 : Le sujet réalise les 4 blocs expérimentaux en suivant les instructions à l'écran."))
    pdf.ln(3)

    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 8, clean_text("PHASE 3 : Traitement et Analyse"), 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 11)
    
    pdf.set_font('Courier', '', 10)
    pdf.cell(0, 6, "python Clean_Data\\process_data.py          # 1. Filtre & Nettoyage", 0, 1, fill=True)
    pdf.cell(0, 6, "python Process_Stat\\analysis_master.py     # 2. Stats & Graphes", 0, 1, fill=True)
    pdf.cell(0, 6, "python Process_Stat\\analysis_ml.py         # 3. Machine Learning", 0, 1, fill=True)
    pdf.cell(0, 6, "python Paper\\generate_master_report.py     # 4. Rapport Final", 0, 1, fill=True)
    pdf.ln(3)

    pdf.output(os.path.join(OUTPUT_DIR, "03_Guide_Utilisateur.pdf"))

if __name__ == "__main__":
    print(f"Génération des fichiers PDF dans '{OUTPUT_DIR}'...")
    create_fiche_info()
    create_consentement()
    create_guide_utilisateur() 
    print("Succès ! Les 3 fiches PDF ont été générées et adaptées.")