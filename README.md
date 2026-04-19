# 🎯 HaptiMed: Evaluation of Surgical Expertise

This research project aims to discriminate the level of clinical expertise (Novices vs. Experts) in endonasal surgery through the analysis of kinematic and haptic biomarkers. It relies on an instrumented steering task (Accot and Zhai's Steering Task) modified to include axial force constraints.

> **⚠️ Note on Dataset Size (Moodle 100MB Limit)**
> To comply with the Moodle upload restriction, the `data/` folder included in this repository contains a representative "Toy Dataset" (3 subjects) allowing the complete execution of the `main.py` pipeline. 
> The full clinical dataset containing all 1700+ trials (~300MB), which was used to generate the final statistics and the HTML report, is available for download here: **[INSÈRE TON LIEN DRIVE ICI]**

**Author:** Malo Bertrand--Goarin  
**Program:** Master 2 in Training Engineering and Performance Optimization (DigiMov Track)  
**Laboratory:** EuroMov Digital Health in Motion (Univ. Montpellier / CHU Guy de Chauliac)  
**GitHub Link:** https://github.com/Malo-ai/Projet_HaptiMed
**Data & Env:** https://drive.google.com/drive/folders/1EQ3Lkahn02ljXNYQ1N83-YI-BxInymgd?usp=drive_link

---

## 📂 Project Structure (Safe Logic)

The repository architecture guarantees process isolation (acquisition vs. processing) and total reproducibility of the analyses:

* **`main.py`**: Main orchestrator. A single entry point that executes the entire analysis and report generation pipeline.
* **`environment.yml`**: File to replicate the exact Conda environment (PyQt6, Scipy, Scikit-Learn, FPDF, etc.).
* **`data/`**: Contains raw tablet data (`raw/`), filtered data (`clean/`), and descriptor matrices (`features/`).
* **`doc/` & `Paper_intervention/`**: Auto-generated HTML reports and administrative PDF forms (consent, information sheets).
* **`results/`**: Centralized storage for all generated charts (H1, H2, H3) and inferential statistics tables (APA standards).
* **`sources/`**: The core source code, divided into logical clusters:
    * `/1_Passation_Test`: Graphical Interface (PyQt6) for 120 Hz acquisition and MVC calibration.
    * `/2_Clean_Data`: Butterworth filtering and kinematic metrics extraction (Jerk, IPe).
    * `/3_Process_Stat`: Hypothesis validation (Mann-Whitney) and Machine Learning models.
    * `/4_Paper`: Scripts to generate technical documentation and PDFs.

---

## 🧬 Scientific Hypotheses Evaluated

1.  **H1 - Macroscopic Efficiency:** Validation of the effective Performance Index (IPe) as a baseline discriminator between naive subjects and medical personnel.
2.  **H2 - The Cost of Force (Asymmetry):** Adding a haptic constraint (FVP dual task) disproportionately degrades the accuracy of novices compared to experts.
3.  **H3 - The Dynamic Signature (3D Coupling):** Experts possess a proactive internal model (*feedforward*) resulting in a highly compact and repeatable 3D interference volume (Space x Force).

---

## 🚀 Installation and Execution

This pipeline is designed to be portable and fully automated (Windows, Mac, Linux).

### 1. Environment Preparation
```bash
conda env create -f environment.yml
conda activate env_haptimed