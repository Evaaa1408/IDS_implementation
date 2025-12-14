// content.js
console.log("🟢 Content script loaded and ready!");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("📩 Content script received message:", request.action);
    console.log("📊 Message data:", request.data);
    
    if (request.action === "SHOW_BLOCK") {
        console.log("🔴 Content: Calling showBlockingOverlay()");
        showBlockingOverlay(request.data);
    } else if (request.action === "SHOW_WARNING") {
        console.log("🟡 Content: Calling showWarningOverlay()");
        showWarningOverlay(request.data);
    } else if (request.action === "SHOW_SAFE") {
        console.log("🟢 Content: Calling showSafeNotification()");
        showSafeNotification(request.data);
    } else {
        console.warn("⚠️ Unknown action:", request.action);
    }
    
    sendResponse({received: true});
    return true;
});

function formatProbability(value) {
    if (value === undefined || value === null || isNaN(value)) {
        return "N/A";
    }
    // value is expected to be a percentage number (0-100)
    return parseFloat(value).toFixed(1) + "%";
}

function showBlockingOverlay(data) {
    console.log("🔴🔴🔴 CREATING RED BLOCKING OVERLAY 🔴🔴🔴");
    console.log("Data received:", data);
    removeOverlays();

    const overlay = document.createElement('div');
    overlay.id = 'phishing-block-overlay';
    // Use a high z-index and ensure it covers everything
    overlay.style.cssText = `
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background-color: rgba(220, 0, 0, 0.98) !important;
        z-index: 2147483647 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        color: white !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        text-align: center !important;
        backdrop-filter: blur(5px) !important;
    `;

    // Extract values safely
    const finalRisk = formatProbability(data.final_risk_pct);
    const urlRisk = formatProbability(data.url_prob);
    const contentRisk = formatProbability(data.content_prob);

    overlay.innerHTML = `
        <div style="max-width: 800px; padding: 40px; background: rgba(0,0,0,0.2); border-radius: 15px; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
            <div style="font-size: 5em; margin-bottom: 20px;">🛑</div>
            <h1 style="font-size: 3.5em; margin-bottom: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">Phishing Detected</h1>
            <p style="font-size: 1.4em; line-height: 1.6; margin-bottom: 30px; font-weight: 300;">
                Our security system has flagged this website as <strong>dangerously suspicious</strong>.<br>
                Entering your personal information here may result in identity theft.
            </p>
            
            <div style="display: flex; justify-content: space-around; margin-bottom: 30px; background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;">
                <div style="text-align: center;">
                    <div style="font-size: 0.9em; text-transform: uppercase; opacity: 0.8;">Overall Risk</div>
                    <div style="font-size: 2.5em; font-weight: bold;">${finalRisk}</div>
                </div>
                <div style="text-align: center; border-left: 1px solid rgba(255,255,255,0.3); padding-left: 20px;">
                    <div style="font-size: 0.9em; text-transform: uppercase; opacity: 0.8;">URL Analysis</div>
                    <div style="font-size: 1.5em; font-weight: bold;">${urlRisk}</div>
                </div>
                <div style="text-align: center; border-left: 1px solid rgba(255,255,255,0.3); padding-left: 20px;">
                    <div style="font-size: 0.9em; text-transform: uppercase; opacity: 0.8;">Content Analysis</div>
                    <div style="font-size: 1.5em; font-weight: bold;">${contentRisk}</div>
                </div>
            </div>

            <div style="font-size: 1.1em; margin-bottom: 40px; font-style: italic; opacity: 0.9;">
                "${data.message || 'Suspicious patterns detected.'}"
            </div>

            <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
                <button id="btn-goback-block" style="padding: 16px 32px; font-size: 1.2em; cursor: pointer; border: none; background: white; color: #cc0000; border-radius: 8px; font-weight: bold; transition: transform 0.2s;">
                    ◀ GO BACK TO SAFETY
                </button>
                <button id="btn-learn-more-block" style="padding: 16px 32px; font-size: 1.1em; cursor: pointer; border: 2px solid white; background: rgba(255,255,255,0.1); color: white; border-radius: 8px; font-weight: bold; transition: all 0.2s;">
                    📚 LEARN MORE
                </button>
                <button id="btn-proceed-block" style="padding: 16px 32px; font-size: 1.1em; cursor: pointer; border: 2px solid rgba(255,255,255,0.5); background: transparent; color: rgba(255,255,255,0.8); border-radius: 8px; transition: all 0.2s;">
                    I Understand the Risk ▶
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';
    console.log("✅ RED blocking overlay added to DOM");

    document.getElementById('btn-goback-block').addEventListener('click', () => {
        window.history.back();
    });

    document.getElementById('btn-learn-more-block').addEventListener('click', () => {
        window.open('https://www.comparitech.com/blog/vpn-privacy/what-are-malicious-websites/', '_blank');
    });

    document.getElementById('btn-proceed-block').addEventListener('click', () => {
        removeOverlays();
        document.body.style.overflow = 'auto';
    });
}

function showWarningOverlay(data) {
    console.log("🟡🟡🟡 CREATING YELLOW WARNING OVERLAY 🟡🟡🟡");
    console.log("Data received:", data);
    removeOverlays();

    const overlay = document.createElement('div');
    overlay.id = 'phishing-warn-overlay';
    overlay.style.cssText = `
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background-color: rgba(255, 140, 0, 0.96) !important;
        z-index: 2147483647 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        color: white !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        text-align: center !important;
        backdrop-filter: blur(5px) !important;
    `;

    const finalRisk = formatProbability(data.final_risk_pct);
    const urlRisk = formatProbability(data.url_prob);
    const contentRisk = formatProbability(data.content_prob);

    overlay.innerHTML = `
        <div style="max-width: 800px; padding: 40px; background: rgba(0,0,0,0.1); border-radius: 15px; border: 1px solid rgba(255,255,255,0.2);">
            <div style="font-size: 4em; margin-bottom: 20px;">⚠️</div>
            <h1 style="font-size: 3em; margin-bottom: 15px; font-weight: 700;">Suspicious Activity Detected</h1>
            <p style="font-size: 1.3em; line-height: 1.6; margin-bottom: 30px;">
                This website shows characteristics often found in phishing attacks.<br>
                Proceed only if you trust this source.
            </p>
            
            <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 30px;">
                <div><strong>Risk Level:</strong> ${finalRisk}</div>
                <div><strong>URL Score:</strong> ${urlRisk}</div>
                <div><strong>Content Score:</strong> ${contentRisk}</div>
            </div>

            <div style="margin-top: 40px; display: flex; justify-content: center; gap: 20px;">
                <button id="btn-goback-warn" style="padding: 15px 30px; font-size: 1.1em; cursor: pointer; border: none; background: white; color: #e65100; border-radius: 8px; font-weight: bold;">
                    ◀ Go Back
                </button>
                <button id="btn-proceed-warn" style="padding: 15px 30px; font-size: 1.1em; cursor: pointer; border: 2px solid white; background: transparent; color: white; border-radius: 8px;">
                    Continue Anyway
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';
    console.log("✅ YELLOW warning overlay added to DOM");

    document.getElementById('btn-goback-warn').addEventListener('click', () => {
        window.history.back();
    });

    document.getElementById('btn-proceed-warn').addEventListener('click', () => {
        removeOverlays();
        document.body.style.overflow = 'auto';
    });
}

function removeOverlays() {
    const blockOverlay = document.getElementById('phishing-block-overlay');
    const warnOverlay = document.getElementById('phishing-warn-overlay');
    
    if (blockOverlay) blockOverlay.remove();
    if (warnOverlay) warnOverlay.remove();
}

function showSafeNotification(data) {
    console.log("🟢🟢🟢 CREATING GREEN SAFE NOTIFICATION 🟢🟢🟢");
    console.log("Data received:", data);
    
    // Remove any existing notification
    const existing = document.getElementById('phishing-safe-notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.id = 'phishing-safe-notification';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999999;
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(40, 167, 69, 0.3);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 14px;
        min-width: 280px;
        max-width: 350px;
        animation: slideIn 0.3s ease-out;
        cursor: pointer;
    `;
    
    const isWhitelisted = data.whitelisted || false;
    const riskPct = data.final_risk_pct || 0;
    
    notification.innerHTML = `
        <style>
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        </style>
        <div style="display: flex; align-items: center; gap: 12px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M12 2L3 7v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z"/>
                <path d="M9 12l2 2 4-4"/>
            </svg>
            <div style="flex: 1;">
                <div style="font-weight: 600; margin-bottom: 4px;">
                    ✓ Website is Safe
                </div>
                <div style="font-size: 12px; opacity: 0.9;">
                    Risk: ${riskPct.toFixed(1)}%
                </div>
            </div>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" style="opacity: 0.7;">
                <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
            </svg>
        </div>
    `;
    
    document.body.appendChild(notification);
    console.log("✅ GREEN safe notification added to DOM");
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 3000);
    
    // Click to dismiss
    notification.addEventListener('click', () => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    });
}
