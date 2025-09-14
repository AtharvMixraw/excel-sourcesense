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
        uploadArea.addEventListener('click', () => {
            if (fileInput) fileInput.click();
        });
        
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

function validateAndProcessFile(file) {
    const allowedTypes = ['.xlsx', '.xls', '.csv'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
        showError('Invalid file type. Please upload .xlsx, .xls, or .csv files only.');
        return;
    }
    
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
        showError('File size exceeds 50MB limit. Please choose a smaller file.');
        return;
    }
    
    uploadFile(file);
}

// File upload function - WITH TEMPORAL INTEGRATION
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
            
            // IMPORTANT: Store temporal info at the TOP LEVEL of extractedMetadata
            extractedMetadata.temporal_available = result.temporal_available;
            extractedMetadata.temporal_dashboard_url = result.temporal_dashboard_url;
            
            console.log('Stored workflow data:', {
                workflow_id: currentWorkflowId,
                temporal_available: extractedMetadata.temporal_available,
                temporal_url: extractedMetadata.temporal_dashboard_url
            });
            
            updateProgress(100, 'Processing complete!');
            
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

// Load sample file - WITH TEMPORAL INTEGRATION
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
            
            // IMPORTANT: Store temporal info at the TOP LEVEL of extractedMetadata  
            extractedMetadata.temporal_available = result.temporal_available;
            extractedMetadata.temporal_dashboard_url = result.temporal_dashboard_url;
            
            console.log('Stored sample workflow data:', {
                workflow_id: currentWorkflowId,
                temporal_available: extractedMetadata.temporal_available,
                temporal_url: extractedMetadata.temporal_dashboard_url
            });
            
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

// Show results - WITH TEMPORAL INTEGRATION
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

        // IMPORTANT: Show temporal card FIRST before populating other sections
        const temporalCard = document.getElementById('temporalCard');
        if (temporalCard && currentWorkflowId) {
            temporalCard.style.display = 'block';  // Make sure it's visible
            
            console.log('Showing temporal card for workflow:', currentWorkflowId);
            
            // Display temporal info immediately
            displayTemporalInfo({
                workflow_id: currentWorkflowId,
                temporal_dashboard_url: extractedMetadata.temporal_dashboard_url || `http://localhost:8233/namespaces/default/workflows/${currentWorkflowId}`,
                temporal_available: extractedMetadata.temporal_available || false
            });
        } else {
            console.log('Temporal card or workflow ID not found:', { temporalCard, currentWorkflowId });
        }

        // Populate all other sections
        displayFileOverview();
        displaySchemaInformation();
        displayBusinessContext();
        displayLineage();
        displayDataQuality();
        displayVisualizations();

        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Display Temporal Dashboard Info - ENHANCED FROM FIRST VERSION
function displayTemporalInfo(data) {
    const temporalInfo = document.getElementById('temporalInfo');
    if (!temporalInfo) {
        console.error('temporalInfo div not found!');
        return;
    }
    
    console.log('Displaying temporal info:', data);
    console.log('temporalInfo element found:', temporalInfo);
    
    if (data.temporal_available) {
        console.log('Temporal server available - showing full dashboard');
        temporalInfo.innerHTML = `
            <div class="temporal-dashboard">
                <div class="workflow-details">
                    <p><strong>Workflow ID:</strong> <code>${data.workflow_id}</code></p>
                    <p><strong>Status:</strong> <span class="status-badge running">Running</span></p>
                </div>
                <div class="dashboard-actions">
                    <a href="${data.temporal_dashboard_url}" target="_blank" class="btn btn-primary">
                        <i class="fas fa-external-link-alt"></i> Open Temporal Dashboard
                    </a>
                    <button onclick="refreshWorkflowStatus('${data.workflow_id}')" class="btn btn-secondary">
                        <i class="fas fa-sync"></i> Refresh Status
                    </button>
                </div>
            </div>
        `;
    } else {
        console.log('Temporal server not available - showing fallback');
        temporalInfo.innerHTML = `
            <div class="temporal-fallback">
                <div class="workflow-details">
                    <p><strong>Workflow ID:</strong> <code>${data.workflow_id}</code></p>
                    <p><strong>Status:</strong> <span class="status-badge completed">Simulated</span></p>
                </div>
                <div class="info-message">
                    <p><i class="fas fa-info-circle"></i> 
                    Temporal server not running. To enable real-time monitoring:</p>
                    <code>temporal server start-dev --ui-port 8233</code>
                </div>
                <a href="${data.temporal_dashboard_url}" target="_blank" class="btn btn-outline-primary" style="pointer-events: none; opacity: 0.6;">
                    Dashboard (Requires Temporal Server)
                </a>
            </div>
        `;
    }
    
    console.log('Temporal info updated in DOM');
}

// Refresh workflow status - FROM FIRST VERSION
async function refreshWorkflowStatus(workflowId) {
    try {
        const response = await fetch(`/api/workflow/${workflowId}/status`);
        const status = await response.json();
        
        console.log('Workflow status:', status);
        
        // Update status display
        const statusBadge = document.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.textContent = status.status.charAt(0).toUpperCase() + status.status.slice(1);
            statusBadge.className = `status-badge ${status.completed ? 'completed' : 'running'}`;
        }
        
        showToast(`Workflow ${status.status}`, status.completed ? 'success' : 'info');
        
    } catch (error) {
        console.error('Failed to refresh status:', error);
        showToast('Failed to refresh status', 'error');
    }
}

// Business context editing - ENHANCED FROM SECOND VERSION
function displayBusinessContext() {
    const container = document.getElementById('businessContext');
    if (!container) return;
    
    const columns = extractedMetadata.columns_info || [];
    if (columns.length === 0) {
        container.innerHTML = '<p>No column information available for business context.</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="business-context-intro">
            <p>Add business descriptions and tags to enhance metadata value:</p>
        </div>
        <div class="context-grid">
            ${columns.map((col, index) => `
                <div class="context-row">
                    <div class="column-info">
                        <strong>${col.column_name}</strong>
                        <span class="table-name">(${col.table_name})</span>
                        <span class="data-type">${col.data_type}</span>
                    </div>
                    <div class="context-inputs">
                        <div class="input-group">
                            <label>Description:</label>
                            <input type="text" 
                                   data-col="${col.column_name}" 
                                   data-table="${col.table_name}"
                                   class="desc-input" 
                                   value="${col.description || ''}"
                                   placeholder="Add business description...">
                        </div>
                        <div class="input-group">
                            <label>Tags:</label>
                            <input type="text" 
                                   data-col="${col.column_name}" 
                                   data-table="${col.table_name}"
                                   class="tags-input" 
                                   value="${col.tags ? (Array.isArray(col.tags) ? col.tags.join(', ') : col.tags) : ''}"
                                   placeholder="PII, Critical, Customer Data...">
                        </div>
                        <div class="input-group">
                            <label>Business Owner:</label>
                            <input type="text" 
                                   data-col="${col.column_name}" 
                                   data-table="${col.table_name}"
                                   class="owner-input" 
                                   value="${col.owner || ''}"
                                   placeholder="Team or person responsible...">
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
        <div class="context-actions">
            <button class="save-context-btn" onclick="saveBusinessContext()">
                <i class="fas fa-save"></i> Save Business Context
            </button>
            <button class="reset-context-btn" onclick="resetBusinessContext()">
                <i class="fas fa-undo"></i> Reset
            </button>
        </div>
    `;
}

function saveBusinessContext() {
    const columns = extractedMetadata.columns_info || [];
    
    // Update metadata with business context
    document.querySelectorAll('.desc-input').forEach(input => {
        const colName = input.dataset.col;
        const tableName = input.dataset.table;
        const col = columns.find(c => c.column_name === colName && c.table_name === tableName);
        if (col) {
            col.description = input.value.trim();
        }
    });
    
    document.querySelectorAll('.tags-input').forEach(input => {
        const colName = input.dataset.col;
        const tableName = input.dataset.table;
        const col = columns.find(c => c.column_name === colName && c.table_name === tableName);
        if (col) {
            col.tags = input.value.split(',').map(t => t.trim()).filter(t => t.length > 0);
        }
    });
    
    document.querySelectorAll('.owner-input').forEach(input => {
        const colName = input.dataset.col;
        const tableName = input.dataset.table;
        const col = columns.find(c => c.column_name === colName && c.table_name === tableName);
        if (col) {
            col.owner = input.value.trim();
        }
    });
    
    // Show success message
    showSuccessMessage('Business context saved successfully!');
    
    // Refresh displays
    displayColumns();
}

function resetBusinessContext() {
    if (confirm('Are you sure you want to reset all business context changes?')) {
        displayBusinessContext();
    }
}

// Enhanced lineage detection - FROM SECOND VERSION
function detectRelationships() {
    const columns = extractedMetadata.columns_info || [];
    if (columns.length === 0) return [];
    
    let relationships = [];
    
    // Method 1: Exact column name matches across different tables
    columns.forEach((colA, idxA) => {
        columns.forEach((colB, idxB) => {
            if (idxA !== idxB && 
                colA.column_name.toLowerCase() === colB.column_name.toLowerCase() && 
                colA.table_name !== colB.table_name) {
                relationships.push({
                    from: `${colA.table_name}.${colA.column_name}`,
                    to: `${colB.table_name}.${colB.column_name}`,
                    type: 'exact_match',
                    strength: 'high'
                });
            }
        });
    });
    
    // Method 2: Similar column names (fuzzy matching)
    columns.forEach((colA, idxA) => {
        columns.forEach((colB, idxB) => {
            if (idxA !== idxB && colA.table_name !== colB.table_name) {
                const similarity = calculateStringSimilarity(
                    colA.column_name.toLowerCase(), 
                    colB.column_name.toLowerCase()
                );
                
                if (similarity > 0.7 && similarity < 1.0) {
                    relationships.push({
                        from: `${colA.table_name}.${colA.column_name}`,
                        to: `${colB.table_name}.${colB.column_name}`,
                        type: 'similar_name',
                        strength: 'medium',
                        similarity: similarity
                    });
                }
            }
        });
    });
    
    // Remove duplicates and sort by strength
    const uniqueRelationships = relationships.filter((rel, index, self) => 
        index === self.findIndex(r => r.from === rel.from && r.to === rel.to)
    );
    
    return uniqueRelationships.sort((a, b) => {
        const strengthOrder = { 'high': 3, 'medium': 2, 'low': 1 };
        return strengthOrder[b.strength] - strengthOrder[a.strength];
    });
}

// Enhanced lineage display with visualization - FROM SECOND VERSION
function displayLineage() {
    const container = document.getElementById('lineageViz');
    if (!container) {
        console.log('Lineage container not found');
        return;
    }
    
    const relationships = detectRelationships();
    console.log('Detected relationships:', relationships);
    
    if (relationships.length === 0) {
        container.innerHTML = `
            <div class="lineage-empty">
                <i class="fas fa-project-diagram"></i>
                <p>No column relationships detected.</p>
                <p><small>Relationships are detected based on column name similarities across tables.</small></p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="lineage-header">
            <p>Found ${relationships.length} potential relationship(s) between columns:</p>
        </div>
        <div class="relationships-list">
            ${relationships.map(rel => `
                <div class="relationship-item ${rel.strength}">
                    <div class="relationship-info">
                        <span class="from">${rel.from}</span>
                        <i class="fas fa-arrow-right"></i>
                        <span class="to">${rel.to}</span>
                    </div>
                    <div class="relationship-meta">
                        <span class="type">${rel.type.replace('_', ' ')}</span>
                        <span class="strength ${rel.strength}">${rel.strength}</span>
                        ${rel.similarity ? `<span class="similarity">${Math.round(rel.similarity * 100)}% similar</span>` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
        <div class="lineage-visualization">
            <h4>Visual Representation</h4>
            <div class="lineage-graph-container">
                <svg id="lineageGraph"></svg>
            </div>
        </div>
    `;
    
    // Try to load D3 and render graph
    setTimeout(() => {
        loadD3AndRenderLineage(relationships);
    }, 100);
}

function loadD3AndRenderLineage(relationships) {
    // Check if D3 is available
    if (typeof d3 === "undefined") {
        console.log('D3 not available, loading from CDN...');
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js';
        script.onload = () => {
            console.log('D3 loaded, rendering graph...');
            renderLineageGraph(relationships);
        };
        script.onerror = () => {
            console.error('Failed to load D3, showing fallback...');
            showLineageFallback(relationships);
        };
        document.head.appendChild(script);
    } else {
        console.log('D3 available, rendering graph...');
        renderLineageGraph(relationships);
    }
}

function renderLineageGraph(edges) {
    try {
        console.log('Rendering lineage graph with', edges.length, 'edges');
        
        // Prepare nodes and links
        let nodeMap = {};
        let links = [];
        
        edges.forEach((rel) => {
            const fromTable = rel.from.split('.')[0];
            const toTable = rel.to.split('.')[0];
            
            nodeMap[rel.from] = { 
                id: rel.from, 
                group: fromTable,
                table: fromTable,
                column: rel.from.split('.')[1]
            };
            nodeMap[rel.to] = { 
                id: rel.to, 
                group: toTable,
                table: toTable,
                column: rel.to.split('.')[1]
            };
            
            links.push({
                source: rel.from,
                target: rel.to,
                strength: rel.strength,
                type: rel.type
            });
        });
        
        const nodes = Object.values(nodeMap);
        console.log('Nodes:', nodes.length, 'Links:', links.length);
        
        // Get container dimensions
        const container = document.querySelector('.lineage-graph-container');
        if (!container) {
            console.error('Graph container not found');
            return;
        }
        
        const containerRect = container.getBoundingClientRect();
        const margin = { top: 20, right: 20, bottom: 20, left: 20 };
        const width = Math.max(400, containerRect.width - margin.left - margin.right);
        const height = 400;
        
        console.log('Container dimensions:', width, 'x', height);
        
        // Set up SVG
        const svg = d3.select("#lineageGraph")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
            .style("max-width", "100%")
            .style("height", "auto");
        
        // Clear any existing content
        svg.selectAll("*").remove();
        
        // Create main group
        const g = svg.append("g")
            .attr("transform", `translate(${margin.left}, ${margin.top})`);
        
        // Create simulation
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(100).strength(0.8))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(40))
            .force("x", d3.forceX(width / 2).strength(0.1))
            .force("y", d3.forceY(height / 2).strength(0.1));
        
        // Create links
        const link = g.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(links)
            .enter()
            .append("line")
            .attr("stroke", d => {
                switch(d.strength) {
                    case 'high': return '#48bb78';
                    case 'medium': return '#ed8936';
                    case 'low': return '#f56565';
                    default: return '#718096';
                }
            })
            .attr("stroke-width", d => d.strength === 'high' ? 3 : 2)
            .attr("stroke-dasharray", d => d.type === 'similar_name' ? "5,5" : "none")
            .attr("opacity", 0.7);
        
        // Create node groups
        const nodeGroup = g.append("g")
            .attr("class", "nodes")
            .selectAll("g")
            .data(nodes)
            .enter()
            .append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        // Add circles to nodes
        nodeGroup.append("circle")
            .attr("r", 12)
            .attr("fill", d => {
                // Generate color based on table name
                const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00c9ff'];
                const hash = d.table.split('').reduce((a, b) => {
                    a = ((a << 5) - a) + b.charCodeAt(0);
                    return a & a;
                }, 0);
                return colors[Math.abs(hash) % colors.length];
            })
            .attr("stroke", "#fff")
            .attr("stroke-width", 2);
        
        // Add labels
        nodeGroup.append("text")
            .text(d => d.column || d.id.split('.')[1] || d.id)
            .attr("font-size", "10px")
            .attr("font-family", "-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif")
            .attr("text-anchor", "middle")
            .attr("dy", -18)
            .attr("fill", "#2d3748")
            .attr("font-weight", "500");
        
        // Add tooltips
        nodeGroup.append("title")
            .text(d => d.id);
        
        // Update positions on simulation tick
        simulation.on("tick", () => {
            // Keep nodes within bounds
            nodes.forEach(d => {
                d.x = Math.max(25, Math.min(width - 25, d.x));
                d.y = Math.max(25, Math.min(height - 25, d.y));
            });
            
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            nodeGroup
                .attr("transform", d => `translate(${d.x}, ${d.y})`);
        });
        
        // Drag functions
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = Math.max(25, Math.min(width - 25, event.x));
            d.fy = Math.max(25, Math.min(height - 25, event.y));
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        // Add zoom functionality
        const zoom = d3.zoom()
            .scaleExtent([0.5, 2])
            .on("zoom", (event) => {
                g.attr("transform", 
                    `translate(${margin.left + event.transform.x}, ${margin.top + event.transform.y}) scale(${event.transform.k})`
                );
            });
        
        svg.call(zoom);
        
        // Add reset button
        const existingButton = container.querySelector('.reset-zoom-btn');
        if (existingButton) {
            existingButton.remove();
        }
        
        const resetButton = document.createElement('button');
        resetButton.innerHTML = '<i class="fas fa-expand-arrows-alt"></i> Reset View';
        resetButton.className = 'reset-zoom-btn';
        resetButton.onclick = () => {
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity.translate(0, 0).scale(1)
            );
        };
        container.appendChild(resetButton);
        
        console.log('Lineage graph rendered successfully');
        
    } catch (error) {
        console.error('Error rendering lineage graph:', error);
        showLineageFallback(edges);
    }
}

function showLineageFallback(relationships) {
    const container = document.querySelector('.lineage-graph-container');
    if (container) {
        container.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; text-align: center; padding: 20px;">
                <i class="fas fa-project-diagram" style="font-size: 3rem; color: #718096; margin-bottom: 20px;"></i>
                <h4 style="color: #2d3748; margin-bottom: 10px;">Interactive Visualization Unavailable</h4>
                <p style="color: #718096; margin: 0;">The relationship list above shows all detected connections.</p>
            </div>
        `;
    }
}

// String similarity calculation - SHARED UTILITY
function calculateStringSimilarity(str1, str2) {
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    
    if (longer.length === 0) return 1.0;
    
    const editDistance = levenshteinDistance(longer, shorter);
    return (longer.length - editDistance) / longer.length;
}

function levenshteinDistance(str1, str2) {
    const matrix = [];
    
    for (let i = 0; i <= str2.length; i++) {
        matrix[i] = [i];
    }
    
    for (let j = 0; j <= str1.length; j++) {
        matrix[0][j] = j;
    }
    
    for (let i = 1; i <= str2.length; i++) {
        for (let j = 1; j <= str1.length; j++) {
            if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
                matrix[i][j] = matrix[i - 1][j - 1];
            } else {
                matrix[i][j] = Math.min(
                    matrix[i - 1][j - 1] + 1,
                    matrix[i][j - 1] + 1,
                    matrix[i - 1][j] + 1
                );
            }
        }
    }
    
    return matrix[str2.length][str1.length];
}

// Display file overview - ENHANCED
function displayFileOverview() {
    const container = document.getElementById('fileOverview');
    if (!container) return;

    const data = extractedMetadata.database_info || {};
    
    container.innerHTML = `
        <div class="overview-item">
            <i class="fas fa-database"></i>
            <div class="overview-content">
                <h4>Database Name</h4>
                <p>${data.database_name || 'Unknown'}</p>
            </div>
        </div>
        <div class="overview-item">
            <i class="fas fa-weight-hanging"></i>
            <div class="overview-content">
                <h4>File Size</h4>
                <p>${formatFileSize(data.file_size || 0)}</p>
            </div>
        </div>
        <div class="overview-item">
            <i class="fas fa-table"></i>
            <div class="overview-content">
                <h4>Sheets</h4>
                <p>${data.sheet_count || 0}</p>
            </div>
        </div>
        <div class="overview-item">
            <i class="fas fa-clock"></i>
            <div class="overview-content">
                <h4>Modified</h4>
                <p>${formatDate(data.modified_date)}</p>
            </div>
        </div>
    `;
}

// Display schema information - ENHANCED
function displaySchemaInformation() {
    displayTables();
    displayColumns();
}

function displayTables() {
    const container = document.getElementById('tablesGrid');
    if (!container) return;
    
    const tables = extractedMetadata.tables_info || [];
    if (tables.length === 0) {
        container.innerHTML = '<p>No table information available.</p>';
        return;
    }
    
    container.innerHTML = tables.map(table => `
        <div class="table-card">
            <div class="table-name">
                <i class="fas fa-table"></i>
                <h4>${table.table_name}</h4>
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

function displayColumns() {
    const container = document.getElementById('columnsTable');
    if (!container) return;
    
    const columns = extractedMetadata.columns_info || [];
    if (columns.length === 0) {
        container.innerHTML = '<p>No column information available.</p>';
        return;
    }
    
    container.innerHTML = `
        <table class="columns-table">
            <thead>
                <tr>
                    <th>Table</th>
                    <th>Column Name</th>
                    <th>Data Type</th>
                    <th>Description</th>
                    <th>Tags</th>
                    <th>Owner</th>
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
                        <td><span class="data-type-badge ${col.data_type?.toLowerCase() || 'varchar'}">${col.data_type}</span></td>
                        <td><span class="description">${col.description || '-'}</span></td>
                        <td><span class="tags">${col.tags ? (Array.isArray(col.tags) ? col.tags.join(', ') : col.tags) : '-'}</span></td>
                        <td><span class="owner">${col.owner || '-'}</span></td>
                        <td>${col.is_nullable}</td>
                        <td>${col.unique_percentage || 0}%</td>
                        <td>${col.null_percentage || 0}%</td>
                        <td><span class="quality-badge ${(col.quality_level || 'medium').toLowerCase()}">${col.quality_level || 'MEDIUM'}</span></td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Display data quality - ENHANCED
function displayDataQuality() {
    const container = document.getElementById('qualityMetrics');
    if (!container) return;

    const columns = extractedMetadata.columns_info || [];
    if (columns.length === 0) {
        container.innerHTML = '<p>No quality metrics available.</p>';
        return;
    }

    const qualityCounts = {
        HIGH: columns.filter(col => col.quality_level === 'HIGH').length,
        MEDIUM: columns.filter(col => col.quality_level === 'MEDIUM').length,
        LOW: columns.filter(col => col.quality_level === 'LOW').length
    };

    const totalColumns = columns.length;
    const avgNullPercentage = columns.reduce((sum, col) => sum + (col.null_percentage || 0), 0) / totalColumns;
    const avgUniquePercentage = columns.reduce((sum, col) => sum + (col.unique_percentage || 0), 0) / totalColumns;

    // Calculate overall score
    const overallScore = Math.round((qualityCounts.HIGH * 100 + qualityCounts.MEDIUM * 70 + qualityCounts.LOW * 30) / totalColumns);

    container.innerHTML = `
        <div class="quality-item ${getQualityClass(overallScore)}">
            <i class="fas fa-chart-line"></i>
            <div class="quality-content">
                <h4>Overall Quality Score</h4>
                <p class="quality-score">${overallScore}%</p>
            </div>
        </div>
        <div class="quality-item">
            <i class="fas fa-check-circle"></i>
            <div class="quality-content">
                <h4>High Quality Columns</h4>
                <p>${qualityCounts.HIGH} (${((qualityCounts.HIGH / totalColumns) * 100).toFixed(1)}%)</p>
            </div>
        </div>
        <div class="quality-item">
            <i class="fas fa-exclamation-triangle"></i>
            <div class="quality-content">
                <h4>Medium Quality Columns</h4>
                <p>${qualityCounts.MEDIUM} (${((qualityCounts.MEDIUM / totalColumns) * 100).toFixed(1)}%)</p>
            </div>
        </div>
        <div class="quality-item">
            <i class="fas fa-times-circle"></i>
            <div class="quality-content">
                <h4>Low Quality Columns</h4>
                <p>${qualityCounts.LOW} (${((qualityCounts.LOW / totalColumns) * 100).toFixed(1)}%)</p>
            </div>
        </div>
        <div class="quality-item">
            <i class="fas fa-chart-bar"></i>
            <div class="quality-content">
                <h4>Average Completeness</h4>
                <p>${(100 - avgNullPercentage).toFixed(1)}%</p>
            </div>
        </div>
        <div class="quality-item">
            <i class="fas fa-fingerprint"></i>
            <div class="quality-content">
                <h4>Average Uniqueness</h4>
                <p>${avgUniquePercentage.toFixed(1)}%</p>
            </div>
        </div>
    `;
}

// Display visualizations - ENHANCED WITH PLOTLY
function displayVisualizations() {
    const container = document.getElementById('visualizations');
    if (!container) return;

    const visualizations = extractedMetadata.visualizations || [];
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

    // Create charts with Plotly if available
    visualizations.forEach((viz, index) => {
        setTimeout(() => createInteractiveChart(viz, `chart-${index}`), 100 * index);
    });
}

// Create interactive charts with Plotly - ENHANCED
function createInteractiveChart(vizData, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    console.log('Creating chart:', vizData.type, 'for', containerId);
    
    try {
        // Check if Plotly is available
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
            // Try to load Plotly from CDN
            loadPlotlyAndRenderChart(vizData, containerId);
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

function loadPlotlyAndRenderChart(vizData, containerId) {
    console.log('Loading Plotly from CDN...');
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.26.0/plotly.min.js';
    script.onload = () => {
        console.log('Plotly loaded, creating chart...');
        createInteractiveChart(vizData, containerId);
    };
    script.onerror = () => {
        console.error('Failed to load Plotly, showing fallback...');
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div style="padding: 40px; text-align: center; background: #f8f9fa; border-radius: 8px;">
                    <i class="fas fa-chart-${vizData.type === 'bar_chart' ? 'bar' : vizData.type === 'pie_chart' ? 'pie' : 'area'}" style="font-size: 2rem; color: #667eea; margin-bottom: 15px;"></i>
                    <h4>${vizData.title}</h4>
                    <p>Chart type: ${vizData.type}</p>
                    <p><em>Interactive chart unavailable</em></p>
                </div>
            `;
        }
    };
    document.head.appendChild(script);
}

// Tab switching function
function switchTab(tabName) {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabButtons.forEach(btn => btn.classList.remove('active'));
    tabPanes.forEach(pane => pane.classList.remove('active'));
    
    // Find and activate the correct tab button
    const activeButton = document.querySelector(`.tab-btn[onclick="switchTab('${tabName}')"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
    
    // Activate the correct content pane
    const targetPane = document.getElementById(`${tabName}Content`);
    if (targetPane) {
        targetPane.classList.add('active');
    }
}

// Export metadata function - ENHANCED
async function exportMetadata(format) {
    try {
        if (!extractedMetadata || Object.keys(extractedMetadata).length === 0) {
            showError('No metadata available to export');
            return;
        }
        
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                metadata: extractedMetadata,
                format: format,
                workflow_id: currentWorkflowId
            })
        });
        
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Create download
            const blob = new Blob([result.content], {
                type: format === 'json' ? 'application/json' : 'text/csv'
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `metadata_${currentWorkflowId || 'export'}.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showSuccessMessage(`Metadata exported as ${format.toUpperCase()}`);
        }
        
    } catch (error) {
        console.error('Export error:', error);
        showError(`Failed to export metadata: ${error.message}`);
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

function formatDate(date) {
    if (!date) return 'Unknown';
    const d = new Date(date);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
}

function getQualityClass(score) {
    if (score >= 80) return 'high';
    if (score >= 60) return 'medium';
    return 'low';
}

function showError(message) {
    const errorModal = document.getElementById('errorModal');
    const errorMessage = document.getElementById('errorMessage');
    if (errorModal && errorMessage) {
        errorMessage.textContent = message;
        errorModal.style.display = 'block';
    } else {
        alert(message); // Fallback
    }
    console.error(message);
}

function showSuccessMessage(message) {
    const notification = document.createElement('div');
    notification.className = 'success-notification';
    notification.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>${message}</span>
    `;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 10px;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function closeModal() {
    const errorModal = document.getElementById('errorModal');
    if (errorModal) {
        errorModal.style.display = 'none';
    }
}

function showToast(message, type = 'info') {
    console.log(`Toast [${type}]: ${message}`);
    // Could implement actual toast notifications here
}

// Close modal when clicking outside
window.onclick = function(event) {
    const errorModal = document.getElementById('errorModal');
    if (event.target === errorModal) {
        closeModal();
    }
}

// Console log for debugging
console.log('Excel SourceSense script loaded successfully (Merged Version)');