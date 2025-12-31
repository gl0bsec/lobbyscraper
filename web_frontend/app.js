// Global state
let allInitiatives = [];
let filteredInitiatives = [];
let currentPage = 1;
const itemsPerPage = 20;

// DOM Elements - wrapped in DOMContentLoaded to ensure elements exist
let searchInput, clearSearch, topicFilter, feedbackFilter, startDate, endDate;
let searchButton, resultsContainer, resultsInfo, resultCount, loading, emptyState, downloadCSV;

// Initialize
async function init() {
    showLoading();
    try {
        const response = await fetch('/api/initiatives');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        allInitiatives = data.initiatives || [];

        console.log('Loaded initiatives:', allInitiatives.length); // Debug log

        populateFilters();
        hideLoading();
        showEmptyState();
    } catch (error) {
        console.error('Error loading initiatives:', error);
        hideLoading();
        resultsContainer.innerHTML = '<div class="error">Error loading initiatives. Please try again.</div>';
    }
}

// Populate filter dropdowns
function populateFilters() {
    // Topic filter
    const topics = new Map();
    allInitiatives.forEach(initiative => {
        if (initiative.topics) {
            initiative.topics.forEach(topic => {
                if (topic.code && topic.label) {
                    topics.set(topic.code, topic.label);
                }
            });
        }
    });

    [...topics.entries()].sort((a, b) => a[1].localeCompare(b[1])).forEach(([code, label]) => {
        const option = document.createElement('option');
        option.value = code;
        option.textContent = label;
        topicFilter.appendChild(option);
    });

    // Feedback status filter
    const feedbackStatuses = [...new Set(allInitiatives.map(i => i.feedbackStatus))].filter(Boolean).sort();
    feedbackStatuses.forEach(status => {
        const option = document.createElement('option');
        option.value = status;
        option.textContent = formatStatus(status);
        feedbackFilter.appendChild(option);
    });
}

// Format status text
function formatStatus(status) {
    if (!status) return 'N/A';
    return status.split('_').map(word =>
        word.charAt(0) + word.slice(1).toLowerCase()
    ).join(' ');
}

// Search and filter
function performSearch() {
    console.log('performSearch called'); // Debug log
    const searchTerm = searchInput.value.toLowerCase().trim();
    const selectedTopic = topicFilter.value;
    const selectedFeedback = feedbackFilter.value;
    const startDateValue = startDate.value;
    const endDateValue = endDate.value;

    console.log('Search params:', { searchTerm, selectedTopic, selectedFeedback, startDateValue, endDateValue }); // Debug log

    filteredInitiatives = allInitiatives.filter(initiative => {
        // Text search
        if (searchTerm) {
            const searchableText = [
                initiative.shortTitle,
                initiative.reference,
                initiative.id?.toString(),
                initiative.foreseenActType
            ].filter(Boolean).join(' ').toLowerCase();

            if (!searchableText.includes(searchTerm)) {
                return false;
            }
        }

        // Topic filter
        if (selectedTopic) {
            if (!initiative.topics || !initiative.topics.some(t => t.code === selectedTopic)) {
                return false;
            }
        }

        // Feedback status filter
        if (selectedFeedback && initiative.feedbackStatus !== selectedFeedback) {
            return false;
        }

        // Date range filter
        if (startDateValue || endDateValue) {
            const feedbackStart = initiative.feedbackStartDate ? new Date(initiative.feedbackStartDate) : null;
            const feedbackEnd = initiative.feedbackEndDate ? new Date(initiative.feedbackEndDate) : null;

            if (startDateValue) {
                const filterStart = new Date(startDateValue);
                if (!feedbackStart || feedbackStart < filterStart) {
                    return false;
                }
            }

            if (endDateValue) {
                const filterEnd = new Date(endDateValue);
                if (!feedbackEnd || feedbackEnd > filterEnd) {
                    return false;
                }
            }
        }

        return true;
    });

    console.log('Filtered results:', filteredInitiatives.length); // Debug log
    currentPage = 1;
    displayResults();
}

// Display results
function displayResults() {
    if (filteredInitiatives.length === 0) {
        showEmptyState();
        hideResultsInfo();
        return;
    }

    hideEmptyState();
    showResultsInfo();

    resultCount.textContent = filteredInitiatives.length;

    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, filteredInitiatives.length);
    const pageInitiatives = filteredInitiatives.slice(startIndex, endIndex);

    resultsContainer.innerHTML = pageInitiatives.map(initiative => createResultCard(initiative)).join('');

    // Add infinite scroll if more results
    if (endIndex < filteredInitiatives.length) {
        addInfiniteScroll();
    }
}

// Create result card
function createResultCard(initiative) {
    const topicLabels = initiative.topics ? initiative.topics.slice(0, 2).map(t => t.label).join(', ') : '';
    const topicCount = initiative.topics ? initiative.topics.length : 0;
    const topicDisplay = topicLabels + (topicCount > 2 ? ` +${topicCount - 2}` : '');

    // Determine feedback badge class
    let feedbackBadgeClass = 'badge-feedback disabled';
    if (initiative.feedbackStatus === 'OPEN') {
        feedbackBadgeClass = 'badge-feedback';
    } else if (initiative.feedbackStatus === 'CLOSED') {
        feedbackBadgeClass = 'badge-feedback closed';
    } else if (initiative.feedbackStatus === 'UPCOMING') {
        feedbackBadgeClass = 'badge-feedback planned';
    } else if (initiative.feedbackStatus === 'DISABLED') {
        feedbackBadgeClass = 'badge-feedback disabled';
    }

    const statusIcon = initiative.initiativeStatus === 'PUBLISHED' ? '📄' :
                      initiative.initiativeStatus === 'ADOPTED' ? '✓' :
                      initiative.initiativeStatus === 'PLANNED' ? '⏱' : '•';

    return `
        <div class="result-item" onclick="window.open('${initiative.initiativeUrl}', '_blank')">
            <div class="result-preview">${statusIcon}</div>

            <div class="result-content">
                <div class="result-title">${highlightText(escapeHtml(initiative.shortTitle || 'Untitled'))}</div>
                <div class="result-meta">
                    ${escapeHtml(initiative.reference || 'N/A')}
                    ${topicDisplay ? ` • ${escapeHtml(topicDisplay)}` : ''}
                </div>
            </div>

            <div class="result-feedback-status">
                ${initiative.feedbackStatus ? `
                    <span class="badge ${feedbackBadgeClass}">${formatStatus(initiative.feedbackStatus)}</span>
                ` : '<span class="badge badge-feedback disabled">N/A</span>'}
            </div>

            <div class="result-date">${initiative.feedbackEndDate ? formatDate(initiative.feedbackEndDate) : (initiative.feedbackStartDate ? formatDate(initiative.feedbackStartDate) : 'N/A')}</div>

            <div class="result-actions">
                <button class="action-btn" onclick="event.stopPropagation(); window.open('${initiative.initiativeUrl}', '_blank')" title="Open">→</button>
            </div>
        </div>
    `;
}

// Highlight search terms
function highlightText(text) {
    const searchTerm = searchInput.value.trim();
    if (!searchTerm) return text;

    const regex = new RegExp(`(${escapeRegex(searchTerm)})`, 'gi');
    return text.replace(regex, '<span class="highlight">$1</span>');
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeRegex(text) {
    return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function showLoading() {
    loading.style.display = 'block';
    resultsContainer.style.display = 'none';
    emptyState.style.display = 'none';
}

function hideLoading() {
    loading.style.display = 'none';
    resultsContainer.style.display = 'flex';
}

function showEmptyState() {
    emptyState.style.display = 'block';
    resultsContainer.innerHTML = '';
}

function hideEmptyState() {
    emptyState.style.display = 'none';
}

function showResultsInfo() {
    resultsInfo.style.display = 'block';
}

function hideResultsInfo() {
    resultsInfo.style.display = 'none';
}

// Infinite scroll
function addInfiniteScroll() {
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            currentPage++;
            const startIndex = (currentPage - 1) * itemsPerPage;
            const endIndex = Math.min(startIndex + itemsPerPage, filteredInitiatives.length);
            const pageInitiatives = filteredInitiatives.slice(startIndex, endIndex);

            resultsContainer.innerHTML += pageInitiatives.map(initiative => createResultCard(initiative)).join('');

            if (endIndex >= filteredInitiatives.length) {
                observer.disconnect();
            }
        }
    }, { threshold: 0.1 });

    const lastItem = resultsContainer.lastElementChild;
    if (lastItem) {
        observer.observe(lastItem);
    }
}


// Download CSV
function downloadFilteredCSV() {
    const data = filteredInitiatives.length > 0 ? filteredInitiatives : allInitiatives;
    const sample = data.slice(0, 100); // Limit to 100 for sample

    const headers = ['ID', 'Title', 'Reference', 'Status', 'Topics', 'Feedback Status', 'Start Date', 'End Date', 'URL'];
    const rows = sample.map(i => [
        i.id,
        i.shortTitle,
        i.reference,
        i.initiativeStatus,
        i.topics ? i.topics.map(t => t.label).join('; ') : '',
        i.feedbackStatus || '',
        i.feedbackStartDate || '',
        i.feedbackEndDate || '',
        i.initiativeUrl
    ]);

    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'initiatives_sample.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Initialize DOM elements and app when DOM is ready
function initDOMElements() {
    searchInput = document.getElementById('searchInput');
    clearSearch = document.getElementById('clearSearch');
    topicFilter = document.getElementById('topicFilter');
    feedbackFilter = document.getElementById('feedbackFilter');
    startDate = document.getElementById('startDate');
    endDate = document.getElementById('endDate');
    searchButton = document.getElementById('searchButton');
    resultsContainer = document.getElementById('resultsContainer');
    resultsInfo = document.getElementById('resultsInfo');
    resultCount = document.getElementById('resultCount');
    loading = document.getElementById('loading');
    emptyState = document.getElementById('emptyState');
    downloadCSV = document.getElementById('downloadCSV');

    console.log('DOM elements initialized:', {
        searchInput: !!searchInput,
        searchButton: !!searchButton,
        resultsContainer: !!resultsContainer
    });
}

// Setup event listeners
function setupEventListeners() {
    // Search input events
    searchInput.addEventListener('input', (e) => {
        clearSearch.style.display = e.target.value ? 'block' : 'none';
    });

    searchInput.addEventListener('keypress', (e) => {
        console.log('Keypress event:', e.key); // Debug
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });

    searchInput.addEventListener('keydown', (e) => {
        console.log('Keydown event:', e.key); // Debug
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });

    clearSearch.addEventListener('click', () => {
        searchInput.value = '';
        clearSearch.style.display = 'none';
        performSearch();
    });

    searchButton.addEventListener('click', () => {
        console.log('Search button clicked'); // Debug
        performSearch();
    });

    // Filter clear buttons
    document.querySelectorAll('.filter-clear').forEach(button => {
        button.addEventListener('click', (e) => {
            const filterType = e.target.dataset.filter;

            switch(filterType) {
                case 'topic':
                    topicFilter.value = '';
                    break;
                case 'feedback':
                    feedbackFilter.value = '';
                    break;
                case 'date':
                    startDate.value = '';
                    endDate.value = '';
                    break;
            }

            performSearch();
        });
    });

    // Auto-search on filter change
    topicFilter.addEventListener('change', performSearch);
    feedbackFilter.addEventListener('change', performSearch);
    startDate.addEventListener('change', performSearch);
    endDate.addEventListener('change', performSearch);

    downloadCSV.addEventListener('click', (e) => {
        e.preventDefault();
        downloadFilteredCSV();
    });

    console.log('Event listeners setup complete');
}

// Initialize the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initDOMElements();
        setupEventListeners();
        init();
    });
} else {
    // DOM already loaded
    initDOMElements();
    setupEventListeners();
    init();
}
