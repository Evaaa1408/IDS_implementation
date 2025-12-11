// Clean up checked tabs when they're closed
chrome.tabs.onRemoved.addListener((tabId) => {
    checkedTabs.delete(tabId);
});

async function checkUrl(url, tabId) {
    try {
        console.log("📡 Capturing HTML for:", url);
        
        // ========================================================
        // METHOD 1: Try to capture HTML from content script
        // ========================================================
        let htmlContent = null;
        
        try {
            // First, check if we can access this tab
            const tab = await chrome.tabs.get(tabId);
            
            if (!tab.url.startsWith('chrome://') && 
                !tab.url.startsWith('chrome-extension://') &&
                !tab.url.startsWith('edge://')) {
                
                // Execute script to get HTML
                const results = await chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    func: () => {
                        try {
                            return document.documentElement.outerHTML;
                        } catch (e) {
                            return null;
                        }
                    }
                });
                
                if (results && results[0] && results[0].result) {
                    htmlContent = results[0].result;
                    console.log("✅ HTML captured successfully:", htmlContent.length, "characters");
                } else {
                    console.warn("⚠️ HTML capture returned empty result");
                }
            } else {
                console.warn("⚠️ Cannot capture HTML from system page");
            }
        } catch (err) {
            console.error("❌ HTML capture failed:", err.message);
            console.log("🔄 Continuing with URL-only mode...");
        }

        // ========================================================
        // Send request to backend
        // ========================================================
        console.log("📤 Sending to API:", {
            url: url,
            hasHTML: htmlContent !== null,
            htmlLength: htmlContent ? htmlContent.length : 0
        });
        
        const response = await fetch(API_ENDPOINT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ 
                url: url,
                html_content: htmlContent
            })
        });

        if (!response.ok) {
            console.error("❌ API Error:", response.status, response.statusText);
            // Show error badge
            chrome.action.setBadgeText({ text: "ERR", tabId: tabId });
            chrome.action.setBadgeBackgroundColor({ color: "#ff9800", tabId: tabId });
            return;
        }

        const data = await response.json();
        console.log("📥 API Response:", data);

        // ========================================================
        // Handle result
        // ========================================================
        if (data.is_phishing) {
            console.log("🚨 PHISHING DETECTED!");
            handlePhishingDetection(tabId, data);
        } else {
            console.log("✅ Site is SAFE");
            chrome.action.setBadgeText({ text: "SAFE", tabId: tabId });
            chrome.action.setBadgeBackgroundColor({ color: "#28a745", tabId: tabId });
        }

    } catch (error) {
        console.error("❌ Connection Failed:", error);
        // Show error badge
        chrome.action.setBadgeText({ text: "ERR", tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: "#ff9800", tabId: tabId });
    }
}

function handlePhishingDetection(tabId, data) {
    // 1. Set Red Badge
    chrome.action.setBadgeText({ text: "SUS", tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#d9534f", tabId: tabId });

    // 2. Create notification
    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon.png',
        title: '🚨 Phishing Warning!',
        message: `This site may be dangerous!\nConfidence: ${(data.final_probability * 100).toFixed(1)}%\nClick for details.`,
        priority: 2,
        requireInteraction: true
    });

    // 3. Send warning to content script
    try {
        chrome.tabs.sendMessage(tabId, { 
            action: "SHOW_WARNING", 
            data: data 
        }, (response) => {
            // Handle potential errors silently
            if (chrome.runtime.lastError) {
                console.warn("Could not send message to content script:", chrome.runtime.lastError.message);
            }
        });
    } catch (err) {
        console.warn("Error sending warning:", err);
    }
}

// Listen for extension installation/update
chrome.runtime.onInstalled.addListener(() => {
    console.log("🚀 Phishing Detector Extension Loaded!");
    console.log("📡 API Endpoint:", API_ENDPOINT);
});