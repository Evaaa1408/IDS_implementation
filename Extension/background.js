// background.js - FIXED VERSION
const API_ENDPOINT = "http://localhost:5000/predict";

// Track which tabs have been checked to avoid duplicate requests
const checkedTabs = new Set();

// ========================================================
// SINGLE tab update listener with proper timing
// ========================================================
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // Only check when page is completely loaded
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
        // Avoid duplicate checks
        if (!checkedTabs.has(tabId)) {
            checkedTabs.add(tabId);
            
            // Wait 1500ms to ensure HTML is fully rendered
            setTimeout(() => {
                checkUrl(tab.url, tabId);
            }, 1500);
        }
    }
});

// Clean up checked tabs when they're closed
chrome.tabs.onRemoved.addListener((tabId) => {
    checkedTabs.delete(tabId);
});

async function checkUrl(url, tabId) {
    try {
        console.log("📡 Scanning:", url);
        
        // Wait additional time for dynamic content
        await new Promise(resolve => setTimeout(resolve, 500));
        
        let htmlContent = null;
        let htmlCaptured = false;
        
        try {
            const tab = await chrome.tabs.get(tabId);
            
            // Check if we can access this tab
            if (!tab.url.startsWith('chrome://') && 
                !tab.url.startsWith('chrome-extension://') &&
                !tab.url.startsWith('edge://')) {
                
                // Execute script with error handling
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
                    htmlCaptured = true;
                    console.log("✅ HTML captured:", htmlContent.length, "bytes");
                } else {
                    console.error("❌ HTML capture failed - no result");
                }
            }
        } catch (err) {
            console.error("❌ HTML capture exception:", err.message);
        }

        // Log if HTML capture failed
        if (!htmlCaptured) {
            console.error("🚨 WARNING: Proceeding without HTML - Model 2023 will be skipped!");
        }

       // ========================================================
        // Send to API
        // ========================================================
        console.log("📤 Sending to API...");
        console.log("   URL:", url);
        console.log("   HTML:", htmlCaptured ? `${htmlContent.length} bytes` : "Not captured");
        
        const response = await fetch(API_ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                url: url,
                html_content: htmlContent,
                html_captured: htmlCaptured
            })
        });

        if (!response.ok) {
            console.error("❌ API Error:", response.status, response.statusText);
            showErrorBadge(tabId);
            return;
        }

        const data = await response.json();
        
        // ========================================================
        // Log API Response
        // ========================================================
        console.log("📥 API Response:");
        console.log("   Risk Level:", data.risk_level);
        console.log("   Final Risk:", data.final_risk_pct + "%");
        console.log("   URL Risk:", (data.url_prob * 100).toFixed(1) + "%");
        console.log("   Content Risk:", (data.content_prob * 100).toFixed(1) + "%");
        console.log("   Color:", data.color);
        console.log("   Whitelisted:", data.whitelisted);
        console.log("   Is Phishing:", data.is_phishing);

        // ========================================================
        // Handle result based on risk level
        // ========================================================
        handleResult(tabId, data);

    } catch (error) {
        console.error("❌ Connection Failed:", error);
        showErrorBadge(tabId);
    }
}

function handleResult(tabId, data) {
    const riskLevel = data.risk_level || 'UNKNOWN';
    const color = data.color || 'gray';
    const riskPct = data.final_risk_pct || 0;
    
    console.log("🎯 Handling result:", riskLevel, "(" + riskPct.toFixed(1) + "%)");
    
    // ========================================================
    // Set badge based on risk level
    // ========================================================
    if (riskLevel === 'VERY SUSPICIOUS' || riskPct > 75) {
        // RED - High risk
        chrome.action.setBadgeText({ text: "RISK", tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: "#d9534f", tabId: tabId });
        
        console.log("🔴 BLOCKING page");
        showBlockingOverlay(tabId, data);
        
    } else if (riskLevel === 'POSSIBLY MALICIOUS' || riskPct > 40) {
        // YELLOW - Medium risk
        chrome.action.setBadgeText({ text: "WARN", tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: "#ff9800", tabId: tabId });
        
        console.log("🟡 WARNING for page");
        showWarningOverlay(tabId, data);
        
    } else {
        // GREEN - Safe
        chrome.action.setBadgeText({ text: "SAFE", tabId: tabId });
        chrome.action.setBadgeBackgroundColor({ color: "#28a745", tabId: tabId });
        
        console.log("🟢 Page is SAFE");
    }
}

function showBlockingOverlay(tabId, data) {
    try {
        console.log("Attempting to inject blocking overlay...");
        chrome.tabs.sendMessage(tabId, { 
            action: "SHOW_BLOCK",
            data: {
                url: data.url,
                risk_level: data.risk_level,
                final_risk_pct: data.final_risk_pct,
                url_prob: data.url_prob * 100,
                content_prob: data.content_prob * 100,
                message: data.message,
                whitelisted: data.whitelisted
            }
        }, (response) => {
            if (chrome.runtime.lastError) {
                console.warn("Could not inject overlay:", chrome.runtime.lastError.message);
            } else {
                console.log("✅ Blocking overlay injected");
            }
        });
    } catch (err) {
        console.warn("Could not inject blocking overlay:", err);
    }
}

function showWarningOverlay(tabId, data) {
    try {
        console.log("Attempting to inject warning overlay...");
        chrome.tabs.sendMessage(tabId, { 
            action: "SHOW_WARNING",
            data: {
                url: data.url,
                risk_level: data.risk_level,
                final_risk_pct: data.final_risk_pct,
                url_prob: data.url_prob * 100,
                content_prob: data.content_prob * 100,
                message: data.message,
                whitelisted: data.whitelisted
            }
        }, (response) => {
            if (chrome.runtime.lastError) {
                console.warn("Could not inject overlay:", chrome.runtime.lastError.message);
            } else {
                console.log("✅ Warning overlay injected");
            }
        });
    } catch (err) {
        console.warn("Could not inject warning overlay:", err);
    }
}

function showErrorBadge(tabId) {
    chrome.action.setBadgeText({ text: "ERR", tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#6c757d", tabId: tabId });
}

// Extension loaded
chrome.runtime.onInstalled.addListener(() => {
    console.log("="*70);
    console.log("🚀 Rule-Based Phishing Detector Loaded!");
    console.log("="*70);
    console.log("📡 API Endpoint:", API_ENDPOINT);
    console.log("🔒 Method: Rule-Based Fusion (No Ensemble)");
    console.log("🛡️  Whitelist: Enabled");
    console.log("="*70);
});

// Log when extension starts
console.log("🟢 Extension background script active");
console.log("📡 Monitoring tabs for phishing...");
