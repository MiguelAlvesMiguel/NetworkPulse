import requests
import dns.resolver
import time
import netifaces
import subprocess
import json
import stun

def detect_nat_type():
    """Detect NAT type using STUN protocol."""
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

def get_dns_servers():
    """Get list of DNS servers."""
    resolver = dns.resolver.Resolver()
    return resolver.nameservers

def test_dns_servers(servers):
    """Test DNS servers response time."""
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
    """Get ISP information using ipinfo.io."""
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
    """Get public IP address."""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip = response.json().get('ip', 'N/A')
        return ip
    except Exception as e:
        return f'Erro: {e}'

def get_internal_network_info():
    """Get internal network properties."""
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
    """Test connectivity to external hosts."""
    results = []
    for host in hosts:
        try:
            param = '-n' if subprocess.call('ping -n 1 localhost', shell=True, stdout=subprocess.DEVNULL) == 0 else '-c'
            command = ['ping', param, '4', host]
            output = subprocess.check_output(command, universal_newlines=True)
            latency_line = [line for line in output.split('\n') if 'tempo médio' in line or 'avg' in line]
            if latency_line:
                latency = ''.join(filter(str.isdigit, latency_line[0]))
                results.append({'Host': host, 'Latência Média (ms)': latency, 'Status': 'Alcançável'})
            else:
                results.append({'Host': host, 'Latência Média (ms)': None, 'Status': 'Alcançável, mas sem dados de latência'})
        except subprocess.CalledProcessError:
            results.append({'Host': host, 'Latência Média (ms)': None, 'Status': 'Inalcançável'})
    return results

def network_performance_test():
    """Test network performance using speedtest-cli."""
    try:
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
