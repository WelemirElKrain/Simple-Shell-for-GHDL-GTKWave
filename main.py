# -*- coding: utf-8 -*-
"""
VHDL Shell Interface (PyQt5)
Author: Andrii Sokolov
Description:
    Simple GUI wrapper for GHDL + GTKWave
"""
import time
import sys, os
from PyQt5.QtCore import QProcess
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from ShellUI import Ui_MainWindow


class ShellUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_output)

        # --- Variables ---
        self.ghdl_path = ""
        self.gtkwave_path = ""
        self.current_file = None
        self.config_path = os.path.join(os.path.dirname(__file__), "path_config.txt")

        # --- Load saved paths ---
        self.load_paths()

        # --- Connect buttons ---
        self.ui.runGKTWaveButton.clicked.connect(self.rungktwave_button)
        self.ui.compileButton.clicked.connect(self.compile_button)
        self.ui.testButton.clicked.connect(self.test_button)

        # --- Connect menu actions ---
        self.ui.actionNew.triggered.connect(self.new_file)
        self.ui.actionOpen.triggered.connect(self.open_file)
        self.ui.actionSave_as.triggered.connect(self.save_file)
        self.ui.actionSet_PATH.triggered.connect(self.set_path)

    # === File operations ===
    def new_file(self):
        self.ui.codeEdit.clear()
        self.current_file = None

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open VHDL File", "", "VHDL Files (*.vhdl *.vhd)")
        if path:
            with open(path, "r") as f:
                self.ui.codeEdit.setPlainText(f.read())
            self.current_file = path

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "VHDL Files (*.vhdl *.vhd)")
        if path:
            with open(path, "w") as f:
                f.write(self.ui.codeEdit.toPlainText())
            self.current_file = path

    # === Compilation & Simulation ===
    def compile_button(self):
        """Compile and run VHDL simulation via GHDL."""
    
        if not self.ghdl_path:
            self.ui.consoleEdit.append("[Error] GHDL path not set!")
            return
        if not self.current_file:
            self.ui.consoleEdit.append("[Error] No VHDL file opened!")
            return
    
        # Save file
        with open(self.current_file, "w") as f:
            f.write(self.ui.codeEdit.toPlainText())
    
        filename = os.path.basename(self.current_file)
        folder = os.path.dirname(self.current_file)
        cwd = os.getcwd()
        os.chdir(folder)
    
        # Detect entity
        with open(self.current_file, "r") as f:
            entity_name = None
            for line in f:
                if line.strip().lower().startswith("entity "):
                    entity_name = line.split()[1]
                    break
        if not entity_name:
            entity_name = os.path.splitext(filename)[0]
    
        # Stop time
        limit_time = str(self.ui.spinBox.value()) + "ns"
        if self.ui.spinBox.value() <= 0:
            limit_time = "100ns"
            self.ui.consoleEdit.append("[Warning] stop-time set to default 100ns.")
    
        self.ui.consoleEdit.clear()
        self.ui.consoleEdit.append(f"Compiling all VHDL files in {folder} ...")
    
        # Analyze all VHDL files
        for file in os.listdir(folder):
            if file.lower().endswith((".vhd", ".vhdl")):
                filepath = os.path.normpath(os.path.join(folder, file))
                self.ui.consoleEdit.append(f"Analyzing {file} ...")
                code = QProcess.execute(self.ghdl_path, ["-a", "--warn-no-library", filepath])
                if code != 0:
                    self.ui.consoleEdit.append(f"[Error] Failed to analyze {file}")
                    os.chdir(cwd)
                    return
    
        # Give GHDL a short delay to flush library
        time.sleep(0.2)
    
        # Elaborate
        self.ui.consoleEdit.append(f"Elaborating entity: {entity_name}")
        code = QProcess.execute(self.ghdl_path, ["-e", entity_name])
        if code != 0:
            self.ui.consoleEdit.append(f"[Error] Elaboration failed for {entity_name}")
            os.chdir(cwd)
            return
    
        # Run simulation
        self.ui.consoleEdit.append(f"Running simulation for {entity_name}, stop-time={limit_time}")
        self.process.setWorkingDirectory(folder)
        self.process.start(self.ghdl_path, ["-r", entity_name, f"--stop-time={limit_time}", "--vcd=wave.vcd"])
    
        # Debug info
        time.sleep(0.5)
        if os.path.exists("wave.vcd"):
            self.ui.consoleEdit.append(f"[Info] wave.vcd generated ({os.path.getsize('wave.vcd')} bytes)")
        else:
            self.ui.consoleEdit.append("[Warning] wave.vcd not found!")
    
        self.ui.consoleEdit.append("[Done] Compilation and simulation finished successfully.")
        os.chdir(cwd)

    def test_button(self):
        """Run syntax check and dependency analysis."""
    
        if not self.ghdl_path:
            self.ui.consoleEdit.append("[Error] GHDL path not set!")
            return
        if not self.current_file:
            self.ui.consoleEdit.append("[Error] No VHDL file opened!")
            return
    
        # Save current code
        with open(self.current_file, "w") as f:
            f.write(self.ui.codeEdit.toPlainText())
    
        filename = os.path.basename(self.current_file)
        folder = os.path.dirname(self.current_file)
        cwd = os.getcwd()
    
        os.chdir(folder)
        self.ui.consoleEdit.clear()
        self.ui.consoleEdit.append(f"Testing syntax of {self.current_file} ...")
    
        # Rebuild work library
        for file in os.listdir(folder):
            if file.lower().endswith((".vhd", ".vhdl")):
                filepath = os.path.normpath(os.path.join(folder, file))
                self.ui.consoleEdit.append(f"Analyzing {file} ...")
                QProcess.execute(self.ghdl_path, ["-a", "--warn-no-library", filepath])
    
        # Syntax check
        self.ui.consoleEdit.append(f"Checking {filename} ...")
        code = QProcess.execute(self.ghdl_path, ["-s", self.current_file])
    
        os.chdir(cwd)
        time.sleep(0.2)
    
        if code != 0:
            self.ui.consoleEdit.append(f"[Error] Syntax errors detected in {filename}")
        else:
            self.ui.consoleEdit.append("[Done] Syntax OK. All dependencies analyzed successfully.")



    def rungktwave_button(self):
        """Open GTKWave with wave.vcd."""
        if not self.gtkwave_path:
            self.ui.consoleEdit.append("[Error] GTKWave path not set!")
            return

        folder = os.path.dirname(self.current_file) if self.current_file else "."
        wave_path = os.path.join(folder, "wave.vcd")

        if not os.path.exists(wave_path):
            self.ui.consoleEdit.append("[Warning] wave.vcd not found — run simulation first.")
            return

        self.ui.consoleEdit.append("Opening GTKWave ...")
        self.process.startDetached(self.gtkwave_path, [wave_path])

    # === Paths ===
    def set_path(self):
        ghdl_path, _ = QFileDialog.getOpenFileName(self, "Select GHDL executable", "", "Executable files (*.exe);;All files (*)")
        if ghdl_path:
            self.ghdl_path = ghdl_path
            self.ui.consoleEdit.append(f"GHDL path set to: {ghdl_path}")

        gtkwave_path, _ = QFileDialog.getOpenFileName(self, "Select GTKWave executable", "", "Executable files (*.exe);;All files (*)")
        if gtkwave_path:
            self.gtkwave_path = gtkwave_path
            self.ui.consoleEdit.append(f"GTKWave path set to: {gtkwave_path}")

        self.save_paths()
        msg = f"GHDL: {self.ghdl_path or 'not set'}, GTKWave: {self.gtkwave_path or 'not set'}"
        self.ui.statusbar.showMessage(msg)

    def save_paths(self):
        with open(self.config_path, "w") as f:
            f.write(f"GHDL={self.ghdl_path}\nGTKWave={self.gtkwave_path}\n")

    def load_paths(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                for line in f:
                    if line.startswith("GHDL="):
                        self.ghdl_path = line.strip().split("=", 1)[1]
                    elif line.startswith("GTKWave="):
                        self.gtkwave_path = line.strip().split("=", 1)[1]

            if self.ghdl_path or self.gtkwave_path:
                self.ui.consoleEdit.append("[Info] Paths loaded from path_config.txt")
                self.ui.statusbar.showMessage(f"GHDL: {self.ghdl_path or 'not set'}, GTKWave: {self.gtkwave_path or 'not set'}")

    def read_output(self):
        output = self.process.readAllStandardOutput().data().decode("utf-8")
        error = self.process.readAllStandardError().data().decode("utf-8")
        if output:
            self.ui.consoleEdit.append(output.strip())
        if error:
            self.ui.consoleEdit.append(f"[Error] {error.strip()}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ShellUI()
    win.show()
    sys.exit(app.exec())
