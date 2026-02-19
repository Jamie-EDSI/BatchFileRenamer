// Global state
let excelUploaded = false;
let filesUploaded = false;
let previewData = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    setupDragAndDrop();
    setupFileInputs();
});

// Setup drag and drop
function setupDragAndDrop() {
    const excelZone = document.getElementById('excelDropZone');
    const filesZone = document.getElementById('filesDropZone');
    
    setupDropZone(excelZone, handleExcelUpload, false);
    setupDropZone(filesZone, handleFilesUpload, true);
}

function setupDropZone(zone, handler, multiple) {
    zone.addEventListener('click', () => {
        if (zone.id === 'excelDropZone') {
            document.getElementById('excelInput').click();
        } else {
            document.getElementById('filesInput').click();
        }
    });
    
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('drag-over');
    });
    
    zone.addEventListener('dragleave', () => {
        zone.classList.remove('drag-over');
    });
    
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        
        const files = multiple ? e.dataTransfer.files : [e.dataTransfer.files[0]];
        handler(files);
    });
}

// Setup file inputs
function setupFileInputs() {
    document.getElementById('excelInput').addEventListener('change', (e) => {
        handleExcelUpload([e.target.files[0]]);
    });
    
    document.getElementById('filesInput').addEventListener('change', (e) => {
        handleFilesUpload(e.target.files);
    });
}

// Handle Excel upload
async function handleExcelUpload(files) {
    if (!files || files.length === 0) return;
    
    const file = files[0];
    
    if (!file.name.match(/\.(xlsx|xls)$/i)) {
        showToast('Please upload an Excel file (.xlsx or .xls)', 'error');
        return;
    }
    
    showLoading('Uploading Excel file...');
    
    const formData = new FormData();
    formData.append('excel', file);
    
    try {
        const response = await fetch('/upload_excel', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            excelUploaded = true;
            document.getElementById('excelDropZone').style.display = 'none';
            document.getElementById('excelStatus').style.display = 'flex';
            document.getElementById('excelFileName').textContent = file.name;
            document.getElementById('excelFileDetail').textContent = data.message;
            showToast(data.message, 'success');
            checkReadyState();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error uploading Excel file: ' + error.message, 'error');
    }
}

// Handle files upload
async function handleFilesUpload(files) {
    if (!files || files.length === 0) return;
    
    showLoading('Uploading files...');
    
    const formData = new FormData();
    Array.from(files).forEach(file => {
        formData.append('files[]', file);
    });
    
    try {
        const response = await fetch('/upload_files', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            filesUploaded = true;
            document.getElementById('filesDropZone').style.display = 'none';
            document.getElementById('filesStatus').style.display = 'flex';
            document.getElementById('filesCount').textContent = `${data.count} files uploaded`;
            document.getElementById('filesDetail').textContent = data.message;
            showToast(data.message, 'success');
            checkReadyState();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error uploading files: ' + error.message, 'error');
    }
}

// Remove Excel
function removeExcel() {
    excelUploaded = false;
    document.getElementById('excelStatus').style.display = 'none';
    document.getElementById('excelDropZone').style.display = 'block';
    document.getElementById('excelInput').value = '';
    checkReadyState();
}

// Remove files
function removeFiles() {
    filesUploaded = false;
    document.getElementById('filesStatus').style.display = 'none';
    document.getElementById('filesDropZone').style.display = 'block';
    document.getElementById('filesInput').value = '';
    checkReadyState();
}

// Check if ready to preview
function checkReadyState() {
    const previewBtn = document.getElementById('previewBtn');
    if (excelUploaded && filesUploaded) {
        previewBtn.disabled = false;
    } else {
        previewBtn.disabled = true;
    }
}

// Preview renames
async function previewRenames() {
    showLoading('Analyzing rename operations...');
    
    try {
        const response = await fetch('/preview', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            previewData = data;
            displayPreview(data);
            
            if (data.summary.error > 0) {
                showToast(`Found ${data.summary.error} error(s). Please review and acknowledge to continue.`, 'warning');
            } else {
                showToast('Preview complete! Ready to rename.', 'success');
            }
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error during preview: ' + error.message, 'error');
    }
}

// Display preview
function displayPreview(data) {
    const container = document.getElementById('previewContainer');
    const summary = document.getElementById('previewSummary');
    const tbody = document.getElementById('previewTableBody');
    const acknowledgeSection = document.getElementById('acknowledgeErrorsSection');
    const acknowledgeText = document.getElementById('acknowledgeErrorsText');
    const acknowledgeCheckbox = document.getElementById('acknowledgeErrorsCheckbox');
    
    // Show container
    container.style.display = 'block';
    
    // Update summary
    summary.innerHTML = `
        <div class="summary-item">
            <span class="summary-label">Ready:</span>
            <span class="summary-value ready">${data.summary.ready}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">Warnings:</span>
            <span class="summary-value warning">${data.summary.warning}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">Errors:</span>
            <span class="summary-value error">${data.summary.error}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">Total:</span>
            <span class="summary-value">${data.summary.total}</span>
        </div>
        ${data.summary.active > 0 || data.summary.terminated > 0 ? `
        <div class="summary-item">
            <span class="summary-label">Active:</span>
            <span class="summary-value" style="color: #06D6A0;">${data.summary.active || 0}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">Terminated:</span>
            <span class="summary-value" style="color: #FF6B35;">${data.summary.terminated || 0}</span>
        </div>
        ` : ''}
    `;
    
    // Show/hide acknowledge errors section
    if (data.summary.error > 0) {
        acknowledgeSection.style.display = 'block';
        acknowledgeText.textContent = `I acknowledge ${data.summary.error} error(s) and want to continue with ${data.summary.ready} valid rename(s)`;
        acknowledgeCheckbox.checked = false;
    } else {
        acknowledgeSection.style.display = 'none';
    }
    
    // Clear and populate table
    tbody.innerHTML = '';
    data.results.forEach(result => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="status-badge ${result.status}">${result.status.toUpperCase()}</span></td>
            <td>${escapeHtml(result.current)}</td>
            <td>${escapeHtml(result.new)}</td>
            <td>${escapeHtml(result.notes)}</td>
        `;
        tbody.appendChild(row);
    });
    
    // Update execute button state
    updateExecuteButton();
    
    // Scroll to preview
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Update execute button state
function updateExecuteButton() {
    const executeBtn = document.getElementById('executeBtn');
    
    if (!previewData) {
        executeBtn.disabled = true;
        return;
    }
    
    const hasReady = previewData.summary.ready > 0;
    const hasErrors = previewData.summary.error > 0;
    const isAcknowledged = document.getElementById('acknowledgeErrorsCheckbox')?.checked || false;
    
    // Enable if: has ready files AND (no errors OR errors acknowledged)
    executeBtn.disabled = !(hasReady && (!hasErrors || isAcknowledged));
}

// Execute renames
async function executeRenames() {
    if (!confirm(`About to rename ${previewData.summary.ready} file(s). This operation cannot be undone. Continue?`)) {
        return;
    }
    
    showLoading('Renaming files...');
    
    try {
        const response = await fetch('/execute', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            displayResults(data);
            showToast(`Successfully renamed ${data.summary.success} file(s)!`, 'success');
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error during rename: ' + error.message, 'error');
    }
}

// Display results
function displayResults(data) {
    const container = document.getElementById('resultsContainer');
    const summary = document.getElementById('resultsSummary');
    const tbody = document.getElementById('previewTableBody');
    
    // Hide preview container
    document.getElementById('previewContainer').style.display = 'none';
    
    // Show results container
    container.style.display = 'block';
    
    // Update summary
    summary.innerHTML = `
        <h3>✓ Rename Complete!</h3>
        <p>Successfully renamed: ${data.summary.success} file(s)</p>
        ${data.summary.failed > 0 ? `<p style="color: var(--error);">Failed: ${data.summary.failed} file(s)</p>` : ''}
    `;
    
    // Update table with results
    tbody.innerHTML = '';
    data.results.forEach(result => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="status-badge ${result.status.toLowerCase()}">${result.status.toUpperCase()}</span></td>
            <td>${escapeHtml(result.current)}</td>
            <td>${escapeHtml(result.new)}</td>
            <td>${escapeHtml(result.notes)}</td>
        `;
        tbody.appendChild(row);
    });
    
    // Disable execute button
    document.getElementById('executeBtn').disabled = true;
    
    // Scroll to results
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Download renamed files
async function downloadFiles() {
    showLoading('Preparing download...');
    
    try {
        const response = await fetch('/download');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `renamed_files_${Date.now()}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            hideLoading();
            showToast('Download started!', 'success');
        } else {
            hideLoading();
            showToast('Error downloading files', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error downloading files: ' + error.message, 'error');
    }
}

// Download report
async function downloadReport() {
    if (!previewData) return;
    
    showLoading('Generating report...');
    
    try {
        const response = await fetch('/download_report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                results: previewData.results
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `rename_report_${Date.now()}.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            hideLoading();
            showToast('Report downloaded!', 'success');
        } else {
            hideLoading();
            showToast('Error downloading report', 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error downloading report: ' + error.message, 'error');
    }
}

// Reset application
async function resetApp() {
    if (!confirm('Are you sure you want to start over? All uploaded files will be cleared.')) {
        return;
    }
    
    showLoading('Resetting...');
    
    try {
        const response = await fetch('/reset', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            location.reload();
        } else {
            showToast(data.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showToast('Error resetting: ' + error.message, 'error');
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const icon = document.getElementById('toastIcon');
    const msg = document.getElementById('toastMessage');
    
    // Set icon based on type
    const icons = {
        success: '✓',
        error: '✗',
        warning: '⚠'
    };
    
    icon.textContent = icons[type] || icons.success;
    msg.textContent = message;
    
    // Remove existing classes
    toast.classList.remove('success', 'error', 'warning');
    toast.classList.add(type);
    
    // Show toast
    toast.classList.add('show');
    
    // Hide after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// Show loading overlay
function showLoading(text = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    loadingText.textContent = text;
    overlay.style.display = 'flex';
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = 'none';
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Chat functionality
let chatMessages = [];

function toggleChat() {
    const chatPanel = document.getElementById('chatPanel');
    const isVisible = chatPanel.style.display !== 'none';
    chatPanel.style.display = isVisible ? 'none' : 'flex';
    
    // Show welcome message if no messages yet
    if (!isVisible && chatMessages.length === 0) {
        addWelcomeMessage();
    }
}

function addWelcomeMessage() {
    // Welcome is already in HTML, just ensure messages are clear
    const messagesContainer = document.getElementById('chatMessages');
    messagesContainer.innerHTML = `
        <div class="chat-welcome">
            <div class="chat-welcome-icon">👋</div>
            <p>Hi! I'm your AI assistant.</p>
            <p class="chat-welcome-hint">Ask me about errors or how to fix them!</p>
        </div>
    `;
}

function addChatMessage(role, content) {
    const messagesContainer = document.getElementById('chatMessages');
    
    // Remove welcome message if it exists
    const welcome = messagesContainer.querySelector('.chat-welcome');
    if (welcome) {
        welcome.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    messageDiv.textContent = content;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    chatMessages.push({ role, content });
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-typing';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="chat-typing-dot"></div>
        <div class="chat-typing-dot"></div>
        <div class="chat-typing-dot"></div>
    `;
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function generateAIResponse(userMessage) {
    let response = '';
    const lowerMsg = userMessage.toLowerCase();
    
    // Context-aware responses based on preview data
    if (previewData && previewData.summary.error > 0) {
        const errorFiles = previewData.results.filter(r => r.status === 'error');
        
        if (lowerMsg.includes('error') || lowerMsg.includes('fix') || lowerMsg.includes('why') || lowerMsg.includes('wrong')) {
            const errorTypes = {
                notFound: 0,
                duplicate: 0,
                exists: 0
            };
            
            errorFiles.forEach(f => {
                if (f.notes.includes('not found')) errorTypes.notFound++;
                if (f.notes.includes('Duplicate')) errorTypes.duplicate++;
                if (f.notes.includes('already exists')) errorTypes.exists++;
            });
            
            response = "I can help you fix these errors! Here's what I found:\n\n";
            
            if (errorTypes.notFound > 0) {
                response += `📁 ${errorTypes.notFound} file(s) not found:\n`;
                response += "The file names in Column A don't match uploaded files.\n\n";
                response += "How to fix:\n";
                response += "• Check spelling and capitalization (case-sensitive)\n";
                response += "• Verify file extensions match (.pdf, .jpg, etc.)\n";
                response += "• Make sure you uploaded all files from Column A\n\n";
            }
            
            if (errorTypes.duplicate > 0) {
                response += `⚠️ ${errorTypes.duplicate} duplicate new name(s):\n`;
                response += "Multiple files are trying to rename to the same name.\n\n";
                response += "**Good news:** The app automatically handles this!\n";
                response += "Duplicates are renamed with (1), (2), etc.\n";
                response += "Example: file.pdf, file (1).pdf, file (2).pdf\n\n";
            }
            
            if (errorTypes.exists > 0) {
                response += `🚫 ${errorTypes.exists} name conflict(s):\n`;
                response += "Files with new names already exist.\n\n";
                response += "How to fix:\n";
                response += "• Choose different names in Column B\n";
                response += "• Remove existing files first\n";
                response += "• Or use 'acknowledge errors' to skip\n\n";
            }
            
            response += "💡 Tip: Check 'acknowledge errors' to rename valid files and skip errors.";
        } else if (lowerMsg.includes('continue') || lowerMsg.includes('skip') || lowerMsg.includes('proceed')) {
            response = `Yes! You can proceed even with errors:\n\n`;
            response += `✅ ${previewData.summary.ready} files ready to rename\n`;
            response += `❌ ${previewData.summary.error} files will be skipped\n\n`;
            response += "To continue:\n";
            response += "1. Check: ✓ 'I acknowledge errors and want to continue'\n";
            response += "2. Click 'Execute Renames'\n";
            response += "3. Only valid files will be renamed\n\n";
            response += "Files with errors stay unchanged for you to fix later!";
        } else {
            response = `I see ${previewData.summary.error} error(s) and ${previewData.summary.ready} file(s) ready.\n\n`;
            response += "I can help with:\n";
            response += "• Explaining what errors mean\n";
            response += "• Showing how to fix them\n";
            response += "• Helping you proceed with valid files\n\n";
            response += "Try asking: 'Why are there errors?' or 'How do I fix this?'";
        }
    } else if (previewData && previewData.summary.error === 0) {
        if (lowerMsg.includes('ready') || lowerMsg.includes('next') || lowerMsg.includes('now')) {
            response = `Perfect! All ${previewData.summary.ready} files ready! 🎉\n\n`;
            response += "Next steps:\n";
            response += "1. Review the preview table\n";
            response += "2. Click 'Execute Renames' when ready\n";
            response += "3. Download your renamed files\n\n";
            response += "This can't be undone, so double-check the names!";
        } else {
            response = "Great! No errors found. All files ready to rename!\n\n";
            response += "You can:\n";
            response += "• Review the preview table\n";
            response += "• Ask about specific files\n";
            response += "• Click 'Execute Renames' when ready\n\n";
            response += "Feel free to ask anything!";
        }
    } else {
        response = "👋 Hi! I'm your File Renamer assistant.\n\n";
        response += "I can help you:\n";
        response += "• Understand preview errors\n";
        response += "• Fix file naming issues\n";
        response += "• Guide you through renaming\n";
        response += "• Answer Excel mapping questions\n\n";
        response += "Upload Excel and files, click 'Preview', and I'll help resolve issues!";
    }
    
    return response;
}

function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addChatMessage('user', message);
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Simulate AI response delay
    setTimeout(() => {
        hideTypingIndicator();
        const response = generateAIResponse(message);
        addChatMessage('assistant', response);
    }, 800);
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendChatMessage();
    }
}
