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
    
    const html = `
        <div class="scan-summary">
            <h3>Local Machine Scan Results</h3>
            <p>IP Address: ${data.device.ip}</p>
            <p>Hostname: ${data.device.hostname}</p>
            <p>App Version: ${data.app_version}</p>
            
            <h4>Open Ports:</h4>
            ${data.device.ports.length > 0 ? `
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Port</th>
                            <th>Service</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.device.ports.map(port => `
                            <tr>
                                <td>${port.port}</td>
                                <td>${port.service}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : '<p>No open ports found</p>'}
        </div>
    `;
    
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
        
        document.getElementById('ip-address').textContent = data.ip_address;
        document.getElementById('hostname').textContent = data.hostname;
    } catch (error) {
        console.error('Error loading system info:', error);
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