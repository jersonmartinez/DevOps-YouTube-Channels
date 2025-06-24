// Modern DevOps YouTube Channels App
let allChannels = [];
let filteredChannels = [];
let favorites = JSON.parse(localStorage.getItem('devops-favorites') || '[]');
let viewMode = 'grid';
let isDarkTheme = localStorage.getItem('devops-theme') === 'dark';

// Active filters
let activeFilters = {
    category: 'all',
    language: 'all',
    techs: [],
    subscriberRange: 'all',
    sortBy: 'name-asc'
};

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    initializeTheme();
    await loadChannelsData();
    setupEventListeners();
    updateStatistics();
    generateTechFilters();
    
    // Add DevOps With Jerson to channels if not exists
    ensureFeaturedChannel();
    
    renderChannels();
    updateFavoritesCount();
    hideLoadingScreen();
});

// Ensure featured channel exists
function ensureFeaturedChannel() {
    const featuredChannel = {
        name: 'DevOps With Jerson',
        author: 'Jerson',
        role: 'DevOps Engineer & Content Creator',
        youtube: 'https://www.youtube.com/@DevOpsWithJerson',
        channelId: 'DevOpsWithJerson',
        linkedin: null,
        category: 'platform-engineering',
        language: 'es',
        tags: ['devops', 'kubernetes', 'docker', 'cicd', 'cloud', 'terraform'],
        description: 'Contenido especializado en las últimas tecnologías y mejores prácticas de DevOps. Desde conceptos básicos hasta implementaciones avanzadas en producción.',
        subscribers: null,
        featured: true
    };
    
    // Check if already exists
    const exists = allChannels.some(ch => ch.channelId === 'DevOpsWithJerson');
    if (!exists) {
        allChannels.unshift(featuredChannel);
    } else {
        // Mark as featured
        const index = allChannels.findIndex(ch => ch.channelId === 'DevOpsWithJerson');
        if (index !== -1) {
            allChannels[index].featured = true;
            // Move to start
            const channel = allChannels.splice(index, 1)[0];
            allChannels.unshift(channel);
        }
    }
}

// Theme Management
function initializeTheme() {
    if (isDarkTheme) {
        document.body.setAttribute('data-theme', 'dark');
        updateThemeIcon();
    }
}

function toggleTheme() {
    isDarkTheme = !isDarkTheme;
    if (isDarkTheme) {
        document.body.setAttribute('data-theme', 'dark');
    } else {
        document.body.removeAttribute('data-theme');
    }
    localStorage.setItem('devops-theme', isDarkTheme ? 'dark' : 'light');
    updateThemeIcon();
}

function updateThemeIcon() {
    const icon = document.querySelector('#themeToggle i');
    icon.className = isDarkTheme ? 'bi bi-sun' : 'bi bi-moon-stars';
}

// Load channels data
async function loadChannelsData() {
    try {
        if (typeof channelsData !== 'undefined') {
            allChannels = [...channelsData];
            filteredChannels = [...allChannels];
        } else {
            // Fallback to JSON
            const response = await fetch('data/channels.json');
            allChannels = await response.json();
            filteredChannels = [...allChannels];
        }
    } catch (error) {
        console.error('Error loading channels:', error);
        showError('Error al cargar los canales');
    }
}

// Setup event listeners
function setupEventListeners() {
    // Search
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    
    // Clear search
    document.getElementById('clearSearch').addEventListener('click', clearSearch);
    
    // Search suggestions
    document.querySelectorAll('.suggestion-tag').forEach(tag => {
        tag.addEventListener('click', () => {
            searchInput.value = tag.dataset.search;
            handleSearch({ target: searchInput });
        });
    });
    
    // Category filters
    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.addEventListener('click', handleCategoryFilter);
    });
    
    // Language filters
    document.querySelectorAll('[data-language]').forEach(btn => {
        btn.addEventListener('click', handleLanguageFilter);
    });
    
    // Subscriber range
    document.getElementById('subscriberRange').addEventListener('change', handleSubscriberFilter);
    
    // Sort
    document.getElementById('sortBy').addEventListener('change', handleSort);
    
    // View mode
    document.querySelectorAll('[data-view]').forEach(btn => {
        btn.addEventListener('click', handleViewChange);
    });
    
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    
    // Favorites
    document.getElementById('favoritesBtn').addEventListener('click', toggleFavoritesSidebar);
    
    // Reset filters
    document.getElementById('resetFilters').addEventListener('click', resetAllFilters);
    
    // Back to top
    window.addEventListener('scroll', handleScroll);
    document.getElementById('backToTop').addEventListener('click', scrollToTop);
}

// Search functionality
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase().trim();
    const clearBtn = document.getElementById('clearSearch');
    
    clearBtn.style.display = searchTerm ? 'block' : 'none';
    
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

function clearSearch() {
    document.getElementById('searchInput').value = '';
    document.getElementById('clearSearch').style.display = 'none';
    filteredChannels = [...allChannels];
    applyFilters();
}

// Filter handlers
function handleCategoryFilter(event) {
    const button = event.target.closest('button');
    activeFilters.category = button.dataset.filter;
    
    document.querySelectorAll('[data-filter]').forEach(btn => {
        btn.classList.remove('active');
    });
    button.classList.add('active');
    
    applyFilters();
}

function handleLanguageFilter(event) {
    const button = event.target.closest('button');
    activeFilters.language = button.dataset.language;
    
    document.querySelectorAll('[data-language]').forEach(btn => {
        btn.classList.remove('active');
    });
    button.classList.add('active');
    
    applyFilters();
}

function handleTechFilter(event) {
    const button = event.target.closest('button');
    const tech = button.dataset.tech;
    
    if (button.classList.contains('active')) {
        button.classList.remove('active');
        activeFilters.techs = activeFilters.techs.filter(t => t !== tech);
    } else {
        button.classList.add('active');
        activeFilters.techs.push(tech);
    }
    
    applyFilters();
}

function handleSubscriberFilter(event) {
    activeFilters.subscriberRange = event.target.value;
    applyFilters();
}

function handleSort(event) {
    activeFilters.sortBy = event.target.value;
    applyFilters();
}

// Apply all filters
function applyFilters() {
    let filtered = [...filteredChannels];
    
    // Category filter
    if (activeFilters.category !== 'all') {
        filtered = filtered.filter(channel => channel.category === activeFilters.category);
    }
    
    // Language filter
    if (activeFilters.language !== 'all') {
        filtered = filtered.filter(channel => channel.language === activeFilters.language);
    }
    
    // Tech filters
    if (activeFilters.techs.length > 0) {
        filtered = filtered.filter(channel => 
            activeFilters.techs.every(tech => channel.tags.includes(tech))
        );
    }
    
    // Subscriber range filter
    if (activeFilters.subscriberRange !== 'all') {
        filtered = filtered.filter(channel => {
            const subs = channel.subscribers || 0;
            switch (activeFilters.subscriberRange) {
                case '0-10k': return subs < 10000;
                case '10k-50k': return subs >= 10000 && subs < 50000;
                case '50k-100k': return subs >= 50000 && subs < 100000;
                case '100k-500k': return subs >= 100000 && subs < 500000;
                case '500k+': return subs >= 500000;
                default: return true;
            }
        });
    }
    
    // Sort
    filtered = sortChannels(filtered, activeFilters.sortBy);
    
    // Update UI
    renderChannels(filtered);
    updateActiveFilters();
    updateResultsCount(filtered.length);
}

// Sort channels
function sortChannels(channels, sortBy) {
    const sorted = [...channels];
    
    switch (sortBy) {
        case 'name-asc':
            return sorted.sort((a, b) => a.name.localeCompare(b.name));
        case 'name-desc':
            return sorted.sort((a, b) => b.name.localeCompare(a.name));
        case 'subs-desc':
            return sorted.sort((a, b) => (b.subscribers || 0) - (a.subscribers || 0));
        case 'subs-asc':
            return sorted.sort((a, b) => (a.subscribers || 0) - (b.subscribers || 0));
        case 'recent':
            // For now, just reverse the order
            return sorted.reverse();
        default:
            return sorted;
    }
}

// Render channels
function renderChannels(channels = filteredChannels) {
    const container = document.getElementById('channelsList');
    const noResults = document.getElementById('noResults');
    
    if (channels.length === 0) {
        container.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    container.style.display = viewMode === 'grid' ? 'grid' : 'block';
    container.className = viewMode === 'grid' ? 'channels-grid' : 'channels-list';
    noResults.style.display = 'none';
    
    const channelsHTML = channels.map((channel, index) => 
        createChannelCard(channel, index)
    ).join('');
    
    container.innerHTML = channelsHTML;
    
    // Add event listeners to new elements
    container.querySelectorAll('.btn-favorite').forEach(btn => {
        btn.addEventListener('click', (e) => toggleFavorite(e, btn.dataset.channelId));
    });
    
    container.querySelectorAll('.btn-video').forEach(btn => {
        btn.addEventListener('click', () => showLatestVideo(btn.dataset.channelId));
    });
}

// Create channel card
function createChannelCard(channel, index) {
    const initials = channel.name.split(' ').map(word => word[0]).join('').substring(0, 2).toUpperCase();
    const isFavorite = favorites.includes(channel.channelId);
    const subscribersBadge = channel.subscribers ? 
        `<span class="stat-badge">
            <i class="bi bi-people-fill"></i>
            ${formatNumber(channel.subscribers)}
        </span>` : '';
    
    const tagsHTML = channel.tags.slice(0, 5).map(tag => 
        `<span class="tag">#${tag}</span>`
    ).join('');
    
    const featuredBadge = channel.featured ? 
        `<div class="featured-badge" style="position: absolute; top: 0.5rem; right: 0.5rem; font-size: 0.75rem;">
            <i class="bi bi-star-fill"></i> Destacado
        </div>` : '';
    
    return `
        <div class="channel-card" style="animation-delay: ${index * 0.05}s">
            ${featuredBadge}
            <div class="channel-header">
                <div class="channel-avatar">${initials}</div>
                <div class="channel-info">
                    <h3 class="channel-title">${channel.name}</h3>
                    <p class="channel-author">${channel.author}</p>
                </div>
                <button class="btn-favorite ${isFavorite ? 'active' : ''}" data-channel-id="${channel.channelId}">
                    <i class="bi ${isFavorite ? 'bi-heart-fill' : 'bi-heart'}"></i>
                </button>
            </div>
            
            <p class="channel-description">${channel.description}</p>
            
            <div class="channel-stats">
                ${subscribersBadge}
                <span class="stat-badge">
                    <i class="bi bi-translate"></i>
                    ${channel.language === 'es' ? 'Español' : 'English'}
                </span>
                <span class="stat-badge">
                    <i class="bi bi-folder"></i>
                    ${formatCategoryName(channel.category)}
                </span>
            </div>
            
            <div class="channel-tags">
                ${tagsHTML}
            </div>
            
            <div class="channel-actions">
                <a href="${channel.youtube}" target="_blank" class="btn-channel btn-youtube">
                    <i class="bi bi-youtube me-1"></i>
                    Ver Canal
                </a>
                <button class="btn-channel btn-video" data-channel-id="${channel.channelId}">
                    <i class="bi bi-play-circle me-1"></i>
                    Último Video
                </button>
                ${channel.linkedin ? `
                    <a href="${channel.linkedin}" target="_blank" class="btn-channel btn-video">
                        <i class="bi bi-linkedin"></i>
                    </a>
                ` : ''}
            </div>
        </div>
    `;
}

// Show latest video
async function showLatestVideo(channelId) {
    const modal = new bootstrap.Modal(document.getElementById('videoModal'));
    const container = document.getElementById('videoContainer');
    const title = document.getElementById('videoModalTitle');
    
    // Show loading
    container.innerHTML = '<div class="text-center p-5"><div class="spinner-border" role="status"></div></div>';
    title.textContent = 'Cargando video...';
    modal.show();
    
    try {
        // For now, just show a placeholder
        // In a real implementation, you would fetch the latest video
        const channel = allChannels.find(ch => ch.channelId === channelId);
        
        // Simulate loading
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // For demo, show channel trailer or a sample video
        const videoId = getChannelVideoId(channelId);
        
        container.innerHTML = `
            <iframe 
                src="https://www.youtube.com/embed/${videoId}?autoplay=1" 
                title="YouTube video player" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
            </iframe>
        `;
        
        title.textContent = `Último video de ${channel.name}`;
    } catch (error) {
        container.innerHTML = '<div class="alert alert-danger m-3">Error al cargar el video</div>';
    }
}

// Get sample video ID for channel (in real app, this would be fetched)
function getChannelVideoId(channelId) {
    // Sample video IDs for demo
    const sampleVideos = {
        'DevOpsWithJerson': 'dQw4w9WgXcQ', // Replace with actual video ID
        'default': 'dQw4w9WgXcQ'
    };
    
    return sampleVideos[channelId] || sampleVideos.default;
}

// Favorites management
function toggleFavorite(event, channelId) {
    event.stopPropagation();
    
    const index = favorites.indexOf(channelId);
    if (index === -1) {
        favorites.push(channelId);
    } else {
        favorites.splice(index, 1);
    }
    
    localStorage.setItem('devops-favorites', JSON.stringify(favorites));
    updateFavoritesCount();
    
    // Update button
    const btn = event.target.closest('.btn-favorite');
    const icon = btn.querySelector('i');
    
    if (index === -1) {
        btn.classList.add('active');
        icon.className = 'bi bi-heart-fill';
    } else {
        btn.classList.remove('active');
        icon.className = 'bi bi-heart';
    }
    
    updateFavoritesSidebar();
}

function updateFavoritesCount() {
    document.getElementById('favoritesCount').textContent = favorites.length;
}

function toggleFavoritesSidebar() {
    const sidebar = document.getElementById('favoritesSidebar');
    sidebar.classList.toggle('show');
    updateFavoritesSidebar();
}

function closeFavorites() {
    document.getElementById('favoritesSidebar').classList.remove('show');
}

function updateFavoritesSidebar() {
    const body = document.getElementById('favoritesBody');
    
    if (favorites.length === 0) {
        body.innerHTML = '<p class="text-muted text-center py-5">No tienes canales favoritos aún</p>';
        return;
    }
    
    const favoriteChannels = allChannels.filter(ch => favorites.includes(ch.channelId));
    const html = favoriteChannels.map(channel => `
        <div class="channel-card mb-3">
            <div class="channel-header">
                <div class="channel-avatar" style="width: 40px; height: 40px; font-size: 1rem;">
                    ${channel.name.substring(0, 2).toUpperCase()}
                </div>
                <div class="channel-info">
                    <h6 class="channel-title mb-0" style="font-size: 1rem;">${channel.name}</h6>
                    <p class="channel-author mb-0" style="font-size: 0.813rem;">${channel.author}</p>
                </div>
            </div>
            <div class="channel-actions mt-2">
                <a href="${channel.youtube}" target="_blank" class="btn btn-sm btn-youtube">
                    <i class="bi bi-youtube me-1"></i>Ver
                </a>
                <button class="btn btn-sm btn-outline-danger" onclick="toggleFavorite(event, '${channel.channelId}')">
                    <i class="bi bi-heart-fill"></i>
                </button>
            </div>
        </div>
    `).join('');
    
    body.innerHTML = html;
}

// View mode
function handleViewChange(event) {
    const button = event.target.closest('button');
    viewMode = button.dataset.view;
    
    document.querySelectorAll('[data-view]').forEach(btn => {
        btn.classList.remove('active');
    });
    button.classList.add('active');
    
    renderChannels(filteredChannels);
}

// Update statistics
function updateStatistics() {
    // Total channels
    document.getElementById('totalChannels').textContent = allChannels.length;
    
    // Total technologies
    const allTechs = new Set();
    allChannels.forEach(channel => {
        channel.tags.forEach(tag => allTechs.add(tag));
    });
    document.getElementById('totalTech').textContent = allTechs.size;
    
    // Total subscribers
    const totalSubs = allChannels.reduce((sum, channel) => sum + (channel.subscribers || 0), 0);
    document.getElementById('totalSubs').textContent = formatNumber(totalSubs);
    
    // Last update
    const lastUpdate = new Date().toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    document.getElementById('lastUpdate').textContent = lastUpdate;
    
    // Update featured channel stats
    updateFeaturedStats();
}

// Update featured channel statistics
async function updateFeaturedStats() {
    const featuredChannel = allChannels.find(ch => ch.channelId === 'DevOpsWithJerson');
    if (featuredChannel && featuredChannel.subscribers) {
        document.getElementById('featuredSubs').textContent = formatNumber(featuredChannel.subscribers);
    } else {
        document.getElementById('featuredSubs').textContent = 'Próximamente';
    }
}

// Generate technology filters
function generateTechFilters() {
    const techsMap = new Map();
    
    allChannels.forEach(channel => {
        channel.tags.forEach(tag => {
            techsMap.set(tag, (techsMap.get(tag) || 0) + 1);
        });
    });
    
    // Sort by frequency and take top 15
    const sortedTechs = Array.from(techsMap.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15);
    
    const container = document.getElementById('techFilters');
    const html = sortedTechs.map(([tech, count]) => `
        <button class="filter-tag" data-tech="${tech}">
            ${tech} <span class="text-muted">(${count})</span>
        </button>
    `).join('');
    
    container.innerHTML = html;
    
    // Add event listeners
    container.querySelectorAll('[data-tech]').forEach(btn => {
        btn.addEventListener('click', handleTechFilter);
    });
}

// Update active filters display
function updateActiveFilters() {
    const section = document.getElementById('activeFiltersSection');
    const list = document.getElementById('activeFiltersList');
    const activeFiltersList = [];
    
    if (activeFilters.category !== 'all') {
        activeFiltersList.push({
            type: 'category',
            value: activeFilters.category,
            label: formatCategoryName(activeFilters.category)
        });
    }
    
    if (activeFilters.language !== 'all') {
        activeFiltersList.push({
            type: 'language',
            value: activeFilters.language,
            label: activeFilters.language === 'es' ? 'Español' : 'English'
        });
    }
    
    activeFilters.techs.forEach(tech => {
        activeFiltersList.push({
            type: 'tech',
            value: tech,
            label: tech
        });
    });
    
    if (activeFilters.subscriberRange !== 'all') {
        activeFiltersList.push({
            type: 'subscriberRange',
            value: activeFilters.subscriberRange,
            label: getSubscriberRangeLabel(activeFilters.subscriberRange)
        });
    }
    
    if (activeFiltersList.length === 0) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'block';
    
    const html = activeFiltersList.map(filter => `
        <span class="active-filter-tag">
            ${filter.label}
            <button onclick="removeFilter('${filter.type}', '${filter.value}')">
                <i class="bi bi-x"></i>
            </button>
        </span>
    `).join('');
    
    list.innerHTML = html;
}

// Remove filter
window.removeFilter = function(type, value) {
    switch (type) {
        case 'category':
            activeFilters.category = 'all';
            document.querySelector('[data-filter="all"]').click();
            break;
        case 'language':
            activeFilters.language = 'all';
            document.querySelector('[data-language="all"]').click();
            break;
        case 'tech':
            const techBtn = document.querySelector(`[data-tech="${value}"]`);
            if (techBtn) techBtn.click();
            break;
        case 'subscriberRange':
            document.getElementById('subscriberRange').value = 'all';
            activeFilters.subscriberRange = 'all';
            applyFilters();
            break;
    }
};

// Reset all filters
function resetAllFilters() {
    // Reset filter values
    activeFilters = {
        category: 'all',
        language: 'all',
        techs: [],
        subscriberRange: 'all',
        sortBy: 'name-asc'
    };
    
    // Reset UI
    document.querySelector('[data-filter="all"]').click();
    document.querySelector('[data-language="all"]').click();
    document.getElementById('subscriberRange').value = 'all';
    document.getElementById('sortBy').value = 'name-asc';
    
    // Clear tech filters
    document.querySelectorAll('[data-tech].active').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Clear search
    clearSearch();
}

window.resetAllFilters = resetAllFilters;

// Update results count
function updateResultsCount(count) {
    document.getElementById('resultsCount').textContent = count;
}

// Scroll handling
function handleScroll() {
    const backToTop = document.getElementById('backToTop');
    if (window.scrollY > 300) {
        backToTop.classList.add('show');
    } else {
        backToTop.classList.remove('show');
    }
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
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
        return (num / 1000000).toFixed(1).replace('.0', '') + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1).replace('.0', '') + 'K';
    }
    return num.toString();
}

function formatCategoryName(category) {
    const names = {
        'platform-engineering': 'Platform Engineering',
        'devsecops': 'DevSecOps',
        'containers': 'Containers',
        'cloud': 'Cloud',
        'automation': 'Automation',
        'homelab': 'HomeLab'
    };
    return names[category] || category;
}

function getSubscriberRangeLabel(range) {
    const labels = {
        '0-10k': 'Menos de 10K',
        '10k-50k': '10K - 50K',
        '50k-100k': '50K - 100K',
        '100k-500k': '100K - 500K',
        '500k+': 'Más de 500K'
    };
    return labels[range] || range;
}

function hideLoadingScreen() {
    setTimeout(() => {
        const loadingScreen = document.getElementById('loadingScreen');
        loadingScreen.classList.add('fade-out');
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 500);
    }, 500);
}

function showError(message) {
    const container = document.getElementById('channelsList');
    container.innerHTML = `
        <div class="alert alert-danger text-center" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            ${message}
        </div>
    `;
}

// Make showLatestVideo available globally
window.showLatestVideo = showLatestVideo;

// About modal
window.showAbout = function() {
    alert('DevOps YouTube Channels - Una colección curada de los mejores canales para aprender DevOps.\n\nCreado con ❤️ por la comunidad DevOps.');
}; 