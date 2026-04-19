import sys, os, csv, math
import numpy as np
import pandas as pd
from scipy import stats, signal
import seaborn as sns

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QLabel, QComboBox, QAbstractItemView, 
                             QFrame, QPushButton, QFileDialog, QMessageBox, 
                             QScrollArea, QSlider, QGroupBox, QTabWidget, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QTextEdit)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D

# ==============================================================
# 1. MOTEUR SCIENTIFIQUE (SÉCURISÉ & ENRICHI)
# ==============================================================
def get_scientific_metrics(df_trial):
    """Calcule les signatures haptico-spatiales 2D et 3D, incluant le Jerk."""
    if df_trial.empty: return None
    
    t = pd.to_numeric(df_trial['Time_Rel']).values
    if len(t) < 15: return None # Protection contre les essais fantômes
    
    f = pd.to_numeric(df_trial.get('P_Raw', 0)).values
    err_rad = pd.to_numeric(df_trial.get('Err_Radiale', 0)).values
    angles = pd.to_numeric(df_trial.get('Angle', 0)).values
    
    # Coordonnées
    z_err = f - 3200.0
    x_err = err_rad * np.cos(angles)
    y_err = err_rad * np.sin(angles)
    
    # Calcul de la dérivée de la force (Instabilité / Jerk)
    dt = np.mean(np.diff(t)) if len(t) > 1 else 0.01
    jerk_f = np.sqrt(np.mean(np.gradient(np.gradient(f, dt), dt)**2))
    
    # Matrices et Volumes
    pts_3d = np.stack((x_err, y_err, z_err), axis=0)
    cov_3d = np.cov(pts_3d)
    
    pts_2d = np.stack((z_err, err_rad), axis=0)
    cov_2d = np.cov(pts_2d)
    
    # Sécurité Mathématique (IsNan / IsInf)
    if np.isnan(cov_3d).any() or np.isinf(cov_3d).any():
        vol_3d, area_2d = 0, 0
    else:
        det_3d = np.linalg.det(cov_3d)
        vol_3d = (4/3) * np.pi * np.sqrt((7.81**3) * det_3d) if det_3d > 0 else 0
        
        det_2d = np.linalg.det(cov_2d)
        area_2d = np.pi * 5.991 * np.sqrt(det_2d) if det_2d > 0 else 0
    
    return {
        "x": x_err, "y": y_err, "z": z_err,
        "vol": vol_3d, "area": area_2d, "jerk": jerk_f,
        "dur": t.max() - t.min(),
        "t_norm": np.linspace(0, 1, len(t))
    }

# ==============================================================
# 2. ONGLET : VISUALISEUR CINÉMATIQUE (MODIFIÉ POUR CLEAN)
# ==============================================================
class TrajectoryCanvas(QWidget):
    def __init__(self, side_label):
        super().__init__()
        self.label = side_label
        self.trials = [] 
        self.R, self.W = 350, 5
        self.target_f, self.tol = 3200, 20
        self.zoom_factor = 1.0
        self.setMinimumWidth(400)
        self.setStyleSheet("background-color: white; border: 1px solid #dfe6e9; border-radius: 5px;")

    def set_data(self, trials, r, w):
        self.trials = trials
        self.R, self.W = r, w
        self.update()

    def update_zoom(self, factor):
        self.zoom_factor = factor
        self.setMinimumHeight(int(700 * factor))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        
        h_traj = int(h * 0.50)
        h_graph = h - h_traj
        cx, cy = w / 2, h_traj / 2

        margin = 30
        disp_R = (min(w/2, h_traj/2) - margin)
        scale = disp_R / self.R if self.R > 0 else 1.0
        
        p.setPen(QPen(QColor("#f1f2f6"), max(1, self.W * scale)))
        p.drawEllipse(QPointF(cx, cy), disp_R, disp_R)

        f_min = self.target_f * (1 - self.tol/100)
        f_max = self.target_f * (1 + self.tol/100)

        if self.trials:
            all_pts = [pt for t in self.trials for pt in t["points"]]
            dx = (min(pt[0] for pt in all_pts) + max(pt[0] for pt in all_pts)) / 2 if all_pts else 960
            dy = (min(pt[1] for pt in all_pts) + max(pt[1] for pt in all_pts)) / 2 if all_pts else 540

            for trial in self.trials:
                pts = trial["points"]
                t_id = int(trial["name"])
                c_green = QColor.fromHsv(120, 220, int(80 + ((t_id-1)%10) * 17.5))
                c_red = QColor.fromHsv(0, 220, int(80 + ((t_id-1)%10) * 17.5))

                for j in range(1, len(pts)):
                    p1, p2 = pts[j-1], pts[j]
                    dist = math.hypot(p2[0] - dx, p2[1] - dy)
                    is_in_tunnel = abs(dist - self.R) <= (self.W / 2)
                    p.setPen(QPen(c_green if is_in_tunnel else c_red, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                    p.drawLine(QPointF(cx + (p1[0]-dx)*scale, cy + (p1[1]-dy)*scale), 
                               QPointF(cx + (p2[0]-dx)*scale, cy + (p2[1]-dy)*scale))

        gx0, gy0, gw, gh = 60, h - 50, w - 80, h_graph - 80
        p.setBrush(QColor("#ffffff")); p.setPen(QPen(QColor("#b2bec3"), 1))
        p.drawRect(int(gx0), int(gy0-gh), int(gw), int(gh))
        y_min_t, y_max_t = gy0 - (f_max/8192)*gh, gy0 - (f_min/8192)*gh
        p.fillRect(int(gx0+1), int(y_min_t), int(gw-1), int(y_max_t - y_min_t), QColor(46, 204, 113, 20))
        
        if self.trials:
            for trial in self.trials:
                pts = trial["points"]
                if not pts: continue
                t_total = pts[-1][2] if pts[-1][2] > 0 else 1.0
                t_id = int(trial["name"])
                c_green = QColor.fromHsv(120, 220, int(80 + ((t_id-1)%10) * 17.5))
                c_red = QColor.fromHsv(0, 220, int(80 + ((t_id-1)%10) * 17.5))

                for k in range(1, len(pts)):
                    p1, p2 = pts[k-1], pts[k]
                    p.setPen(QPen(c_green if f_min <= p2[3] <= f_max else c_red, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                    p.drawLine(QPointF(gx0 + (p1[2]/t_total)*gw, gy0 - (p1[3]/8192)*gh), 
                               QPointF(gx0 + (p2[2]/t_total)*gw, gy0 - (p2[3]/8192)*gh))

class ControlSidebar(QFrame):
    def __init__(self, parent_viewer):
        super().__init__()
        self.parent_viewer = parent_viewer
        self.setFixedWidth(280)
        self.setStyleSheet("background-color: #f8f9fa; border-right: 1px solid #dfe6e9;")
        layout = QVBoxLayout(self)

        self.btn_path = QPushButton("📁 Dossier Données (Clean)")
        self.btn_path.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 5px;")
        self.btn_path.clicked.connect(self.parent_viewer.select_folder)
        layout.addWidget(self.btn_path)

        self.group_a = self.create_subject_group("Sujet 1", "a")
        self.group_b = self.create_subject_group("Sujet 2", "b")
        layout.addWidget(self.group_a); layout.addWidget(self.group_b); layout.addStretch()

    def create_subject_group(self, title, suffix):
        group = QGroupBox(title)
        layout = QVBoxLayout()
        cb_p = QComboBox(); cb_p.addItem("Choisir...")
        setattr(self, f"cb_p_{suffix}", cb_p)
        cb_c = QComboBox(); setattr(self, f"cb_c_{suffix}", cb_c)
        list_t = QListWidget(); list_t.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        list_t.setMaximumHeight(80); setattr(self, f"list_t_{suffix}", list_t)
        
        btn_all = QPushButton("Tout sélectionner")
        btn_all.clicked.connect(list_t.selectAll)
        lbl_stats = QLabel("Sélectionnez des essais...")
        lbl_stats.setStyleSheet("font-family: Consolas; font-size: 11px; background: #2c3e50; color: #ecf0f1; padding: 8px;")
        setattr(self, f"lbl_stats_{suffix}", lbl_stats)

        layout.addWidget(cb_p); layout.addWidget(cb_c); layout.addWidget(list_t); layout.addWidget(btn_all); layout.addWidget(lbl_stats)
        group.setLayout(layout)
        
        cb_p.currentIndexChanged.connect(lambda: self.parent_viewer.load_subject(suffix))
        cb_c.currentIndexChanged.connect(lambda: self.parent_viewer.populate_trials(suffix))
        list_t.itemSelectionChanged.connect(lambda: self.parent_viewer.refresh_canvas(suffix))
        return group

class VisualizerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.data_path = ""
        self.subjects_data = {"a": [], "b": []}
        main_layout = QHBoxLayout(self); main_layout.setContentsMargins(0,0,0,0)
        self.sidebar = ControlSidebar(self)
        main_layout.addWidget(self.sidebar)

        right_layout = QVBoxLayout()
        zoom_bar = QHBoxLayout(); zoom_bar.addWidget(QLabel("<b>ZOOM :</b>"))
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setRange(100, 200); self.slider_zoom.setValue(100)
        self.slider_zoom.valueChanged.connect(self.apply_global_zoom)
        zoom_bar.addWidget(self.slider_zoom); zoom_bar.addStretch()
        right_layout.addLayout(zoom_bar)

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        container = QWidget(); self.canvas_layout = QHBoxLayout(container)
        self.canvas_a = TrajectoryCanvas("Sujet 1"); self.canvas_b = TrajectoryCanvas("Sujet 2")
        self.canvas_layout.addWidget(self.canvas_a); self.canvas_layout.addWidget(self.canvas_b)
        self.scroll.setWidget(container)
        right_layout.addWidget(self.scroll)
        main_layout.addLayout(right_layout, stretch=1)

    def apply_global_zoom(self, val):
        factor = val / 100.0
        self.canvas_a.update_zoom(factor); self.canvas_b.update_zoom(factor)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Ouvrir dossier (Clean/Raw)")
        if path: 
            self.data_path = path
            self.refresh_pids()

    def refresh_pids(self):
        if not os.path.exists(self.data_path): return
        files = [f for f in os.listdir(self.data_path) if f.endswith('_CLEAN.csv') or f.endswith('_RAW.csv')]
        pids = sorted(list(set([f.split('_')[0] for f in files])))
        for s in ["a", "b"]:
            cb = getattr(self.sidebar, f"cb_p_{s}")
            cb.blockSignals(True); cb.clear(); cb.addItem("Choisir..."); cb.addItems(pids); cb.blockSignals(False)

    def load_subject(self, s):
        cb = getattr(self.sidebar, f"cb_p_{s}")
        pid = cb.currentText()
        if pid == "Choisir...": return
        
        # Priorité au fichier CLEAN
        file_path = os.path.join(self.data_path, f"{pid}_CLEAN.csv")
        if not os.path.exists(file_path): file_path = os.path.join(self.data_path, f"{pid}_RAW.csv")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                self.subjects_data[s] = list(csv.DictReader(f))
            blocs = sorted(list(set([row["Bloc"] for row in self.subjects_data[s]])))
            cb_c = getattr(self.sidebar, f"cb_c_{s}")
            cb_c.blockSignals(True); cb_c.clear(); cb_c.addItems(blocs); cb_c.blockSignals(False)
            self.populate_trials(s)

    def populate_trials(self, s):
        lst = getattr(self.sidebar, f"list_t_{s}"); lst.clear()
        bloc = getattr(self.sidebar, f"cb_c_{s}").currentText()
        if not bloc: return
        trials = sorted(list(set([int(row["Trial_in_Bloc"]) for row in self.subjects_data[s] if row["Bloc"] == bloc])))
        for t in trials: lst.addItem(f"Essai {t}")

    def refresh_canvas(self, s):
        bloc = getattr(self.sidebar, f"cb_c_{s}").currentText()
        selected = getattr(self.sidebar, f"list_t_{s}").selectedItems()
        canvas = getattr(self, f"canvas_{s}"); lbl_stats = getattr(self.sidebar, f"lbl_stats_{s}")
        
        if not selected: 
            canvas.set_data([], 350, 5); lbl_stats.setText("Sélectionnez des essais...")
            return

        ids = [i.text().replace("Essai ", "") for i in selected]
        trials_list, times, forces = [], [], []
        stats_text = "<b>--- METRICS ---</b><br>"

        for t_id in ids:
            pts = [(float(row["X"]), float(row["Y"]), float(row["Time_Rel"]), float(row.get("P_Raw",0))) 
                   for row in self.subjects_data[s] if row["Bloc"] == bloc and row["Trial_in_Bloc"] == t_id]
            if pts:
                trials_list.append({"name": t_id, "points": pts})
                mt = pts[-1][2]; f_mean = np.mean([p[3] for p in pts])
                times.append(mt); forces.append(f_mean)
                c_hex = QColor.fromHsv(120, 220, int(80 + ((int(t_id)-1)%10) * 17.5)).name()
                stats_text += f"<span style='color:{c_hex}'>&#9632; E{t_id}</span>: {mt:.2f}s | F:{int(f_mean)}<br>"
        
        canvas.set_data(trials_list, 350, 5)
        if times:
            stats_text += f"<hr><b>MT MOYEN:</b> {np.mean(times):.2f} s<br><b>F MOYENNE:</b> {int(np.mean(forces))}"
            lbl_stats.setText(stats_text)

# ==============================================================
# 3. ONGLET : AIDE & AXES
# ==============================================================
class TutorialTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.fig = Figure(figsize=(5, 5))
        self.canvas = FigureCanvas(self.fig)
        ax = self.fig.add_subplot(111, projection='3d')
        ax.quiver(-15, 0, 0, 30, 0, 0, color='blue', label='Erreur X (px)')
        ax.quiver(0, -15, 0, 0, 30, 0, color='green', label='Erreur Y (px)')
        ax.quiver(0, 0, -1500, 0, 0, 3000, color='red', label='Erreur Force (Δ)')
        ax.scatter(0, 0, 0, color='gold', s=200, marker='*', label="CIBLE IDÉALE")
        ax.set_title("LÉGENDE DES AXES 3D")
        ax.set_xlim(-20, 20); ax.set_ylim(-20, 20); ax.set_zlim(-2000, 2000)
        ax.legend()
        layout.addWidget(self.canvas)
        layout.addWidget(QLabel("<b>Z (Vertical)</b> : Écart à la force cible.<br><b>XY (Horizontal)</b> : Précision du tracé."))

# ==============================================================
# 4. ONGLET : SIGNATURE 3D (EXPERT)
# ==============================================================
class ExpertiseTab(QWidget):
    def __init__(self, main_studio):
        super().__init__()
        self.studio = main_studio
        layout = QHBoxLayout(self)
        
        self.sidebar = QFrame(); self.sidebar.setFixedWidth(280)
        side_lyt = QVBoxLayout(self.sidebar)
        
        self.cb_p = QComboBox(); self.cb_c = QComboBox() 
        self.list_t = QListWidget(); self.list_t.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        
        side_lyt.addWidget(QLabel("<b>1. Sujet</b>")); side_lyt.addWidget(self.cb_p)
        side_lyt.addWidget(QLabel("<b>2. Bloc (FVP)</b>")); side_lyt.addWidget(self.cb_c)
        side_lyt.addWidget(QLabel("<b>3. Sélection</b>")); side_lyt.addWidget(self.list_t)
        
        self.btn_run = QPushButton("⚡ Générer Signature 3D")
        self.btn_run.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; padding: 10px;")
        self.btn_run.clicked.connect(self.update_plot)
        side_lyt.addWidget(self.btn_run)

        self.btn_export = QPushButton("💾 Exporter Figure (PNG)")
        self.btn_export.clicked.connect(self.export_figure)
        side_lyt.addWidget(self.btn_export)
        
        self.lbl_res = QLabel("Métriques...")
        self.lbl_res.setStyleSheet("font-family: Consolas; background: #2c3e50; color: white; padding: 10px;")
        self.lbl_res.setWordWrap(True)
        side_lyt.addWidget(self.lbl_res); side_lyt.addStretch()
        layout.addWidget(self.sidebar)

        self.figure = Figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas, stretch=1)

        self.cb_p.currentIndexChanged.connect(self.load_blocs_for_subject)
        self.cb_c.currentIndexChanged.connect(self.load_trials_for_bloc)

    def load_blocs_for_subject(self):
        pid = self.cb_p.currentText(); path = self.studio.visualizer.data_path
        if not pid or not path: return
        file_path = os.path.join(path, f"{pid}_CLEAN.csv")
        if not os.path.exists(file_path): file_path = os.path.join(path, f"{pid}_RAW.csv")
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            self.cb_c.blockSignals(True); self.cb_c.clear(); self.cb_c.addItems(sorted(df['Bloc'].unique()))
            self.cb_c.blockSignals(False)
            self.load_trials_for_bloc()

    def load_trials_for_bloc(self):
        self.list_t.clear()
        pid = self.cb_p.currentText(); bloc = self.cb_c.currentText(); path = self.studio.visualizer.data_path
        if not pid or not bloc or not path: return
        file_path = os.path.join(path, f"{pid}_CLEAN.csv")
        if not os.path.exists(file_path): file_path = os.path.join(path, f"{pid}_RAW.csv")
        
        df = pd.read_csv(file_path)
        for t in sorted(df[df['Bloc'] == bloc]['Trial_in_Bloc'].unique()): self.list_t.addItem(f"Essai {t}")

    def update_plot(self):
        pid = self.cb_p.currentText(); bloc = self.cb_c.currentText()
        selected = self.list_t.selectedItems(); path = self.studio.visualizer.data_path
        if not selected or not pid or not path: return

        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        
        file_path = os.path.join(path, f"{pid}_CLEAN.csv")
        if not os.path.exists(file_path): file_path = os.path.join(path, f"{pid}_RAW.csv")
        df = pd.read_csv(file_path)
        
        vols, jerks = [], []
        for item in selected:
            tr_id = item.text().replace("Essai ", "")
            trial_df = df[(df['Bloc'] == bloc) & (df['Trial_in_Bloc'].astype(str) == tr_id)]
            metrics = get_scientific_metrics(trial_df)
            
            if metrics:
                ax.scatter(metrics['x'], metrics['y'], metrics['z'], c=metrics['t_norm'], cmap='viridis', s=2, alpha=0.4)
                vols.append(metrics['vol']); jerks.append(metrics['jerk'])

        ax.set_title(f"Signature 3D : {pid} [{bloc}]")
        ax.set_xlim(-15, 15); ax.set_ylim(-15, 15); ax.set_zlim(-1500, 1500)
        ax.scatter(0, 0, 0, color='red', s=100, marker='*', label="Cible")
        self.canvas.draw()
        
        if vols:
            self.lbl_res.setText(f"<b>VOL (3D):</b> {np.mean(vols):.0f}<br><b>JERK:</b> {np.mean(jerks):.2f}<br><b>N=</b> {len(vols)}")

    def export_figure(self):
        pid = self.cb_p.currentText(); bloc = self.cb_c.currentText()
        path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder", f"Signature_{pid}_{bloc}.png", "PNG (*.png)")
        if path:
            self.figure.savefig(path, dpi=300, bbox_inches='tight')
            QMessageBox.information(self, "Succès", "Figure exportée.")

# ==============================================================
# 5. ONGLET : ANALYSEUR STATISTIQUE (StatsTab Complet)
# ==============================================================
class StatsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.df_features = None
        self.metrics_map = {
            'IPe': 'Performance (IPe)',
            'Duration': 'Temps d\'action (MT)',
            'IDe': 'Difficulté Spatiale (IDe)',
            'Be': 'Pente de Fitts (Be)',
            'LDLJ': 'Fluidité Mouvement (Jerk)',
            'Force_SD': 'Stabilité de Force (SD)'
        }

        layout = QVBoxLayout(self)

        # --- PANNEAU SUPÉRIEUR (CHARGEMENT & MODE) ---
        top_panel = QHBoxLayout()
        self.btn_load = QPushButton("📁 Charger dataset_features.csv")
        self.btn_load.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold; padding: 8px;")
        self.btn_load.clicked.connect(self.load_dataset)
        top_panel.addWidget(self.btn_load)

        top_panel.addWidget(QLabel("<b>Granularité de l'Expertise :</b>"))
        self.cb_mode = QComboBox()
        self.cb_mode.addItems(["3 Groupes (Naïf, Novice, Expert)", "4 Groupes (Naïf, Novice 1-3, Novice 4-6, Expert)"])
        self.cb_mode.currentIndexChanged.connect(self.update_available_filters)
        top_panel.addWidget(self.cb_mode)
        top_panel.addStretch()
        layout.addLayout(top_panel)

        # --- PANNEAU DE FILTRAGE ---
        filter_panel = QHBoxLayout()
        
        # 1. Métrique
        metric_group = QGroupBox("1. Variable Dépendante (Y)")
        mlayout = QVBoxLayout()
        self.cb_metric = QComboBox()
        self.cb_metric.addItems(list(self.metrics_map.values()))
        mlayout.addWidget(self.cb_metric)
        metric_group.setLayout(mlayout)
        filter_panel.addWidget(metric_group)

        # 2. Tâche
        task_group = QGroupBox("2. Condition(s)")
        tlayout = QVBoxLayout()
        self.list_tasks = QListWidget()
        self.list_tasks.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        tlayout.addWidget(self.list_tasks)
        task_group.setLayout(tlayout)
        filter_panel.addWidget(task_group)

        # 3. Groupe
        group_group = QGroupBox("3. Groupes à comparer")
        glayout = QVBoxLayout()
        self.list_groups = QListWidget()
        self.list_groups.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        glayout.addWidget(self.list_groups)
        group_group.setLayout(glayout)
        filter_panel.addWidget(group_group)

        self.btn_run = QPushButton("⚡ Calculer Statistiques (ANOVA/T-Test)")
        self.btn_run.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 15px;")
        self.btn_run.clicked.connect(self.run_analysis)
        filter_panel.addWidget(self.btn_run)

        layout.addLayout(filter_panel)

        # --- PANNEAU DE RÉSULTATS (TABLEAU + GRAPH) ---
        results_layout = QHBoxLayout()
        
        self.table_results = QTableWidget()
        self.table_results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        results_layout.addWidget(self.table_results, stretch=1)

        self.figure = Figure(figsize=(6, 5), layout="constrained")
        self.canvas_plot = FigureCanvas(self.figure)
        results_layout.addWidget(self.canvas_plot, stretch=1)

        layout.addLayout(results_layout)

    def load_dataset(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner features.csv", "", "CSV Files (*.csv)")
        if file_path:
            try:
                self.df_features = pd.read_csv(file_path)
                self.btn_load.setText(f"✅ Fichier chargé ({len(self.df_features)} lignes)")
                self.update_available_filters()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Lecture impossible :\n{e}")

    def get_assigned_dataframe(self):
        """Moteur de catégorisation scientifique des sujets."""
        if self.df_features is None: return None
        df = self.df_features.copy()
        mode = self.cb_mode.currentIndex()
        
        def assign_group(row):
            statut = str(row.get('Statut_Principal', '')).strip().lower()
            sous = str(row.get('Sous_Statut', '')).strip().lower()
            annee = str(row.get('Annee_Apprentissage', '')).strip().lower()
            
            if 'diplômé' in sous: 
                return 'Expert'
            
            if 'interne' in statut or 'apprentissage' in sous:
                if mode == 0: 
                    return 'Novice'
                else: 
                    if any(v in annee for v in ['1','2','3']): return 'Novice (1-3)'
                    if any(v in annee for v in ['4','5','6']): return 'Novice (4-6)'
                    return 'Novice'

            if 'non domaine' in statut:
                return 'Naïf'
            
            return 'Autre'
                
        df['Group'] = df.apply(assign_group, axis=1)
        return df[df['Group'] != 'Autre']

    def update_available_filters(self):
        df = self.get_assigned_dataframe()
        if df is None: return
        
        if 'Condition' in df.columns or 'Task_Type' in df.columns:
            col_task = 'Condition' if 'Condition' in df.columns else 'Task_Type'
            self.list_tasks.clear()
            self.list_tasks.addItems([str(x) for x in df[col_task].unique() if str(x) != 'nan'])
            self.list_tasks.selectAll()

        self.list_groups.clear()
        self.list_groups.addItems([g for g in df['Group'].unique() if g != 'Autre'])
        self.list_groups.selectAll()

    def run_analysis(self):
        df = self.get_assigned_dataframe()
        if df is None: return QMessageBox.warning(self, "Erreur", "Chargez le CSV.")
        
        col_task = 'Condition' if 'Condition' in df.columns else 'Task_Type'
        sel_tasks = [i.text() for i in self.list_tasks.selectedItems()]
        sel_groups = [i.text() for i in self.list_groups.selectedItems()]
        
        df_stats = df[(df['Group'].isin(sel_groups)) & (df[col_task].isin(sel_tasks))]
        if df_stats.empty: return QMessageBox.warning(self, "Erreur", "Aucune donnée trouvée.")
        
        lbl = self.cb_metric.currentText()
        col_metric = next(k for k, v in self.metrics_map.items() if v == lbl)
        
        # SÉCURITÉ : Vérifier si la colonne existe
        if col_metric not in df_stats.columns:
            return QMessageBox.warning(self, "Erreur", f"La colonne {col_metric} est introuvable dans le CSV.")

        # --- TABLEAU ---
        headers = ["Tâche", "Métrique"] + sel_groups + ["Test Stat", "p-value"]
        self.table_results.clear()
        self.table_results.setColumnCount(len(headers))
        self.table_results.setHorizontalHeaderLabels(headers)
        self.table_results.setRowCount(0)

        row_idx = 0
        for task in sel_tasks:
            df_t = df_stats[df_stats[col_task] == task].copy()
            df_t[col_metric] = pd.to_numeric(df_t[col_metric], errors='coerce')
            df_t = df_t.dropna(subset=[col_metric])
            
            if df_t.empty: continue

            self.table_results.insertRow(row_idx)
            self.table_results.setItem(row_idx, 0, QTableWidgetItem(task))
            self.table_results.setItem(row_idx, 1, QTableWidgetItem(lbl))

            group_series = []
            col_offset = 2
            
            for g in sel_groups:
                series = df_t[df_t['Group'] == g][col_metric]
                group_series.append(series)
                val_str = f"{np.mean(series):.2f} ± {np.std(series):.2f}" if len(series) > 0 else "-"
                self.table_results.setItem(row_idx, col_offset, QTableWidgetItem(val_str))
                col_offset += 1

            valid_series = [s for s in group_series if len(s) > 1]
            if len(valid_series) == 2:
                _, p = stats.ttest_ind(valid_series[0], valid_series[1], equal_var=False)
                self.table_results.setItem(row_idx, col_offset, QTableWidgetItem("T-Test (Welch)"))
                self.table_results.setItem(row_idx, col_offset + 1, QTableWidgetItem(f"{p:.3f}"))
            elif len(valid_series) > 2:
                _, p = stats.f_oneway(*valid_series)
                self.table_results.setItem(row_idx, col_offset, QTableWidgetItem("ANOVA"))
                self.table_results.setItem(row_idx, col_offset + 1, QTableWidgetItem(f"{p:.3f}"))
            
            row_idx += 1

        # --- GRAPHIQUE (Boxplot) ---
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        sns.set_theme(style="whitegrid")
        df_plot = df_stats.copy()
        df_plot[col_metric] = pd.to_numeric(df_plot[col_metric], errors='coerce')
        sns.boxplot(x="Group", y=col_metric, hue=col_task, data=df_plot, ax=ax, palette="Set2")
        ax.set_title(f"Distribution : {lbl}")
        ax.set_ylabel(lbl)
        ax.set_xlabel("Niveau d'Expertise")
        self.canvas_plot.draw()
        
# ==============================================================
# 6. APPLICATION PRINCIPALE
# ==============================================================
class HaptiMedStudio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HaptiMed Studio 2026")
        self.resize(1600, 950)
        
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        self.visualizer = VisualizerTab()
        self.tutorial = TutorialTab()
        self.expertise = ExpertiseTab(self)
        self.stats = StatsTab()
        
        self.tabs.addTab(self.visualizer, "🔍 1. Visualiseur Cinématique")
        self.tabs.addTab(self.tutorial, "📖 2. Aide & Axes 3D")
        self.tabs.addTab(self.expertise, "🔬 3. Signature d'Expertise 3D")
        self.tabs.addTab(self.stats, "📊 4. Statistiques")
        
        layout.addWidget(self.tabs)

        # Synchronisation
        self.visualizer.sidebar.btn_path.clicked.connect(self.sync_all_tabs)

    def sync_all_tabs(self):
        path = self.visualizer.data_path
        if path:
            files = [f for f in os.listdir(path) if f.endswith('.csv')]
            pids = sorted(list(set([f.split('_')[0] for f in files])))
            
            self.expertise.cb_p.blockSignals(True)
            self.expertise.cb_p.clear()
            self.expertise.cb_p.addItems(pids)
            self.expertise.cb_p.blockSignals(False)
            self.expertise.load_blocs_for_subject()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    try:
        window = HaptiMedStudio()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Erreur critique : {e}")