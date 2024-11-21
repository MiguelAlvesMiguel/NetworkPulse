import tkinter as tk
from tkinter import ttk, scrolledtext
import json
from network_analyzer import NetworkAnalyzer
from datetime import datetime
import queue
import threading

class DebugLogHandler:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.text_widget.tag_configure('timestamp', foreground='gray')
        
    def write(self, message):
        self.queue.put(message)
        
    def flush(self):
        pass
        
    def update(self):
        while not self.queue.empty():
            message = self.queue.get()
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.text_widget.insert(tk.END, f'[{timestamp}] ', 'timestamp')
            self.text_widget.insert(tk.END, message)
            self.text_widget.see(tk.END)
        
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class NetworkAnalyzerGUI:
    def __init__(self):
        print("[DEBUG] Initializing NetworkAnalyzerGUI")
        self.root = tk.Tk()
        self.root.title('NetworkPulse - Diagnóstico de Rede')
        self.root.geometry('1400x800')
        self.root.minsize(1200, 600)
        
        # Configure styles
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), padding=10)
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), padding=5)
        style.configure('Data.TLabel', font=('Segoe UI', 10))
        
        self.analyzer = NetworkAnalyzer()
        self.setup_gui()
        print("[DEBUG] GUI initialization complete")
        
    def setup_gui(self):
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill='both', expand=True)
        
        # Title and controls frame
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(title_frame, text='NetworkPulse', style='Title.TLabel').pack(side='left')
        
        self.refresh_button = ttk.Button(title_frame, text=' Atualizar Tudo', command=self.refresh_all)
        self.refresh_button.pack(side='right')
        
        # Create main content paned window
        paned = ttk.PanedWindow(main_container, orient='horizontal')
        paned.pack(fill='both', expand=True)
        
        # Left panel for network info
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=2)
        
        # Create scrollable frame for panels
        scroll_container = ScrollableFrame(left_frame)
        scroll_container.pack(fill='both', expand=True)
        
        # Grid for panels
        panels_frame = scroll_container.scrollable_frame
        panels_frame.columnconfigure(0, weight=1)
        panels_frame.columnconfigure(1, weight=1)
        
        # Define panels
        self.panels = [
            ('nat', 'Configuração NAT'),
            ('dns', 'Servidores DNS'),
            ('isp', 'Informações do ISP'),
            ('network', 'Rede Interna'),
            ('connectivity', 'Conectividade'),
            ('performance', 'Performance')
        ]
        
        # Create panel frames
        self.panel_frames = {}
        for i, (section, title) in enumerate(self.panels):
            row = i // 2
            col = i % 2
            frame = self.create_panel(panels_frame, title, row, col, section)
            self.panel_frames[section] = frame
            
        # Right panel for debug log
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        # Debug log
        ttk.Label(right_frame, text='Log de Diagnóstico', style='Header.TLabel').pack(fill='x', pady=(0, 5))
        self.debug_text = scrolledtext.ScrolledText(right_frame, height=10, wrap=tk.WORD)
        self.debug_text.pack(fill='both', expand=True)
        
        # Set up debug log handler
        self.log_handler = DebugLogHandler(self.debug_text)
        import sys
        sys.stdout = self.log_handler
        
        # Start log update timer
        self.root.after(100, self.update_log)
            
    def create_panel(self, parent, title, row, col, section_name):
        print(f"[DEBUG] Creating panel: {title}")
        frame = ttk.LabelFrame(parent, text=title, padding=10)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Content frame
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill='both', expand=True)
        
        # Add individual refresh button
        refresh_btn = ttk.Button(
            frame, 
            text="", 
            width=3,
            command=lambda s=section_name: self.refresh_section(s)
        )
        refresh_btn.pack(side='top', anchor='e', pady=(0, 5))
        
        return {'frame': frame, 'content': content_frame, 'refresh': refresh_btn}
            
    def update_panel_content(self, section_name, data):
        print(f"[DEBUG] Updating panel content: {section_name}")
        panel = self.panel_frames[section_name]
        content_frame = panel['content']
        
        # Clear previous content
        for widget in content_frame.winfo_children():
            widget.destroy()
            
        # Display data
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    ttk.Label(content_frame, text=key, style='Header.TLabel').pack(anchor='w', pady=(5,2))
                    for k, v in value.items():
                        ttk.Label(content_frame, text=f"{k}: {v}", style='Data.TLabel').pack(anchor='w', padx=10, pady=2)
                else:
                    ttk.Label(content_frame, text=f"{key}: {value}", style='Data.TLabel').pack(anchor='w', pady=2)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for k, v in item.items():
                        ttk.Label(content_frame, text=f"{k}: {v}", style='Data.TLabel').pack(anchor='w', pady=2)
                else:
                    ttk.Label(content_frame, text=str(item), style='Data.TLabel').pack(anchor='w', pady=2)
                    
    def update_log(self):
        """Update the debug log text widget."""
        self.log_handler.update()
        self.root.after(100, self.update_log)
                    
    def refresh_section(self, section_name):
        """Refresh a single section asynchronously."""
        print(f"[DEBUG] Refreshing section: {section_name}")
        
        def update_section():
            try:
                self.analyzer.collect_section(section_name)
                
                # Map section names to info keys
                section_key_map = {
                    'nat': 'Configuração NAT',
                    'dns': 'Servidores DNS',
                    'isp': 'Informações do ISP',
                    'network': 'Propriedades de Rede Interna',
                    'connectivity': 'Conectividade Externa',
                    'performance': 'Performance da Rede'
                }
                
                if section_key_map[section_name] in self.analyzer.info:
                    data = self.analyzer.info[section_key_map[section_name]]
                    self.root.after(0, lambda: self.update_panel_content(section_name, data))
                else:
                    print(f"[DEBUG] No data found for section {section_name}")
                    raise KeyError(f"No data found for section {section_name}")
                    
            except Exception as e:
                print(f"[DEBUG] Error refreshing section {section_name}: {str(e)}")
                panel = self.panel_frames[section_name]
                content_frame = panel['content']
                for widget in content_frame.winfo_children():
                    widget.destroy()
                ttk.Label(content_frame, text=f"Erro: {str(e)}", style='Data.TLabel').pack(anchor='w')
        
        # Start update in a separate thread
        thread = threading.Thread(target=update_section)
        thread.daemon = True
        thread.start()
            
    def refresh_all(self):
        """Refresh all sections asynchronously."""
        print("[DEBUG] Starting refresh of all sections")
        self.refresh_button.config(state='disabled')
        
        # Start refresh for each section
        for section_name, _ in self.panels:
            self.refresh_section(section_name)
            
        # Re-enable refresh button after a delay
        self.root.after(1000, lambda: self.refresh_button.config(state='normal'))
        
    def run(self):
        # Center window
        width = 1400
        height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Initial refresh
        self.root.after(100, self.refresh_all)
        self.root.mainloop()

if __name__ == "__main__":
    app = NetworkAnalyzerGUI()
    app.run()
