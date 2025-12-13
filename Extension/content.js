// content.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "SHOW_BLOCK") {
        showBlockingOverlay(request.data);
    } else if (request.action === "SHOW_WARNING") {
        showWarningOverlay(request.data);
    }
});

function formatProbability(value) {
    if (value === undefined || value === null || isNaN(value)) {
        return "N/A";
    }
    // value is expected to be a percentage number (0-100)
    return parseFloat(value).toFixed(1) + "%";
}

function showBlockingOverlay(data) {
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

            <div style="display: flex; justify-content: center; gap: 20px;">
                <button id="btn-goback-block" style="padding: 16px 32px; font-size: 1.2em; cursor: pointer; border: none; background: white; color: #cc0000; border-radius: 8px; font-weight: bold; transition: transform 0.2s;">
                    ◀ GO BACK TO SAFETY
                </button>
                <button id="btn-proceed-block" style="padding: 16px 32px; font-size: 1.1em; cursor: pointer; border: 2px solid rgba(255,255,255,0.5); background: transparent; color: rgba(255,255,255,0.8); border-radius: 8px; transition: all 0.2s;">
                    I Understand the Risk ▶
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';

    document.getElementById('btn-goback-block').addEventListener('click', () => {
        window.history.back();
    });

    document.getElementById('btn-proceed-block').addEventListener('click', () => {
        removeOverlays();
        document.body.style.overflow = 'auto';
    });
}

function showWarningOverlay(data) {
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