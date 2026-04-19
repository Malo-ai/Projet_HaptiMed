# generate_tech_doc.py - FINAL TECHNICAL AND SCIENTIFIC REPORT
import os

# --- PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- HTML CONTENT GENERATION ---
html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>HaptiMed - Scientific Report</title>
    
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
        h2 { color: var(--secondary); margin-top: 40px; border-left: 5px solid var(--secondary); padding-left: 15px; background: var(--box-bg); padding: 12px; }
        h3 { color: var(--primary); margin-top: 30px; }
        
        .report-header { background: #ecf0f1; border-left: 5px solid var(--primary); padding: 20px; border-radius: 5px; margin-bottom: 30px; }
        pre { background: #282c34; color: #abb2bf; padding: 15px; border-radius: 8px; overflow-x: auto; font-family: 'Consolas', monospace; font-size: 0.9em; }
        
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid var(--border); padding: 12px; text-align: left; }
        th { background: var(--box-bg); color: var(--primary); }

        /* Hypotheses Grid */
        .hypotheses-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 25px 0; }
        .hyp-card { padding: 20px; border-radius: 8px; border-top: 5px solid; background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        .hyp-card h4 { margin: 0 0 10px 0; color: var(--primary); }
        .hyp-tag { display: inline-block; margin-top: 10px; font-size: 0.8em; font-weight: bold; text-transform: uppercase; color: var(--secondary); }

        .math-box { background: #fff; border: 1px dashed #bdc3c7; padding: 20px; text-align: center; margin: 25px 0; border-radius: 8px; font-size: 1.25em; }
        .confidence-tag { font-weight: bold; color: var(--accent); }
    </style>
</head>
<body>

    <div class="report-header">
        <h2>Engineering and Ergonomics of Physical Activity</h2>
        <p><strong>Project:</strong> HaptiMed - Quantitative Assessment of Surgical Dexterity</p>
        <p><strong>Author:</strong> Malo Bertrand--Goarin</p>
        <p><strong>GitHub Repository:</strong> <a href="https://github.com/Malo-ai/Projet_HaptiMed" target="_blank">https://github.com/Malo-ai/Projet_HaptiMed</a></p>
    </div>

    <h1>Technical and Scientific Documentation</h1>

    <h2>1. Digital Tools and Python Libraries</h2>
    <table>
        <tr>
            <th>Library</th>
            <th>Scientific & Technical Implementation</th>
        </tr>
        <tr>
            <td><code>PyQt6</code></td>
            <td>Real-time acquisition loop (120Hz). Handles <code>QTabletEvent</code> for high-precision pressure and coordinate tracking during the steering task.</td>
        </tr>
        <tr>
            <td><code>NumPy / Pandas</code></td>
            <td>Vectorized computation of kinematic derivatives (Velocity, Acceleration, Jerk) and management of the features dataset.</td>
        </tr>
        <tr>
            <td><code>SciPy (Signal/Stats)</code></td>
            <td>Implementation of 2nd-order Butterworth filters using <code>filtfilt</code> (zero-phase distortion) and non-parametric statistical testing (Mann-Whitney U).</td>
        </tr>
        <tr>
            <td><code>Scikit-Learn</code></td>
            <td>Machine Learning classification using <code>RandomForestClassifier</code> combined with <code>LeaveOneOut</code> (LOOCV) cross-validation to prevent overfitting on a small cohort.</td>
        </tr>
    </table>

    <h2>2. Scientific Framework and Hypotheses</h2>
    <p>This pipeline investigates three core hypotheses regarding motor control in endonasal surgery, followed by a predictive Machine Learning model.</p>

    <div class="hypotheses-grid">
        <div class="hyp-card" style="border-top-color: #3498db;">
            <h4>H1: Macroscopic Efficiency</h4>
            <p>Experts optimize the Speed-Accuracy tradeoff ($IP_e$) compared to novices on a standard visuo-spatial task.</p>
            <span class="hyp-tag">Script: 05_analysis_H1.py</span>
        </div>
        <div class="hyp-card" style="border-top-color: #9b59b6;">
            <h4>H2: Haptic Asymmetry</h4>
            <p>Adding a constant pressure constraint (FVP task) creates a dual-task interference that disproportionately degrades novices' performance.</p>
            <span class="hyp-tag">Script: 05_analysis_H2.py</span>
        </div>
        <div class="hyp-card" style="border-top-color: #27ae60;">
            <h4>H3: Dynamic Signature (2D & 3D)</h4>
            <p>Expertise manifests as proactive control (feedforward), reducing the spatial-haptic dispersion (Covariance Ellipse) and the 3D Interference Volume.</p>
            <span class="hyp-tag">Scripts: 05_analysis_H3.py / 05_analysis_exploratoire.py</span>
        </div>
        <div class="hyp-card" style="border-top-color: #e67e22;">
            <h4>Machine Learning Classification</h4>
            <p>Random Forest models can accurately classify clinical seniority (Novice vs. Expert) based on kinematic smoothness ($LDLJ$) and force stability.</p>
            <span class="hyp-tag">Script: analysis_ml.py</span>
        </div>
    </div>

    <h2>3. Mathematical Formulations & Implementation</h2>

    <h3>3.1. Data Cleaning (<code>04_process_data.py</code>)</h3>
    <p>Raw kinematic data ($X$, $Y$, and $P_{raw}$) are filtered using a low-pass Butterworth filter applied with <code>filtfilt</code>.</p>
<pre><code>def butter_lowpass_filter(data, cutoff=10.0, fs=120.0, order=2):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)</code></pre>

    <h3>3.2. H1 - Index of Performance (Fitts' Law)</h3>
    <p>We quantify the effective throughput ($IP_e$) by calculating the effective width ($W_e$) based on the standard deviation of the radial error ($\sigma_R$).</p>
    <div class="math-box">
        $$W_e = 4.133 \times \sigma_R \quad ; \quad ID_e = \log_2\left(\frac{2\pi R_e}{W_e}\right) \quad ; \quad IP_e = \frac{ID_e}{MT}$$
    </div>

    <h3>3.3. H2 - Cost of Force (Asymmetry)</h3>
    <p>We compute the performance drop ($\Delta IP_e$) induced by the haptic constraint to evaluate cognitive load.</p>
    <div class="math-box">
        $$\Delta IP_e = IP_{e (VP)} - IP_{e (FVP)}$$
    </div>

    <h3>3.4. H3 - Spatial-Haptic Coupling (2D Ellipse)</h3>
    <p>To measure the interference between force control and spatial precision, we compute the area of a 95% confidence ellipse.</p>
    <div class="math-box">
        $$Area = \pi \times k^2 \times \sqrt{\det(Cov)} \quad \text{with} \quad k^2 = 5.991$$
    </div>

    <h3>3.5. H3 - 3D Master Signature (State-Space Volume)</h3>
    <p>The ultimate surgical signature is defined by the volume of an ellipsoid in a 3D state-space (X Error, Y Error, Force Error). A smaller volume proves active reduction of degrees of freedom.</p>
    <div class="math-box">
        $$Volume = \frac{4}{3} \pi \times \sqrt{(k^2)^3 \times \det(Cov)} \quad \text{with} \quad k^2 = 7.81$$
    </div>
<pre><code>def calculate_ellipsoid_volume(x_err, y_err, z_err):
    data = np.stack((x_err, y_err, z_err), axis=0)
    cov = np.cov(data)
    det_cov = np.linalg.det(cov)
    if det_cov <= 0: return 0.0
    return (4/3) * np.pi * np.sqrt((7.81**3) * det_cov)</code></pre>

    <h2>4. Scientific Risk and Benefit Analysis</h2>
    <table>
        <tr>
            <th>Analysis Type</th>
            <th>Benefit / Scientific Contribution</th>
            <th>Potential Risk</th>
        </tr>
        <tr>
            <td>3D Ellipsoid Volume</td>
            <td>Quantifies total motor uncertainty and proactive control in a single mathematical metric.</td>
            <td>Sensitive to outliers (a single sudden tremor can artificially inflate the covariance matrix).</td>
        </tr>
        <tr>
            <td>Random Forest + LOOCV</td>
            <td>Identifies hidden biomotor patterns to discriminate expertise beyond classical statistics.</td>
            <td>Over-fitting risk remains possible despite LOOCV due to the small clinical cohort size.</td>
        </tr>
        <tr>
            <td>Zero-phase Filtering</td>
            <td>Isolates voluntary movement from sensor noise without shifting the timestamps of the data.</td>
            <td>Setting the cutoff too low (e.g., 5Hz instead of 10Hz) could erase rapid corrective micro-movements.</td>
        </tr>
    </table>

    <h2>5. LLM Usage Disclosure</h2>
    <p>In accordance with the course guidelines, Large Language Models (LLMs) were used to optimize the code modularity, translate technical documentation, and ensure APA compliance in statistical outputs. All logic, mathematical models (determinants, Butterworth, Fitts), and interpretations were heavily supervised and validated by the author.</p>

</body>
</html>
"""

# --- SAVE TO ROOT ---
output_file = os.path.join(BASE_DIR, "Bertrand--Goarin.Malo.html")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[SUCCESS] Scientific documentation generated: {output_file}")