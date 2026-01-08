// News feed functionality
function loadNewsFeed() {
    fetch('/api/news/')
        .then(response => response.json())
        .then(data => {
            const newsContainer = document.getElementById('news-feed');
            if (newsContainer && data.news) {
                newsContainer.innerHTML = '';
                data.news.forEach(article => {
                    const articleElement = createNewsArticle(article);
                    newsContainer.appendChild(articleElement);
                });
            }
        })
        .catch(error => {
            console.error('Error loading news:', error);
            showNewsError('Failed to load news feed');
        });
}

function createNewsArticle(article) {
    const articleDiv = document.createElement('div');
    articleDiv.className = 'news-article';
    
    const title = document.createElement('h3');
    title.className = 'news-title';
    const titleLink = document.createElement('a');
    titleLink.href = article.link;
    titleLink.target = '_blank';
    titleLink.textContent = article.title;
    title.appendChild(titleLink);
    
    const meta = document.createElement('div');
    meta.className = 'news-meta';
    meta.textContent = new Date(article.published).toLocaleString();
    
    const summary = document.createElement('div');
    summary.className = 'news-summary';
    summary.innerHTML = article.summary;
    
    articleDiv.appendChild(title);
    articleDiv.appendChild(meta);
    articleDiv.appendChild(summary);
    
    return articleDiv;
}

function showNewsError(message) {
    const errorDiv = document.getElementById('news-error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

// Auto-refresh news feed every 5 minutes
function startNewsUpdates(interval = 300000) {
    loadNewsFeed();
    return setInterval(loadNewsFeed, interval);
}

// Initialize news feed when page loads
document.addEventListener('DOMContentLoaded', () => {
    const newsContainer = document.getElementById('news-feed');
    if (newsContainer) {
        loadNewsFeed();
        startNewsUpdates();
    }
});