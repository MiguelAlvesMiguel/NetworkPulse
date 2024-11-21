#!/usr/bin/env python3
"""
NetworkPulse - IONIC Health Network Analysis Tool
A comprehensive network analysis tool for medical equipment monitoring.
"""

import sys
import subprocess
import importlib
import tkinter as tk
from tkinter import ttk, messagebox

REQUIRED_PACKAGES = {
    'dnspython': 'dnspython>=2.4.2',
    'requests': 'requests>=2.31.0',
    'netifaces': 'netifaces>=0.11.0',
    'speedtest-cli': 'speedtest-cli>=2.1.3',
    'stun': 'stun>=0.1.12'
}

def is_package_installed(package_name):
    """Check if a package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_spec, progress_window=None, progress_label=None):
    """Install a Python package."""
    try:
        if progress_label:
            package_name = package_spec.split('>=')[0]
            progress_label.config(text=f"Installing {package_name}...")
            progress_window.update()
            
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            package_spec
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if progress_label:
            progress_label.config(text=f"Installed {package_name} successfully!")
            progress_window.update()
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Check and install missing dependencies."""
    missing_packages = []
    for package_name, package_spec in REQUIRED_PACKAGES.items():
        if not is_package_installed(package_name):
            missing_packages.append(package_spec)

    if missing_packages:
        # Create progress window
        progress_window = tk.Tk()
        progress_window.title("Installing Dependencies")
        progress_window.geometry("300x150")
        
        # Center the window
        screen_width = progress_window.winfo_screenwidth()
        screen_height = progress_window.winfo_screenheight()
        x = (screen_width - 300) // 2
        y = (screen_height - 150) // 2
        progress_window.geometry(f"300x150+{x}+{y}")
        
        # Add progress information
        ttk.Label(
            progress_window,
            text="Installing required packages...",
            font=('Arial', 12)
        ).pack(pady=20)
        
        progress_label = ttk.Label(
            progress_window,
            text="Starting installation...",
            font=('Arial', 10)
        )
        progress_label.pack(pady=10)
        
        progress = ttk.Progressbar(
            progress_window,
            mode='indeterminate',
            length=200
        )
        progress.pack(pady=10)
        progress.start()
        
        installation_failed = False
        for package_spec in missing_packages:
            if not install_package(package_spec, progress_window, progress_label):
                installation_failed = True
                package_name = package_spec.split('>=')[0]
                messagebox.showerror(
                    "Installation Error",
                    f"Failed to install {package_name}.\n"
                    "Please try installing dependencies manually using:\n"
                    "pip install -r requirements.txt"
                )
                progress_window.destroy()
                sys.exit(1)
        
        if not installation_failed:
            progress.stop()
            progress_label.config(text="All dependencies installed successfully!")
            progress_window.after(1500, progress_window.destroy)
            progress_window.mainloop()

def main():
    """Main entry point of the application."""
    # Check and install dependencies before importing GUI
    check_and_install_dependencies()
    
    # Import GUI after ensuring dependencies are installed
    from gui import NetworkAnalyzerGUI
    
    try:
        app = NetworkAnalyzerGUI()
        app.run()
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"An error occurred while starting the application:\n{str(e)}"
        )
        sys.exit(1)

if __name__ == '__main__':
    main()
