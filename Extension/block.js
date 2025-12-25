// Get parameters from URL
const params = new URLSearchParams(window.location.search);
const blockedUrl = params.get('url') || 'Unknown URL';
const risk = params.get('risk') || '--';
const level = params.get('level') || 'high';
const urlProb = params.get('url_prob') || '--';
const contentProb = params.get('content_prob') || '--';

// Update page content
document.getElementById('blocked-url').textContent = decodeURIComponent(blockedUrl);
document.getElementById('risk-percent').textContent = risk + '%';
document.getElementById('url-percent').textContent = urlProb + '%';
document.getElementById('content-percent').textContent = contentProb + '%';

// Adjust for warning level (yellow)
if (level === 'medium') {
    document.body.classList.add('warning-mode');
    document.getElementById('title').textContent = 'SUSPICIOUS WEBSITE';
    document.getElementById('subtitle').textContent = 'This website shows some suspicious characteristics. Exercise caution if you choose to proceed.';
    document.querySelector('.icon').textContent = '';
}

function goBack() {
    window.close();
}

function openDashboard() {
    window.open('http://localhost:5000/dashboard', '_blank');
}

function proceedAnyway() {
    // Tell background script to bypass this URL
    chrome.runtime.sendMessage({
        action: 'BYPASS_URL',
        url: decodeURIComponent(blockedUrl)
    }, () => {
        // After background script adds to bypass list, navigate
        window.location.href = decodeURIComponent(blockedUrl);
    });
}

// Add event listeners when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('btn-back').addEventListener('click', goBack);
    document.getElementById('btn-dashboard').addEventListener('click', openDashboard);
    document.getElementById('btn-proceed').addEventListener('click', proceedAnyway);
});
