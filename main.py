# main.py - GLOBAL ORCHESTRATOR FOR THE HAPTIMED PROJECT
import os
import subprocess
import sys

def run_script(script_path):
    """Runs a Python script and checks if it executed successfully."""
    print("\n" + "="*60)
    print(f"🚀 EXECUTING: {script_path}")
    print("="*60)
    
    try:
        # subprocess guarantees memory isolation between each script
        subprocess.run([sys.executable, script_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Fatal ERROR in {script_path}")
        print(f"Error code: {e.returncode}")
        return False

if __name__ == "__main__":
    print("🌟 STARTING THE COMPLETE HAPTIMED PIPELINE (Master 2)")
    
    # Strict definition of the analytical pipeline
    # (Passation scripts are not run here as they require a human subject)
    pipeline = [
        # 1. Signal processing and biomarker extraction
        "sources/2_Clean_Data/04_process_data.py",
        
        # 2. Statistical and Inferential Analyses (H1, H2, H3)
        "sources/3_Process_Stat/05_analysis_H1.py",
        "sources/3_Process_Stat/05_analysis_H2.py",
        "sources/3_Process_Stat/05_analysis_H3.py",
        "sources/3_Process_Stat/05_analysis_exploratoire.py",
        
        # Note: If you have an analysis_ml.py file, add it here with the correct path
        # e.g., "sources/3_Process_Stat/analysis_ml.py",
        
        # 3. Documentation and PDF generation
        "sources/4_Paper/generate_tech_doc.py",
        "sources/4_Paper/kit_complet_pdf.py"
    ]
    
    success_count = 0
    for script in pipeline:
        # Path normalization according to the OS (Windows/Mac)
        script_path = os.path.normpath(script)
        
        if not os.path.exists(script_path):
            print(f"⚠️ FILE NOT FOUND: {script_path}")
            print("Check the folder structure in the 'sources/' directory")
            break
            
        if run_script(script_path):
            success_count += 1
        else:
            print("\n⛔ Pipeline stopped due to a technical error.")
            break

    if success_count == len(pipeline):
        print("\n" + "!"*60)
        print("✅ PIPELINE SUCCESSFULLY COMPLETED!")
        print("All charts, statistics, and reports have been generated.")
        print("Check the 'results/', 'doc/', and 'Paper_intervention/' folders.")
        print("!"*60)