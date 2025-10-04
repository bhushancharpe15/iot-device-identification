// IoT Device Identification System - JavaScript

// Global variable to track modal state
let loadingModalInstance = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    setupEventListeners();
    
    // Load dataset information
    loadDatasetInfo();
    
    // Add modal cleanup event listener
    const modalElement = document.getElementById('loadingModal');
    if (modalElement) {
        modalElement.addEventListener('hidden.bs.modal', function() {
            // Clean up when modal is hidden
            loadingModalInstance = null;
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
        });
    }
}

function setupEventListeners() {
    // Form submission
    const form = document.getElementById('predictionForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function handleFormSubmit(e) {
    e.preventDefault();
    
    // Show loading modal
    showLoadingModal();
    
    // Collect form data
    const formData = new FormData(document.getElementById('predictionForm'));
    const data = {};
    
    // Convert FormData to object
    for (let [key, value] of formData.entries()) {
        data[key] = value || '0';
    }
    
    // Make prediction request
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(data)
    })
    .then(response => response.json())
    .then(result => {
        hideLoadingModal();
        if (result.success) {
            displayResults(result);
        } else {
            showError('Prediction failed: ' + (result.error || 'Unknown error'));
        }
    })
    .catch(error => {
        hideLoadingModal();
        showError('Network error: ' + error.message);
    })
    .finally(() => {
        // Ensure modal is hidden even if there are any issues
        setTimeout(() => {
            hideLoadingModal();
        }, 100);
    });
}

function displayResults(result) {
    const resultsSection = document.getElementById('results');
    const resultContainer = document.getElementById('predictionResult');
    
    // Create results HTML
    const resultsHTML = `
        <div class="result-card fade-in">
            <div class="text-center mb-4">
                <div class="device-icon">
                    ${getDeviceIcon(result.predicted_class)}
                </div>
                <h2 class="mb-3">Predicted Device: ${formatDeviceName(result.predicted_class)}</h2>
                <div class="confidence-score">
                    <h4>Confidence: ${(result.confidence_scores[result.predicted_class] * 100).toFixed(2)}%</h4>
                </div>
            </div>
            
            <div class="confidence-breakdown">
                <h5 class="mb-3">Confidence Breakdown:</h5>
                ${result.sorted_confidence.map(([device, confidence]) => `
                    <div class="mb-2">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span>${formatDeviceName(device)}</span>
                            <span>${(confidence * 100).toFixed(2)}%</span>
                        </div>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${confidence * 100}%"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="confidenceChart"></canvas>
        </div>
    `;
    
    resultContainer.innerHTML = resultsHTML;
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Create chart
    createConfidenceChart(result.sorted_confidence);
}

function createConfidenceChart(confidenceData) {
    const ctx = document.getElementById('confidenceChart').getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: confidenceData.map(([device, _]) => formatDeviceName(device)),
            datasets: [{
                label: 'Confidence Score',
                data: confidenceData.map(([_, confidence]) => confidence * 100),
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)',
                    'rgba(240, 147, 251, 0.8)',
                    'rgba(245, 87, 108, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(13, 202, 240, 0.8)',
                    'rgba(25, 135, 84, 0.8)',
                    'rgba(220, 53, 69, 0.8)',
                    'rgba(111, 66, 193, 0.8)'
                ],
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(118, 75, 162, 1)',
                    'rgba(240, 147, 251, 1)',
                    'rgba(245, 87, 108, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(13, 202, 240, 1)',
                    'rgba(25, 135, 84, 1)',
                    'rgba(220, 53, 69, 1)',
                    'rgba(111, 66, 193, 1)'
                ],
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Device Classification Confidence Scores',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            animation: {
                duration: 2000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function getDeviceIcon(deviceType) {
    const icons = {
        'baby_monitor': 'fas fa-baby',
        'lights': 'fas fa-lightbulb',
        'motion_sensor': 'fas fa-eye',
        'security_camera': 'fas fa-video',
        'smoke_detector': 'fas fa-fire',
        'socket': 'fas fa-plug',
        'thermostat': 'fas fa-thermometer-half',
        'TV': 'fas fa-tv',
        'watch': 'fas fa-clock'
    };
    return icons[deviceType] || 'fas fa-microchip';
}

function formatDeviceName(deviceType) {
    return deviceType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function loadSampleData() {
    showLoadingModal();
    
    fetch('/sample_data')
    .then(response => response.json())
    .then(data => {
        hideLoadingModal();
        if (data.error) {
            showError('Failed to load sample data: ' + data.error);
        } else {
            populateForm(data);
            showSuccess('Sample data loaded successfully!');
        }
    })
    .catch(error => {
        hideLoadingModal();
        showError('Network error: ' + error.message);
    });
}

function populateForm(data) {
    // Populate form fields with sample data
    Object.keys(data).forEach(key => {
        if (key !== 'actual_category') {
            const input = document.getElementById(key);
            if (input) {
                input.value = data[key];
            }
        }
    });
    
    // Show actual category if available
    if (data.actual_category) {
        showInfo(`Sample data from: ${formatDeviceName(data.actual_category)}`);
    }
}

function clearForm() {
    document.getElementById('predictionForm').reset();
    document.getElementById('results').style.display = 'none';
    showSuccess('Form cleared successfully!');
}

function loadDatasetInfo() {
    fetch('/dataset_info')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Failed to load dataset info:', data.error);
        } else {
            console.log('Dataset loaded:', data);
            // You can use this data to display statistics on the page
        }
    })
    .catch(error => {
        console.error('Network error loading dataset info:', error);
    });
}

function showLoadingModal() {
    const modalElement = document.getElementById('loadingModal');
    if (modalElement) {
        // Store the modal instance globally
        loadingModalInstance = new bootstrap.Modal(modalElement);
        loadingModalInstance.show();
    }
}

function hideLoadingModal() {
    if (loadingModalInstance) {
        loadingModalInstance.hide();
        loadingModalInstance = null;
    }
    
    // Force cleanup of modal elements
    const modalElement = document.getElementById('loadingModal');
    if (modalElement) {
        // Remove modal backdrop if it exists
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        
        // Remove modal-open class from body
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        // Force hide the modal element
        modalElement.style.display = 'none';
        modalElement.classList.remove('show');
    }
}

function showError(message) {
    showAlert(message, 'danger');
}

function showSuccess(message) {
    showAlert(message, 'success');
}

function showInfo(message) {
    showAlert(message, 'info');
}

function showAlert(message, type) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Utility function to validate form inputs
function validateForm() {
    const requiredFields = ['bytes', 'packets', 'duration'];
    let isValid = true;
    
    requiredFields.forEach(fieldName => {
        const field = document.getElementById(fieldName);
        if (field && (!field.value || field.value.trim() === '')) {
            field.classList.add('is-invalid');
            isValid = false;
        } else if (field) {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Add form validation on input
document.addEventListener('input', function(e) {
    if (e.target.classList.contains('form-control')) {
        e.target.classList.remove('is-invalid');
    }
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter to submit form
    if (e.ctrlKey && e.key === 'Enter') {
        const form = document.getElementById('predictionForm');
        if (form) {
            form.dispatchEvent(new Event('submit'));
        }
    }
    
    // Escape to clear form
    if (e.key === 'Escape') {
        clearForm();
    }
});
