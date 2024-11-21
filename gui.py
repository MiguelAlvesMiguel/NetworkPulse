import tkinter as tk
from tkinter import ttk
from network_analyzer import NetworkAnalyzer

class NetworkAnalyzerGUI:
    """GUI class for the Network Analyzer application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Análise de Rede - IONIC Health')
        self.root.geometry('1024x768')
        self.analyzer = NetworkAnalyzer()
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the GUI components."""
        # Configuração do estilo
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Data.TLabel', font=('Arial', 10))
        style.configure('Section.TFrame', relief='raised', padding=10)
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(
            title_frame,
            text='Análise de Rede - IONIC Health',
            style='Title.TLabel'
        ).pack()
        
        # Container para os painéis
        panels_frame = ttk.Frame(main_frame)
        panels_frame.pack(fill='both', expand=True)
        
        # Criar grid 2x3 para os painéis
        panels_frame.columnconfigure(0, weight=1)
        panels_frame.columnconfigure(1, weight=1)
        
        # Criação dos painéis
        self.create_panel(panels_frame, 'Configuração NAT', 0, 0, 'nat')
        self.create_panel(panels_frame, 'Servidores DNS', 0, 1, 'dns')
        self.create_panel(panels_frame, 'Informações do ISP', 1, 0, 'isp')
        self.create_panel(panels_frame, 'Rede Interna', 1, 1, 'network')
        self.create_panel(panels_frame, 'Conectividade', 2, 0, 'connectivity')
        self.create_panel(panels_frame, 'Performance', 2, 1, 'performance')
        
        # Botão para atualizar tudo
        ttk.Button(
            main_frame,
            text='Atualizar Todas as Informações',
            command=self.refresh_all
        ).pack(pady=20)
        
    def create_panel(self, parent, title, row, col, section_name):
        """Create a panel for displaying network information."""
        frame = ttk.Frame(parent, style='Section.TFrame')
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Cabeçalho do painel
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(
            header_frame,
            text=title,
            style='Header.TLabel'
        ).pack(side='left')
        ttk.Button(
            header_frame,
            text='Atualizar',
            command=lambda s=section_name: self.refresh_section(s)
        ).pack(side='right')
        
        # Área de conteúdo
        content_frame = ttk.Frame(frame)
        content_frame.pack(fill='both', expand=True)
        setattr(self, f'{section_name}_content', content_frame)
        
    def update_panel_content(self, section_name, data):
        """Update the content of a panel with new data."""
        content_frame = getattr(self, f'{section_name}_content')
        # Limpar conteúdo anterior
        for widget in content_frame.winfo_children():
            widget.destroy()
            
        # Adicionar novo conteúdo
        if isinstance(data, dict):
            for k, v in data.items():
                item_frame = ttk.Frame(content_frame)
                item_frame.pack(fill='x', pady=2)
                ttk.Label(
                    item_frame,
                    text=f"{k}:",
                    style='Data.TLabel'
                ).pack(side='left')
                ttk.Label(
                    item_frame,
                    text=str(v),
                    style='Data.TLabel'
                ).pack(side='left', padx=(5, 0))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for k, v in item.items():
                        item_frame = ttk.Frame(content_frame)
                        item_frame.pack(fill='x', pady=2)
                        ttk.Label(
                            item_frame,
                            text=f"{k}:",
                            style='Data.TLabel'
                        ).pack(side='left')
                        ttk.Label(
                            item_frame,
                            text=str(v),
                            style='Data.TLabel'
                        ).pack(side='left', padx=(5, 0))
                    ttk.Separator(content_frame).pack(fill='x', pady=5)
                    
    def refresh_section(self, section_name):
        """Refresh a specific section of the network analysis."""
        self.analyzer.collect_section(section_name)
        section_key = {
            'nat': 'Configuração NAT',
            'dns': 'Servidores DNS',
            'isp': 'Informações do ISP',
            'network': 'Propriedades de Rede Interna',
            'connectivity': 'Conectividade Externa',
            'performance': 'Performance da Rede'
        }[section_name]
        self.update_panel_content(section_name, self.analyzer.info[section_key])
        
    def refresh_all(self):
        """Refresh all sections of the network analysis."""
        self.analyzer.collect_all_info()
        for section in ['nat', 'dns', 'isp', 'network', 'connectivity', 'performance']:
            self.refresh_section(section)
            
    def run(self):
        """Start the GUI application."""
        self.refresh_all()
        self.root.mainloop()
