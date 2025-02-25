async function startScan() {
    const button = document.getElementById('scan-btn');
    const results = document.getElementById('results-content');
    
    button.disabled = true;
    button.textContent = 'Scanning...';
    
    try {
        const response = await fetch('/api/scan', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        results.innerHTML = `<p class="error">Error during scan: ${error.message}</p>`;
    } finally {
        button.disabled = false;
        button.textContent = 'Start Network Scan';
    }
}

function displayResults(data) {
    const results = document.getElementById('results-content');
    
    // Si aucune interface n'a été trouvée
    if (data.devices.length === 0) {
        results.innerHTML = `<p>No active network interfaces found</p>`;
        return;
    }
    
    // Créer le HTML pour afficher les résultats de chaque interface
    let html = `<div class="scan-summary">
        <h3>Network Scan Results</h3>
        <p>App Version: ${data.app_version}</p>`;
    
    // Pour chaque interface réseau
    data.devices.forEach(device => {
        html += `
        <div class="interface-result">
            <h4>Interface: ${device.interface_name}</h4>
            <p>IP Address: ${device.ip}</p>
            
            <h5>Open Ports:</h5>
            ${device.ports.length > 0 ? `
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Port</th>
                            <th>Service</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${device.ports.map(port => `
                            <tr>
                                <td>${port.port}</td>
                                <td>${port.service}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : '<p>No open ports found</p>'}
        </div>
        <hr>`;
    });
    
    html += `</div>`;
    results.innerHTML = html;
}

// Charger les informations système au chargement de la page
window.addEventListener('load', async () => {
    await loadSystemInfo();
});

async function loadSystemInfo() {
    try {
        const response = await fetch('/api/system-info');
        const data = await response.json();
        
        // Afficher le nom d'hôte
        document.getElementById('hostname').textContent = data.hostname;
        
        // Afficher les interfaces réseau
        const interfacesContainer = document.getElementById('interfaces-list');
        
        if (data.network_interfaces.length === 0) {
            interfacesContainer.innerHTML = '<p>No network interfaces found</p>';
            return;
        }
        
        let interfacesHtml = '';
        
        // Pour chaque interface réseau
        data.network_interfaces.forEach(interface => {
            const statusClass = interface.status === 'up' ? 'status-up' : 'status-down';
            
            interfacesHtml += `
            <div class="interface-card">
                <div class="interface-header">
                    <h4>${interface.name}</h4>
                    <span class="status ${statusClass}">${interface.status}</span>
                </div>
                
                <div class="interface-addresses">
                    ${interface.addresses.map(addr => {
                        if (addr.type === 'IPv4') {
                            return `
                            <div class="address-item">
                                <span class="address-type">${addr.type}:</span>
                                <span class="address-value">${addr.address}</span>
                                <span class="address-cidr">(${addr.cidr})</span>
                            </div>`;
                        } else {
                            return `
                            <div class="address-item">
                                <span class="address-type">${addr.type}:</span>
                                <span class="address-value">${addr.address}</span>
                            </div>`;
                        }
                    }).join('')}
                </div>
            </div>`;
        });
        
        interfacesContainer.innerHTML = interfacesHtml;
    } catch (error) {
        console.error('Error loading system info:', error);
        document.getElementById('interfaces-list').innerHTML = 
            `<p class="error">Error loading network interfaces: ${error.message}</p>`;
    }
}

async function pingServer() {
    const serverIP = document.getElementById('server-ip').value;
    const resultDiv = document.getElementById('ping-result');
    
    // Validation basique de l'IP
    if (!serverIP) {
        resultDiv.innerHTML = '<div class="result-error">Please enter an IP</div>';
        return;
    }
    
    try {
        resultDiv.innerHTML = '<div>Test in progress...</div>';
        const response = await fetch(`/api/ping/${serverIP}`);
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <div class="result-success">
                    ✓ ${data.message} (${data.ip})
                    ${data.latency !== null ? `<br>Latency: ${data.latency} ${data.latency_unit}` : ''}
                </div>`;
        } else {
            resultDiv.innerHTML = `
                <div class="result-error">
                    ✗ ${data.message} (${data.ip})
                </div>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="result-error">
                Test Error : ${error.message}
            </div>`;
    }
}