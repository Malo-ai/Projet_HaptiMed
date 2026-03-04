from fpdf import FPDF
import os

LOGO_FILE = "image_d9e00a.png" 
# Chemin direct et précis vers ton dossier
OUTPUT_DIR = r"C:\Projet_HaptiMed\Paper_intervention" 

class HaptiMedPDF(FPDF):
    def header(self):
        # Insertion du logo
        if os.path.exists(LOGO_FILE):
            self.image(LOGO_FILE, 10, 8, 40)
        
        # En-tête du labo
        self.set_font('Arial', 'B', 10)
        self.cell(45) 
        self.cell(0, 10, 'Laboratoire EuroMov Digital Health in Motion - Univ. Montpellier', 0, 1, 'L')
        
        # On force le curseur Y à 55 (bien en dessous du logo)
        self.set_y(55)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def clean_text(txt):
    # Garde les accents français mais retire les symboles spéciaux qui font planter FPDF
    txt = txt.replace("’", "'").replace("…", "...").replace("•", "-")
    return txt.encode('latin-1', 'replace').decode('latin-1')

def create_fiche_info():
    pdf = HaptiMedPDF()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, clean_text("1. FICHE D'INFORMATION PARTICIPANT"), 0, 1, 'L')
    pdf.ln(3)

    sections = [
        ("Titre de l'étude", "Évaluation de la performance sur une tâche de guidage simulée (steering task)."),
        ("Contexte", "Cette étude est menée dans le cadre d'un stage de recherche au laboratoire EuroMov Digital Health in Motion (Université de Montpellier), sous la supervision de Nicolas Sutton-Charani."),
        ("Objectif", "Mesurer la précision, la vitesse et la force de chirurgiens et chirurgiens en apprentissage lors d'une tâche de guidage nécessitant un contrôle moteur fin."),
        ("Critères de participation", "- Inclusion : Être chirurgien ou chirurgien en apprentissage (interne, chef de clinique, etc.), être en bonne santé générale.\n- Exclusion : Présenter des troubles moteurs, neurologiques ou musculo-squelettiques affectant les membres supérieurs ; présenter des troubles non corrigés de la vision."),
        ("Déroulement", "- Durée totale : environ 20 minutes.\n- Une phase d'entraînement suivie de 10 essais.\n- Mesure du temps, des erreurs, de la force et de la trajectoire.\n- Questionnaire de ressenti à la fin."),
        ("Données collectées", "- Données de performance (temps, erreurs, trajectoire, force).\n- Données démographiques minimales (statut, tranche d'expérience professionnelle).\n- Aucune donnée nominative directement liée aux résultats."),
        ("Confidentialité et anonymisation", "Les données seront codées (ex. : P01, P02...). La correspondance code/identité sera stockée séparément sur un serveur sécurisé d'EuroMov DHM. Les données ne seront utilisées qu'à des fins de recherche scientifique."),
        ("Droits des participants", "- Participation volontaire.\n- Possibilité de se retirer à tout moment sans justification.\n- Droit d'accès, de rectification et de suppression des données (RGPD)."),
        ("Contact", "Chercheur responsable : Nicolas Sutton-Charani - [Email]\nÉtudiant stagiaire : [Ton Nom] - [Email]")
    ]

    for title, text in sections:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, clean_text(title), 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, clean_text(text))
        pdf.ln(2)

    # Sauvegarde dans le dossier spécifié
    pdf.output(os.path.join(OUTPUT_DIR, "01_Fiche_Information.pdf"))

def create_consentement():
    pdf = HaptiMedPDF()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, clean_text("2. FORMULAIRE DE CONSENTEMENT ÉCLAIRÉ"), 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, clean_text("Titre : Évaluation de la performance sur une steering task."), 0, 1)
    pdf.ln(5)
    pdf.cell(0, 10, clean_text("Je soussigné(e) : __________________________________________"), 0, 1)
    pdf.ln(10)
    
    items = [
        "Déclare avoir lu et compris la fiche d'information.",
        "Confirme ne présenter aucun des critères d'exclusion mentionnés.",
        "Accepte volontairement de participer à cette étude.",
        "Autorise l'utilisation de mes données anonymisées à des fins de recherche.",
        "Sais que je peux me retirer à tout moment sans conséquence."
    ]
    
    for item in items:
        pdf.cell(10, 10, "[  ]", 0, 0)
        pdf.cell(0, 10, clean_text(item), 0, 1)

    pdf.ln(25)
    pdf.cell(90, 10, clean_text("Signature du participant :"), 0, 0)
    pdf.cell(0, 10, "Date : ____ / ____ / 2026", 0, 1)
    pdf.ln(20)
    pdf.cell(90, 10, clean_text("Signature du chercheur :"), 0, 0)
    pdf.cell(0, 10, clean_text("Fait à Montpellier"), 0, 1)

    # Sauvegarde dans le dossier spécifié
    pdf.output(os.path.join(OUTPUT_DIR, "02_Consentement_Eclaire.pdf"))

def create_tableau_suivi():
    pdf = HaptiMedPDF()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, clean_text("3. TABLEAU DE SUIVI DES DONNÉES ANONYMISÉES"), 0, 1, 'C')
    pdf.ln(5)

    pdf.set_font('Arial', 'B', 9)
    cols = ["Code", "Statut / Exp", "Bloc 1", "Bloc 2", "Bloc 3", "Bloc 4", "Commentaires"]
    widths = [15, 25, 18, 18, 18, 18, 75]
    
    for i in range(len(cols)):
        pdf.cell(widths[i], 10, clean_text(cols[i]), 1, 0, 'C')
    pdf.ln()

    pdf.set_font('Arial', '', 10)
    for _ in range(15):
        for w in widths:
            pdf.cell(w, 10, "", 1, 0)
        pdf.ln()

    # Sauvegarde dans le dossier spécifié
    pdf.output(os.path.join(OUTPUT_DIR, "03_Tableau_Suivi.pdf"))

if __name__ == "__main__":
    print(f"Génération des fichiers PDF en cours dans le dossier '{OUTPUT_DIR}'...")
    create_fiche_info()
    create_consentement()
    create_tableau_suivi()
    print("Succès ! Les 3 fiches PDF ont été générées et rangées.")