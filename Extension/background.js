// Background Service Worker
// Listens for tab updates and sends URLs to the local Python API

const API_ENDPOINT = "http://localhost:5000/predict";

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // Only check when the page is fully loaded and starts with http/https
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
        console.log("Checking URL:", tab.url);
        checkUrl(tab.url, tabId);
    }
});

async function checkUrl(url, tabId) {
    try {
        const response = await fetch(API_ENDPOINT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) {
            console.error("API Error:", response.statusText);
            return;
        }

        const data = await response.json();
        console.log("Prediction Result:", data);

        if (data.is_phishing) {
            handlePhishingDetection(tabId, data);
        } else {
            // Safe site - maybe set a green badge
            chrome.action.setBadgeText({ text: "SAFE", tabId: tabId });
            chrome.action.setBadgeBackgroundColor({ color: "#28a745", tabId: tabId });
        }

    } catch (error) {
        console.error("Connection Failed:", error);
    }
}

function handlePhishingDetection(tabId, data) {
    // 1. Set Red Badge
    chrome.action.setBadgeText({ text: "SUS", tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#d9534f", tabId: tabId });

    // 2. Notify User (Optional: Create notification)
    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon.png', // valid icon needed for this to work
        title: 'Phishing Warning!',
        message: `This site is flagged as Phishing!\nConfidence: ${(data.final_probability * 100).toFixed(2)}%`,
        priority: 2
    });

    // 3. Inject Warning (Optional - Block the page)
    // We send a message to content.js to show the overlay
    chrome.tabs.sendMessage(tabId, { action: "SHOW_WARNING", data: data });
}
