document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and content
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Show corresponding content
            const tabName = tab.getAttribute('data-tab');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });

    // Chat functionality
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});

let sessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);

function appendMessage(role, content) {
    const chatHistory = document.getElementById('chat-history');
    if (!chatHistory) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', role);
    messageDiv.textContent = content;
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function displayEntities(entities) {
    const container = document.getElementById('entities-container');
    if (!container) return;
    
    container.innerHTML = '<h3>Detected Entities</h3>';
    
    for (const [key, value] of Object.entries(entities)) {
        const entityDiv = document.createElement('div');
        entityDiv.innerHTML = `<strong>${key}:</strong> ${value}`;
        container.appendChild(entityDiv);
    }
}

function displayClauses(clauses) {
    const container = document.getElementById('clauses-container');
    if (!container) return;
    
    container.innerHTML = '<h3>Relevant Clauses</h3>';
    
    clauses.forEach(clause => {
        const clauseDiv = document.createElement('div');
        clauseDiv.classList.add('clause');
        clauseDiv.innerHTML = `
            <p><strong>Document:</strong> ${clause.document_id}</p>
            <p><strong>Page:</strong> ${clause.page_number}</p>
            <p>${clause.clause_text}</p>
        `;
        container.appendChild(clauseDiv);
    });
}

function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;
    
    appendMessage('user', message);
    input.value = '';
    
    fetch('/api/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            question: message,
            session_id: sessionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            appendMessage('assistant', 'Error: ' + data.error);
        } else {
            appendMessage('assistant', data.answer);
            if (data.entities) displayEntities(data.entities);
            if (data.relevant_clauses) displayClauses(data.relevant_clauses);
        }
    })
    .catch(error => {
        appendMessage('assistant', 'An error occurred. Please try again.');
        console.error('Error:', error);
    });
}

function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file');
        return;
    }

    const formData = new FormData();
    formData.append('source_type', 'file');
    formData.append('source', file);
    
    uploadDocument(formData);
}

function uploadURL() {
    const urlInput = document.getElementById('url-input');
    const url = urlInput.value.trim();
    if (!url) {
        alert('Please enter a URL');
        return;
    }
    
    const data = {
        source_type: 'url',
        source: url
    };
    
    uploadDocument(JSON.stringify(data));
}

function uploadDocument(data) {
    const statusDiv = document.getElementById('upload-status');
    if (!statusDiv) return;
    
    statusDiv.textContent = 'Processing...';
    
    const isFormData = data instanceof FormData;
    const url = '/api/ingest/';
    
    fetch(url, {
        method: 'POST',
        body: isFormData ? data : JSON.stringify(data),
        headers: isFormData ? {
            'X-CSRFToken': getCookie('csrftoken')
        } : {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            statusDiv.textContent = `Success! Document ID: ${data.document_id}, Chunks: ${data.chunks}`;
        } else {
            statusDiv.textContent = `Error: ${data.error || 'Unknown error'}`;
        }
    })
    .catch(error => {
        statusDiv.textContent = 'Upload failed. Please try again.';
        console.error('Error:', error);
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}