// CTF Security Lab - Main JavaScript
// API Integration & Dynamic UI

const API_BASE = window.location.origin + '/api/v1';
let authToken = localStorage.getItem('ctf_token');
let currentUser = null;

// ==================== AUTH SYSTEM ====================

async function login(username, password) {
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.access_token) {
            authToken = data.access_token;
            localStorage.setItem('ctf_token', authToken);
            currentUser = data;
            updateNavbar();
            showNotification('Login successful! 🎉', 'success');
            setTimeout(() => window.location.href = '/challenges', 1000);
        } else {
            showNotification(data.message || 'Login failed', 'error');
        }
    } catch (error) {
        showNotification('Connection error', 'error');
    }
}

async function register(userData) {
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Registration successful! Please login.', 'success');
            setTimeout(() => window.location.href = '/login', 1500);
        } else {
            showNotification(data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showNotification('Connection error', 'error');
    }
}

function logout() {
    localStorage.removeItem('ctf_token');
    authToken = null;
    currentUser = null;
    showNotification('Logged out successfully', 'success');
    setTimeout(() => window.location.href = '/', 1000);
}

async function checkAuth() {
    if (!authToken) return false;
    
    try {
        const response = await fetch(`${API_BASE}/users/me`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            updateNavbar();
            return true;
        } else {
            logout();
            return false;
        }
    } catch {
        return false;
    }
}

function updateNavbar() {
    const navAuth = document.getElementById('navAuth');
    const navUser = document.getElementById('navUser');
    
    if (currentUser) {
        navAuth?.classList.add('hidden');
        navUser?.classList.remove('hidden');
        
        const scoreEl = document.getElementById('userScore');
        if (scoreEl) scoreEl.textContent = `${currentUser.stats?.total_score || 0} pts`;
    } else {
        navAuth?.classList.remove('hidden');
        navUser?.classList.add('hidden');
    }
}

// ==================== CHALLENGES ====================

async function loadChallenges(filters = {}) {
    try {
        const response = await fetch(`${API_BASE}/challenges`, {
            headers: authToken ? { 'Authorization': `Bearer ${authToken}` } : {}
        });
        
        const data = await response.json();
        displayChallenges(data.challenges || []);
    } catch (error) {
        showNotification('Failed to load challenges', 'error');
    }
}

function displayChallenges(challenges) {
    const grid = document.getElementById('challengesGrid');
    if (!grid) return;
    
    grid.innerHTML = challenges.map(challenge => createChallengeCard(challenge)).join('');
}

function createChallengeCard(challenge) {
    const icons = {
        'sql_injection': '💉',
        'xss': '📜',
        'command_injection': '💻',
        'path_traversal': '📂',
        'xxe': '📋',
        'ssrf': '🌐',
        'deserialization': '📦',
        'csrf': '🔗',
        'lfi': '📄',
        'rfi': '🌍'
    };
    
    const difficultyColors = {
        'easy': 'success',
        'medium': 'warning',
        'hard': 'error'
    };
    
    const icon = icons[challenge.vulnerability_type] || '🎯';
    const color = difficultyColors[challenge.difficulty] || 'primary';
    const solvedClass = challenge.solved_by_user ? 'solved' : '';
    
    return `
        <div class="challenge-card ${solvedClass}" onclick="openChallenge('${challenge.id}')">
            <div class="challenge-icon">${icon}</div>
            <div class="challenge-header">
                <h3>${challenge.title}</h3>
                <span class="badge badge-${color}">${challenge.difficulty}</span>
            </div>
            <p class="challenge-desc">${challenge.description}</p>
            <div class="challenge-footer">
                <span class="points">${challenge.points} pts</span>
                <span class="solves">${challenge.solver_count || 0} solves</span>
            </div>
            ${challenge.solved_by_user ? '<div class="solved-badge">✓ SOLVED</div>' : ''}
        </div>
    `;
}

async function openChallenge(challengeId) {
    window.location.href = `/challenge/${challengeId}`;
}

// ==================== EXPLOIT INTERFACES ====================

const exploitInterfaces = {
    sql_injection: createSQLInterface,
    xss: createXSSInterface,
    command_injection: createCommandInterface,
    path_traversal: createFileInterface,
    xxe: createXMLInterface,
    lfi: createLFIInterface
};

function createSQLInterface(challenge) {
    return `
        <div class="exploit-interface sql-interface">
            <div class="interface-header">
                <h3>💉 SQL Injection Exploit</h3>
                <button class="btn btn-sm" onclick="showSQLHints()">
                    <i class="fas fa-lightbulb"></i> Hints
                </button>
            </div>
            
            <div class="sql-editor">
                <div class="editor-tabs">
                    <button class="tab active" onclick="switchTab('login')">Login Form</button>
                    <button class="tab" onclick="switchTab('search')">Search</button>
                </div>
                
                <div class="editor-content" id="loginForm">
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" id="sqlUsername" placeholder="admin' OR '1'='1' --" class="sql-input">
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" id="sqlPassword" placeholder="anything" class="sql-input">
                    </div>
                    <button class="btn btn-primary" onclick="exploitSQL('${challenge.id}')">
                        <i class="fas fa-bolt"></i> Exploit
                    </button>
                </div>
            </div>
            
            <div class="exploit-output" id="sqlOutput">
                <div class="terminal-header">Output</div>
                <div class="terminal-body">
                    <div class="prompt">Waiting for exploitation attempt...</div>
                </div>
            </div>
            
            <div class="sql-hints hidden" id="sqlHints">
                <h4>Common SQL Injection Payloads:</h4>
                <div class="hints-list">
                    <code onclick="useSQLPayload(this)">admin' --</code>
                    <code onclick="useSQLPayload(this)">admin' OR '1'='1' --</code>
                    <code onclick="useSQLPayload(this)">admin' OR 1=1 --</code>
                    <code onclick="useSQLPayload(this)">admin' UNION SELECT NULL--</code>
                </div>
            </div>
        </div>
    `;
}

function createXSSInterface(challenge) {
    return `
        <div class="exploit-interface xss-interface">
            <div class="interface-header">
                <h3>📜 XSS Exploit Playground</h3>
                <button class="btn btn-sm" onclick="showXSSHints()">
                    <i class="fas fa-lightbulb"></i> Payloads
                </button>
            </div>
            
            <div class="xss-editor">
                <div class="split-view">
                    <div class="editor-panel">
                        <h4>Input</h4>
                        <textarea id="xssPayload" placeholder="<script>alert('XSS')</script>" rows="10"></textarea>
                        <button class="btn btn-primary" onclick="exploitXSS('${challenge.id}')">
                            <i class="fas fa-code"></i> Test XSS
                        </button>
                    </div>
                    <div class="preview-panel">
                        <h4>Preview (Reflected)</h4>
                        <iframe id="xssPreview" sandbox="allow-scripts"></iframe>
                    </div>
                </div>
            </div>
            
            <div class="xss-payloads hidden" id="xssPayloads">
                <code onclick="useXSSPayload(this)">&lt;script&gt;alert(1)&lt;/script&gt;</code>
                <code onclick="useXSSPayload(this)">&lt;img src=x onerror=alert(1)&gt;</code>
                <code onclick="useXSSPayload(this)">&lt;svg onload=alert(1)&gt;</code>
            </div>
        </div>
    `;
}

function createCommandInterface(challenge) {
    return `
        <div class="exploit-interface cmd-interface">
            <div class="interface-header">
                <h3>💻 Command Injection Terminal</h3>
            </div>
            
            <div class="terminal">
                <div class="terminal-header">
                    <span class="terminal-dot red"></span>
                    <span class="terminal-dot yellow"></span>
                    <span class="terminal-dot green"></span>
                    <span class="terminal-title">Target System Shell</span>
                </div>
                <div class="terminal-body" id="cmdOutput">
                    <div class="terminal-line">
                        <span class="prompt">root@target:~#</span> Welcome to command injection challenge
                    </div>
                    <div class="terminal-line">
                        <span class="prompt">root@target:~#</span> Try: ping 127.0.0.1; cat /etc/passwd
                    </div>
                </div>
                <div class="terminal-input">
                    <span class="prompt">root@target:~#</span>
                    <input type="text" id="cmdInput" placeholder="ping 127.0.0.1" 
                           onkeypress="if(event.key==='Enter') exploitCommand('${challenge.id}')">
                    <button onclick="exploitCommand('${challenge.id}')">Execute</button>
                </div>
            </div>
        </div>
    `;
}

function createFileInterface(challenge) {
    return `
        <div class="exploit-interface file-interface">
            <div class="interface-header">
                <h3>📂 Path Traversal File Browser</h3>
            </div>
            
            <div class="file-browser">
                <div class="browser-toolbar">
                    <input type="text" id="filePath" placeholder="../../../etc/passwd" value="/">
                    <button class="btn btn-primary" onclick="exploitTraversal('${challenge.id}')">
                        <i class="fas fa-folder-open"></i> Read File
                    </button>
                </div>
                
                <div class="quick-paths">
                    <button onclick="setPath('/etc/passwd')">passwd</button>
                    <button onclick="setPath('../../../etc/shadow')">shadow</button>
                    <button onclick="setPath('../../config.ini')">config</button>
                    <button onclick="setPath('flag.txt')">flag.txt</button>
                </div>
                
                <div class="file-viewer" id="fileContent">
                    <div class="placeholder">Select a file to view its contents...</div>
                </div>
            </div>
        </div>
    `;
}

function createXMLInterface(challenge) {
    return `
        <div class="exploit-interface xml-interface">
            <div class="interface-header">
                <h3>📋 XXE Exploit Editor</h3>
            </div>
            
            <div class="xml-editor">
                <textarea id="xmlPayload" rows="15">
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>
  <data>&xxe;</data>
</root>
                </textarea>
                <button class="btn btn-primary" onclick="exploitXXE('${challenge.id}')">
                    <i class="fas fa-file-code"></i> Send XML
                </button>
            </div>
        </div>
    `;
}

function createLFIInterface(challenge) {
    return `
        <div class="exploit-interface lfi-interface">
            <div class="interface-header">
                <h3>📄 Local File Inclusion</h3>
            </div>
            
            <div class="lfi-panel">
                <div class="url-bar">
                    <span>http://target.com/page.php?file=</span>
                    <input type="text" id="lfiFile" placeholder="../../../../etc/passwd">
                    <button onclick="exploitLFI('${challenge.id}')">Include</button>
                </div>
                
                <div class="lfi-techniques">
                    <h4>Try these techniques:</h4>
                    <button onclick="useLFI('php://filter/convert.base64-encode/resource=index.php')">
                        PHP Filter
                    </button>
                    <button onclick="useLFI('/var/log/apache/access.log')">
                        Log Poisoning
                    </button>
                    <button onclick="useLFI('../../../../../proc/self/environ')">
                        /proc/self/environ
                    </button>
                </div>
            </div>
        </div>
    `;
}

// ==================== EXPLOIT FUNCTIONS ====================

async function exploitSQL(challengeId) {
    const username = document.getElementById('sqlUsername').value;
    const password = document.getElementById('sqlPassword').value;
    const outputEl = document.getElementById('sqlOutput');
    
    outputEl.innerHTML = '<div class="loading">Exploiting...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/vulnerabilities/sql-injection/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        displayExploitResult(data, 'sqlOutput');
        
        if (data.flag_system) {
            handleFlagDiscovery(challengeId, data);
        }
    } catch (error) {
        outputEl.innerHTML = '<div class="error">Exploit failed</div>';
    }
}

async function exploitXSS(challengeId) {
    const payload = document.getElementById('xssPayload').value;
    
    try {
        const response = await fetch(`${API_BASE}/vulnerabilities/xss?query=${encodeURIComponent(payload)}`);
        const data = await response.json();
        
        // Show in preview
        const preview = document.getElementById('xssPreview');
        preview.srcdoc = data.results || '';
        
        if (data.flag) {
            handleFlagDiscovery(challengeId, data);
        }
    } catch (error) {
        showNotification('XSS test failed', 'error');
    }
}

async function exploitCommand(challengeId) {
    const command = document.getElementById('cmdInput').value;
    const outputEl = document.getElementById('cmdOutput');
    
    const loadingLine = document.createElement('div');
    loadingLine.className = 'terminal-line';
    loadingLine.innerHTML = `<span class="prompt">root@target:~#</span> ${command}`;
    outputEl.appendChild(loadingLine);
    
    try {
        const response = await fetch(`${API_BASE}/vulnerabilities/command-injection/ping`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ host: command })
        });
        
        const data = await response.json();
        
        const resultLine = document.createElement('div');
        resultLine.className = 'terminal-line output';
        resultLine.textContent = data.output || data.message;
        outputEl.appendChild(resultLine);
        
        if (data.flag) {
            const flagLine = document.createElement('div');
            flagLine.className = 'terminal-line success';
            flagLine.textContent = `[+] Flag discovered: ${data.flag}`;
            outputEl.appendChild(flagLine);
            
            handleFlagDiscovery(challengeId, data);
        }
        
        document.getElementById('cmdInput').value = '';
    } catch (error) {
        const errorLine = document.createElement('div');
        errorLine.className = 'terminal-line error';
        errorLine.textContent = '[!] Command failed';
        outputEl.appendChild(errorLine);
    }
}

async function exploitTraversal(challengeId) {
    const filepath = document.getElementById('filePath').value;
    
    try {
        const response = await fetch(`${API_BASE}/vulnerabilities/directory-traversal/read?filepath=${encodeURIComponent(filepath)}`);
        const data = await response.json();
        
        const viewer = document.getElementById('fileContent');
        if (data.success) {
            viewer.innerHTML = `<pre>${data.content}</pre>`;
            
            if (data.flag_system) {
                handleFlagDiscovery(challengeId, data);
            }
        } else {
            viewer.innerHTML = `<div class="error">${data.message}</div>`;
        }
    } catch (error) {
        document.getElementById('fileContent').innerHTML = '<div class="error">Failed to read file</div>';
    }
}

// ==================== FLAG HANDLING ====================

function handleFlagDiscovery(challengeId, exploitData) {
    showFlagModal(challengeId, exploitData.flag_system || exploitData);
}

function showFlagModal(challengeId, flagData) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content flag-modal">
            <div class="flag-header">
                <h2>🎉 Flag Discovered!</h2>
                <span class="close" onclick="closeModal(this)">&times;</span>
            </div>
            
            <div class="encrypted-flag">
                <h3>Encrypted Flag:</h3>
                <code>${flagData.encrypted_flag || 'Encrypted data...'}</code>
            </div>
            
            <div class="flag-decrypt">
                <p>🔐 The flag is encrypted! Decrypt it with your exploitation proof:</p>
                <button class="btn btn-primary btn-large" onclick="decryptFlag('${challengeId}', '${JSON.stringify(flagData).replace(/'/g, "\\'")}')">
                    <i class="fas fa-unlock"></i> Decrypt Flag
                </button>
            </div>
            
            <div class="flag-info">
                <p>✅ Exploitation successful!</p>
                <p>⏱️ Decrypt within 1 hour</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

async function decryptFlag(challengeId, flagDataStr) {
    const flagData = JSON.parse(flagDataStr);
    
    try {
        const response = await fetch(`${API_BASE}/challenges/${challengeId}/decrypt-flag`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                encrypted_flag: flagData.encrypted_flag,
                exploitation_proof: flagData.exploitation_proof,
                timestamp: flagData.timestamp,
                verification_hash: flagData.verification_hash
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showDecryptedFlag(challengeId, data.flag);
        } else {
            showNotification(data.error || 'Decryption failed', 'error');
        }
    } catch (error) {
        showNotification('Decryption error', 'error');
    }
}

function showDecryptedFlag(challengeId, flag) {
    const modal = document.querySelector('.flag-modal');
    modal.innerHTML = `
        <div class="flag-header">
            <h2>🎊 Flag Decrypted!</h2>
        </div>
        
        <div class="decrypted-flag">
            <div class="flag-reveal">
                <code class="flag-text">${flag}</code>
                <button class="btn btn-sm" onclick="copyFlag('${flag}')">
                    <i class="fas fa-copy"></i> Copy
                </button>
            </div>
        </div>
        
        <div class="flag-submit">
            <input type="text" id="flagInput" value="${flag}" readonly>
            <button class="btn btn-primary btn-large" onclick="submitFlag('${challengeId}', '${flag}')">
                <i class="fas fa-flag"></i> Submit Flag
            </button>
        </div>
    `;
}

async function submitFlag(challengeId, flag) {
    try {
        const response = await fetch(`${API_BASE}/challenges/${challengeId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ flag })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showSuccessAnimation(data);
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        } else {
            showNotification('Incorrect flag', 'error');
        }
    } catch (error) {
        showNotification('Submission error', 'error');
    }
}

// ==================== UI HELPERS ====================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 10);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showSuccessAnimation(data) {
    const animation = document.createElement('div');
    animation.className = 'success-animation';
    animation.innerHTML = `
        <div class="success-content">
            <div class="success-icon">🎉</div>
            <h2>Challenge Solved!</h2>
            <p class="points">+${data.points_earned} points</p>
            <p class="total">Total Score: ${data.total_score}</p>
            ${data.badge ? `<div class="badge-earned">${data.badge}</div>` : ''}
        </div>
    `;
    document.body.appendChild(animation);
}

function closeModal(element) {
    element.closest('.modal').remove();
}

function copyFlag(flag) {
    navigator.clipboard.writeText(flag);
    showNotification('Flag copied!', 'success');
}

// ==================== INIT ====================

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    
    // Load page-specific content
    const path = window.location.pathname;
    
    if (path === '/challenges' || path === '/challenges.html') {
        loadChallenges();
    }
    
    if (path.startsWith('/challenge/')) {
        const challengeId = path.split('/')[2];
        loadChallengeDetail(challengeId);
    }
});
