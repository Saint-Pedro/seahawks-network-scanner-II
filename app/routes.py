from flask import Blueprint, render_template, jsonify, request
import nmap
import socket
import platform
import os
import subprocess
import psutil
import ipaddress

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/system-info')
def get_system_info():
    hostname = socket.gethostname()
    
    # Récupération de toutes les interfaces réseau
    network_interfaces = []
    
    # Utilisation de psutil pour obtenir les infos détaillées sur les interfaces
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        # Ignorer les interfaces virtuelles ou non pertinentes comme Docker, VMware, etc.
        if interface_name.startswith(('vEthernet', 'VMware', 'docker', 'vboxnet')):
            continue
            
        interface_info = {
            'name': interface_name,
            'addresses': [],
            'status': 'down'  # Par défaut
        }
        
        # Vérifier si l'interface est active
        if interface_name in psutil.net_if_stats():
            stats = psutil.net_if_stats()[interface_name]
            interface_info['status'] = 'up' if stats.isup else 'down'
        
        # Récupérer les adresses IP (IPv4 et IPv6)
        for addr in interface_addresses:
            if addr.family == socket.AF_INET:  # IPv4
                try:
                    # Convertir en CIDR en utilisant le masque de sous-réseau
                    ip = addr.address
                    netmask = addr.netmask
                    if netmask:
                        # Convertir le masque en préfixe CIDR
                        prefix_length = ipaddress.IPv4Network(f'0.0.0.0/{netmask}', False).prefixlen
                        cidr = f"{ip}/{prefix_length}"
                    else:
                        cidr = f"{ip}/32"  # Default if no netmask
                        
                    interface_info['addresses'].append({
                        'type': 'IPv4',
                        'address': ip,
                        'cidr': cidr,
                        'netmask': netmask
                    })
                except Exception as e:
                    # En cas d'erreur, ajouter l'adresse sans CIDR
                    interface_info['addresses'].append({
                        'type': 'IPv4',
                        'address': addr.address,
                        'cidr': f"{addr.address}/unknown",
                        'netmask': addr.netmask
                    })
            elif addr.family == socket.AF_INET6:  # IPv6
                interface_info['addresses'].append({
                    'type': 'IPv6',
                    'address': addr.address
                })
        
        # Ajouter l'interface à la liste seulement si elle a des adresses
        if interface_info['addresses']:
            network_interfaces.append(interface_info)
    
    return jsonify({
        'hostname': hostname,
        'network_interfaces': network_interfaces
    })

@main.route('/api/scan', methods=['POST'])
def scan_network():
    try:
        # Récupérer toutes les interfaces réseau
        network_interfaces = []
        
        # Utilisation de psutil pour obtenir les infos détaillées sur les interfaces
        for interface_name, interface_addresses in psutil.net_if_addrs().items():
            # Ignorer les interfaces virtuelles ou non pertinentes
            if interface_name.startswith(('vEthernet', 'VMware', 'docker', 'vboxnet')):
                continue
                
            # Ne considérer que les interfaces actives
            if interface_name in psutil.net_if_stats() and psutil.net_if_stats()[interface_name].isup:
                # Ne récupérer que les adresses IPv4
                for addr in interface_addresses:
                    if addr.family == socket.AF_INET:
                        # Récupérer l'interface et son adresse IP
                        interface_info = {
                            'name': interface_name,
                            'ip': addr.address
                        }
                        network_interfaces.append(interface_info)
        
        # Scanner chaque interface réseau
        scanner = nmap.PortScanner()
        scan_results = []
        
        for interface in network_interfaces:
            local_ip = interface['ip']
            interface_name = interface['name']
            
            # Scanner uniquement cette interface
            scanner.scan(local_ip, arguments='-sS -F')  # Fast scan des ports courants
            
            # Collecter les informations
            device_info = {
                'interface_name': interface_name,
                'ip': local_ip,
                'hostname': socket.gethostname(),
                'status': 'up',
                'ports': []
            }
            
            # Récupérer les ports ouverts
            if local_ip in scanner.all_hosts():
                if 'tcp' in scanner[local_ip]:
                    for port, port_info in scanner[local_ip]['tcp'].items():
                        if port_info['state'] == 'open':
                            device_info['ports'].append({
                                'port': port,
                                'service': port_info['name']
                            })
            
            scan_results.append(device_info)

        return jsonify({
            'success': True,
            'devices': scan_results,
            'app_version': '1.1.0'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/ping/<ip>')
def ping_server(ip):
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', ip]
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        output = stdout.decode('cp850' if platform.system().lower() == 'windows' else 'utf-8')
        
        if process.returncode == 0:
            latency = None
            for line in output.split('\n'):
                # Version française "temps="
                if 'temps=' in line.lower():
                    try:
                        temps_str = line.split('temps=')[1].split('ms')[0].strip()
                        temps_str = temps_str.replace(',', '.')
                        latency = int(float(temps_str))
                        break
                    except:
                        continue
                
                # Version anglaise "time="
                elif 'time=' in line.lower():
                    try:
                        latency = float(line.split('time=')[1].split(' ms')[0].strip())
                        break
                    except:
                        continue

            return jsonify({
                'status': 'success',
                'message': 'Server reachable',
                'ip': ip,
                'latency': latency,
                'latency_unit': 'ms'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Server unreachable',
                'ip': ip
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500