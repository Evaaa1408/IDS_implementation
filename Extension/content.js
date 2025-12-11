// Content.js
// Listens for messages from background.js to show warnings

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "SHOW_WARNING") {
        showWarningOverlay(request.data);
    }
});

function showWarningOverlay(data) {
    // Check if overlay already exists
    if (document.getElementById('phishing-warning-overlay')) return;

    const overlay = document.createElement('div');
    overlay.id = 'phishing-warning-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 0, 0, 0.95);
        z-index: 999999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
        font-family: Arial, sans-serif;
        text-align: center;
    `;

    overlay.innerHTML = `
        <h1 style="font-size: 3em; margin-bottom: 20px;">⚠️ PHISHING DETECTED!</h1>
        <p style="font-size: 1.5em; max-width: 800px;">
            This website has been flagged by our Ensemble Model as potentially dangerous.<br>
            It may be trying to steal your personal information.
        </p>
        <div style="margin-top: 20px; font-size: 1.2em;">
            <strong>Probability:</strong> ${(data.final_probability * 100).toFixed(2)}%
        </div>
        <div style="margin-top: 40px;">
            <button id="btn-goback" style="padding: 15px 30px; font-size: 1.2em; cursor: pointer; border: none; background: white; color: red; border-radius: 5px; margin-right: 20px;">
                ◀ Go Back (Recommended)
            </button>
            <button id="btn-proceed" style="padding: 15px 30px; font-size: 1.2em; cursor: pointer; border: 2px solid white; background: transparent; color: white; border-radius: 5px;">
                I Understand the Risk ▶
            </button>
        </div>
    `;

    document.body.appendChild(overlay);

    // Stop scrolling
    document.body.style.overflow = 'hidden';

    // Button Logic
    document.getElementById('btn-goback').addEventListener('click', () => {
        window.history.back();
    });

    document.getElementById('btn-proceed').addEventListener('click', () => {
        document.body.removeChild(overlay);
        document.body.style.overflow = 'auto'; // Restore scrolling
    });
}
