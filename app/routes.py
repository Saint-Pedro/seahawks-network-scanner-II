from flask import Blueprint, render_template, jsonify
import nmap
import socket
import platform
import os
import subprocess

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/system-info')
def get_system_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return jsonify({
        'hostname': hostname,
        'ip_address': ip_address
    })

@main.route('/api/scan', methods=['POST'])
def scan_network():
    try:
        # Obtenir l'IP locale
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        # Scanner uniquement la machine locale
        scanner = nmap.PortScanner()
        scanner.scan(local_ip, arguments='-sS -F')  # Fast scan des ports courants

        # Collecter les informations
        device_info = {
            'ip': local_ip,
            'hostname': hostname,
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

        return jsonify({
            'success': True,
            'device': device_info,
            'app_version': '1.0.0'
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