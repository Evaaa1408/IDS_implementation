// Get parameters from URL
const params = new URLSearchParams(window.location.search);
const blockedUrl = params.get('url') || 'Unknown URL';
const risk = params.get('risk') || '--';
const level = params.get('level') || 'high';

// Update page content
document.getElementById('blocked-url').textContent = decodeURIComponent(blockedUrl);
document.getElementById('risk-percent').textContent = risk + '%';

// Adjust for warning level (yellow)
if (level === 'medium') {
    document.body.classList.add('warning-mode');
    document.getElementById('title').textContent = 'SUSPICIOUS WEBSITE';
    document.getElementById('subtitle').textContent = 'This website shows some suspicious characteristics. Exercise caution if you choose to proceed.';
    document.querySelector('.icon').textContent = '⚠️';
}

function goBack() {
    // Close the current tab instead of going back
    // (going back would try to load the blocked URL again)
    window.close();
}

function openDashboard() {
    window.open('http://localhost:5000/dashboard', '_blank');
}

function proceedAnyway() {
    // Go to the blocked URL
    window.location.href = decodeURIComponent(blockedUrl);
}

// Add event listeners when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('btn-back').addEventListener('click', goBack);
    document.getElementById('btn-dashboard').addEventListener('click', openDashboard);
    document.getElementById('btn-proceed').addEventListener('click', proceedAnyway);
});
