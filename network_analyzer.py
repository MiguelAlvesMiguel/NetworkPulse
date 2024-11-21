from network_utils import (
    detect_nat_type,
    get_dns_servers,
    test_dns_servers,
    get_isp_info,
    get_internal_network_info,
    ping_test,
    network_performance_test
)

class NetworkAnalyzer:
    """Main class for collecting and managing network information."""
    
    def __init__(self):
        self.info = {}
        
    def collect_section(self, section_name):
        """Collect information for a specific section."""
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
        """Collect information for all sections."""
        sections = ['nat', 'dns', 'isp', 'network', 'connectivity', 'performance']
        for section in sections:
            self.collect_section(section)
        return self.info
