// content.js

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("Content.js received message:", request.action, request);
    
    if (request.action === "SHOW_SAFE") {
        console.log("Showing GREEN safe notification");
        showSafeNotification(request.data);
    } else if (request.action === "SHOW_FALSE_POSITIVE") {
        console.log("Showing BLUE false positive notification");
        showFalsePositiveNotification(request.data);
    } else {
        console.log("Unknown action:", request.action);
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


function showSafeNotification(data) {
    
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

function showFalsePositiveNotification(data) {
    
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
        background: linear-gradient(135deg, #0066FF 0%, #0052CC 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 102, 255, 0.3);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 14px;
        min-width: 320px;
        max-width: 380px;
        animation: slideIn 0.3s ease-out;
        cursor: pointer;
    `;
    
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
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 16v-4M12 8h.01"/>
            </svg>
            <div style="flex: 1;">
                <div style="font-weight: 600; margin-bottom: 4px;">
                    ✓ Safe Site (Verified)
                </div>
                <div style="font-size: 12px; opacity: 0.9;">
                    Previously reported as false positive
                </div>
                <div style="font-size: 11px; opacity: 0.7; margin-top: 4px;">
                    Model predicted: ${data.model_prediction || 'unknown'}
                </div>
            </div>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" style="opacity: 0.7;">
                <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
            </svg>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-dismiss after 5 seconds (longer than normal safe notification)
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 5000);
    
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
