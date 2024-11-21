import requests
import dns.resolver
import time
import netifaces
import subprocess
import json
import tkinter as tk
from tkinter import ttk
import stun  # Biblioteca para detecção do tipo de NAT

def get_dns_servers():
    resolver = dns.resolver.Resolver()
    return resolver.nameservers

def test_dns_servers(servers):
    results = []
    for server in servers:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [server]
        try:
            start = time.time()
            answer = resolver.resolve('www.google.com', 'A')
            end = time.time()
            latency = (end - start) * 1000  # Convert to milliseconds
            results.append({'Servidor DNS': server, 'Latência (ms)': round(latency, 2), 'Status': 'Respondendo'})
        except Exception as e:
            results.append({'Servidor DNS': server, 'Latência (ms)': None, 'Status': 'Sem resposta'})
    return results

def get_isp_info():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        return {
            'ISP': data.get('org', 'N/A'),
            'Localização': f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}",
            'ASN': data.get('asn', 'N/A'),
            'IP': data.get('ip', 'N/A')
        }
    except Exception as e:
        return {'Erro': str(e)}

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip = response.json().get('ip', 'N/A')
        return ip
    except Exception as e:
        return f'Erro: {e}'

def get_internal_network_info():
    interfaces = netifaces.interfaces()
    network_info = []
    for iface in interfaces:
        addr = netifaces.ifaddresses(iface)
        ip_info = addr.get(netifaces.AF_INET, [{}])[0]
        mac_info = addr.get(netifaces.AF_LINK, [{}])[0]
        gateway_info = netifaces.gateways().get('default', {})
        gateway = gateway_info.get(netifaces.AF_INET, [None])[0]
        network_info.append({
            'Interface': iface,
            'Endereço IP': ip_info.get('addr', 'N/A'),
            'Máscara de Sub-rede': ip_info.get('netmask', 'N/A'),
            'Gateway Padrão': gateway if gateway else 'N/A',
            'Endereço MAC': mac_info.get('addr', 'N/A')
        })
    return network_info

def ping_test(hosts):
    results = []
    for host in hosts:
        try:
            # O parâmetro '-n' no Windows e '-c' no Unix para o número de pacotes
            param = '-n' if subprocess.call('ping -n 1 localhost', shell=True, stdout=subprocess.DEVNULL) == 0 else '-c'
            command = ['ping', param, '4', host]
            output = subprocess.check_output(command, universal_newlines=True)
            latency_line = [line for line in output.split('\n') if 'tempo médio' in line or 'avg' in line]
            if latency_line:
                # Extrair a latência média
                latency = ''.join(filter(str.isdigit, latency_line[0]))
                results.append({'Host': host, 'Latência Média (ms)': latency, 'Status': 'Alcançável'})
            else:
                results.append({'Host': host, 'Latência Média (ms)': None, 'Status': 'Alcançável, mas sem dados de latência'})
        except subprocess.CalledProcessError:
            results.append({'Host': host, 'Latência Média (ms)': None, 'Status': 'Inalcançável'})
    return results

def network_performance_test():
    try:
        # Use speedtest-cli instead of speedtest library for better reliability
        result = subprocess.run(['speedtest-cli', '--json'], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                'Status': 'Sucesso',
                'Velocidade de Download (Mbps)': round(data['download'] / 10**6, 2),
                'Velocidade de Upload (Mbps)': round(data['upload'] / 10**6, 2),
                'Ping (ms)': round(data['ping'], 2),
                'ISP do Servidor': data['server']['sponsor']
            }
    except subprocess.TimeoutExpired:
        return {'Status': 'Erro: Timeout durante o teste de velocidade'}
    except Exception as e:
        return {'Status': f'Erro: {str(e)}'}

def detect_nat_type():
    try:
        nat = stun.get_ip_info()
        if nat[1] is None:  # If external IP is None, try alternative STUN server
            stun.STUN_SERVERS = [('stun.l.google.com', 19302)]
            nat = stun.get_ip_info()
        
        nat_types = {
            'Blocked': 'Bloqueado',
            'Open Internet': 'Internet Aberta',
            'Full Cone': 'NAT Cone Completo',
            'Restricted NAT': 'NAT Restrito',
            'Port Restricted NAT': 'NAT com Porta Restrita',
            'Symmetric NAT': 'NAT Simétrico'
        }
        
        return {
            'Tipo de NAT': nat_types.get(nat[0], nat[0]),
            'IP Externo': nat[1] or 'Não detectado',
            'Porta Externa': nat[2] or 'Não detectada'
        }
    except Exception as e:
        return {
            'Tipo de NAT': 'Não detectado',
            'IP Externo': 'Não detectado',
            'Porta Externa': 'Não detectada',
            'Erro': str(e)
        }

class NetworkAnalyzer:
    def __init__(self):
        self.info = {}
        
    def collect_section(self, section_name):
        if section_name == 'nat':
            self.info['Configuração NAT'] = detect_nat_type()
        elif section_name == 'dns':
            dns_servers = get_dns_servers()
            self.info['Servidores DNS'] = test_dns_servers(dns_servers)
        elif section_name == 'isp':
            self.info['Informações do ISP'] = get_isp_info()
        elif section_name == 'network':
            self.info['Propriedades de Rede Interna'] = get_internal_network_info()
        elif section_name == 'connectivity':
            self.info['Conectividade Externa'] = ping_test(['google.com', 'amazon.com'])
        elif section_name == 'performance':
            self.info['Performance da Rede'] = network_performance_test()
        
    def collect_all_info(self):
        sections = ['nat', 'dns', 'isp', 'network', 'connectivity', 'performance']
        for section in sections:
            self.collect_section(section)
        return self.info

class NetworkAnalyzerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Análise de Rede - IONIC Health')
        self.root.geometry('1024x768')
        self.analyzer = NetworkAnalyzer()
        self.setup_gui()
        
    def setup_gui(self):
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
        self.analyzer.collect_all_info()
        for section in ['nat', 'dns', 'isp', 'network', 'connectivity', 'performance']:
            self.refresh_section(section)
            
    def run(self):
        self.refresh_all()
        self.root.mainloop()

if __name__ == '__main__':
    app = NetworkAnalyzerGUI()
    app.run()
