// background.js
const API_ENDPOINT = "http://localhost:5000/predict";

// Track which tabs have been checked to avoid duplicate requests
const checkedTabs = new Map(); 
const pendingChecks = new Map(); // Track ongoing checks
const checkResults = new Map(); // Store check results for notifications

// ========================================================
// PHASE 1: PRE-NAVIGATION CHECK - Block dangerous sites FAST
// ========================================================
chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
    // Only check main frame navigations (not iframes)
    if (details.frameId !== 0) return;
    
    const { tabId, url } = details;
    
    // Skip internal pages and localhost
    if (!url.startsWith('http')) return;
    if (url.includes('localhost') || url.includes('127.0.0.1')) return;
    
    try {
        const urlObj = new URL(url);
        const domain = urlObj.hostname;
        
        // Skip chrome internal
        if (domain.startsWith('chrome')) return;
        
        // Get last checked domain
        const lastDomain = checkedTabs.get(tabId);
        
        // Only check if domain changed
        if (lastDomain === domain) return;
        
        checkedTabs.set(tabId, domain);
        pendingChecks.set(tabId, url);
        
        // Fast pre-navigation check (blocking dangerous sites immediately)
        await fastSecurityCheck(url, tabId);
        
    } catch (e) {
        console.error("URL parsing error:", e);
    }
});

// ========================================================
// PHASE 2: POST-LOAD CHECK - Show notifications after page loads
// ========================================================
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // Only act when page finishes loading
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
        // If we have a stored result for this tab, show the notification
        const result = checkResults.get(tabId);
        if (result) {
            console.log("📬 Showing post-load notification for:", tab.url);
            handleResult(tabId, result);
            checkResults.delete(tabId); // Clean up
        }
    }
});

// Clean up when tabs close
chrome.tabs.onRemoved.addListener((tabId) => {
    checkedTabs.delete(tabId);
    pendingChecks.delete(tabId);
    checkResults.delete(tabId);
});

async function checkUrl(url, tabId) {
    try {
        console.log("📡 Fast scanning:", url);
        
        // ========================================================
        // PHASE 1: IMMEDIATE URL-ONLY CHECK (Fast ~200ms)
        // ========================================================
        const urlOnlyResponse = await fetch(API_ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                url: url,
                html_content: null,
                html_captured: false
            })
        });

        if (!urlOnlyResponse.ok) {
            console.error("❌ API Error:", urlOnlyResponse.status);
            showErrorBadge(tabId);
            return;
        }

        const urlOnlyData = await urlOnlyResponse.json();
        
        console.log("⚡ Fast URL check:", urlOnlyData.risk_level, urlOnlyData.final_risk_pct + "%");
        
        // If URL-only check shows high risk, BLOCK IMMEDIATELY
        if (urlOnlyData.final_risk_pct > 60 || urlOnlyData.risk_level === 'VERY SUSPICIOUS') {
            console.log("🔴 IMMEDIATE BLOCK based on URL");
            handleResult(tabId, urlOnlyData);
            return; // Don't bother with content check
        }
        
        // If URL is safe or medium risk, continue to content check
        console.log("🟡 URL appears safe, checking content...");
        
        // ========================================================
        // PHASE 2: BACKGROUND CONTENT CHECK (Slower ~2s)
        // ========================================================
        // Wait for page to render
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        let htmlContent = null;
        let htmlCaptured = false;
        
        try {
            const tab = await chrome.tabs.get(tabId);
            
            if (!tab.url.startsWith('chrome://') && 
                !tab.url.startsWith('chrome-extension://') &&
                !tab.url.startsWith('edge://')) {
                
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
                }
            }
        } catch (err) {
            console.error("❌ HTML capture exception:", err.message);
        }

        // Full analysis with content
        const fullResponse = await fetch(API_ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                url: url,
                html_content: htmlContent,
                html_captured: htmlCaptured
            })
        });

        if (!fullResponse.ok) {
            console.error("❌ Full API Error:", fullResponse.status);
            return; // Keep showing URL-only result
        }

        const fullData = await fullResponse.json();
        
        console.log("📥 Full analysis:", fullData.risk_level, fullData.final_risk_pct + "%");
        
        // Update with full analysis result
        handleResult(tabId, fullData);

    } catch (error) {
        console.error("❌ Connection Failed:", error);
        showErrorBadge(tabId);
    }
}

// ========================================================
// FAST SECURITY CHECK - Runs before page loads
// ========================================================
async function fastSecurityCheck(url, tabId) {
    try {
        console.log("🛡️ Pre-navigation check:", url);
        
        // Fast URL-only check
        const response = await fetch(API_ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                url: url,
                html_content: null,
                html_captured: false
            })
        });

        if (!response.ok) {
            console.error("❌ API Error:", response.status);
            return; // Let page load on API error
        }

        const data = await response.json();
        
        console.log("⚡ Fast Check Result:", data.risk_level, data.final_risk_pct + "%");
        console.log("📊 Full API Response:", JSON.stringify(data, null, 2));
        
        // Store result for post-load notification
        checkResults.set(tabId, data);
        
        // If high risk (>60%), BLOCK immediately by injecting block overlay
        if (data.final_risk_pct > 60 || data.risk_level === 'VERY SUSPICIOUS') {
            console.log("🚫 BLOCKING - High risk detected:", data.final_risk_pct + "%");
            
            // Wait a moment for tab to be ready, then inject block
            setTimeout(() => {
                chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    func: (riskData) => {
                        // Clear and block page
                        document.documentElement.innerHTML = '';
                        document.body.innerHTML = `
                            <style>
                                body { margin: 0; padding: 0; overflow: hidden; 
                                       background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
                                       display: flex; align-items: center; justify-content: center;
                                       min-height: 100vh; color: white;
                                       font-family: -apple-system, system-ui, sans-serif; }
                                .content { text-align: center; max-width: 600px; padding: 40px; }
                                h1 { font-size: 48px; margin-bottom: 20px; }
                                p { font-size: 20px; margin-bottom: 40px; opacity: 0.9; }
                                .stats { display: flex; gap: 30px; justify-content: center; margin-bottom: 40px; }
                                .stat { background: rgba(0,0,0,0.3); padding: 20px; border-radius: 12px; }
                                .label { font-size: 12px; text-transform: uppercase; opacity: 0.7; }
                                .value { font-size: 36px; font-weight: 700; margin-top: 8px; }
                                button { padding: 16px 32px; font-size: 18px; font-weight: 600;
                                        border: none; border-radius: 8px; cursor: pointer; margin: 0 10px; }
                                .primary { background: white; color: #dc2626; }
                                .secondary { background: transparent; color: white; border: 2px solid white; }
                            </style>
                            <div class="content">
                                <h1>🛡️ PHISHING DETECTED</h1>
                                <p>This website has been flagged as dangerously suspicious.<br>
                                Proceeding may result in identity theft.</p>
                                <div class="stats">
                                    <div class="stat">
                                        <div class="label">Risk Level</div>
                                        <div class="value">${riskData.risk}%</div>
                                    </div>
                                </div>
                                <button class="primary" onclick="history.back()">◀ Go Back</button>
                                <button class="secondary" onclick="location.reload()">I Understand ▶</button>
                            </div>
                        `;
                    },
                    args: [{ risk: data.final_risk_pct }]
                });
            }, 100);
            
            // Set red badge
            chrome.action.setBadgeText({ text: "⛔", tabId });
            chrome.action.setBadgeBackgroundColor({ color: "#DC2626", tabId });
            
        } else {
            // Medium/low risk - set badge, notification will show post-load
            if (data.final_risk_pct > 40) {
                chrome.action.setBadgeText({ text: "⚠", tabId });
                chrome.action.setBadgeBackgroundColor({ color: "#FF9800", tabId });
            } else {
                chrome.action.setBadgeText({ text: "✓", tabId });
                chrome.action.setBadgeBackgroundColor({ color: "#10B981", tabId });
            }
        }
        
    } catch (error) {
        console.error("❌ Security check error:", error);
    } finally {
        pendingChecks.delete(tabId);
    }
}

function handleResult(tabId, data) {
    const riskLevel = data.risk_level || 'UNKNOWN';
    const color = data.color || 'gray';
    const riskPct = data.final_risk_pct || 0;
    
    console.log("\n" + "=".repeat(70));
    console.log("🎯 HANDLE RESULT - TabId:", tabId);
    console.log("   Risk Level:", riskLevel);
    console.log("   Risk Pct:", riskPct.toFixed(1) + "%");
    console.log("   Color:", color);
    console.log("   Data:", data);
    console.log("=".repeat(70) + "\n");
    
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
        
        // Show small green notification
        showSafeNotification(tabId, data);
    }
}

function showBlockingOverlay(tabId, data) {
    try {
        console.log("🔴 SHOW_BLOCK - Attempting to inject RED blocking overlay for tabId:", tabId);
        console.log("🔴 Message payload:", {
            action: "SHOW_BLOCK",
            risk_pct: data.final_risk_pct
        });
        
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
                console.error("❌ FAILED to inject RED overlay:", chrome.runtime.lastError.message);
            } else {
                console.log("✅ RED blocking overlay message sent successfully");
            }
        });
    } catch (err) {
        console.error("❌ Exception in showBlockingOverlay:", err);
    }
}

function showWarningOverlay(tabId, data) {
    try {
        console.log("🟡 SHOW_WARNING - Attempting to inject YELLOW warning overlay for tabId:", tabId);
        console.log("🟡 Message payload:", {
            action: "SHOW_WARNING",
            risk_pct: data.final_risk_pct
        });
        
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
                console.error("❌ FAILED to inject YELLOW overlay:", chrome.runtime.lastError.message);
            } else {
                console.log("✅ YELLOW warning overlay message sent successfully");
            }
        });
    } catch (err) {
        console.error("❌ Exception in showWarningOverlay:", err);
    }
}

function showSafeNotification(tabId, data) {
    try {
        console.log("🟢 SHOW_SAFE - Attempting to show GREEN safe notification for tabId:", tabId);
        console.log("🟢 Message payload:", {
            action: "SHOW_SAFE",
            risk_pct: data.final_risk_pct
        });
        
        chrome.tabs.sendMessage(tabId, { 
            action: "SHOW_SAFE",
            data: {
                url: data.url,
                risk_level: data.risk_level,
                final_risk_pct: data.final_risk_pct,
                whitelisted: data.whitelisted
            }
        }, (response) => {
            if (chrome.runtime.lastError) {
                console.error("❌ FAILED to show GREEN notification:", chrome.runtime.lastError.message);
            } else {
                console.log("✅ GREEN safe notification message sent successfully");
            }
        });
    } catch (err) {
        console.error("❌ Exception in showSafeNotification:", err);
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
