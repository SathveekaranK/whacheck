// Tab Switching
const tabs = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const targetTab = tab.dataset.tab;

        // Update active tab
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Update active content
        tabContents.forEach(content => content.classList.remove('active'));
        document.getElementById(`${targetTab}-tab`).classList.add('active');
    });
});

// Single Validation
const validateBtn = document.getElementById('validateBtn');
const phoneInput = document.getElementById('phoneInput');
const countryInput = document.getElementById('countryInput');
const singleResults = document.getElementById('singleResults');

validateBtn.addEventListener('click', async () => {
    const phone = phoneInput.value.trim();
    const country = countryInput.value;

    if (!phone) {
        alert('Please enter a phone number');
        return;
    }

    // Show loading state
    validateBtn.disabled = true;
    validateBtn.innerHTML = '<span>Validating...</span><span class="btn-icon">⏳</span>';

    try {
        const response = await fetch('/api/v1/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                phone_number: phone,
                country_code: country,
                context: {
                    user_id: 'web_user',
                    source: 'web_ui'
                }
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            displaySingleResults(data);
        } else {
            alert('Validation failed: ' + (data.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error(error);
        alert('Network error. Please try again.');
    } finally {
        validateBtn.disabled = false;
        validateBtn.innerHTML = '<span>Validate Now</span><span class="btn-icon">→</span>';
    }
});

function displaySingleResults(data) {
    // Show results container
    singleResults.style.display = 'block';
    singleResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Status badge
    const statusBadge = document.getElementById('statusBadge');
    if (data.success) {
        statusBadge.textContent = '✓ Valid';
        statusBadge.className = 'status-badge success';
    } else {
        statusBadge.textContent = '✗ Invalid';
        statusBadge.className = 'status-badge error';
    }

    // Confidence score
    const score = data.confidence_score || 0;
    document.getElementById('confidenceScore').textContent = score.toFixed(0);
    document.getElementById('scoreFill').style.width = score + '%';

    // Result values
    document.getElementById('formattedNumber').textContent = data.formatted_number || 'N/A';
    document.getElementById('country').textContent = data.country_code || 'N/A';
    document.getElementById('carrier').textContent = data.carrier || 'N/A';
    document.getElementById('lineType').textContent = data.line_type || 'N/A';
    document.getElementById('whatsapp').textContent = data.whatsapp_available ? '✓ Yes' : '✗ No';
    document.getElementById('accountType').textContent = data.account_type || 'N/A';

    // Reasoning
    document.getElementById('reasoning').textContent = data.reasoning || 'No reasoning provided';

    // Metadata
    const processingTime = data.metadata?.processing_time_ms;
    document.getElementById('processingTime').textContent = processingTime ? `${processingTime.toFixed(0)}ms` : 'N/A';
    document.getElementById('strategy').textContent = data.validation_strategy || 'N/A';
}

// Batch Upload
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const statusText = document.getElementById('statusText');
const batchResults = document.getElementById('batchResults');
let currentBatchData = null;

// Drag and drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length) handleFile(files[0]);
});

dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

async function handleFile(file) {
    if (!file.name.endsWith('.csv')) {
        alert('Please upload a CSV file');
        return;
    }

    // Update UI
    document.querySelector('.drop-text').textContent = file.name;
    progressContainer.style.display = 'block';
    batchResults.style.display = 'none';

    // Animated progress (simulated)
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressBar.style.width = progress + '%';
    }, 300);

    // Upload CSV
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/v1/validate/batch', {
            method: 'POST',
            body: formData
        });

        clearInterval(interval);
        progressBar.style.width = '100%';

        if (response.ok) {
            statusText.textContent = '✓ Validation Complete!';
            const csvText = await response.text();
            currentBatchData = csvText;
            displayBatchResults(csvText);
        } else {
            statusText.textContent = '✗ Error processing file';
            progressBar.style.background = 'var(--danger)';
        }
    } catch (error) {
        console.error(error);
        clearInterval(interval);
        statusText.textContent = '✗ Network error';
        progressBar.style.background = 'var(--danger)';
    }
}

function displayBatchResults(csvText) {
    // Parse CSV
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',');
    const rows = lines.slice(1);

    // Build table
    const tableBody = document.getElementById('tableBody');
    tableBody.innerHTML = '';

    rows.forEach((row, index) => {
        if (!row.trim()) return;

        const cells = parseCSVLine(row);
        const tr = document.createElement('tr');

        // Extract key fields (adjust indices based on your CSV structure)
        const phone = cells[0] || '';
        const formatted = cells[1] || '';
        const country = cells[4] || '';
        const carrier = cells[3] || '';
        const whatsapp = cells[5] || '';
        const confidence = parseFloat(cells[6]) || 0;

        // Build row
        tr.innerHTML = `
            <td>${phone.replace(/'/g, '')}</td>
            <td>${formatted}</td>
            <td>${country}</td>
            <td>${carrier}</td>
            <td>${whatsapp === 'True' || whatsapp === 'TRUE' ? '✓ Yes' : '✗ No'}</td>
            <td>
                <div class="confidence-cell">
                    <span class="confidence-dot ${getConfidenceClass(confidence)}"></span>
                    ${confidence.toFixed(0)}%
                </div>
            </td>
        `;

        tableBody.appendChild(tr);
    });

    // Show results
    batchResults.style.display = 'block';
    batchResults.scrollIntoView({ behavior: 'smooth' });
}

function parseCSVLine(line) {
    // Simple CSV parser that handles quoted fields
    const result = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];

        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current);

    return result;
}

function getConfidenceClass(score) {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
}

// Download CSV
document.getElementById('downloadBtn').addEventListener('click', () => {
    if (!currentBatchData) return;

    const blob = new Blob([currentBatchData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'validation_results_' + new Date().toISOString().split('T')[0] + '.csv';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
});
