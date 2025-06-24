// Main application logic
let allChannels = [];
let filteredChannels = [];
let activeCategory = 'all';
let activeLanguage = 'all';
let activeTechs = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadChannelsData();
        setupEventListeners();
        updateStatistics();
        renderChannels();
        generateTechFilters();
    } catch (error) {
        console.error('Error initializing app:', error);
        showError('Error al cargar los datos');
    }
});

// Load channels data from the generated file
async function loadChannelsData() {
    // This assumes channels-data.js sets a global 'channelsData' variable
    if (typeof channelsData !== 'undefined') {
        allChannels = channelsData;
        filteredChannels = [...allChannels];
    } else {
        // Fallback: try to load from JSON
        try {
            const response = await fetch('data/channels.json');
            allChannels = await response.json();
            filteredChannels = [...allChannels];
        } catch (error) {
            console.error('Error loading channels data:', error);
            throw error;
        }
    }
}

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', debounce(handleSearch, 300));

    // Category filters
    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.addEventListener('click', handleCategoryFilter);
    });

    // Language filters
    document.querySelectorAll('[data-language]').forEach(btn => {
        btn.addEventListener('click', handleLanguageFilter);
    });
}

// Handle search input
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase().trim();
    
    if (searchTerm === '') {
        filteredChannels = [...allChannels];
    } else {
        filteredChannels = allChannels.filter(channel => {
            return (
                channel.name.toLowerCase().includes(searchTerm) ||
                channel.author.toLowerCase().includes(searchTerm) ||
                channel.role.toLowerCase().includes(searchTerm) ||
                channel.description.toLowerCase().includes(searchTerm) ||
                channel.tags.some(tag => tag.toLowerCase().includes(searchTerm))
            );
        });
    }
    
    applyFilters();
}

// Handle category filter
function handleCategoryFilter(event) {
    const button = event.target;
    activeCategory = button.dataset.filter;
    
    // Update UI
    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.classList.remove('active', 'btn-primary');
        btn.classList.add('btn-outline-primary');
    });
    button.classList.remove('btn-outline-primary');
    button.classList.add('active', 'btn-primary');
    
    applyFilters();
}

// Handle language filter
function handleLanguageFilter(event) {
    const button = event.target;
    activeLanguage = button.dataset.language;
    
    // Update UI
    document.querySelectorAll('[data-language]').forEach(btn => {
        btn.classList.remove('active', 'btn-success');
        btn.classList.add('btn-outline-success');
    });
    button.classList.remove('btn-outline-success');
    button.classList.add('active', 'btn-success');
    
    applyFilters();
}

// Handle technology filter
function handleTechFilter(event) {
    const button = event.target;
    const tech = button.dataset.tech;
    
    if (button.classList.contains('active')) {
        button.classList.remove('active', 'btn-info');
        button.classList.add('btn-outline-info');
        activeTechs = activeTechs.filter(t => t !== tech);
    } else {
        button.classList.remove('btn-outline-info');
        button.classList.add('active', 'btn-info');
        activeTechs.push(tech);
    }
    
    applyFilters();
}

// Apply all active filters
function applyFilters() {
    let filtered = [...filteredChannels];
    
    // Category filter
    if (activeCategory !== 'all') {
        filtered = filtered.filter(channel => channel.category === activeCategory);
    }
    
    // Language filter
    if (activeLanguage !== 'all') {
        filtered = filtered.filter(channel => channel.language === activeLanguage);
    }
    
    // Technology filters
    if (activeTechs.length > 0) {
        filtered = filtered.filter(channel => 
            activeTechs.every(tech => channel.tags.includes(tech))
        );
    }
    
    renderChannels(filtered);
}

// Render channels to the DOM
function renderChannels(channels = filteredChannels) {
    const container = document.getElementById('channelsList');
    
    if (channels.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <i class="bi bi-search fs-1 text-muted"></i>
                <h4 class="mt-3">No se encontraron canales</h4>
                <p>Intenta con otros términos de búsqueda o filtros</p>
            </div>
        `;
        return;
    }
    
    const channelsHTML = channels.map(channel => createChannelCard(channel)).join('');
    container.innerHTML = channelsHTML;
}

// Create a channel card HTML
function createChannelCard(channel) {
    const initials = channel.name.split(' ').map(word => word[0]).join('').substring(0, 2);
    const subscribersBadge = channel.subscribers ? 
        `<span class="stat-badge">
            <i class="bi bi-people-fill"></i>
            ${formatNumber(channel.subscribers)} suscriptores
        </span>` : '';
    
    const tagsHTML = channel.tags.map(tag => 
        `<span class="tag">${tag}</span>`
    ).join('');
    
    return `
        <div class="channel-card">
            <div class="channel-header">
                <div class="channel-avatar">${initials}</div>
                <div>
                    <h3 class="channel-title">${channel.name}</h3>
                    <p class="channel-role mb-0">${channel.role}</p>
                    <small class="text-muted">${channel.author}</small>
                </div>
            </div>
            
            <p class="mb-2">${channel.description}</p>
            
            <div class="channel-stats">
                ${subscribersBadge}
                <span class="stat-badge">
                    <i class="bi bi-translate"></i>
                    ${channel.language === 'es' ? 'Español' : 'English'}
                </span>
                <span class="stat-badge tag-category">
                    <i class="bi bi-folder"></i>
                    ${formatCategoryName(channel.category)}
                </span>
            </div>
            
            <div class="tags-container">
                ${tagsHTML}
            </div>
            
            <div class="btn-links">
                <a href="${channel.youtube}" target="_blank" class="btn-channel btn-youtube">
                    <i class="bi bi-youtube me-1"></i>
                    Ver Canal
                </a>
                ${channel.linkedin ? `
                    <a href="${channel.linkedin}" target="_blank" class="btn-channel btn-linkedin">
                        <i class="bi bi-linkedin me-1"></i>
                        LinkedIn
                    </a>
                ` : ''}
            </div>
        </div>
    `;
}

// Update statistics
function updateStatistics() {
    document.getElementById('totalChannels').textContent = allChannels.length;
    document.getElementById('spanishChannels').textContent = 
        allChannels.filter(c => c.language === 'es').length;
    document.getElementById('englishChannels').textContent = 
        allChannels.filter(c => c.language === 'en').length;
}

// Generate technology filters dynamically
function generateTechFilters() {
    const techsSet = new Set();
    allChannels.forEach(channel => {
        channel.tags.forEach(tag => techsSet.add(tag));
    });
    
    const techsArray = Array.from(techsSet).sort();
    const container = document.getElementById('techFilters');
    
    const techsHTML = techsArray.map(tech => `
        <button class="btn btn-outline-info filter-btn" data-tech="${tech}">
            ${tech}
        </button>
    `).join('');
    
    container.innerHTML = techsHTML;
    
    // Add event listeners
    container.querySelectorAll('[data-tech]').forEach(btn => {
        btn.addEventListener('click', handleTechFilter);
    });
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatNumber(num) {
    if (!num) return '0';
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function formatCategoryName(category) {
    const categoryNames = {
        'platform-engineering': 'Platform Engineering',
        'devsecops': 'DevSecOps',
        'containers': 'Containers',
        'cloud': 'Cloud',
        'automation': 'Automation',
        'homelab': 'HomeLab'
    };
    return categoryNames[category] || category;
}

function showError(message) {
    const container = document.getElementById('channelsList');
    container.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            ${message}
        </div>
    `;
} 