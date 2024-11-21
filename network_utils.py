import socket
import dns.resolver
import requests
import netifaces
import subprocess
import stun
import speedtest
import time
import platform
from typing import List, Dict, Any, Union

def detect_nat_type() -> Dict[str, str]:
    """Detect NAT type using STUN protocol."""
    print("[DEBUG] Starting NAT detection")
    try:
        nat_type, external_ip, external_port = stun.get_ip_info(
            source_ip="0.0.0.0",
            source_port=54320,
            stun_host="stun.l.google.com",
            stun_port=19302
        )
        print(f"[DEBUG] NAT detection successful: {nat_type}")
        return {
            'NAT Type': nat_type,
            'External IP': external_ip if external_ip else "Não detectado",
            'External Port': str(external_port) if external_port else "Não detectado"
        }
    except Exception as e:
        print(f"[DEBUG] Error in NAT detection: {str(e)}")
        return {
            'NAT Type': 'Erro ao detectar NAT',
            'Error': str(e)
        }

def get_dns_servers() -> List[str]:
    """Get list of DNS servers."""
    print("[DEBUG] Getting DNS servers")
    try:
        resolver = dns.resolver.Resolver()
        dns_servers = resolver.nameservers
        print(f"[DEBUG] Found DNS servers: {dns_servers}")
        return dns_servers
    except Exception as e:
        print(f"[DEBUG] Error getting DNS servers: {str(e)}")
        return ['8.8.8.8', '8.8.4.4']  # Google DNS as fallback

def test_dns_servers(servers: List[str]) -> Dict[str, Dict[str, Union[str, float]]]:
    """Test DNS servers response time."""
    print("[DEBUG] Testing DNS servers")
    results = {}
    for server in servers:
        try:
            print(f"[DEBUG] Testing DNS server: {server}")
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [server]
            resolver.timeout = 2
            resolver.lifetime = 2
            
            start_time = time.time()
            resolver.resolve('google.com', 'A')
            response_time = (time.time() - start_time) * 1000
            
            results[server] = {
                'Status': 'Online',
                'Response Time': f"{response_time:.2f}ms"
            }
            print(f"[DEBUG] DNS server {server} test successful")
        except Exception as e:
            print(f"[DEBUG] Error testing DNS server {server}: {str(e)}")
            results[server] = {
                'Status': 'Offline',
                'Error': str(e)
            }
    return results

def get_isp_info() -> Dict[str, str]:
    """Get ISP information using ipapi.co."""
    print("[DEBUG] Getting ISP information")
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        data = response.json()
        print("[DEBUG] ISP information retrieved successfully")
        return {
            'ISP': data.get('org', 'Não detectado'),
            'IP': data.get('ip', 'Não detectado'),
            'City': data.get('city', 'Não detectada'),
            'Region': data.get('region', 'Não detectada'),
            'Country': data.get('country_name', 'Não detectado')
        }
    except Exception as e:
        print(f"[DEBUG] Error getting ISP information: {str(e)}")
        return {
            'Error': f"Falha ao obter informações do ISP: {str(e)}"
        }

def get_internal_network_info() -> Dict[str, Any]:
    """Get internal network interface information."""
    print("[DEBUG] Getting internal network information")
    network_info = {}
    try:
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            try:
                print(f"[DEBUG] Analyzing interface: {interface}")
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    network_info[interface] = {
                        'IPv4': addrs[netifaces.AF_INET][0].get('addr', 'Não detectado'),
                        'Netmask': addrs[netifaces.AF_INET][0].get('netmask', 'Não detectada')
                    }
                    if 'broadcast' in addrs[netifaces.AF_INET][0]:
                        network_info[interface]['Broadcast'] = addrs[netifaces.AF_INET][0]['broadcast']
                print(f"[DEBUG] Interface {interface} analyzed successfully")
            except Exception as e:
                print(f"[DEBUG] Error analyzing interface {interface}: {str(e)}")
                network_info[interface] = {'Error': str(e)}
    except Exception as e:
        print(f"[DEBUG] Error getting network interfaces: {str(e)}")
        return {'Error': str(e)}
    return network_info

def ping_test(hosts: List[str]) -> Dict[str, Dict[str, Union[str, float]]]:
    """Test connectivity to multiple hosts."""
    print("[DEBUG] Starting ping tests")
    results = {}
    ping_param = '-n' if platform.system().lower() == 'windows' else '-c'
    
    for host in hosts:
        try:
            print(f"[DEBUG] Pinging host: {host}")
            cmd = ['ping', ping_param, '1', host]
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            response_time = (time.time() - start_time) * 1000
            
            if result.returncode == 0:
                results[host] = {
                    'Status': 'Online',
                    'Response Time': f"{response_time:.2f}ms"
                }
                print(f"[DEBUG] Ping to {host} successful")
            else:
                results[host] = {
                    'Status': 'Offline',
                    'Error': 'Host não alcançável'
                }
                print(f"[DEBUG] Ping to {host} failed")
        except Exception as e:
            print(f"[DEBUG] Error pinging {host}: {str(e)}")
            results[host] = {
                'Status': 'Erro',
                'Error': str(e)
            }
    return results

def network_performance_test() -> Dict[str, Union[str, float]]:
    """Test network download and upload speeds."""
    print("[DEBUG] Starting network performance test")
    try:
        st = speedtest.Speedtest()
        print("[DEBUG] Getting best server")
        st.get_best_server()
        
        print("[DEBUG] Testing download speed")
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        print(f"[DEBUG] Download speed: {download_speed:.2f} Mbps")
        
        print("[DEBUG] Testing upload speed")
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        print(f"[DEBUG] Upload speed: {upload_speed:.2f} Mbps")
        
        print("[DEBUG] Getting ping")
        ping = st.results.ping
        
        return {
            'Download': f"{download_speed:.2f} Mbps",
            'Upload': f"{upload_speed:.2f} Mbps",
            'Ping': f"{ping:.2f} ms"
        }
    except Exception as e:
        print(f"[DEBUG] Error in network performance test: {str(e)}")
        return {
            'Error': f"Falha ao realizar teste de velocidade: {str(e)}"
        }
