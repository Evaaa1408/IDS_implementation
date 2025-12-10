document.addEventListener('DOMContentLoaded', () => {
    const scanBtn = document.getElementById('scan-btn');
    const statusBox = document.getElementById('status-box');
    const loader = document.getElementById('loader');
    const detailsDiv = document.getElementById('result-details');

    // Get current tab URL
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        const currentTab = tabs[0];
        if (currentTab.url.startsWith('http')) {
            // Optional: Automatically check status if we stored it in background
            // distinct from manual scan
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
            
            try {
                const response = await fetch("http://localhost:5000/predict", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({ url: url })
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

        detailsDiv.innerHTML = `
            <div class="detail-row"><span>Probability:</span> <strong>${(data.final_probability * 100).toFixed(2)}%</strong></div>
            <div class="detail-row"><span>Model 2025 (URL):</span> <span>${(data.prob_2025 * 100).toFixed(1)}%</span></div>
            <div class="detail-row"><span>Model 2023 (Content):</span> <span>${data.prob_2023 !== undefined ? (data.prob_2023 * 100).toFixed(1) + '%' : 'N/A'}</span></div>
        `;
    }
});
