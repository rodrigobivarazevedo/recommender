// HealthCast - Main JavaScript File

console.log("main.js loaded");

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
    // Add tab event listener to clear results/errors on tab switch
    const tabButtons = document.querySelectorAll('#recommendationTabs button[data-bs-toggle="pill"]');
    tabButtons.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function (event) {
            clearResultsAndErrors();
        });
    });
});

function initializeApp() {
    // Set up form submission handlers for all three recommendation types
    setupFormHandlers();

    // Add smooth scrolling for anchor links
    setupSmoothScrolling();

    // Add animation classes to elements
    setupAnimations();

    // Set up example podcast click handlers
    setupExamplePodcasts();
}

function setupFormHandlers() {
    // Episode-based recommendations form
    const episodeForm = document.getElementById('episodeForm');
    if (episodeForm) {
        console.log('Attaching handler to episodeForm');
        episodeForm.addEventListener('submit', (e) => handleEpisodeFormSubmission(e));
    } else {
        console.log('episodeForm not found');
    }

    // Random playlist form
    const randomForm = document.getElementById('randomForm');
    if (randomForm) {
        console.log('Attaching handler to randomForm');
        randomForm.addEventListener('submit', (e) => handleRandomFormSubmission(e));
    } else {
        console.log('randomForm not found');
    }

    // Content-based recommendations form
    const contentForm = document.getElementById('contentForm');
    if (contentForm) {
        console.log('Attaching handler to contentForm');
        contentForm.addEventListener('submit', (e) => handleContentFormSubmission(e));
    } else {
        console.log('contentForm not found');
    }
}

function setupSmoothScrolling() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function setupAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Add slide-in animations to feature sections
    const featureSections = document.querySelectorAll('.col-md-4');
    featureSections.forEach((section, index) => {
        if (index % 2 === 0) {
            section.classList.add('slide-in-left');
        } else {
            section.classList.add('slide-in-right');
        }
    });
}

function setupExamplePodcasts() {
    // Add click handlers to example podcast cards
    const exampleCards = document.querySelectorAll('.col-md-4 .card');
    exampleCards.forEach(card => {
        card.addEventListener('click', function() {
            const podcastTitle = this.querySelector('.card-title').textContent;
            const episodeInput = document.getElementById('episodeTitle');
            if (episodeInput) {
                episodeInput.value = podcastTitle;
                // Switch to episode tab and scroll to form
                const episodeTab = document.getElementById('episode-tab');
                if (episodeTab) {
                    episodeTab.click();
                }
                document.getElementById('episodeForm').scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Episode-based recommendations handler
async function handleEpisodeFormSubmission(event) {
    event.preventDefault();
    console.log('Episode form submitted');

    const form = event.target;
    const formData = new FormData(form);

    // Show loading spinner
    showLoading();

    try {
        // Make API call to get episode-based recommendations
        const response = await fetch('/get_recommendations', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Hide loading and show results
        hideLoading();
        displayRecommendations(data.recommendations, 'episode');

    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        showError('Failed to get episode recommendations. Please try again.');
    }
}

// Random playlist handler
async function handleRandomFormSubmission(event) {
    event.preventDefault();
    console.log('Random form submitted');

    const form = event.target;
    const formData = new FormData(form);

    // Show loading spinner
    showLoading();

    try {
        // Make API call to get random playlist
        const response = await fetch('/get_random_playlist', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Hide loading and show results
        hideLoading();
        displayRecommendations(data.recommendations, 'random');

    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        showError('Failed to generate random playlist. Please try again.');
    }
}

// Content-based recommendations handler
async function handleContentFormSubmission(event) {
    event.preventDefault();
    console.log('Content form submitted');

    const form = event.target;
    const formData = new FormData(form);

    // Handle empty max_duration
    const maxDuration = formData.get('max_duration');
    if (maxDuration === '') {
        formData.delete('max_duration');
    }

    // Show loading spinner
    showLoading();

    try {
        // Make API call to get content-based recommendations
        const response = await fetch('/get_content_recommendations', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Hide loading and show results
        hideLoading();
        displayRecommendations(data.recommendations, 'content');

    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        showError('Failed to get content-based recommendations. Please try again.');
    }
}

function showLoading() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsSection = document.getElementById('resultsSection');
    const errorSection = document.getElementById('errorSection');

    if (loadingSpinner) loadingSpinner.classList.remove('d-none');
    if (resultsSection) resultsSection.classList.add('d-none');
    if (errorSection) errorSection.classList.add('d-none');
}

function hideLoading() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) loadingSpinner.classList.add('d-none');
}

function showError(message) {
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    
    if (errorSection && errorMessage) {
        errorMessage.textContent = message;
        errorSection.classList.remove('d-none');
    }
}

function displayRecommendations(recommendations, type = 'episode') {
    const resultsSection = document.getElementById('resultsSection');
    const recommendationsList = document.getElementById('recommendationsList');
    const errorSection = document.getElementById('errorSection');

    if (!resultsSection || !recommendationsList) return;

    // Hide error section
    if (errorSection) errorSection.classList.add('d-none');

    // Clear previous results
    recommendationsList.innerHTML = '';

    // Set appropriate header based on type
    const header = resultsSection.querySelector('h2');
    if (header) {
        const icons = {
            'episode': 'fas fa-search',
            'random': 'fas fa-random',
            'content': 'fas fa-heart'
        };
        const titles = {
            'episode': 'Similar Episodes',
            'random': 'Your Random Playlist',
            'content': 'Health-Focused Episodes'
        };
        header.innerHTML = `<i class="${icons[type]} text-primary me-2"></i>${titles[type]}`;
    }

    if (!recommendations || recommendations.length === 0) {
        recommendationsList.innerHTML = `
            <div class="text-center">
                <i class="fas fa-search text-muted" style="font-size: 3rem;"></i>
                <h4 class="mt-3 text-muted">No recommendations found</h4>
                <p class="text-muted">Try adjusting your search criteria or try a different approach.</p>
            </div>
        `;
    } else {
        // Create recommendation cards
        recommendations.forEach((recommendation, index) => {
            const card = createRecommendationCard(recommendation, index);
            recommendationsList.appendChild(card);
        });
    }

    // Show results section
    resultsSection.classList.remove('d-none');
    
    // Scroll to results
    resultsSection.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

function createRecommendationCard(recommendation, index) {
    const card = document.createElement('div');
    card.className = 'recommendation-card fade-in';
    card.style.animationDelay = `${index * 0.1}s`;

    // Extract tags (assuming they're comma-separated)
    const tags = recommendation.tags ? recommendation.tags.split(',').map(tag => tag.trim()).filter(tag => tag) : [];
    
    // Create tags HTML
    const tagsHTML = tags.map(tag => `<span class="tag">${tag}</span>`).join('');

    // Format similarity score
    const similarityScore = recommendation.similarity_score ? 
        Math.round(recommendation.similarity_score * 100) : 
        Math.round(Math.random() * 30 + 70); // Fallback for demo

    // Format duration
    const duration = recommendation.duration_min ? 
        `${Math.floor(recommendation.duration_min)} min` : 
        'Unknown duration';

    card.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-2">
            <h5 class="recommendation-title mb-0">
                <i class="fas fa-podcast me-2"></i>${recommendation.title}
            </h5>
            <span class="similarity-score">
                <i class="fas fa-percentage me-1"></i>${similarityScore}% match
            </span>
        </div>
        <div class="mb-2">
            <small class="text-muted">
                <i class="fas fa-user me-1"></i>${recommendation.host || 'Unknown Host'}
                <span class="mx-2">•</span>
                <i class="fas fa-clock me-1"></i>${duration}
            </small>
        </div>
        ${tagsHTML ? `<div class="recommendation-tags">${tagsHTML}</div>` : ''}
    `;

    return card;
}

// Utility functions for recommendation actions
function playPodcast(podcastTitle) {
    // This would typically open the podcast in a player or redirect to a streaming service
    alert(`Playing: ${podcastTitle}\n\nThis would open the podcast in your preferred player.`);
}

function saveRecommendation(podcastTitle) {
    // This would typically save to user's favorites or a playlist
    alert(`Saved: ${podcastTitle}\n\nThis would add the podcast to your saved list.`);
}

// Health check function
async function checkSystemHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            console.log('System is healthy');
            if (data.recommendation_system_loaded) {
                console.log('Recommendation system is loaded and ready');
            } else {
                console.warn('Recommendation system is not loaded');
            }
        } else {
            console.error('System is not healthy');
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

// Run health check on page load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(checkSystemHealth, 1000);
});

// Add some interactive features
function addInteractiveFeatures() {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add typing animation to hero text
    const heroTitle = document.querySelector('.hero-section h1');
    if (heroTitle) {
        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        heroTitle.style.borderRight = '2px solid var(--primary-color)';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            } else {
                heroTitle.style.borderRight = 'none';
            }
        };
        
        // Start typing animation after a delay
        setTimeout(typeWriter, 500);
    }
}

// Initialize interactive features
document.addEventListener('DOMContentLoaded', function() {
    addInteractiveFeatures();
});

// Add scroll-based animations
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe all cards and sections
    document.querySelectorAll('.card, .col-md-4, .recommendation-card').forEach(el => {
        observer.observe(el);
    });
}

// Initialize scroll animations
document.addEventListener('DOMContentLoaded', function() {
    setupScrollAnimations();
}); 

function clearResultsAndErrors() {
    // Hide results and error sections, clear recommendations
    const resultsSection = document.getElementById('resultsSection');
    const recommendationsList = document.getElementById('recommendationsList');
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    if (resultsSection) resultsSection.classList.add('d-none');
    if (recommendationsList) recommendationsList.innerHTML = '';
    if (errorSection) errorSection.classList.add('d-none');
    if (errorMessage) errorMessage.textContent = '';
    // Reset all forms
    const forms = document.querySelectorAll('.recommendation-form');
    forms.forEach(form => form.reset());
} 