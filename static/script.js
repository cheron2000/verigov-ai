const API_ENDPOINT_SMART = '/api/verify';
const API_ENDPOINT_AUDIT = '/api/audit';
const API_ENDPOINT_WHITELIST = '/api/whitelist';
// Load whitelist and audit on page load
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initNavigation();
    loadWhitelist();
    loadAudit();
    loadRecentActivity();
    loadTrustedSources();
    updateTodayCount();
});

// Navigation functionality
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            link.classList.add('active');
            
            // Get the section to scroll to
            const section = link.getAttribute('data-section');
            
            // Handle different sections
            if (section === 'dashboard') {
                // Scroll to top
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else if (section === 'verify') {
                // Scroll to verification panel
                document.getElementById('verify').scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else if (section === 'sources') {
                // Scroll to sources section
                document.getElementById('sources').scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else if (section === 'reports') {
                // Scroll to reports/audit trail
                document.getElementById('reports').scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    // Update active nav based on scroll position
    window.addEventListener('scroll', () => {
        const sections = ['verify', 'sources', 'reports'];
        let current = 'dashboard';
        
        sections.forEach(section => {
            const element = document.getElementById(section);
            if (element) {
                const rect = element.getBoundingClientRect();
                if (rect.top <= 100 && rect.bottom >= 100) {
                    current = section;
                }
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-section') === current) {
                link.classList.add('active');
            }
        });
    });
}

// Theme Toggle
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        themeToggle.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
}

// Update today's count
function updateTodayCount() {
    const count = localStorage.getItem('todayCount') || 0;
    document.getElementById('todayCount').textContent = count;
}

// Load recent activity
async function loadRecentActivity() {
    try {
        const response = await fetch(`${API_ENDPOINT_AUDIT}?limit=5`);
        const entries = await response.json();
        
        const activityDiv = document.getElementById('recentActivity');
        
        if (entries && entries.length > 0) {
            activityDiv.innerHTML = entries.slice(0, 5).reverse().map(entry => `
                <div class="activity-item">
                    <div>${entry.event_type.replace(/_/g, ' ')}</div>
                    <div class="time">${formatTimeAgo(entry.timestamp)}</div>
                </div>
            `).join('');
        } else {
            activityDiv.innerHTML = '<div class="loading-small">No activity yet</div>';
        }
    } catch (error) {
        document.getElementById('recentActivity').innerHTML = '<div class="loading-small">Error loading</div>';
    }
}

// Load trusted sources for sidebar
async function loadTrustedSources() {
    const sourcesDiv = document.getElementById('trustedSources');
    if (!sourcesDiv) return;

    try {
        const response = await fetch(API_ENDPOINT_WHITELIST);
        const data = await response.json();

        if (data.sources && data.sources.length > 0) {
            sourcesDiv.innerHTML = data.sources.slice(0, 5).map(source => `
                <div class="source-item">
                    <strong>${source.name}</strong>
                    <small>${source.domain}</small>
                </div>
            `).join('');
        } else {
            sourcesDiv.innerHTML = '<div class="loading-small">No sources</div>';
        }
    } catch (error) {
        sourcesDiv.innerHTML = '<div class="loading-small">Error loading</div>';
    }
}

// Format time ago
function formatTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = Math.floor((now - time) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}

// Handle form submission
const verifyForm = document.getElementById('verifyForm');
if (verifyForm) {
    verifyForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const claim = document.getElementById('claim').value.trim();
        const sources = [
            document.getElementById('source1').value.trim(),
            document.getElementById('source2').value.trim(),
            document.getElementById('source3').value.trim()
        ].filter(s => s !== '');

        if (!claim) {
            alert('Please enter a claim to verify');
            return;
        }

        const loadingMsg = document.getElementById('loadingMessage');
        const steps = document.querySelectorAll('.step');
        document.getElementById('loading').style.display = 'block';
        document.getElementById('result').style.display = 'none';
        document.getElementById('verifyBtn').disabled = true;

        steps.forEach((step, index) => {
            setTimeout(() => {
                steps.forEach(s => s.classList.remove('active'));
                step.classList.add('active');
            }, index * 1000);
        });

        try {
            if (sources.length > 0) {
                loadingMsg.textContent = `Using your ${sources.length} source(s)...`;
            } else {
                loadingMsg.textContent = 'Analyzing claim and auto-selecting sources...';
            }

            console.log('Using SMART endpoint with auto source selection');

            const response = await fetch(API_ENDPOINT_SMART, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ claim, sources })
            });

            const result = await response.json();

            if (response.ok) {
                displayResult(result);
                loadAudit();
                loadRecentActivity();

                const count = parseInt(localStorage.getItem('todayCount') || 0) + 1;
                localStorage.setItem('todayCount', count);
                updateTodayCount();
            } else {
                alert('Error: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            alert('Network error: ' + error.message);
        } finally {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('verifyBtn').disabled = false;
            steps.forEach(s => s.classList.remove('active'));
        }
    });
}

function displayResult(result) {
    const resultDiv = document.getElementById('result');
    const contentDiv = document.getElementById('resultContent');
    
    // Fix: Parse nested JSON in explanation if present
    let explanation = result.explanation || 'No explanation provided';
    let actualStatus = result.status;
    let actualConfidence = result.confidence;
    
    // Check if explanation contains JSON (starts with ```json or {)
    if (explanation.includes('```json') || (explanation.trim().startsWith('{') && explanation.includes('"explanation"'))) {
        try {
            // Remove markdown code blocks
            let cleaned = explanation.replace(/```json/g, '').replace(/```/g, '').trim();
            
            // Try to parse as JSON
            const parsed = JSON.parse(cleaned);
            
            // Extract the actual values from nested JSON
            if (parsed.explanation) {
                explanation = parsed.explanation;
            }
            if (parsed.status) {
                actualStatus = parsed.status;
            }
            if (parsed.confidence !== undefined) {
                actualConfidence = parsed.confidence;
            }
            
            console.log('Extracted from nested JSON:', { actualStatus, actualConfidence, explanationLength: explanation.length });
        } catch (e) {
            // If JSON parsing fails, try to extract explanation text manually
            const expMatch = explanation.match(/"explanation"\s*:\s*"([^"]+)"/);
            if (expMatch) {
                explanation = expMatch[1];
            }
            console.log('Manual extraction used');
        }
    }
    
    // Ensure confidence is a valid number
    const confidence = Math.min(Math.max(parseFloat(actualConfidence) || 0, 0), 100);
    
    const statusEmoji = {
        'VERIFIED': '✅',
        'PARTIALLY_VERIFIED': '⚠️',
        'UNVERIFIED': '❓',
        'FALSE': '❌',
        'NO_SOURCES': '🚫',
        'ERROR': '⚠️'
    };
    
    const emoji = statusEmoji[actualStatus] || '❓';
    
    // Research method badge
    const methodBadges = {
        'user_provided_sources': '👤 User Sources',
        'auto_selected_sources': '🧠 Auto-Selected Sources',
        'ai_knowledge_base': '🤖 AI Knowledge Base',
        'error': '⚠️ Error'
    };
    
    const methodBadge = methodBadges[result.research_method] || result.research_method;
    
    contentDiv.innerHTML = `
        <div>
            <span class="status-badge status-${actualStatus}">
                ${emoji} ${actualStatus.replace(/_/g, ' ')}
            </span>
            <span class="status-badge" style="background: #17a2b8; margin-left: 10px;">
                ${methodBadge}
            </span>
        </div>
        
        <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-left: 3px solid #17a2b8;">
            <strong>🔍 Research Method:</strong>
            <p style="margin: 5px 0 0 0; font-size: 0.9em;">${result.research_note || 'Standard verification'}</p>
        </div>
        
        ${result.topics_identified && result.topics_identified.length > 0 ? `
        <div style="margin-top: 10px;">
            <strong>📚 Topics Identified:</strong>
            <div style="margin-top: 5px;">
                ${result.topics_identified.map(topic => 
                    `<span style="display: inline-block; background: #e9ecef; padding: 3px 8px; border-radius: 3px; margin: 2px; font-size: 0.85em;">${topic}</span>`
                ).join('')}
            </div>
        </div>
        ` : ''}
        
        <div style="margin-top: 15px;">
            <strong>Confidence Score:</strong>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${confidence}%">
                    ${Math.round(confidence)}%
                </div>
            </div>
        </div>
        
        <div>
            <strong>Claim:</strong>
            <p>${result.claim}</p>
        </div>
        
        <div>
            <strong>Explanation:</strong>
            <div class="explanation">${explanation}</div>
        </div>
        
        <div style="margin-top: 15px;">
            <small>Sources checked: ${result.sources_checked}</small>
            ${result.sources_selected && result.sources_selected.length > 0 ? 
                `<br><small>Selected sources: ${result.sources_selected.slice(0, 2).map(s => s.replace('https://www.', '').replace('/', '')).join(', ')}</small>` 
                : ''}
        </div>
    `;
    
    resultDiv.style.display = 'block';
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function loadWhitelist() {
    const whitelistDiv = document.getElementById('whitelist');
    if (!whitelistDiv) return;

    try {
        const response = await fetch(API_ENDPOINT_WHITELIST);
        const data = await response.json();

        if (data.sources && data.sources.length > 0) {
            whitelistDiv.innerHTML = data.sources.map(source => `
                <div class="whitelist-item">
                    <strong>${source.domain}</strong>
                    <small>${source.name}</small>
                </div>
            `).join('');
        } else {
            whitelistDiv.innerHTML = '<p>No sources configured</p>';
        }
    } catch (error) {
        whitelistDiv.innerHTML = '<p>Error loading whitelist</p>';
    }
}

async function loadAudit() {
    const auditDiv = document.getElementById('auditTrail');
    if (!auditDiv) return;

    try {
        const response = await fetch(`${API_ENDPOINT_AUDIT}?limit=10`);
        const entries = await response.json();

        if (entries && entries.length > 0) {
            auditDiv.innerHTML = entries.reverse().map(entry => `
                <div class="audit-item">
                    <div class="event-type">${entry.event_type.replace(/_/g, ' ')}</div>
                    <div class="timestamp">${new Date(entry.timestamp).toLocaleString()}</div>
                </div>
            `).join('');
        } else {
            auditDiv.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>No verification history yet</p>
                </div>
            `;
        }
    } catch (error) {
        auditDiv.innerHTML = '<div class="loading-small">Error loading audit log</div>';
    }
}

// Download report function
function downloadReport() {
    const resultContent = document.getElementById('resultContent').innerText;
    const blob = new Blob([resultContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `verigov-report-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

// Clear history function
function clearHistory() {
    if (confirm('Are you sure you want to clear the verification history?')) {
        document.getElementById('auditTrail').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>No verification history yet</p>
            </div>
        `;
        localStorage.setItem('todayCount', 0);
        updateTodayCount();
    }
}

// Global variable to store all sources
let allSourcesData = [];

// Show all sources modal
async function showAllSources() {
    const modal = document.getElementById('sourcesModal');
    const sourcesList = document.getElementById('allSourcesList');
    
    modal.classList.add('show');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
    
    // Load all sources if not already loaded
    if (allSourcesData.length === 0) {
        try {
            const response = await fetch(API_ENDPOINT_WHITELIST);
            const data = await response.json();
            allSourcesData = data.sources || [];
        } catch (error) {
            sourcesList.innerHTML = '<div class="loading-small">Error loading sources</div>';
            return;
        }
    }
    
    displayAllSources(allSourcesData);
}

// Display all sources in the modal
function displayAllSources(sources) {
    const sourcesList = document.getElementById('allSourcesList');
    const sourcesCount = document.getElementById('sourcesCount');
    
    sourcesCount.textContent = sources.length;
    
    if (sources.length === 0) {
        sourcesList.innerHTML = '<div class="loading-small">No sources configured</div>';
        return;
    }
    
    // Categorize sources
    const categories = {
        'Government - India': ['india.gov.in', 'nic.in', 'mygov.in'],
        'Government - International': ['gov.uk', 'europa.eu', 'usa.gov'],
        'Health Organizations': ['who.int', 'cdc.gov', 'nih.gov'],
        'Scientific': ['nasa.gov', 'nature.com', 'science.org', 'esa.int'],
        'International Organizations': ['un.org', 'worldbank.org', 'imf.org']
    };
    
    sourcesList.innerHTML = sources.map(source => {
        // Determine category
        let category = 'Other';
        for (const [cat, domains] of Object.entries(categories)) {
            if (domains.some(d => source.domain.includes(d))) {
                category = cat;
                break;
            }
        }
        
        // Get icon based on category
        let icon = 'fa-globe';
        if (category.includes('Government')) icon = 'fa-landmark';
        else if (category.includes('Health')) icon = 'fa-heartbeat';
        else if (category.includes('Scientific')) icon = 'fa-flask';
        else if (category.includes('International')) icon = 'fa-flag';
        
        return `
            <div class="source-card" data-name="${source.name.toLowerCase()}" data-domain="${source.domain.toLowerCase()}">
                <div class="source-card-header">
                    <div class="source-icon">
                        <i class="fas ${icon}"></i>
                    </div>
                    <div class="source-info">
                        <div class="source-name">${source.name}</div>
                        <div class="source-domain">${source.domain}</div>
                    </div>
                </div>
                <div class="source-category">${category}</div>
            </div>
        `;
    }).join('');
}

// Close sources modal
function closeSourcesModal() {
    const modal = document.getElementById('sourcesModal');
    modal.classList.remove('show');
    document.body.style.overflow = ''; // Restore scrolling
    document.getElementById('sourcesSearch').value = ''; // Clear search
}

// Filter sources in modal
function filterSources() {
    const searchTerm = document.getElementById('sourcesSearch').value.toLowerCase();
    const sourceCards = document.querySelectorAll('.source-card');
    let visibleCount = 0;
    
    sourceCards.forEach(card => {
        const name = card.getAttribute('data-name');
        const domain = card.getAttribute('data-domain');
        
        if (name.includes(searchTerm) || domain.includes(searchTerm)) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    document.getElementById('sourcesCount').textContent = visibleCount;
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('sourcesModal');
    if (e.target === modal) {
        closeSourcesModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeSourcesModal();
    }
});
