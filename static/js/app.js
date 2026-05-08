/**
 * AI Risk Narrative Generator - Frontend Application
 * Integrates with Flask backend APIs for risk analysis
 */

// ===== Configuration =====
const API_CONFIG = {
  baseURL: window.location.origin,
  endpoints: {
    describe: '/describe',
    recommend: '/recommend',
    report: '/generate-report',
    health: '/health'
  },
  timeout: 30000 // 30 seconds
};

// ===== DOM Elements =====
const form = document.getElementById('assistantForm');
const submitBtn = document.getElementById('submitBtn');
const clearBtn = document.getElementById('clearBtn');
const riskTypeInput = document.getElementById('riskType');
const severitySelect = document.getElementById('severity');
const detailsTextarea = document.getElementById('details');
const charCount = document.getElementById('charCount');
const responseBody = document.getElementById('responseBody');
const healthBadge = document.getElementById('healthBadge');
const apiStatus = document.getElementById('apiStatus');
const cacheStatus = document.getElementById('cacheStatus');
const footerTime = document.getElementById('footerTime');

// ===== Utility Functions =====

/**
 * Show toast notification
 * @param {string} message - Toast message
 * @param {string} type - 'success', 'error', 'info', 'warning'
 * @param {number} duration - Duration in ms
 */
function showToast(message, type = 'info', duration = 4000) {
  const toastHTML = `
    <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="toast-header">
        <strong class="me-auto">
          ${type === 'success' ? '<i class="bi bi-check-circle text-success"></i>' : 
            type === 'error' ? '<i class="bi bi-exclamation-circle text-danger"></i>' : 
            type === 'warning' ? '<i class="bi bi-exclamation-triangle text-warning"></i>' :
            '<i class="bi bi-info-circle text-info"></i>'}
          ${type.charAt(0).toUpperCase() + type.slice(1)}
        </strong>
        <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    </div>
  `;

  const container = document.getElementById('toastContainer');
  const toastElement = document.createElement('div');
  toastElement.innerHTML = toastHTML;
  container.appendChild(toastElement);

  const toast = new bootstrap.Toast(toastElement.querySelector('.toast'));
  toast.show();

  setTimeout(() => {
    toastElement.remove();
  }, duration);
}

/**
 * Show loading state
 */
function showLoading() {
  responseBody.innerHTML = `
    <div id="loadingState">
      <div class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted mb-1">Generating AI insight...</p>
        <small id="responseTime" class="text-muted">Processing...</small>
      </div>
    </div>
  `;
}

/**
 * Display success response
 * @param {object} data - API response data
 * @param {string} endpoint - API endpoint called
 * @param {number} timeMs - Response time in milliseconds
 */
function showSuccessResponse(data, endpoint, timeMs) {
  document.getElementById('emptyState')?.remove();
  
  const responseHtml = `
    <div id="successResponse">
      <div class="row g-2 mb-3">
        <div class="col-auto">
          <span class="badge bg-success">
            <i class="bi bi-check-circle me-1"></i>Success
          </span>
        </div>
        <div class="col-auto">
          <span id="endpointBadge" class="badge bg-info text-dark">
            <i class="bi bi-link-45deg me-1"></i>${endpoint}
          </span>
        </div>
        <div class="col-auto">
          <span id="timingBadge" class="badge bg-secondary">
            <i class="bi bi-clock me-1"></i>${timeMs}ms
          </span>
        </div>
        <div class="ms-auto">
          <button class="btn btn-sm btn-outline-secondary" id="copyBtn">
            <i class="bi bi-clipboard me-1"></i>Copy JSON
          </button>
        </div>
      </div>
      <pre id="jsonResponse" class="bg-dark p-3 rounded border border-secondary mb-0"><code>${JSON.stringify(data, null, 2)}</code></pre>
    </div>
  `;

  responseBody.innerHTML = responseHtml;

  // Add copy functionality
  document.getElementById('copyBtn').addEventListener('click', () => {
    const jsonText = JSON.stringify(data, null, 2);
    navigator.clipboard.writeText(jsonText).then(() => {
      showToast('JSON copied to clipboard!', 'success', 2000);
    }).catch(() => {
      showToast('Failed to copy JSON', 'error');
    });
  });

  // Auto-scroll to response
  responseBody.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Display error response
 * @param {string} message - Error message
 * @param {string} details - Error details
 */
function showErrorResponse(message, details = '') {
  document.getElementById('emptyState')?.remove();
  
  const errorHtml = `
    <div id="errorResponse">
      <div class="alert alert-danger mb-0">
        <h6 class="alert-heading">
          <i class="bi bi-exclamation-triangle me-2"></i>Error
        </h6>
        <p id="errorMessage" class="mb-2">${message}</p>
        ${details ? `<small class="text-muted">${details}</small>` : ''}
      </div>
    </div>
  `;

  responseBody.innerHTML = errorHtml;
  responseBody.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Fetch from API with timeout
 * @param {string} url - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise}
 */
async function fetchWithTimeout(url, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

/**
 * Update health status
 */
async function updateHealthStatus() {
  try {
    const response = await fetchWithTimeout(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.health}`);
    const health = await response.json();

    if (response.ok) {
      // API is healthy
      apiStatus.innerHTML = '<i class="bi bi-check-circle me-1 text-success"></i> Configured';
      apiStatus.className = 'badge bg-success';
      
      // Cache status
      if (health.cache && health.cache.status === 'healthy') {
        cacheStatus.innerHTML = '<i class="bi bi-hourglass-bottom me-1 text-info"></i> Connected';
        cacheStatus.className = 'badge bg-info text-dark';
      } else {
        cacheStatus.innerHTML = '<i class="bi bi-exclamation-circle me-1"></i> Offline';
        cacheStatus.className = 'badge bg-warning';
      }

      healthBadge.innerHTML = '<i class="bi bi-check-circle me-1 text-success"></i> Service Healthy';
      healthBadge.className = 'badge bg-success';
    } else {
      throw new Error('Health check failed');
    }
  } catch (error) {
    apiStatus.innerHTML = '<i class="bi bi-x-circle me-1 text-danger"></i> Not Configured';
    apiStatus.className = 'badge bg-danger';
    cacheStatus.innerHTML = '<i class="bi bi-x-circle me-1"></i> Offline';
    cacheStatus.className = 'badge bg-danger';
    healthBadge.innerHTML = '<i class="bi bi-x-circle me-1 text-danger"></i> Service Offline';
    healthBadge.className = 'badge bg-danger';
  }
}

/**
 * Update character counter
 */
function updateCharCount() {
  const count = detailsTextarea.value.length;
  const max = detailsTextarea.maxLength;
  const percentage = (count / max) * 100;
  
  charCount.textContent = `${count}/${max}`;
  
  // Change color based on usage
  if (percentage > 90) {
    charCount.className = 'text-danger';
  } else if (percentage > 75) {
    charCount.className = 'text-warning';
  } else {
    charCount.className = 'text-muted';
  }
}

/**
 * Update footer time
 */
function updateFooterTime() {
  const now = new Date();
  const timeString = now.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  });
  footerTime.textContent = timeString;
}

/**
 * Validate form inputs
 * @returns {object} Validation result with isValid flag and errors
 */
function validateForm() {
  const errors = [];
  
  if (!riskTypeInput.value.trim()) {
    errors.push('Risk Type is required');
  }
  
  if (!severitySelect.value.trim()) {
    errors.push('Severity Level is required');
  }
  
  if (!detailsTextarea.value.trim()) {
    errors.push('Risk Details are required');
  }
  
  if (detailsTextarea.value.trim().length < 10) {
    errors.push('Risk Details must be at least 10 characters');
  }
  
  return {
    isValid: errors.length === 0,
    errors: errors
  };
}

// ===== Event Listeners =====

/**
 * Form submission handler
 */
form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Validate form
  const validation = validateForm();
  if (!validation.isValid) {
    validation.errors.forEach(error => {
      showToast(error, 'warning');
    });
    return;
  }

  // Get selected endpoint
  const selectedTask = document.querySelector('input[name="task"]:checked');
  if (!selectedTask) {
    showToast('Please select an analysis type', 'warning');
    return;
  }

  const endpoint = selectedTask.value;

  // Prepare request payload
  const payload = {
    risk_type: riskTypeInput.value.trim(),
    severity: severitySelect.value.trim(),
    details: detailsTextarea.value.trim()
  };

  // Disable submit button and show loading
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
  
  showLoading();

  try {
    // Make API request with timing
    const startTime = performance.now();
    
    const response = await fetchWithTimeout(`${API_CONFIG.baseURL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const endTime = performance.now();
    const responseTime = Math.round(endTime - startTime);

    const responseData = await response.json();

    if (response.ok) {
      showSuccessResponse(responseData, endpoint, responseTime);
      showToast('Analysis generated successfully!', 'success');
    } else {
      showErrorResponse(
        responseData.error || 'API Error',
        `Status: ${response.status} - ${response.statusText}`
      );
      showToast(`Error: ${responseData.error || 'Failed to generate analysis'}`, 'error');
    }
  } catch (error) {
    // Handle different error types
    let errorMessage = 'Failed to generate analysis';
    let errorDetails = '';

    if (error.name === 'AbortError') {
      errorMessage = 'Request Timeout';
      errorDetails = `The request took longer than ${API_CONFIG.timeout}ms`;
    } else if (error instanceof TypeError) {
      errorMessage = 'Network Error';
      errorDetails = 'Unable to connect to the service. Check your connection and try again.';
    } else {
      errorDetails = error.message;
    }

    showErrorResponse(errorMessage, errorDetails);
    showToast(errorMessage, 'error');
  } finally {
    // Re-enable submit button
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="bi bi-send me-2"></i>Send to Assistant';
  }
});

/**
 * Clear form handler
 */
clearBtn.addEventListener('click', () => {
  form.reset();
  riskTypeInput.value = 'Cybersecurity';
  severitySelect.value = 'High';
  updateCharCount();
  responseBody.innerHTML = `
    <div id="emptyState" class="text-center py-5">
      <i class="bi bi-chat-dots display-1 text-muted opacity-25"></i>
      <p class="text-muted mt-3 mb-0">
        Submit your risk details to see AI-generated insights
      </p>
    </div>
  `;
  showToast('Form cleared', 'info', 1500);
});

/**
 * Character counter update
 */
detailsTextarea.addEventListener('input', updateCharCount);

/**
 * Task selection change
 */
document.querySelectorAll('input[name="task"]').forEach(radio => {
  radio.addEventListener('change', function() {
    // Visual feedback for selected task (Bootstrap handles this with btn-check)
    showToast(`Selected: ${this.nextElementSibling.querySelector('span:first-of-type')?.textContent || 'Analysis'}`, 'info', 1500);
  });
});

// ===== Initialization =====

/**
 * Initialize application
 */
async function initializeApp() {
  // Check health on page load
  await updateHealthStatus();

  // Update character count
  updateCharCount();

  // Update footer time
  updateFooterTime();
  setInterval(updateFooterTime, 1000);

  // Set initial empty state
  responseBody.innerHTML = `
    <div id="emptyState" class="text-center py-5">
      <i class="bi bi-chat-dots display-1 text-muted opacity-25"></i>
      <p class="text-muted mt-3 mb-0">
        Submit your risk details to see AI-generated insights
      </p>
    </div>
  `;

  // Focus on form for better UX
  riskTypeInput.focus();

  showToast('AI Risk Narrative Generator loaded successfully', 'success', 2500);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializeApp);

// Update health status periodically (every 30 seconds)
setInterval(updateHealthStatus, 30000);
