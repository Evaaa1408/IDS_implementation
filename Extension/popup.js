//popup.js

document.addEventListener('DOMContentLoaded', () => {
    const scanBtn = document.getElementById('scan-btn');
    const statusBox = document.getElementById('status-box');
    const loader = document.getElementById('loader');
    const detailsDiv = document.getElementById('result-details');

    // Get current tab URL
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        const currentTab = tabs[0];
        if (currentTab.url.startsWith('http')) {
            // Tab is scannable
        } else {
            statusBox.textContent = "Cannot Scan System Page";
            scanBtn.disabled = true;
        }
    });

    scanBtn.addEventListener('click', async () => {
        // UI Reset
        statusBox.className = 'status-box unknown';
        statusBox.textContent = "Scanning...";
        loader.style.display = 'block';
        detailsDiv.innerHTML = '';
        scanBtn.disabled = true;

        chrome.tabs.query({active: true, currentWindow: true}, async (tabs) => {
            const url = tabs[0].url;
            const tabId = tabs[0].id;
            
            // ========================================================
            // CRITICAL FIX: Capture HTML from the current page
            // ========================================================
            let htmlContent = null;
            
            try {
                const results = await chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    func: () => document.documentElement.outerHTML
                });
                
                if (results && results[0] && results[0].result) {
                    htmlContent = results[0].result;
                    console.log("✅ HTML captured:", htmlContent.length, "characters");
                }
            } catch (err) {
                console.warn("⚠️ Could not capture HTML:", err);
                // Continue without HTML (URL-only mode)
            }
            
            // ========================================================
            // Send both URL and HTML to backend
            // ========================================================
            try {
                const response = await fetch("http://localhost:5000/predict", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({ 
                        url: url,
                        html_content: htmlContent  // ✅ NOW SENDING HTML!
                    })
                });

                if (!response.ok) throw new Error("API Error");

                const data = await response.json();
                loader.style.display = 'none';
                scanBtn.disabled = false;

                displayResult(data);

            } catch (error) {
                console.error(error);
                statusBox.textContent = "API Error (Is Flask running?)";
                statusBox.className = 'status-box unknown';
                loader.style.display = 'none';
                scanBtn.disabled = false;
            }
        });
    });

    function displayResult(data) {
        if (data.is_phishing) {
            statusBox.textContent = "⚠️ PHISHING DETECTED";
            statusBox.className = 'status-box warning';
        } else {
            statusBox.textContent = "✅ SAFE WEBSITE";
            statusBox.className = 'status-box safe';
        }

        // Enhanced display with decision logic
        const model2023Display = data.prob_2023 !== null && data.prob_2023 !== undefined
            ? `${(data.prob_2023 * 100).toFixed(1)}%`
            : 'N/A';

        detailsDiv.innerHTML = `
            <div class="detail-row"><span>Confidence:</span> <strong>${(data.final_probability * 100).toFixed(2)}%</strong></div>
            <div class="detail-row"><span>Model 2025 (URL):</span> <span>${(data.prob_2025 * 100).toFixed(1)}%</span></div>
            <div class="detail-row"><span>Model 2023 (Content):</span> <span>${model2023Display}</span></div>
            ${data.decision_logic ? `<div class="detail-row"><span>Method:</span> <span style="font-size: 0.85em;">${data.decision_logic}</span></div>` : ''}
            ${data.html_quality ? `<div class="detail-row"><span>HTML Quality:</span> <span>${data.html_quality}</span></div>` : ''}
        `;
    }
});