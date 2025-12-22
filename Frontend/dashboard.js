// ============================================================
// ENHANCED DASHBOARD JAVASCRIPT WITH EX PLAINABILITY
// ============================================================

// Global state
let allLogs = [];
let currentDisplayedLogs = [];
let currentFilter = "all";

// ============================================================
// THEME MANAGEMENT
// ============================================================

function initTheme() {
  const savedTheme = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  const newTheme = currentTheme === "light" ? "dark" : "light";

  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);

  // Add animation to theme toggle button
  const toggleBtn = document.getElementById("themeToggle");
  toggleBtn.style.transform = "rotate(360deg) scale(1.2)";
  setTimeout(() => {
    toggleBtn.style.transform = "";
  }, 500);
}

// ============================================================
// DATA FETCHING
// ============================================================

async function fetchLogs() {
  try {
    const response = await fetch("/api/logs");
    const data = await response.json();

    if (data.success) {
      allLogs = data.logs;
      await fetchStats(); // Refresh stats too
      renderTable(allLogs);
      updateTableInfo(allLogs.length);
    } else {
      showError("Failed to load logs");
    }
  } catch (error) {
    showError("Error loading dashboard data");
  }
}

async function fetchStats() {
  try {
    const response = await fetch("/api/stats");
    const data = await response.json();

    if (data.success) {
      updateStatistics(data);
    }
  } catch (error) {
  }
}

function showError(message) {
}

// ============================================================
// STATISTICS UPDATE
// ============================================================

function updateStatistics(stats) {
  // Update main stats cards (overall counts)
  animateCounter("totalBlocked", stats.total_detections || allLogs.length);
  animateCounter("highRisk", stats.blocked_total || 0);
  animateCounter("mediumRisk", stats.warned_total || 0);
  animateCounter("falsePositiveCount", stats.false_positives_total || 0);

}

function animateCounter(elementId, targetValue) {
  const element = document.getElementById(elementId);
  const duration = 1000;
  const steps = 30;
  const increment = targetValue / steps;
  let current = 0;

  const timer = setInterval(() => {
    current += increment;
    if (current >= targetValue) {
      element.textContent = targetValue;
      clearInterval(timer);
    } else {
      element.textContent = Math.floor(current);
    }
  }, duration / steps);
}

// ============================================================
// TABLE RENDERING
// ============================================================

function renderTable(logs) {
  currentDisplayedLogs = logs;
  const tbody = document.getElementById("logTableBody");

  if (logs.length === 0) {
    tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 3rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
                    <p style="font-size: 1.2rem; color: var(--text-secondary);">No logs found</p>
                </td>
            </tr>
        `;
    return;
  }

  tbody.innerHTML = logs
    .map((log, index) => {
      // Get prediction with fallback
      const prediction = log.prediction || (log.probability > 0.5 ? "Phishing" : "Legitimate");

      // Get risk level with proper color
      const riskLevel = log.risk_level || getRiskLevel(log.probability);
      const riskColor = getRiskColor(riskLevel);

      // Get action with fallback
      const action = log.action || "Unknown";

      // Check if this URL + timestamp is marked as false positive
      const isMarked =
        window.markedFalsePositives &&
        window.markedFalsePositives.some(
          (fp) => fp.url === log.url && fp.timestamp === log.timestamp
        );

      // Admin column - either "Reviewed" or "Report" button
      const adminCell = isMarked
        ? `<span class="fp-reviewed-badge"> Reviewed </span>`
        : `<button class="fp-btn-modern" onclick="event.stopPropagation(); markFalsePositive('${log.url}', '${log.timestamp}')" title="Report False Positive">
                <span class="fp-icon"> </span>
                <span class="fp-text">Report</span>
            </button>`;

      return `
        <tr style="animation-delay: ${index * 0.05}s" onclick="toggleDetails('${index}')">
            <td>${formatTimestamp(log.timestamp)}</td>
            <td class="url-cell" title="${log.url}">${truncateUrl(log.url)}</td>
            <td>
                <span style="font-weight: 600; color: ${prediction === 'Phishing' ? '#ef4444' : '#10b981'};">
                    ${prediction === 'Phishing' ? '⚠️' : '✅'} ${prediction}
                </span>
            </td>
            <td>
                <span class="risk-level-badge" style="background: ${riskColor}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: 600;">
                    ${riskLevel}
                </span>
            </td>
            <td>
                <span class="action-badge action-${action.toLowerCase()}">
                    ${getActionIcon(action)} ${action}
                </span>
            </td>
            <td>
                ${adminCell}
            </td>
        </tr>
        <tr id="details-${index}" class="details-row" style="display: none;">
            <td colspan="7">
                <div class="details-panel">
                    <div class="details-grid">
                        <div class="detail-item">
                            <strong>📊 Probability:</strong> ${log.probability}
                        </div>
                        <div class="detail-item">
                            <strong>🎯 Risk Level:</strong> ${riskLevel}
                        </div>
                        </div>
                        <div class="detail-item">
                            <strong>🌐 Full URL:</strong> <span style="word-break: break-all;">${
                              log.url
                            }</span>
                        </div>
                    </div>
                    <h4>🔍 Why was this URL flagged?</h4>
                    <div class="explanation-box">
                        ${formatDetailedReason(log.detailed_reason || log.reason)}
                    </div>
                </div>
            </td>
        </tr>
        `;
    })
    .join("");
}

function getRiskLevel(probability) {
  const prob = parseFloat(probability);
  if (prob >= 0.8) return "High Risk";
  if (prob >= 0.5) return "Medium Risk";
  if (prob >= 0.3) return "Low Risk";
  return "Safe";
}

function getRiskColor(riskLevel) {
  const colors = {
    "High Risk": "#ef4444",
    "Medium Risk": "#f59e0b",
    "Low Risk": "#eab308",
    Safe: "#10b981",
  };
  return colors[riskLevel] || "#6b7280";
}

function extractDomain(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch (e) {
    const match = url.match(/^(?:https?:\/\/)?(?:www\.)?([^\/\?#]+)/);
    return match ? match[1] : "Unknown";
  }
}

function formatDetailedReason(reason) {
  if (!reason) return "<p>No detailed information available</p>";

  // If reason contains bullet points, format them nicely
  if (reason.includes("•")) {
    const points = reason.split("•").filter((p) => p.trim());
    return (
      "<ul>" + points.map((p) => `<li>${p.trim()}</li>`).join("") + "</ul>"
    );
  }

  return `<p>${reason}</p>`;
}

function toggleDetails(index) {
  const detailsRow = document.getElementById(`details-${index}`);
  const dataRow = detailsRow.previousElementSibling;

  if (detailsRow.style.display === "none") {
    // Close all other details and remove selection
    document.querySelectorAll(".details-row").forEach((row) => {
      row.style.display = "none";
    });
    document
      .querySelectorAll(".data-table tbody tr:not(.details-row)")
      .forEach((row) => {
        row.classList.remove("selected");
      });

    // Open this one and mark as selected
    detailsRow.style.display = "table-row";
    dataRow.classList.add("selected");
  } else {
    detailsRow.style.display = "none";
    dataRow.classList.remove("selected");
  }
}

function formatTimestamp(timestamp) {
  if (!timestamp) return "Invalid Date";

  const date = new Date(timestamp);

  // Check if date is valid
  if (isNaN(date.getTime())) return "Invalid Date";

  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString() + " " + date.toLocaleTimeString();
}

function truncateUrl(url) {
  if (url.length <= 50) return url;
  return url.substring(0, 47) + "...";
}

function getActionIcon(action) {
  const icons = {
    Blocked: "🚫",
    Warned: "⚠️",
    Allowed: "✓",
  };
  return icons[action] || "";
}

function updateTableInfo(count) {
  const info = document.getElementById("tableInfo");
  info.textContent = `Showing ${count} detection${count !== 1 ? "s" : ""}`;
}

// ============================================================
// FILTERING FUNCTIONS
// ============================================================


function filterLogs(filterType) {
  currentFilter = filterType;
  
  // Update button states
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.dataset.filter === filterType) {
      btn.classList.add('active');
    }
  });
  
  // Special handling for False Positives
  if (filterType === 'FalsePositives') {
    fetchFalsePositives();
  } else {
    applyFilters();
  }
}

function applyFilters() {
  const searchTerm = document.getElementById("searchInput").value.toLowerCase();
  const dateFilter = document.getElementById("dateFilterType").value;

  let filtered = allLogs;

  // Apply action filter
  if (currentFilter !== "all") {
    filtered = filtered.filter((log) => log.action === currentFilter);
  }

  // Apply date filter
  filtered = filterByDate(filtered, dateFilter);

  // Apply search filter
  if (searchTerm) {
    filtered = filtered.filter((log) =>
      log.url.toLowerCase().includes(searchTerm)
    );
  }

  renderTable(filtered);
  updateTableInfo(filtered.length);
}

function filterByDate(logs, filterType) {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  return logs.filter((log) => {
    if (!log.timestamp) return false;
    const logDate = new Date(log.timestamp);

    // Handle specific month selection (month-1, month-2, etc.)
    if (filterType.startsWith("month-")) {
      const monthsAgo = parseInt(filterType.split("-")[1]);

      // Month-0 is a separator, show all
      if (monthsAgo === 0) return true;

      // Calculate the target month
      const targetDate = new Date(
        now.getFullYear(),
        now.getMonth() - monthsAgo,
        1
      );
      const targetYear = targetDate.getFullYear();
      const targetMonth = targetDate.getMonth();

      return (
        logDate.getFullYear() === targetYear &&
        logDate.getMonth() === targetMonth
      );
    }

    switch (filterType) {
      case "today":
        const logDay = new Date(
          logDate.getFullYear(),
          logDate.getMonth(),
          logDate.getDate()
        );
        return logDay.getTime() === today.getTime();

      case "week":
        const weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        return logDate >= weekAgo;

      case "month":
        return (
          logDate.getMonth() === now.getMonth() &&
          logDate.getFullYear() === now.getFullYear()
        );

      case "year":
        return logDate.getFullYear() === now.getFullYear();

      default:
        return true;
    }
  });
}

async function fetchFalsePositives() {
  try {
    const response = await fetch("/api/false_positives");

    const data = await response.json();

    if (data.success) {
      // Convert false positive format to match log format for rendering
      const fpLogs = data.false_positives.map((fp) => ({
        timestamp: fp.original_detection_time || fp.timestamp,
        url: fp.url,
        prediction: fp.predicted_label,
        probability: (fp.confidence * 100).toFixed(2) + "%",
        action: "Reported FP",
        risk_level: fp.risk_level,
        reason: fp.detection_reason,
        detailed_reason: fp.detailed_features,
      }));

      renderTable(fpLogs);
      updateTableInfo(fpLogs.length);
    } else {
      renderTable([]);
      updateTableInfo(0);
    }
  } catch (error) {
    renderTable([]);
    updateTableInfo(0);
  }
}

// ============================================================
// FALSE POSITIVE MARKING
// ============================================================

let pendingFPUrl = null;
let pendingFPTimestamp = null;

function markFalsePositive(url, timestamp) {
  // Store pending values
  pendingFPUrl = url;
  pendingFPTimestamp = timestamp;

  // Update modal with URL
  document.getElementById("fpModalUrl").textContent = url;

  // Show modal
  const modal = document.getElementById("fpModal");
  modal.style.display = "flex";
  document.body.style.overflow = "hidden";
}

function closeFPModal() {
  const modal = document.getElementById("fpModal");
  modal.style.display = "none";
  document.body.style.overflow = "";
  pendingFPUrl = null;
  pendingFPTimestamp = null;
}

async function confirmFalsePositive() {
  if (!pendingFPUrl) return;

  try {
    const response = await fetch("/api/mark_false_positive", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: pendingFPUrl,
        timestamp: pendingFPTimestamp,
        note: "", // No note needed anymore
      }),
    });

    const data = await response.json();

    if (data.success) {
      // Initialize tracking array if needed
      if (!window.markedFalsePositives) {
        window.markedFalsePositives = [];
      }

      // Add to marked list (prevent duplicate marking)
      if (!data.already_marked) {
        window.markedFalsePositives.push({
          url: pendingFPUrl,
          timestamp: pendingFPTimestamp,
        });
      }

      // Show success notification
      showNotification("✅ Marked as false positive successfully!", "success");

      // Refresh the logs to remove the entry from the table
      await fetchLogs();
      
      // Refresh stats
      fetchStats();

      closeFPModal();
    } else {
      showNotification("Failed to mark as false positive", "error");
    }
  } catch (error) {
    showNotification(" Error: Could not mark as false positive", "error");
  }
}

// Load false positive URLs on page load for persistence
async function loadMarkedFalsePositives() {
  try {
    const response = await fetch('/api/false_positives');
    const data = await response.json();
    
    if (data.success) {
      window.markedFalsePositives = data.false_positives.map(fp => ({
        url: fp.url,
        timestamp: fp.original_detection_time || fp.timestamp
      }));
    }
  } catch (error) {
    window.markedFalsePositives = [];
  }
}

function showNotification(message, type) {
  // Create simple notification
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        border-radius: 12px;
        font-weight: 600;
        z-index: 10002;
        animation: slideInRight 0.3s ease-out;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    `;

  if (type === "success") {
    notification.style.background = "linear-gradient(135deg, #10b981, #059669)";
    notification.style.color = "white";
  } else {
    notification.style.background = "linear-gradient(135deg, #ef4444, #dc2626)";
    notification.style.color = "white";
  }

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = "slideOutRight 0.3s ease-out";
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// ============================================================
// FILTERING & SEARCH
// ============================================================


function applyFilters() {
  const searchQuery = document
    .getElementById("searchInput")
    .value.toLowerCase();
  const dateFilterType =
    document.getElementById("dateFilterType")?.value || "all";

  let filtered = allLogs;

  // Apply action filter
  if (currentFilter !== "all") {
    filtered = filtered.filter((log) => log.action === currentFilter);
  }

  // Apply date filter
  if (dateFilterType !== "all") {
    filtered = filterByDate(filtered, dateFilterType);
  }

  // Apply search filter
  if (searchQuery) {
    filtered = filtered.filter(
      (log) =>
        log.url.toLowerCase().includes(searchQuery) ||
        (log.reason && log.reason.toLowerCase().includes(searchQuery))
    );
  }

  renderTable(filtered);
  updateTableInfo(filtered.length);
}

function filterByDate(logs, filterType) {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  // Check if there's a custom date selected (from calendar icon)
  const customDateInput = document.getElementById("customDate");
  const customDateValue = customDateInput?.value;

  if (customDateValue) {
    // Filter by custom date if one is selected
    return logs.filter((log) => {
      if (!log.timestamp) return false;
      const logDate = new Date(log.timestamp);
      const selectedDate = new Date(customDateValue);
      const logDay = new Date(
        logDate.getFullYear(),
        logDate.getMonth(),
        logDate.getDate()
      );
      const selectedDay = new Date(
        selectedDate.getFullYear(),
        selectedDate.getMonth(),
        selectedDate.getDate()
      );
      return logDay.getTime() === selectedDay.getTime();
    });
  }

  // Otherwise use dropdown filter
  return logs.filter((log) => {
    if (!log.timestamp) return false;
    const logDate = new Date(log.timestamp);

    switch (filterType) {
      case "today":
        const logDay = new Date(
          logDate.getFullYear(),
          logDate.getMonth(),
          logDate.getDate()
        );
        return logDay.getTime() === today.getTime();

      case "week":
        const weekAgo = new Date(today);
        weekAgo.setDate(weekAgo.getDate() - 7);
        return logDate >= weekAgo;

      case "month":
        return (
          logDate.getMonth() === now.getMonth() &&
          logDate.getFullYear() === now.getFullYear()
        );

      case "year":
        return logDate.getFullYear() === now.getFullYear();

      default:
        return true;
    }
  });
}

// ============================================================
// REFRESH FUNCTIONALITY
// ============================================================

function refreshDashboard() {
  const refreshBtn = document.getElementById("refreshBtn");
  const refreshIcon = refreshBtn.querySelector(".refresh-icon");

  refreshIcon.style.animation = "spin 1s linear";

  fetchLogs().then(() => {
    setTimeout(() => {
      refreshIcon.style.animation = "";
    }, 1000);
  });
}

function exportToCSV() {
  if (!currentDisplayedLogs || currentDisplayedLogs.length === 0) {
    showNotification("No data to export", "error");
    return;
  }

  // Define headers
  const headers = ["Timestamp", "URL", "Prediction", "Probability", "Risk Level", "Action", "Reason"];
  
  // Convert logs to CSV rows
  const csvRows = [headers.join(",")];
  
  currentDisplayedLogs.forEach(log => {
    let timestampStr = log.timestamp;
    try {
        timestampStr = new Date(log.timestamp).toLocaleString();
    } catch(e) {}

    // Helper to clean text: remove emojis and replace bullets
    const cleanForCSV = (text) => {
        if (!text) return "";
        return text
            .toString()
            .replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F700}-\u{1F7FF}\u{1F900}-\u{1F9FF}]/gu, '') 
            .replace(/•/g, '-')     
            .replace(/â€¢/g, '-')   
            .replace(/ðŸŸ¡/g, '')  
            .replace(/ðŸ/g, '')    
            .trim();
    };

    const prediction = log.prediction || (log.probability > 0.5 ? 'Phishing' : 'Legitimate');
    const riskLevel = log.risk_level || getRiskLevel(log.probability);
    const action = log.action || 'Unknown';
    const reason = log.detailed_reason || log.reason || '';

    const row = [
      `"${timestampStr}"`,
      `"${(log.url || '').replace(/"/g, '""')}"`,
      `"${cleanForCSV(prediction)}"`,
      `"${log.probability}"`,
      `"${cleanForCSV(riskLevel)}"`,
      `"${cleanForCSV(action)}"`,
      `"${cleanForCSV(reason).replace(/"/g, '""')}"`
    ];
    csvRows.push(row.join(","));
  });
  
  // Create blob and download link
  const csvString = csvRows.join("\n");
  // Add BOM (Byte Order Mark) for Excel to recognize UTF-8
  const blob = new Blob(["\uFEFF" + csvString], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement("a");
  link.href = url;
  link.download = `detection_logs_${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
  
  showNotification("✅ Export started!", "success");
}

// ============================================================
// CUSTOM DATE PICKER FUNCTIONS
// ============================================================

let activeTab = "date";

function openDatePicker() {
  const modal = document.getElementById("datePickerModal");
  modal.style.display = "flex";
  document.body.style.overflow = "hidden";

  // Populate year dropdown if not already done
  populateYearDropdown();
}

function closeDatePicker() {
  const modal = document.getElementById("datePickerModal");
  modal.style.display = "none";
  document.body.style.overflow = "";
}

function switchTab(tabName) {
  activeTab = tabName;

  // Update tab buttons
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.remove("active");
    if (btn.dataset.tab === tabName) {
      btn.classList.add("active");
    }
  });

  // Update tab content
  document.querySelectorAll(".tab-content").forEach((content) => {
    content.classList.remove("active");
  });
  document.getElementById(`${tabName}Tab`).classList.add("active");
}

function populateYearDropdown() {
  const select = document.getElementById("customYearInput");
  if (select.options.length > 1) return; // Already populated

  const currentYear = new Date().getFullYear();
  for (let year = currentYear; year >= currentYear - 10; year--) {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year;
    select.appendChild(option);
  }
}

function applyCustomDate() {
  let selectedValue, displayText;

  if (activeTab === "date") {
    const dateInput = document.getElementById("customDateInput");
    selectedValue = dateInput.value;
    if (!selectedValue) {
      alert("Please select a date");
      return;
    }
    const date = new Date(selectedValue);
    displayText = date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
    window.customFilterType = "date";
    window.customFilterValue = selectedValue;
  } else if (activeTab === "month") {
    const monthInput = document.getElementById("customMonthInput");
    selectedValue = monthInput.value;
    if (!selectedValue) {
      alert("Please select a month");
      return;
    }
    const monthNames = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];
    displayText = monthNames[parseInt(selectedValue)];
    window.customFilterType = "month";
    window.customFilterValue = selectedValue; // Store as month index (0-11)
  } else if (activeTab === "year") {
    const yearInput = document.getElementById("customYearInput");
    selectedValue = yearInput.value;
    if (!selectedValue) {
      alert("Please select a year");
      return;
    }
    displayText = selectedValue;
    window.customFilterType = "year";
    window.customFilterValue = selectedValue;
  }

  // Update button text
  document.getElementById("timeRangeText").textContent = displayText;

  // Apply filters
  applyFilters();
  closeDatePicker();
}

// Update applyFilters to check for custom filter
const originalApplyFilters = applyFilters;
applyFilters = function () {
  const searchTerm = document.getElementById("searchInput").value.toLowerCase();

  let filtered = allLogs;

  // Apply action filter
  if (currentFilter !== "all") {
    filtered = filtered.filter((log) => log.action === currentFilter);
  }

  // Apply custom date/month/year filter
  if (window.customFilterType && window.customFilterValue) {
    filtered = filterByCustomSelection(
      filtered,
      window.customFilterType,
      window.customFilterValue
    );
  }

  // Apply search filter
  if (searchTerm) {
    filtered = filtered.filter((log) =>
      log.url.toLowerCase().includes(searchTerm)
    );
  }

  renderTable(filtered);
  updateTableInfo(filtered.length);
};

function filterByCustomSelection(logs, type, value) {
  return logs.filter((log) => {
    if (!log.timestamp) return false;
    const logDate = new Date(log.timestamp);

    if (type === "date") {
      const selectedDate = new Date(value);
      const logDay = new Date(
        logDate.getFullYear(),
        logDate.getMonth(),
        logDate.getDate()
      );
      const selectedDay = new Date(
        selectedDate.getFullYear(),
        selectedDate.getMonth(),
        selectedDate.getDate()
      );
      return logDay.getTime() === selectedDay.getTime();
    } else if (type === "month") {
      // Match by month index (0-11) across all years
      return logDate.getMonth() === parseInt(value);
    } else if (type === "year") {
      return logDate.getFullYear() === parseInt(value);
    }
    return true;
  });
}

// ============================================================
// EVENT LISTENERS
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
  
  // Initialize theme
  initTheme();
  
  // Load marked false positives for persistent state
  loadMarkedFalsePositives();

  // Theme toggle
  document.getElementById("themeToggle").addEventListener("click", toggleTheme);

  // Filter buttons
  const filterButtons = document.querySelectorAll(".filter-btn");
  
  filterButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterLogs(btn.dataset.filter);
    });
  });

  // Search input
  document.getElementById("searchInput").addEventListener("input", (e) => {
    applyFilters();
  });

  // Time range button click - open date picker
  const timeRangeButton = document.getElementById("timeRangeButton");
  if (timeRangeButton) {
    timeRangeButton.addEventListener("click", () => {
      openDatePicker();
    });
  }

  // Refresh button
  document
    .getElementById("refreshBtn")
    .addEventListener("click", refreshDashboard);

  // Load initial data
  fetchLogs();

  // Auto-refresh every 30 seconds
  setInterval(fetchLogs, 30000);
});

// ============================================================
// ADDITIONAL ANIMATIONS
// ============================================================

// Parallax effect
document.addEventListener("mousemove", (e) => {
  const sun = document.querySelector(".sun");
  const moon = document.querySelector(".moon");

  const moveX = (e.clientX / window.innerWidth - 0.5) * 20;
  const moveY = (e.clientY / window.innerHeight - 0.5) * 20;

  if (sun) {
    sun.style.transform = `translate(${moveX}px, ${moveY}px)`;
  }
  if (moon) {
    moon.style.transform = `translate(${moveX}px, ${moveY}px)`;
  }
});
