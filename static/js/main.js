// Tab switching function
function switchTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    if (tab === 'text') {
        document.getElementById('textTab').classList.add('active');
    } else {
        document.getElementById('fileTab').classList.add('active');
    }
}

// Get server IP (network IP, not localhost)
// Get server IP (network IP, not localhost)
async function getServerIP() {
    try {
        const response = await fetch('/api/network-ip');
        if (response.ok) {
            const data = await response.json();
            const port = window.location.port;
            
            // If port is 80 or 443, don't show it (default ports)
            if (port === '80' || port === '443' || port === '') {
                document.getElementById('serverIp').textContent = `${data.ip}`;
            } else {
                document.getElementById('serverIp').textContent = `${data.ip}:${port}`;
            }
        } else {
            const host = window.location.host;
            // Check if host already includes port
            if (host.includes(':')) {
                document.getElementById('serverIp').textContent = host;
            } else {
                document.getElementById('serverIp').textContent = host;
            }
        }
    } catch (error) {
        console.error('Failed to get server IP:', error);
        const host = window.location.host;
        document.getElementById('serverIp').textContent = host;
    }
}

// Timer update function - FIXED
function updateTimers() {
    const timers = document.querySelectorAll('.timer');
    
    timers.forEach(timerElement => {
        const expiresAtStr = timerElement.getAttribute('data-expires');
        if (!expiresAtStr) return;
        
        try {
            const expiry = new Date(expiresAtStr);
            const now = new Date();
            
            if (isNaN(expiry.getTime())) {
                timerElement.textContent = 'Invalid date';
                return;
            }
            
            const diff = expiry - now;
            
            // If expired (allow 1 second tolerance)
            if (diff <= 0) {
                timerElement.textContent = 'Expired';
                timerElement.style.color = '#ef4444';
                timerElement.classList.add('expired');
                return;
            }
            
            // Calculate time components
            const hours = Math.floor(diff / 3600000);
            const minutes = Math.floor((diff % 3600000) / 60000);
            const seconds = Math.floor((diff % 60000) / 1000);
            
            // Format the display
            let timeText = '';
            if (hours > 0) {
                timeText = `${hours}h ${minutes}m ${seconds}s`;
            } else if (minutes > 0) {
                timeText = `${minutes}m ${seconds}s`;
            } else {
                timeText = `${seconds}s`;
            }
            
            timerElement.textContent = timeText;
            timerElement.classList.remove('expired');
            
            // Change color based on remaining time
            if (diff < 60000) { // Less than 1 minute
                timerElement.style.color = '#f59e0b';
            } else if (diff < 300000) { // Less than 5 minutes
                timerElement.style.color = '#f97316';
            } else {
                timerElement.style.color = '#4ade80';
            }
            
        } catch (error) {
            console.error('Timer update error:', error);
            timerElement.textContent = 'Error';
        }
    });
}

// Helper function to handle API responses
async function handleAPIResponse(response) {
    const contentType = response.headers.get('content-type');
    
    if (!response.ok) {
        if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        } else {
            const text = await response.text();
            console.error('Non-JSON response:', text.substring(0, 200));
            throw new Error(`Server error (${response.status})`);
        }
    }
    
    if (contentType && contentType.includes('application/json')) {
        return await response.json();
    } else {
        const text = await response.text();
        throw new Error('Server returned unexpected response format');
    }
}

// Toggle drawer for text content
function toggleDrawer(itemId) {
    const drawer = document.getElementById(`drawer-${itemId}`);
    
    // If this drawer is already open, close it
    if (drawer.style.display === 'block') {
        closeDrawer(itemId);
        return;
    }
    
    // Close all other open drawers first
    document.querySelectorAll('.drawer').forEach(d => {
        d.style.display = 'none';
    });
    
    // Open this drawer
    drawer.style.display = 'block';
    
    // Smooth scroll to drawer
    drawer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Close specific drawer
function closeDrawer(itemId) {
    const drawer = document.getElementById(`drawer-${itemId}`);
    drawer.style.display = 'none';
}

// Close all drawers
function closeAllDrawers() {
    document.querySelectorAll('.drawer').forEach(drawer => {
        drawer.style.display = 'none';
    });
}

// Close drawer when clicking outside (optional)
document.addEventListener('click', function(event) {
    // Check if click is outside any drawer and not on a view button
    const isDrawer = event.target.closest('.drawer');
    const isViewBtn = event.target.closest('.view-btn');
    
    if (!isDrawer && !isViewBtn) {
        closeAllDrawers();
    }
});

// Make drawer functions available globally
window.toggleDrawer = toggleDrawer;
window.closeDrawer = closeDrawer;
window.closeAllDrawers = closeAllDrawers;

// Simple and reliable copy function
async function copyTextContent(itemId, content) {
    // If content is passed directly (from the button click)
    let textToCopy = content;
    
    // If it's a string that was passed as HTML escaped, decode it
    if (typeof textToCopy === 'string') {
        // Handle the case where content is passed as a string
        textToCopy = textToCopy.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
    }
    
    // If no content, try to get from the page
    if (!textToCopy || textToCopy === 'undefined') {
        // For detail page
        const preElement = document.querySelector('.text-content pre');
        if (preElement) {
            textToCopy = preElement.innerText;
        }
    }
    
    // If still no content and we have itemId, fetch from server
    if ((!textToCopy || textToCopy === 'undefined') && itemId) {
        try {
            const response = await fetch(`/api/item/${itemId}/content`);
            if (response.ok) {
                const data = await response.json();
                textToCopy = data.content;
            } else {
                showCopyMessage('Failed to get content', 'error');
                return;
            }
        } catch (error) {
            console.error('Fetch error:', error);
            showCopyMessage('Failed to get content', 'error');
            return;
        }
    }
    
    if (!textToCopy || textToCopy === 'undefined' || textToCopy === '') {
        showCopyMessage('Nothing to copy', 'error');
        return;
    }
    
    // Method 1: Modern Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(textToCopy);
            showCopyMessage('Copied!', 'success');
            return;
        } catch (err) {
            console.log('Clipboard API failed, trying fallback:', err);
        }
    }
    
    // Method 2: Fallback using textarea (works on most browsers)
    try {
        const textarea = document.createElement('textarea');
        textarea.value = textToCopy;
        textarea.style.position = 'fixed';
        textarea.style.top = '-9999px';
        textarea.style.left = '-9999px';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        textarea.setSelectionRange(0, textToCopy.length);
        
        const successful = document.execCommand('copy');
        document.body.removeChild(textarea);
        
        if (successful) {
            showCopyMessage('Copied!', 'success');
        } else {
            showCopyMessage('Copy failed. Select text manually.', 'error');
        }
    } catch (err) {
        console.error('Fallback copy failed:', err);
        showCopyMessage('Press Ctrl+C to copy', 'error');
    }
}

// Helper function to show copy feedback
function showCopyMessage(message, type) {
    // Find the button that was clicked
    let button = null;
    if (window.event && window.event.target) {
        button = window.event.target.closest('.copy-btn-action, .copy-btn, .action-btn');
    }
    
    if (button) {
        const originalHTML = button.innerHTML;
        const originalColor = button.style.backgroundColor;
        
        if (type === 'success') {
            button.innerHTML = '✅ ' + message;
            button.style.backgroundColor = '#48bb78';
        } else {
            button.innerHTML = '❌ ' + message;
            button.style.backgroundColor = '#ef4444';
        }
        
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.style.backgroundColor = originalColor;
        }, 2000);
    } else {
        // Show a temporary alert/popup
        const popup = document.createElement('div');
        popup.textContent = message;
        popup.style.position = 'fixed';
        popup.style.bottom = '20px';
        popup.style.left = '50%';
        popup.style.transform = 'translateX(-50%)';
        popup.style.padding = '10px 20px';
        popup.style.borderRadius = '8px';
        popup.style.backgroundColor = type === 'success' ? '#48bb78' : '#ef4444';
        popup.style.color = 'white';
        popup.style.zIndex = '10000';
        popup.style.fontWeight = 'bold';
        popup.style.fontSize = '14px';
        document.body.appendChild(popup);
        
        setTimeout(() => {
            popup.remove();
        }, 2000);
    }
}

// Make copy function available globally
window.copyTextContent = copyTextContent;

// Share text
document.getElementById('textForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const title = document.getElementById('textTitle').value;
    const content = document.getElementById('textContent').value;
    const expiry = document.getElementById('textExpiry').value;
    
    const resultDiv = document.getElementById('textResult');
    const button = e.target.querySelector('button');
    
    if (!content.trim()) {
        resultDiv.style.display = 'block';
        resultDiv.style.background = '#fee';
        resultDiv.style.borderColor = '#fcc';
        resultDiv.innerHTML = '❌ Please enter some text to share';
        return;
    }
    
    button.disabled = true;
    button.textContent = 'Sharing...';
    resultDiv.style.display = 'none';
    
    try {
        const response = await fetch('/share/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content, expiry })
        });
        
        const data = await handleAPIResponse(response);
        
        if (data.success) {
            resultDiv.style.display = 'block';
            resultDiv.style.background = '#f0fdf4';
            resultDiv.style.borderColor = '#86efac';
            resultDiv.innerHTML = '✅ Text shared successfully! Refreshing page...';
            setTimeout(() => window.location.reload(), 1500);
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Share text error:', error);
        resultDiv.style.display = 'block';
        resultDiv.style.background = '#fee';
        resultDiv.style.borderColor = '#fcc';
        resultDiv.innerHTML = `❌ Error: ${error.message}`;
        button.disabled = false;
        button.textContent = '📤 Share Text';
    }
});

// Share file
document.getElementById('fileForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const expiry = document.getElementById('fileExpiry').value;
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file');
        return;
    }
    
    const resultDiv = document.getElementById('fileResult');
    const button = e.target.querySelector('button');
    
    button.disabled = true;
    button.textContent = 'Uploading...';
    resultDiv.style.display = 'none';
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('expiry', expiry);
    
    try {
        const response = await fetch('/share/file', {
            method: 'POST',
            body: formData
        });
        
        const data = await handleAPIResponse(response);
        
        if (data.success) {
            resultDiv.style.display = 'block';
            resultDiv.style.background = '#f0fdf4';
            resultDiv.style.borderColor = '#86efac';
            resultDiv.innerHTML = '✅ File shared successfully! Refreshing page...';
            setTimeout(() => window.location.reload(), 1500);
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Share file error:', error);
        resultDiv.style.display = 'block';
        resultDiv.style.background = '#fee';
        resultDiv.style.borderColor = '#fcc';
        resultDiv.innerHTML = `❌ Error: ${error.message}`;
        button.disabled = false;
        button.textContent = '📤 Upload & Share';
    }
});

// Initialize on page load
window.addEventListener('load', () => {
    console.log('Page loaded, starting timers...');
    getServerIP();
    updateTimers();
});

// Auto-refresh timers every second
setInterval(updateTimers, 1000);

// Make switchTab available globally
window.switchTab = switchTab;