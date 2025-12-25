// background.js
const API_ENDPOINT = "http://localhost:5000/predict";

// Track which tabs have been checked to avoid duplicate requests
const checkedTabs = new Map();
const pendingChecks = new Map(); // Track ongoing checks
const checkResults = new Map(); // Store check results for notifications
const bypassedUrls = new Set();

// ========================================================
// PHASE 1: PRE-NAVIGATION CHECK - Block dangerous sites FAST
// ========================================================
chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  // Only check main frame navigations (not iframes)
  if (details.frameId !== 0) return;

  const { tabId, url } = details;

  // Skip internal pages and localhost
  if (!url.startsWith("http")) return;
  if (url.includes("localhost") || url.includes("127.0.0.1")) return;

  try {
    const urlObj = new URL(url);
    const domain = urlObj.hostname;

    // Skip chrome internal
    if (domain.startsWith("chrome")) return;

    // Check if user explicitly chose to proceed to this URL
    if (bypassedUrls.has(url)) {
      console.log("Bypassing check - user chose to proceed:", url);
      return;
    }

    // Skip search engines and common safe sites
    const skipDomains = [
            'google.com', 'www.google.com', 'google.com.my', 'google.co.uk',
            'bing.com', 'www.bing.com',
            'duckduckgo.com', 'www.duckduckgo.com',
            'yahoo.com', 'www.yahoo.com', 'search.yahoo.com',
            'baidu.com', 'www.baidu.com',
            'yandex.com', 'www.yandex.com',
            'wikipedia.org', 'en.wikipedia.org', 'www.wikipedia.org',
            'github.com', 'www.github.com',
            'stackoverflow.com', 'www.stackoverflow.com',
            'reddit.com', 'www.reddit.com',
            'twitter.com', 'www.twitter.com', 'x.com', 'www.x.com',
            'youtube.com', 'www.youtube.com',
            'shopee.com.my', 'shopee.sg', 'shopee.ph', 'shopee.co.id',
            'www.shopee.com.my', 'www.shopee.sg',
            'lazada.com.my', 'lazada.sg', 'lazada.co.th',
            'www.lazada.com.my', 'www.lazada.sg',
            'amazon.com', 'www.amazon.com', 'amazon.sg',
            'sephora.com', 'www.sephora.com', 'sephora.my', 'www.sephora.my',
            'zalora.com.my', 'www.zalora.com.my'
    ];

    if (skipDomains.includes(domain)) {
      console.log("⏭️ Skipping safe domain:", domain);
      return;
    }

    // Also skip if URL contains search query patterns
    const urlPath = urlObj.pathname + urlObj.search;
    if (
      urlPath.includes("/search?") ||
      urlPath.includes("?q=") ||
      urlPath.includes("&q=") ||
      urlPath.includes("?query=")
    ) {
      console.log("⏭️ Skipping search query URL:", url);
      return;
    }

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
  if (
    changeInfo.status === "complete" &&
    tab.url &&
    tab.url.startsWith("http")
  ) {
    // If we have a stored result for this tab, show the notification
    const result = checkResults.get(tabId);
    if (result) {
      console.log("📬 Showing post-load notification for:", tab.url);
      
      // Check if this is a false positive override
      if (result.is_false_positive === true) {
        console.log("🔵 Page loaded - sending blue false positive notification to content script");
        
        // Send blue notification for false positive (to content script on real pages)
        chrome.tabs
          .sendMessage(tabId, {
            action: "SHOW_FALSE_POSITIVE",
            data: {
              url: tab.url,
              message: result.message,
              model_prediction: result.model_prediction,
              final_decision: result.final_decision,
            },
          })
          .then(() => {
            console.log("✅ Blue notification sent successfully to content script");
            checkResults.delete(tabId); // Clean up
          })
          .catch((err) => console.error("Failed to send blue notification:", err.message));
      } else {
        // Normal safe/warning notification
        handleResult(tabId, result);
        checkResults.delete(tabId); // Clean up
      }
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
        html_captured: false,
      }),
    });

    if (!urlOnlyResponse.ok) {
      console.error("❌ API Error:", urlOnlyResponse.status);
      showErrorBadge(tabId);
      return;
    }

    const urlOnlyData = await urlOnlyResponse.json();

    console.log(
      "⚡ Fast URL check:",
      urlOnlyData.risk_level,
      urlOnlyData.final_risk_pct + "%"
    );

    // If URL-only check shows high risk, BLOCK IMMEDIATELY
    if (
      urlOnlyData.final_risk_pct > 60 ||
      urlOnlyData.risk_level === "VERY SUSPICIOUS"
    ) {
      console.log("🔴 IMMEDIATE BLOCK based on URL");
      handleResult(tabId, urlOnlyData);
      return; // Don't bother with content check
    }

    // ========================================================
    // PHASE 2: BACKGROUND CONTENT CHECK (Slower ~2s)
    // ========================================================
    // Wait for page to render
    await new Promise((resolve) => setTimeout(resolve, 1500));

    let htmlContent = null;
    let htmlCaptured = false;

    try {
      const tab = await chrome.tabs.get(tabId);

      if (
        !tab.url.startsWith("chrome://") &&
        !tab.url.startsWith("chrome-extension://") &&
        !tab.url.startsWith("edge://")
      ) {
        const results = await chrome.scripting.executeScript({
          target: { tabId: tabId },
          func: () => {
            try {
              return document.documentElement.outerHTML;
            } catch (e) {
              return null;
            }
          },
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
        html_captured: htmlCaptured,
      }),
    });

    if (!fullResponse.ok) {
      console.error("❌ Full API Error:", fullResponse.status);
      return; // Keep showing URL-only result
    }

    const fullData = await fullResponse.json();

    console.log(
      "📥 Full analysis:",
      fullData.risk_level,
      fullData.final_risk_pct + "%"
    );

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

    // CRITICAL FIX: Check if user explicitly chose to proceed to this URL FIRST
    if (bypassedUrls.has(url)) {
      console.log("⏭️ Bypassing pre-check - user chose to proceed:", url);
      return; // Don't inject overlay or check - let page load
    }

    // IMMEDIATELY inject "Checking..." overlay to prevent page from showing
    chrome.scripting
      .executeScript({
        target: { tabId: tabId },
        func: () => {
          // Block entire page with semi-transparent overlay + small popup
          const overlay = document.createElement("div");
          overlay.id = "phishing-check-overlay";
          overlay.innerHTML = `
                    <style>
                        #phishing-check-overlay {
                            position: fixed !important;
                            top: 0 !important;
                            left: 0 !important;
                            width: 100% !important;
                            height: 100% !important;
                            background: rgba(0, 0, 0, 0.85) !important;
                            backdrop-filter: blur(10px) !important;
                            display: flex !important;
                            align-items: center !important;
                            justify-content: center !important;
                            z-index: 2147483647 !important;
                            font-family: -apple-system, system-ui, sans-serif !important;
                        }
                        .check-card {
                            background: white !important;
                            border-radius: 16px !important;
                            padding: 30px 40px !important;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.3) !important;
                            text-align: center !important;
                            max-width: 320px !important;
                        }
                        .spinner {
                            width: 40px !important;
                            height: 40px !important;
                            margin: 0 auto 20px !important;
                            border: 3px solid #e5e7eb !important;
                            border-top-color: #3b82f6 !important;
                            border-radius: 50% !important;
                            animation: spin 0.8s linear infinite !important;
                        }
                        @keyframes spin { to { transform: rotate(360deg); } }
                        .check-card h3 {
                            margin: 0 0 10px 0 !important;
                            font-size: 18px !important;
                            font-weight: 600 !important;
                            color: #1f2937 !important;
                        }
                        .check-card p {
                            margin: 0 !important;
                            font-size: 14px !important;
                            color: #6b7280 !important;
                        }
                    </style>
                    <div class="check-card">
                        <div class="spinner"></div>
                        <h3>🔍 Checking Security</h3>
                        <p>Analyzing for threats...</p>
                    </div>
                `;
          // Inject ASAP - use documentElement if body not ready
          const target = document.body || document.documentElement;
          target.appendChild(overlay);

          // Also hide page content temporarily
          if (document.body) {
            document.body.style.visibility = "hidden";
          }
        },
        world: "MAIN",
      })
      .catch((err) => console.error("Failed to inject checking overlay:", err));

    // Fast URL-only check
    const response = await fetch(API_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: url,
        html_content: null,
        html_captured: false,
      }),
    });

    if (!response.ok) {
      console.error("API Error:", response.status);
      return; // Let page load on API error
    }

    const data = await response.json();

    console.log(
      "⚡ Fast Check Result:",
      data.risk_level,
      data.final_risk_pct + "%"
    );
    console.log("📊 Full API Response:", JSON.stringify(data, null, 2));

    // ========================================================
    // CHECK FOR FALSE POSITIVE OVERRIDE
    // ========================================================
    if (data.overridden === true) {
      console.log("🔵 FALSE POSITIVE OVERRIDE DETECTED!");
      console.log("   Model predicted:", data.model_prediction);
      console.log("   Final decision:", data.final_decision);
      console.log("   Reason:", data.override_reason);

      // Remove the checking overlay immediately
      chrome.scripting
        .executeScript({
          target: { tabId: tabId },
          func: () => {
            const overlay = document.getElementById("phishing-check-overlay");
            if (overlay) overlay.remove();
            // Restore page visibility
            if (document.body) {
              document.body.style.visibility = "visible";
            }
          },
        })
        .catch((err) => console.log("Overlay already removed:", err));

      // Set BLUE badge for false positive
      chrome.action.setBadgeText({ text: "FP", tabId });
      chrome.action.setBadgeBackgroundColor({ color: "#0066FF", tabId });

      // Store false positive data for notification after page loads
      // Mark it as a false positive so the onUpdated handler knows to show blue notification
      data.is_false_positive = true;
      checkResults.set(tabId, data);
      
      console.log("✅ False positive data stored for later notification");
      
      // Fallback: If page doesn't finish loading (error page, blocked, etc.),
      // send notification after 2 seconds anyway
      setTimeout(() => {
        const storedResult = checkResults.get(tabId);
        if (storedResult && storedResult.is_false_positive) {
          console.log("⏰ Timeout reached - sending blue notification now");
          
          // Use Chrome's native notification API (works on error pages)
          // Send to content script (original working approach)
          chrome.tabs.sendMessage(tabId, {
            action: "SHOW_FALSE_POSITIVE",
            data: {
              url: url,
              message: data.message || "Verified safe",
              model_prediction: data.model_prediction,
              final_decision: data.final_decision,
            },
          })
          .then(() => {
            console.log("✅ Blue notification sent successfully");
            checkResults.delete(tabId);
          })
          .catch((err) => console.log("⚠️ Content script not available:", err.message));
        }
      }, 2000);

      return; // DO NOT BLOCK - Allow navigation
    }

    // Store result for post-load notification
    checkResults.set(tabId, data);

    // CHANGED: Block VERY HIGH risk (>80%) with RED, Medium risk (40-80%) with YELLOW
    if (data.final_risk_pct > 80 || data.risk_level === "VERY SUSPICIOUS") {
      console.log(
        "🚫 HIGH RISK BLOCKING - Risk:",
        data.final_risk_pct.toFixed(1) + "%"
      );

      // Redirect to local blocking page (works even if target doesn't exist)
      const urlProb = (data.url_prob * 100).toFixed(1);
      const contentProb = (data.content_prob * 100).toFixed(1);
      const blockUrl =
        chrome.runtime.getURL("block.html") +
        `?url=${encodeURIComponent(url)}&risk=${data.final_risk_pct.toFixed(
          1
        )}&level=high&url_prob=${urlProb}&content_prob=${contentProb}`;
      chrome.tabs.update(tabId, { url: blockUrl });

      chrome.action.setBadgeText({ text: "⛔", tabId });
      chrome.action.setBadgeBackgroundColor({ color: "#DC2626", tabId });
    } else if (data.final_risk_pct > 40) {
      // MEDIUM risk - show YELLOW warning before page loads
      console.log(
        "⚠️ MEDIUM RISK WARNING - Risk:",
        data.final_risk_pct.toFixed(1) + "%"
      );

      // Redirect to local warning page
      const urlProb = (data.url_prob * 100).toFixed(1);
      const contentProb = (data.content_prob * 100).toFixed(1);
      const blockUrl =
        chrome.runtime.getURL("block.html") +
        `?url=${encodeURIComponent(url)}&risk=${data.final_risk_pct.toFixed(
          1
        )}&level=medium&url_prob=${urlProb}&content_prob=${contentProb}`;
      chrome.tabs.update(tabId, { url: blockUrl });

      chrome.action.setBadgeText({ text: "⚠", tabId });
      chrome.action.setBadgeBackgroundColor({ color: "#FF9800", tabId });
    } else {
      // Low risk - REMOVE checking overlay and allow page to load
      chrome.action.setBadgeText({ text: "✓", tabId });
      chrome.action.setBadgeBackgroundColor({ color: "#10B981", tabId });

      // Remove the checking overlay and restore visibility
      setTimeout(() => {
        chrome.scripting
          .executeScript({
            target: { tabId: tabId },
            func: () => {
              const overlay = document.getElementById("phishing-check-overlay");
              if (overlay) overlay.remove();
              // Restore page visibility
              if (document.body) {
                document.body.style.visibility = "visible";
              }
            },
          })
          .catch((err) => console.log("Overlay already removed:", err));
      }, 100);
    }
  } catch (error) {
    console.error("Security check error:", error);
  } finally {
    pendingChecks.delete(tabId);
  }
}

function handleResult(tabId, data) {
  const riskLevel = data.risk_level || "UNKNOWN";
  const color = data.color || "gray";
  const riskPct = data.final_risk_pct || 0;

  console.log("\n" + "=".repeat(70));
  console.log("HANDLE RESULT - TabId:", tabId);
  console.log("Risk Level:", riskLevel);
  console.log("Risk Pct:", riskPct.toFixed(1) + "%");
  console.log("Color:", color);
  console.log("Data:", data);
  console.log("=".repeat(70) + "\n");

  // ========================================================
  // Set badge based on risk level
  // ========================================================
  if (riskLevel === "VERY SUSPICIOUS" || riskPct > 75) {
    // RED - High risk
    chrome.action.setBadgeText({ text: "RISK", tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#d9534f", tabId: tabId });
    console.log("🔴 High risk detected - block.html already displayed");
  } else if (riskLevel === "POSSIBLY MALICIOUS" || riskPct > 40) {
    // YELLOW - Medium risk
    chrome.action.setBadgeText({ text: "WARN", tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#ff9800", tabId: tabId });
    console.log("🟡 Medium risk detected - block.html already displayed");
  } else {
    // GREEN - Safe
    chrome.action.setBadgeText({ text: "SAFE", tabId: tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#28a745", tabId: tabId });
    console.log("🟢 Page is SAFE");

    // Show small green notification
    showSafeNotification(tabId, data);
  }
}

function showSafeNotification(tabId, data) {
  try {
    console.log(
      "🟢 SHOW_SAFE - Attempting to show GREEN safe notification for tabId:",
      tabId
    );
    console.log("🟢 Message payload:", {
      action: "SHOW_SAFE",
      risk_pct: data.final_risk_pct,
    });

    chrome.tabs.sendMessage(
      tabId,
      {
        action: "SHOW_SAFE",
        data: {
          url: data.url,
          risk_level: data.risk_level,
          final_risk_pct: data.final_risk_pct,
          whitelisted: data.whitelisted,
        },
      },
      (response) => {
        if (chrome.runtime.lastError) {
          console.error(
            "FAILED to show GREEN notification:",
            chrome.runtime.lastError.message
          );
        } else {
          console.log("GREEN safe notification message sent successfully");
        }
      }
    );
  } catch (err) {
    console.error("Exception in showSafeNotification:", err);
  }
}

function showErrorBadge(tabId) {
  chrome.action.setBadgeText({ text: "ERR", tabId: tabId });
  chrome.action.setBadgeBackgroundColor({ color: "#6c757d", tabId: tabId });
}

// Listen for bypass requests
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "BYPASS_URL") {
    const url = message.url;
    console.log("✅ Adding URL to bypass list:", url);
    bypassedUrls.add(url);

    // Auto-remove from bypass after 1 minute (safety measure)
    setTimeout(() => {
      bypassedUrls.delete(url);
      console.log("⏰ Removed URL from bypass list:", url);
    }, 1 * 60 * 1000);

    sendResponse({ success: true });
  }
  return true;
});

// Extension loaded
chrome.runtime.onInstalled.addListener(() => {
  console.log("=" * 70);
  console.log("Rule-Based Phishing Detector Loaded!");
  console.log("=" * 70);
  console.log("API Endpoint:", API_ENDPOINT);
  console.log("Method: Rule-Based Fusion (No Ensemble)");
  console.log("Whitelist: Enabled");
  console.log("=" * 70);
});

// Log when extension starts
console.log("Extension background script active");
console.log("Monitoring tabs for phishing...");

