// Global variables
let currentWorkflowId = null;
let extractedMetadata = {};
let processingInterval = null;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const statusSection = document.getElementById('statusSection');
const resultsSection = document.getElementById('resultsSection');
const loadingOverlay = document.getElementById('loadingOverlay');
const errorModal = document.getElementById('errorModal');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    console.log('Excel SourceSense initialized');
    initializeEventListeners();
});

// Event Listeners
function initializeEventListeners() {
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    if (uploadArea) {
        // Click to upload
        uploadArea.addEventListener('click', () => {
            if (fileInput) fileInput.click();
        });
        
        // Drag and drop events
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleFileDrop);
    }
}

// File handling functions
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        validateAndProcessFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleFileDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        validateAndProcessFile(files[0]);
    }
}

// File validation and processing
function validateAndProcessFile(file) {
    // Validate file type
    const allowedTypes = ['.xlsx', '.xls', '.csv'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
        showError('Invalid file type. Please upload .xlsx, .xls, or .csv files only.');
        return;
    }
    
    // Validate file size (50MB limit)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    if (file.size > maxSize) {
        showError('File size exceeds 50MB limit. Please choose a smaller file.');
        return;
    }
    
    // Process the file
    uploadFile(file);
}

// File upload function
async function uploadFile(file) {
    try {
        console.log('Starting file upload:', file.name);
        showProcessingStatus();
        
        const formData = new FormData();
        formData.append('file', file);
        
        updateProgress(25, 'Uploading file...');
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('Upload response:', result);
        
        if (result.success && result.result) {
            extractedMetadata = result.result;
            currentWorkflowId = result.workflow_id;
            
            updateProgress(100, 'Processing complete!');
            
            // Show results after brief delay
            setTimeout(() => {
                showResults();
            }, 1000);
        } else {
            throw new Error('Upload failed: ' + (result.message || 'Unknown error'));
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        hideProcessingStatus();
        showError(`Failed to upload file: ${error.message}`);
    }
}

// Load sample file
async function loadSampleFile(filename) {
    try {
        console.log('Loading sample file:', filename);
        showProcessingStatus();
        
        updateProgress(25, 'Loading sample file...');
        
        const response = await fetch(`/api/sample/${filename}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`Failed to load sample file: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('Sample file response:', result);
        
        if (result.success && result.result) {
            extractedMetadata = result.result;
            currentWorkflowId = result.workflow_id;
            
            updateProgress(100, 'Processing complete!');
            
            setTimeout(() => {
                showResults();
            }, 1000);
        } else {
            throw new Error('Failed to load sample file: ' + (result.message || 'Unknown error'));
        }
        
    } catch (error) {
        console.error('Sample file error:', error);
        hideProcessingStatus();
        showError(`Failed to load sample file: ${error.message}`);
    }
}

// Show processing status
function showProcessingStatus() {
    if (statusSection) {
        statusSection.style.display = 'block';
        statusSection.scrollIntoView({ behavior: 'smooth' });
        
        // Animate through steps
        setTimeout(() => updateProgress(25, 'Extracting metadata...'), 500);
        setTimeout(() => updateProgress(50, 'Analyzing data quality...'), 1000);
        setTimeout(() => updateProgress(75, 'Generating visualizations...'), 1500);
    }
}

function updateProgress(percentage, message) {
    const progressFill = document.getElementById('progressFill');
    const statusMessage = document.getElementById('statusMessage');
    
    if (progressFill) {
        progressFill.style.width = percentage + '%';
    }
    
    if (statusMessage && message) {
        statusMessage.textContent = message;
    }
    
    // Update step indicators
    const steps = ['step1', 'step2', 'step3', 'step4'];
    const stepThresholds = [25, 50, 75, 100];
    
    steps.forEach((stepId, index) => {
        const step = document.getElementById(stepId);
        if (step) {
            if (percentage >= stepThresholds[index]) {
                step.classList.remove('active');
                step.classList.add('completed');
                const icon = step.querySelector('i');
                if (icon) {
                    icon.className = 'fas fa-check-circle';
                }
            } else if (percentage >= (stepThresholds[index] - 25)) {
                step.classList.add('active');
            }
        }
    });
}

function hideProcessingStatus() {
    if (statusSection) {
        statusSection.style.display = 'none';
    }
}

// Show results
function showResults() {
    console.log('Showing results:', extractedMetadata);
    
    if (!extractedMetadata || Object.keys(extractedMetadata).length === 0) {
        showError('No metadata extracted from the file');
        return;
    }
    
    hideProcessingStatus();
    
    if (resultsSection) {
        resultsSection.style.display = 'block';
        resultsSection.classList.add('fade-in');
        
        // Populate all sections
        displayFileOverview();
        displaySchemaInformation();
        displayDataQuality();
        displayVisualizations();
        
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Display file overview
function displayFileOverview() {
    const container = document.getElementById('fileOverview');
    if (!container || !extractedMetadata.database_info) {
        console.log('No file overview container or data');
        return;
    }
    
    const data = extractedMetadata.database_info;
    console.log('Database info:', data);
    
    container.innerHTML = `
        <div class="overview-item">
            <i class="fas fa-file"></i>
            <h4>File Name</h4>
            <p>${data.database_name || 'Unknown'}</p>
        </div>
        <div class="overview-item">
            <i class="fas fa-hdd"></i>
            <h4>File Size</h4>
            <p>${formatFileSize(data.file_size || 0)}</p>
        </div>
        <div class="overview-item">
            <i class="fas fa-table"></i>
            <h4>Sheets</h4>
            <p>${data.sheet_count || 0}</p>
        </div>
        <div class="overview-item">
            <i class="fas fa-clock"></i>
            <h4>Modified</h4>
            <p>${formatDate(data.modified_date)}</p>
        </div>
    `;
}

// Display schema information
function displaySchemaInformation() {
    displayTables();
    displayColumns();
}

// Display tables
function displayTables() {
    const container = document.getElementById('tablesGrid');
    if (!container || !extractedMetadata.tables_info) {
        console.log('No tables container or data');
        return;
    }
    
    const tables = extractedMetadata.tables_info;
    console.log('Tables info:', tables);
    
    container.innerHTML = tables.map(table => `
        <div class="table-card">
            <div class="table-name">
                <i class="fas fa-table"></i>
                ${table.table_name}
            </div>
            <div class="table-stats">
                <div class="stat-item">
                    <div class="stat-value">${table.row_count || 0}</div>
                    <div class="stat-label">Rows</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${table.column_count || 0}</div>
                    <div class="stat-label">Columns</div>
                </div>
            </div>
        </div>
    `).join('');
}

// Display columns
function displayColumns() {
    const container = document.getElementById('columnsTable');
    if (!container || !extractedMetadata.columns_info) {
        console.log('No columns container or data');
        return;
    }
    
    const columns = extractedMetadata.columns_info;
    console.log('Columns info:', columns);
    
    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Table</th>
                    <th>Column Name</th>
                    <th>Data Type</th>
                    <th>Nullable</th>
                    <th>Unique %</th>
                    <th>Null %</th>
                    <th>Quality</th>
                </tr>
            </thead>
            <tbody>
                ${columns.map(col => `
                    <tr>
                        <td>${col.table_name}</td>
                        <td>${col.column_name}</td>
                        <td><span class="data-type-${col.data_type.toLowerCase()}">${col.data_type}</span></td>
                        <td>${col.is_nullable}</td>
                        <td>${col.unique_percentage || 0}%</td>
                        <td>${col.null_percentage || 0}%</td>
                        <td><span class="quality-${(col.quality_level || 'medium').toLowerCase()}">${col.quality_level || 'MEDIUM'}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Display data quality
function displayDataQuality() {
    const container = document.getElementById('qualityMetrics');
    if (!container || !extractedMetadata.columns_info) {
        console.log('No quality container or data');
        return;
    }
    
    const columns = extractedMetadata.columns_info;
    const totalColumns = columns.length;
    const highQuality = columns.filter(col => (col.quality_level || 'MEDIUM') === 'HIGH').length;
    const mediumQuality = columns.filter(col => (col.quality_level || 'MEDIUM') === 'MEDIUM').length;
    const lowQuality = columns.filter(col => (col.quality_level || 'MEDIUM') === 'LOW').length;
    
    const avgNullPercentage = totalColumns > 0 ? 
        columns.reduce((sum, col) => sum + (col.null_percentage || 0), 0) / totalColumns : 0;
    const avgUniquePercentage = totalColumns > 0 ? 
        columns.reduce((sum, col) => sum + (col.unique_percentage || 0), 0) / totalColumns : 0;
    
    const overallScore = totalColumns > 0 ? 
        Math.round((highQuality * 100 + mediumQuality * 70 + lowQuality * 30) / totalColumns) : 0;
    
    container.innerHTML = `
        <div class="quality-item ${getQualityClass(overallScore)}">
            <div class="quality-score ${getQualityClass(overallScore)}">${overallScore}%</div>
            <h4>Overall Quality</h4>
        </div>
        <div class="quality-item">
            <div class="quality-score high">${highQuality}</div>
            <h4>High Quality Columns</h4>
        </div>
        <div class="quality-item">
            <div class="quality-score medium">${mediumQuality}</div>
            <h4>Medium Quality Columns</h4>
        </div>
        <div class="quality-item">
            <div class="quality-score low">${lowQuality}</div>
            <h4>Low Quality Columns</h4>
        </div>
        <div class="quality-item">
            <div class="quality-score">${avgNullPercentage.toFixed(1)}%</div>
            <h4>Avg Null Percentage</h4>
        </div>
        <div class="quality-item">
            <div class="quality-score">${avgUniquePercentage.toFixed(1)}%</div>
            <h4>Avg Uniqueness</h4>
        </div>
    `;
}

// Display visualizations
function displayVisualizations() {
    const container = document.getElementById('visualizations');
    if (!container) {
        console.log('No visualizations container');
        return;
    }
    
    const visualizations = extractedMetadata.visualizations || [];
    console.log('Visualizations:', visualizations);
    
    if (visualizations.length === 0) {
        container.innerHTML = `
            <div class="viz-container">
                <p style="text-align: center; color: #6c757d; padding: 40px;">
                    <i class="fas fa-chart-bar" style="font-size: 2rem; margin-bottom: 10px;"></i><br>
                    No visualizations generated
                </p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = visualizations.map((viz, index) => `
        <div class="viz-container">
            <div class="viz-title">${viz.title}</div>
            <div id="chart-${index}" class="chart-container"></div>
        </div>
    `).join('');
    
    // Create charts with Plotly
    visualizations.forEach((viz, index) => {
        setTimeout(() => createInteractiveChart(viz, `chart-${index}`), 100 * index);
    });
}

// Create interactive charts with Plotly
function createInteractiveChart(vizData, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    console.log('Creating chart:', vizData.type, 'for', containerId);
    
    try {
        if (typeof Plotly !== 'undefined') {
            if (vizData.type === 'bar_chart') {
                const data = [{
                    x: vizData.data.columns,
                    y: vizData.data.null_counts,
                    type: 'bar',
                    marker: {
                        color: 'rgba(102, 126, 234, 0.7)',
                        line: {
                            color: 'rgba(102, 126, 234, 1)',
                            width: 1
                        }
                    },
                    name: 'Null Counts'
                }];
                
                const layout = {
                    title: false,
                    xaxis: { 
                        title: 'Columns',
                        tickangle: -45
                    },
                    yaxis: { title: 'Null Count' },
                    margin: { t: 20, r: 20, b: 100, l: 50 },
                    height: 400,
                    showlegend: false,
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    paper_bgcolor: 'rgba(0,0,0,0)'
                };
                
                const config = {
                    responsive: true,
                    displayModeBar: false
                };
                
                Plotly.newPlot(containerId, data, layout, config);
                
            } else if (vizData.type === 'pie_chart') {
                const data = [{
                    labels: vizData.data.labels,
                    values: vizData.data.values,
                    type: 'pie',
                    marker: {
                        colors: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00c9ff']
                    },
                    textinfo: 'label+percent',
                    textposition: 'outside'
                }];
                
                const layout = {
                    title: false,
                    margin: { t: 20, r: 20, b: 20, l: 20 },
                    height: 400,
                    showlegend: true,
                    legend: {
                        orientation: 'v',
                        x: 1.05,
                        y: 0.5
                    },
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    paper_bgcolor: 'rgba(0,0,0,0)'
                };
                
                const config = {
                    responsive: true,
                    displayModeBar: false
                };
                
                Plotly.newPlot(containerId, data, layout, config);
                
            } else if (vizData.type === 'heatmap') {
                const stats = vizData.data.statistics;
                const columns = vizData.data.columns;
                
                if (columns.length > 0 && stats[columns[0]]) {
                    const statNames = Object.keys(stats[columns[0]]);
                    
                    const zValues = statNames.map(stat => 
                        columns.map(col => stats[col] ? (stats[col][stat] || 0) : 0)
                    );
                    
                    const data = [{
                        z: zValues,
                        x: columns,
                        y: statNames,
                        type: 'heatmap',
                        colorscale: 'Viridis',
                        showscale: true
                    }];
                    
                    const layout = {
                        title: false,
                        xaxis: { 
                            title: 'Columns',
                            tickangle: -45
                        },
                        yaxis: { title: 'Statistics' },
                        margin: { t: 20, r: 50, b: 100, l: 100 },
                        height: 400,
                        plot_bgcolor: 'rgba(0,0,0,0)',
                        paper_bgcolor: 'rgba(0,0,0,0)'
                    };
                    
                    const config = {
                        responsive: true,
                        displayModeBar: false
                    };
                    
                    Plotly.newPlot(containerId, data, layout, config);
                } else {
                    container.innerHTML = `
                        <div style="padding: 40px; text-align: center; color: #6c757d;">
                            <i class="fas fa-chart-area" style="font-size: 2rem; margin-bottom: 10px;"></i><br>
                            No numeric data available for heatmap
                        </div>
                    `;
                }
            }
        } else {
            // Fallback if Plotly is not available
            container.innerHTML = `
                <div style="padding: 40px; text-align: center; background: #f8f9fa; border-radius: 8px;">
                    <i class="fas fa-chart-${vizData.type === 'bar_chart' ? 'bar' : vizData.type === 'pie_chart' ? 'pie' : 'area'}" style="font-size: 2rem; color: #667eea; margin-bottom: 15px;"></i>
                    <h4>${vizData.title}</h4>
                    <p>Chart type: ${vizData.type}</p>
                    <p><em>Loading interactive chart...</em></p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error creating chart:', error);
        container.innerHTML = `
            <div style="padding: 40px; text-align: center; color: #dc3545;">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 10px;"></i><br>
                Error loading chart
            </div>
        `;
    }
}

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    const targetPane = document.getElementById(`${tabName}Content`);
    if (targetPane) {
        targetPane.classList.add('active');
    }
}

// Export metadata
async function exportMetadata(format) {
    try {
        if (!extractedMetadata || Object.keys(extractedMetadata).length === 0) {
            showError('No metadata available to export');
            return;
        }
        
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                metadata: extractedMetadata,
                format: format
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Create downloadable file
            const mimeType = format === 'json' ? 'application/json' : 'text/csv';
            const blob = new Blob([data.content], { type: mimeType });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `metadata_export.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            // Show success message
            console.log(`Metadata exported as ${format}`);
        } else {
            showError('Export failed');
        }
        
    } catch (error) {
        showError('Export failed: ' + error.message);
    }
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (error) {
        return 'Invalid Date';
    }
}

function getQualityClass(score) {
    if (score >= 80) return 'high';
    if (score >= 60) return 'medium';
    return 'low';
}

function showError(message) {
    console.error('Error:', message);
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv && errorModal) {
        errorDiv.textContent = message;
        errorModal.style.display = 'flex';
    } else {
        alert(message); // Fallback
    }
}

function closeModal() {
    if (errorModal) {
        errorModal.style.display = 'none';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target === errorModal) {
        closeModal();
    }
}

// Add some loading animations
function addLoadingAnimation(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.opacity = '0.5';
        element.style.transition = 'opacity 0.3s ease';
    }
}

function removeLoadingAnimation(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.opacity = '1';
    }
}

// Console log for debugging
console.log('Excel SourceSense script loaded successfully');
