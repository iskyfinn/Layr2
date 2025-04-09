/**
 * Layr - Architecture Analysis Platform
 * Main JavaScript Functions
 */

// Enable Bootstrap tooltips
window.addEventListener('load', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
// Add this at the top of your main.js file
console.log('Layr application initializing...');

// Add this to your DOMContentLoaded listener
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    
    // Log button counts to help with debugging
    console.log('Total buttons on page:', document.querySelectorAll('button').length);
    console.log('Bootstrap buttons on page:', document.querySelectorAll('.btn').length);
    
    // Check if tooltip initialization succeeds
    try {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        console.log('Tooltips initialized:', tooltipList.length);
    } catch (e) {
        console.error('Error initializing tooltips:', e);
    }
});

    // Format application status badges
    formatStatusBadges();
    
    // Initialize other components
    initFlashMessages();

    // Additional initializations
    if (document.getElementById('ask-question-btn')) {
        initAskQuestionModal();
    }
    
    if (document.getElementById('btn-all')) {
        initAppStatusFilters();
    }
});

/**
 * Layr - Architecture Recommendations Page
 * JavaScript functionality specific to the architecture recommendations view
 */

document.addEventListener('DOMContentLoaded', function() {
    // Ask Question Modal
    document.getElementById('ask-question-btn')?.addEventListener('click', function(e) {
        e.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('askQuestionModal'));
        modal.show();
    });
    
    document.getElementById('submit-question')?.addEventListener('click', function() {
        const question = document.getElementById('question').value;
        
        if (!question.trim()) {
            alert('Please enter a question');
            return;
        }
        
        // Show loading indicator
        document.getElementById('answer-content').innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"></div></div>';
        document.getElementById('answer-container').classList.remove('d-none');
        
        // Submit question to API
        const appId = document.getElementById('application-id')?.value;
        
        fetch('/applications/ask_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                app_id: appId || null
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display answer with markdown formatting
                document.getElementById('answer-content').innerHTML = '<pre class="mb-0">' + data.response + '</pre>';
            } else {
                document.getElementById('answer-content').innerHTML = '<div class="alert alert-danger">' + (data.error || 'Failed to get answer') + '</div>';
            }
        })
        .catch(error => {
            document.getElementById('answer-content').innerHTML = '<div class="alert alert-danger">Error communicating with server</div>';
            console.error('Error:', error);
        });
    });
});

/**
 * Layr - Modernization Strategies Page
 * JavaScript functionality specific to the modernization strategies view
 */

document.addEventListener('DOMContentLoaded', function() {
    // Ask Question Modal
    document.getElementById('ask-question-btn')?.addEventListener('click', function(e) {
        e.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('askQuestionModal'));
        modal.show();
    });
    
    document.getElementById('submit-question')?.addEventListener('click', function() {
        const question = document.getElementById('question').value;
        
        if (!question.trim()) {
            alert('Please enter a question');
            return;
        }
        
        // Show loading indicator
        document.getElementById('answer-content').innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"></div></div>';
        document.getElementById('answer-container').classList.remove('d-none');
        
        // Submit question to API
        const appId = document.getElementById('application-id')?.value;
        
        fetch('/applications/ask_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                app_id: appId || null
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display answer with markdown formatting
                document.getElementById('answer-content').innerHTML = '<pre class="mb-0">' + data.response + '</pre>';
            } else {
                document.getElementById('answer-content').innerHTML = '<div class="alert alert-danger">' + (data.error || 'Failed to get answer') + '</div>';
            }
        })
        .catch(error => {
            document.getElementById('answer-content').innerHTML = '<div class="alert alert-danger">Error communicating with server</div>';
            console.error('Error:', error);
        });
    });
});

/**
 * Layr - Patterns Analysis Page
 * JavaScript functionality specific to the patterns analysis view
 */

document.addEventListener('DOMContentLoaded', function() {
    // Ask Question Modal
    document.getElementById('ask-question-btn')?.addEventListener('click', function(e) {
        e.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('askQuestionModal'));
        modal.show();
    });
    
    document.getElementById('submit-question')?.addEventListener('click', function() {
        const question = document.getElementById('question').value;
        
        if (!question.trim()) {
            alert('Please enter a question');
            return;
        }
        
        // Show loading indicator
        document.getElementById('answer-content').innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"></div></div>';
        document.getElementById('answer-container').classList.remove('d-none');
        
        // Submit question to API
        const appId = document.getElementById('application-id')?.value;
        
        fetch('/applications/ask_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                app_id: appId || null
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display answer with markdown formatting
                document.getElementById('answer-content').innerHTML = '<pre class="mb-0">' + data.response + '</pre>';
            } else {
                document.getElementById('answer-content').innerHTML = '<div class="alert alert-danger">' + (data.error || 'Failed to get answer') + '</div>';
            }
        })
        .catch(error => {
            document.getElementById('answer-content').innerHTML = '<div class="alert alert-danger">Error communicating with server</div>';
            console.error('Error:', error);
        });
    });
});

/**
 * Layr - ARB Dashboard
 * JavaScript functionality specific to the ARB dashboard view
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Application Status Chart
    initApplicationStatusChart();
});

/**
 * Initialize the application status chart
 */
function initApplicationStatusChart() {
    const chartCanvas = document.getElementById('applicationStatusChart');
    
    if (chartCanvas) {
        const ctx = chartCanvas.getContext('2d');
        
        // Get counts from data attributes
        const ptiCount = parseInt(chartCanvas.getAttribute('data-pti-count') || 0);
        const inReviewCount = parseInt(chartCanvas.getAttribute('data-in-review-count') || 0);
        const ptoCount = parseInt(chartCanvas.getAttribute('data-pto-count') || 0);
        const rejectedCount = parseInt(chartCanvas.getAttribute('data-rejected-count') || 0);
        
        const statusChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['PTI', 'In Review', 'PTO', 'Rejected'],
                datasets: [{
                    data: [ptiCount, inReviewCount, ptoCount, rejectedCount],
                    backgroundColor: [
                        '#f1c40f', // PTI
                        '#3498db', // In Review
                        '#2ecc71', // PTO
                        '#e74c3c'  // Rejected
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

/**
 * Layr - Review Application Page
 * JavaScript functionality specific to the application review view
 */

document.addEventListener('DOMContentLoaded', function() {
    // Load ARB insights
    loadArbInsights();
});

/**
 * Load ARB insights for the application
 */
function loadArbInsights() {
    const arbInsightsElement = document.getElementById('arb-insights');
    const appIdElement = document.getElementById('application-id');
    
    if (arbInsightsElement && appIdElement) {
        const appId = appIdElement.value;
        
        fetch(`/arb/insights/${appId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    let insightsHtml = '';
                    
                    if (data.insights.length > 0) {
                        insightsHtml += '<div class="list-group">';
                        data.insights.forEach(insight => {
                            let bgClass = 'bg-light';
                            let iconClass = 'fa-info-circle';
                            
                            if (insight.type === 'warning') {
                                bgClass = 'bg-warning bg-opacity-25';
                                iconClass = 'fa-exclamation-triangle';
                            } else if (insight.type === 'positive') {
                                bgClass = 'bg-success bg-opacity-25';
                                iconClass = 'fa-check-circle';
                            }
                            
                            insightsHtml += `
                                <div class="list-group-item ${bgClass}">
                                    <div class="d-flex">
                                        <div class="me-3">
                                            <i class="fas ${iconClass} fa-lg mt-1"></i>
                                        </div>
                                        <div>
                                            ${insight.message}
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                        insightsHtml += '</div>';
                    } else {
                        insightsHtml = '<div class="alert alert-info">No insights available for this application.</div>';
                    }
                    
                    arbInsightsElement.innerHTML = insightsHtml;
                } else {
                    arbInsightsElement.innerHTML = '<div class="alert alert-danger">' + (data.error || 'Failed to load insights') + '</div>';
                }
            })
            .catch(error => {
                arbInsightsElement.innerHTML = '<div class="alert alert-danger">Error loading insights</div>';
                console.error('Error:', error);
            });
    }
}

/**
 * Layr - Dashboard
 * JavaScript functionality specific to the main dashboard view
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize application filtering
    initAppStatusFilters();
    
    // Initialize status summary chart
    initStatusChart();
    
    // Initialize ask question modal
    initAskQuestionModal();
});

/**
 * Initialize application status filter buttons
 */
function initAppStatusFilters() {
    document.getElementById('btn-all')?.addEventListener('click', function() {
        showApplications('all');
        setActiveButton(this);
    });
    
    document.getElementById('btn-pti')?.addEventListener('click', function() {
        showApplications('PTI');
        setActiveButton(this);
    });
    
    document.getElementById('btn-review')?.addEventListener('click', function() {
        showApplications('In Review');
        setActiveButton(this);
    });
    
    document.getElementById('btn-pto')?.addEventListener('click', function() {
        showApplications('PTO');
        setActiveButton(this);
    });
}

/**
 * Filter application rows by status
 * @param {string} status - The status to filter by ('all' or specific status)
 */
function showApplications(status) {
    const rows = document.querySelectorAll('.app-row');
    rows.forEach(row => {
        if (status === 'all' || row.dataset.status === status) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Set the active button in the filter group
 * @param {HTMLElement} activeButton - The button to set as active
 */
function setActiveButton(activeButton) {
    const buttons = document.querySelectorAll('.btn-group .btn');
    buttons.forEach(button => {
        button.classList.remove('active');
    });
    activeButton.classList.add('active');
}

/**
 * Initialize the status summary chart
 */
function initStatusChart() {
    const chartCanvas = document.getElementById('statusChart');
    
    if (chartCanvas) {
        // Parse application data from data attribute
        const applications = JSON.parse(chartCanvas.getAttribute('data-applications') || '[]');
        
        const statusCounts = {
            'PTI': 0,
            'In Review': 0,
            'PTO': 0,
            'Rejected': 0
        };
        
        applications.forEach(app => {
            statusCounts[app.status] = (statusCounts[app.status] || 0) + 1;
        });
        
        // Create chart
        const ctx = chartCanvas.getContext('2d');
        const statusChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(statusCounts),
                datasets: [{
                    data: Object.values(statusCounts),
                    backgroundColor: [
                        '#f1c40f', // PTI
                        '#3498db', // In Review
                        '#2ecc71', // PTO
                        '#e74c3c'  // Rejected
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

/**
 * Initialize ask question modal functionality
 */
function initAskQuestionModal() {
    // Open modal button
    document.getElementById('ask-question-btn')?.addEventListener('click', function(e) {
        e.preventDefault();
        const modal = new bootstrap.Modal(document.getElementById('askQuestionModal'));
        modal.show();
    });
    
    // Submit question button
    document.getElementById('submit-question')?.addEventListener('click', function() {
        const question = document.getElementById('question').value;
        const appId = document.getElementById('app-context').value;
        
        if (!question.trim()) {
            alert('Please enter a question');
            return;
        }
        
        // Show loading indicator
        document.getElementById('answer-content').innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"></div></div>';
        document.getElementById('answer-container').classList.remove('d-none');
        
        // Submit question to API
        fetch('/applications/ask_question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                app_id: appId || null
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display answer with markdown formatting
                document.getElementById('answer-content').innerHTML = '<pre class="mb-0">' + data.response + '</pre>';
            } else {
                document.getElementById('answer-content').innerHTML = '<div class="alert alert-danger">' + (data.error || 'Failed to get answer') + '</div>';
            }
        })
        .catch(error => {
            document.getElementById('answer-content').innerHTML = '<div class="alert alert-danger">Error communicating with server</div>';
            console.error('Error:', error);
        });
    });
}

// Base JavaScript for Layr application

document.addEventListener('DOMContentLoaded', function() {
    // Load ARB insights
    loadArbInsights();
});

/**
 * Load ARB insights for the application
 */
function loadArbInsights() {
    const arbInsightsElement = document.getElementById('arb-insights');
    const appIdElement = document.getElementById('application-id');
    
    if (arbInsightsElement && appIdElement) {
        const appId = appIdElement.value;
        
        fetch(`/arb/insights/${appId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Display architecture insights
                    let insightsHtml = '';
                    
                    if (data.insights.length > 0) {
                        insightsHtml += '<div class="list-group">';
                        data.insights.forEach(insight => {
                            // Generate insight HTML based on insight type
                            // ...
                        });
                        insightsHtml += '</div>';
                    } else {
                        insightsHtml = '<div class="alert alert-info">No insights available for this application.</div>';
                    }
                    
                    arbInsightsElement.innerHTML = insightsHtml;
                } else {
                    arbInsightsElement.innerHTML = '<div class="alert alert-danger">' + (data.error || 'Failed to load insights') + '</div>';
                }
            })
            .catch(error => {
                arbInsightsElement.innerHTML = '<div class="alert alert-danger">Error loading insights</div>';
                console.error('Error:', error);
            });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Format application status badges
    formatStatusBadges();
});

/**
 * Format application status badges with appropriate colors
 */
function formatStatusBadges() {
    const statusElements = document.querySelectorAll('.status-badge');
    statusElements.forEach(function(element) {
        const status = element.innerText.trim();
        if (status === 'PTI') {
            element.classList.add('status-pti');
        } else if (status === 'In Review') {
            element.classList.add('status-review');
        } else if (status === 'PTO') {
            element.classList.add('status-pto');
        } else if (status === 'Rejected') {
            element.classList.add('status-rejected');
        }
    });
}

/**
 * Layr - Generate HLDD Page
 * JavaScript functionality specific to the HLDD generation view
 */

document.addEventListener('DOMContentLoaded', function() {
    // Functions
    initFunctionButtons();
    
    // Roles
    initRoleButtons();
    
    // Principles
    initPrincipleButtons();
    
    // Components
    initComponentButtons();
    
    // Technology categories and items
    initTechButtons();
    initCategoryButton();
    
    // Data stores
    initDataStoreButtons();
    
    // Environments
    initEnvironmentButtons();
});

/**
 * Initialize add/remove buttons for system functions
 */
function initFunctionButtons() {
    const functionsContainer = document.getElementById('functions-container');
    const addFunctionBtn = document.getElementById('add-function-btn');
    
    if (addFunctionBtn && functionsContainer) {
        addFunctionBtn.addEventListener('click', function() {
            const functionDiv = document.createElement('div');
            functionDiv.className = 'mb-2 input-group';
            functionDiv.innerHTML = `
                <input type="text" class="form-control" name="functions" placeholder="Function description">
                <button type="button" class="btn btn-outline-danger remove-function-btn">
                    <i class="fas fa-times"></i>
                </button>
            `;
            functionsContainer.appendChild(functionDiv);
            
            // Show remove buttons if there's more than one function
            if (functionsContainer.querySelectorAll('.input-group').length > 1) {
                functionsContainer.querySelectorAll('.remove-function-btn').forEach(btn => {
                    btn.style.display = 'block';
                });
            }
        });
        
        functionsContainer.addEventListener('click', function(e) {
            if (e.target.closest('.remove-function-btn')) {
                e.target.closest('.input-group').remove();
                
                // Hide remove buttons if there's only one function left
                if (functionsContainer.querySelectorAll('.input-group').length <= 1) {
                    functionsContainer.querySelectorAll('.remove-function-btn').forEach(btn => {
                        btn.style.display = 'none';
                    });
                }
            }
        });
    }
}

/**
 * Initialize add/remove buttons for user roles
 */
function initRoleButtons() {
    const rolesContainer = document.getElementById('roles-container');
    const addRoleBtn = document.getElementById('add-role-btn');
    
    if (addRoleBtn && rolesContainer) {
        addRoleBtn.addEventListener('click', function() {
            const roleDiv = document.createElement('div');
            roleDiv.className = 'row mb-2 role-row';
            roleDiv.innerHTML = `
                <div class="col-md-4">
                    <input type="text" class="form-control" name="role_name" placeholder="Role name">
                </div>
                <div class="col-md-8">
                    <div class="input-group">
                        <input type="text" class="form-control" name="role_description" placeholder="Role description">
                        <button type="button" class="btn btn-outline-danger remove-role-btn">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
            rolesContainer.appendChild(roleDiv);
            
            // Show remove buttons if there's more than one role
            if (rolesContainer.querySelectorAll('.role-row').length > 1) {
                rolesContainer.querySelectorAll('.remove-role-btn').forEach(btn => {
                    btn.style.display = 'block';
                });
            }
        });
        
        rolesContainer.addEventListener('click', function(e) {
            if (e.target.closest('.remove-role-btn')) {
                e.target.closest('.role-row').remove();
                
                // Hide remove buttons if there's only one role left
                if (rolesContainer.querySelectorAll('.role-row').length <= 1) {
                    rolesContainer.querySelectorAll('.remove-role-btn').forEach(btn => {
                        btn.style.display = 'none';
                    });
                }
            }
        });
    }
}

/**
 * Initialize add/remove buttons for architecture principles
 */
function initPrincipleButtons() {
    const principlesContainer = document.getElementById('principles-container');
    const addPrincipleBtn = document.getElementById('add-principle-btn');
    
    if (addPrincipleBtn && principlesContainer) {
        addPrincipleBtn.addEventListener('click', function() {
            const principleDiv = document.createElement('div');
            principleDiv.className = 'mb-2 input-group';
            principleDiv.innerHTML = `
                <input type="text" class="form-control" name="principles" placeholder="Principle description">
                <button type="button" class="btn btn-outline-danger remove-principle-btn">
                    <i class="fas fa-times"></i>
                </button>
            `;
            principlesContainer.appendChild(principleDiv);
            
            // Show remove buttons if there's more than one principle
            if (principlesContainer.querySelectorAll('.input-group').length > 1) {
                principlesContainer.querySelectorAll('.remove-principle-btn').forEach(btn => {
                    btn.style.display = 'block';
                });
            }
        });
        
        principlesContainer.addEventListener('click', function(e) {
            if (e.target.closest('.remove-principle-btn')) {
                e.target.closest('.input-group').remove();
                
                // Hide remove buttons if there's only one principle left
                if (principlesContainer.querySelectorAll('.input-group').length <= 1) {
                    principlesContainer.querySelectorAll('.remove-principle-btn').forEach(btn => {
                        btn.style.display = 'none';
                    });
                }
            }
        });
    }
}

/**
 * Initialize add/remove buttons for system components
 */
function initComponentButtons() {
    const componentsContainer = document.getElementById('components-container');
    const addComponentBtn = document.getElementById('add-component-btn');
    
    if (addComponentBtn && componentsContainer) {
        addComponentBtn.addEventListener('click', function() {
            const componentDiv = document.createElement('div');
            componentDiv.className = 'row mb-3 component-row';
            componentDiv.innerHTML = `
                <div class="col-md-4">
                    <input type="text" class="form-control" name="component_name" placeholder="Component name">
                </div>
                <div class="col-md-8">
                    <div class="input-group">
                        <input type="text" class="form-control" name="component_description" placeholder="Component description">
                        <button type="button" class="btn btn-outline-danger remove-component-btn">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
            componentsContainer.appendChild(componentDiv);
            
            // Show remove buttons if there's more than one component
            if (componentsContainer.querySelectorAll('.component-row').length > 1) {
                componentsContainer.querySelectorAll('.remove-component-btn').forEach(btn => {
                    btn.style.display = 'block';
                });
            }
        });
        
        componentsContainer.addEventListener('click', function(e) {
            if (e.target.closest('.remove-component-btn')) {
                e.target.closest('.component-row').remove();
                
                // Hide remove buttons if there's only one component left
                if (componentsContainer.querySelectorAll('.component-row').length <= 1) {
                    componentsContainer.querySelectorAll('.remove-component-btn').forEach(btn => {
                        btn.style.display = 'none';
                    });
                }
            }
        });
    }
}

/**
 * Initialize add/remove buttons for technology items
 */
function initTechButtons() {
    const techCategoriesContainer = document.getElementById('tech-categories-container');
    
    if (techCategoriesContainer) {
        // Set up add tech buttons
        const addTechButtons = techCategoriesContainer.querySelectorAll('.add-tech-btn');
        addTechButtons.forEach(button => {
            const category = button.getAttribute('data-category');
            const container = button.closest('.tech-category').querySelector('.tech-items-container');
            
            button.addEventListener('click', function() {
                if (container) {
                    const techItem = container.querySelector('.tech-item');
                    if (techItem) {
                        const newItem = techItem.cloneNode(true);
                        
                        // Clear values
                        newItem.querySelectorAll('input').forEach(input => {
                            if (input.name.includes('_tech_name') || input.name.includes('_tech_version') || input.name.includes('_tech_purpose')) {
                                input.value = '';
                            }
                        });
                        
                        // Show remove button
                        const removeBtn = newItem.querySelector('.remove-tech-btn');
                        if (removeBtn) {
                            removeBtn.style.display = 'block';
                        }
                        
                        container.appendChild(newItem);
                        
                        // Initialize remove buttons
                        setupRemoveButtons(newItem);
                    }
                }
            });
        });
        
        // Set up existing remove buttons
        setupRemoveButtons(techCategoriesContainer);
    }
}

/**
 * Initialize add category button
 */
function initCategoryButton() {
    const techCategoriesContainer = document.getElementById('tech-categories-container');
    const addCategoryBtn = document.getElementById('add-category-btn');
    
    if (addCategoryBtn && techCategoriesContainer) {
        addCategoryBtn.addEventListener('click', function() {
            // Create a dialog to enter category name
            const categoryName = prompt('Enter technology category name:', '');
            
            if (categoryName) {
                // Create new category HTML
                const categoryDiv = document.createElement('div');
                categoryDiv.className = 'tech-category mb-4';
                categoryDiv.innerHTML = `
                    <input type="hidden" name="tech_category" value="${categoryName}">
                    <h6 class="border-bottom pb-2">${categoryName} Technologies</h6>
                    
                    <div class="tech-items-container">
                        <div class="row mb-2 tech-item">
                            <div class="col-md-4">
                                <input type="text" class="form-control" name="${categoryName}_tech_name" placeholder="Technology name">
                            </div>
                            <div class="col-md-3">
                                <input type="text" class="form-control" name="${categoryName}_tech_version" placeholder="Version">
                            </div>
                            <div class="col-md-5">
                                <div class="input-group">
                                    <input type="text" class="form-control" name="${categoryName}_tech_purpose" placeholder="Purpose">
                                    <button type="button" class="btn btn-outline-danger remove-tech-btn" style="display: none;">
                                        <i class="fas fa-times"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <button type="button" class="btn btn-sm btn-outline-primary mt-2 add-tech-btn" data-category="${categoryName}">
                        <i class="fas fa-plus me-1"></i> Add Technology
                    </button>
                `;
                
                techCategoriesContainer.appendChild(categoryDiv);
                
                // Initialize add tech button for new category
                const addTechBtn = categoryDiv.querySelector('.add-tech-btn');
                if (addTechBtn) {
                    const container = categoryDiv.querySelector('.tech-items-container');
                    addTechBtn.addEventListener('click', function() {
                        if (container) {
                            const techItem = container.querySelector('.tech-item');
                            if (techItem) {
                                const newItem = techItem.cloneNode(true);
                                
                                // Clear values
                                newItem.querySelectorAll('input').forEach(input => {
                                    if (input.name.includes('_tech_name') || input.name.includes('_tech_version') || input.name.includes('_tech_purpose')) {
                                        input.value = '';
                                    }
                                });
                                
                                // Show remove button
                                const removeBtn = newItem.querySelector('.remove-tech-btn');
                                if (removeBtn) {
                                    removeBtn.style.display = 'block';
                                }
                                
                                container.appendChild(newItem);
                                
                                // Initialize remove buttons
                                setupRemoveButtons(newItem);
                            }
                        }
                    });
                }
            }
        });
    }
}

/**
 * Initialize add/remove buttons for data stores
 */
function initDataStoreButtons() {
    const dataStoresContainer = document.getElementById('datastores-container');
    const addDataStoreBtn = document.getElementById('add-datastore-btn');
    
    if (addDataStoreBtn && dataStoresContainer) {
        addDataStoreBtn.addEventListener('click', function() {
            const dataStoreDiv = document.createElement('div');
            dataStoreDiv.className = 'row mb-2 datastore-row';
            dataStoreDiv.innerHTML = `
                <div class="col-md-3">
                    <input type="text" class="form-control" name="datastore_name" placeholder="Data store name">
                </div>
                <div class="col-md-3">
                    <input type="text" class="form-control" name="datastore_type" placeholder="Type">
                </div>
                <div class="col-md-6">
                    <div class="input-group">
                        <input type="text" class="form-control" name="datastore_purpose" placeholder="Purpose">
                        <button type="button" class="btn btn-outline-danger remove-datastore-btn">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
            dataStoresContainer.appendChild(dataStoreDiv);
            
            // Show remove buttons if there's more than one data store
            if (dataStoresContainer.querySelectorAll('.datastore-row').length > 1) {
                dataStoresContainer.querySelectorAll('.remove-datastore-btn').forEach(btn => {
                    btn.style.display = 'block';
                });
            }
        });
        
        dataStoresContainer.addEventListener('click', function(e) {
            if (e.target.closest('.remove-datastore-btn')) {
                e.target.closest('.datastore-row').remove();
                
                // Hide remove buttons if there's only one data store left
                if (dataStoresContainer.querySelectorAll('.datastore-row').length <= 1) {
                    dataStoresContainer.querySelectorAll('.remove-datastore-btn').forEach(btn => {
                        btn.style.display = 'none';
                    });
                }
            }
        });
    }
}

/**
 * Initialize add/remove buttons for environments
 */
function initEnvironmentButtons() {
    const environmentsContainer = document.getElementById('environments-container');
    const addEnvironmentBtn = document.getElementById('add-environment-btn');
    
    if (addEnvironmentBtn && environmentsContainer) {
        addEnvironmentBtn.addEventListener('click', function() {
            const environmentDiv = document.createElement('div');
            environmentDiv.className = 'row mb-2 environment-row';
            environmentDiv.innerHTML = `
                <div class="col-md-4">
                    <input type="text" class="form-control" name="environment_name" placeholder="Environment name">
                </div>
                <div class="col-md-8">
                    <div class="input-group">
                        <input type="text" class="form-control" name="environment_description" placeholder="Description">
                        <button type="button" class="btn btn-outline-danger remove-environment-btn">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
            environmentsContainer.appendChild(environmentDiv);
            
            // Show remove buttons if there's more than one environment
            if (environmentsContainer.querySelectorAll('.environment-row').length > 1) {
                environmentsContainer.querySelectorAll('.remove-environment-btn').forEach(btn => {
                    btn.style.display = 'block';
                });
            }
        });
        
        environmentsContainer.addEventListener('click', function(e) {
            if (e.target.closest('.remove-environment-btn')) {
                e.target.closest('.environment-row').remove();
                
                // Hide remove buttons if there's only one environment left
                if (environmentsContainer.querySelectorAll('.environment-row').length <= 1) {
                    environmentsContainer.querySelectorAll('.remove-environment-btn').forEach(btn => {
                        btn.style.display = 'none';
                    });
                }
            }
        });
    }
}

/**
 * Set up remove buttons within a container
 * @param {Element} container - The container element
 */
function setupRemoveButtons(container) {
    const removeButtons = container.querySelectorAll('.remove-tech-btn, .remove-role-btn, .remove-principle-btn, .remove-component-btn, .remove-datastore-btn, .remove-environment-btn, .remove-function-btn');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = button.closest('.row') || button.closest('.input-group');
            if (row) {
                row.remove();
                
                // Update container state
                const parentContainer = button.closest('.tech-items-container, #roles-container, #principles-container, #components-container, #datastores-container, #environments-container, #functions-container');
                if (parentContainer) {
                    const itemSelector = parentContainer.id === 'functions-container' || parentContainer.id === 'principles-container' ? '.input-group' :
                                         parentContainer.id === 'roles-container' ? '.role-row' :
                                         parentContainer.id === 'components-container' ? '.component-row' :
                                         parentContainer.id === 'datastores-container' ? '.datastore-row' :
                                         parentContainer.id === 'environments-container' ? '.environment-row' : '.tech-item';
                                         
                    const items = parentContainer.querySelectorAll(itemSelector);
                    
                    // Hide remove buttons if there's only one item left
                    if (items.length <= 1) {
                        const btnClass = button.classList.contains('remove-tech-btn') ? '.remove-tech-btn' :
                                         button.classList.contains('remove-role-btn') ? '.remove-role-btn' :
                                         button.classList.contains('remove-principle-btn') ? '.remove-principle-btn' :
                                         button.classList.contains('remove-component-btn') ? '.remove-component-btn' :
                                         button.classList.contains('remove-datastore-btn') ? '.remove-datastore-btn' :
                                         button.classList.contains('remove-environment-btn') ? '.remove-environment-btn' : '.remove-function-btn';
                                         
                        parentContainer.querySelectorAll(btnClass).forEach(btn => {
                            btn.style.display = 'none';
                        });
                    }
                }
            }
        });
    });
}

/**
 * Format application status badges with appropriate colors
 */
function formatStatusBadges() {
    const statusElements = document.querySelectorAll('.status-badge');
    statusElements.forEach(function(element) {
        const status = element.innerText.trim();
        if (status === 'PTI') {
            element.classList.add('status-pti');
        } else if (status === 'In Review') {
            element.classList.add('status-review');
        } else if (status === 'PTO') {
            element.classList.add('status-pto');
        } else if (status === 'Rejected') {
            element.classList.add('status-rejected');
        }
    });
}

/**
 * Layr - Generate Diagram Page
 * JavaScript functionality specific to the diagram generation view
 */

document.addEventListener('DOMContentLoaded', function() {
    // System Architecture diagram components
    initComponentButtons();
    initConnectionButtons();
    
    // Deployment diagram environment/components
    initEnvironmentButtons();
    initDeploymentComponentButtons();
    
    // Mermaid diagram editor
    initMermaidEditor();
    
    // Generate diagram button handlers
    initGenerateDiagramButtons();
    
    // Update component selects when components change
    updateComponentSelects();
    updateEnvironmentSelects();
});

/**
 * Initialize add/remove buttons for system components
 */
function initComponentButtons() {
    // Add system component button
    document.getElementById('add-system-component-btn')?.addEventListener('click', function() {
        const container = document.getElementById('system-components-container');
        const componentCards = container.querySelectorAll('.component-card');
        const newCard = componentCards[0].cloneNode(true);
        
        // Clear values
        newCard.querySelectorAll('input').forEach(input => {
            input.value = '';
        });
        
        // Show remove button
        const removeBtn = newCard.querySelector('.remove-component-btn');
        if (removeBtn) {
            removeBtn.style.display = 'inline-block';
            removeBtn.addEventListener('click', function() {
                newCard.remove();
                updateComponentSelects();
            });
        }
        
        // Add new card to container
        container.appendChild(newCard);
        
        // Set up remove buttons on cloned card
        setupRemoveButtons(newCard);
        
        // Update component select dropdowns
        updateComponentSelects();
    });
    
    // Set up existing remove buttons
    const container = document.getElementById('system-components-container');
    if (container) {
        setupRemoveButtons(container);
    }
}

/**
 * Initialize add/remove buttons for connections
 */
function initConnectionButtons() {
    // Add connection button
    document.getElementById('add-system-connection-btn')?.addEventListener('click', function() {
        const container = document.getElementById('system-connections-container');
        const connectionCards = container.querySelectorAll('.connection-card');
        const newCard = connectionCards[0].cloneNode(true);
        
        // Clear description
        newCard.querySelector('input[name="connection_description"]').value = '';
        
        // Show remove button
        const removeBtn = newCard.querySelector('.remove-connection-btn');
        if (removeBtn) {
            removeBtn.style.display = 'inline-block';
            removeBtn.addEventListener('click', function() {
                newCard.remove();
            });
        }
        
        // Add new card to container
        container.appendChild(newCard);
        
        // Set up remove buttons on cloned card
        setupRemoveButtons(newCard);
    });
    
    // Set up existing remove buttons
    const container = document.getElementById('system-connections-container');
    if (container) {
        setupRemoveButtons(container);
    }
}

/**
 * Initialize add/remove buttons for deployment environments
 */
function initEnvironmentButtons() {
    // Add environment button
    document.getElementById('add-deployment-environment-btn')?.addEventListener('click', function() {
        const container = document.getElementById('deployment-environments-container');
        const environmentCards = container.querySelectorAll('.environment-card');
        const newCard = environmentCards[0].cloneNode(true);
        
        // Clear values
        newCard.querySelectorAll('input').forEach(input => {
            input.value = '';
        });
        
        // Show remove button
        const removeBtn = newCard.querySelector('.remove-environment-btn');
        if (removeBtn) {
            removeBtn.style.display = 'inline-block';
            removeBtn.addEventListener('click', function() {
                newCard.remove();
                updateEnvironmentSelects();
            });
        }
        
        // Add new card to container
        container.appendChild(newCard);
        
        // Set up remove buttons on cloned card
        setupRemoveButtons(newCard);
        
        // Update environment select dropdowns
        updateEnvironmentSelects();
    });
    
    // Set up existing remove buttons
    const container = document.getElementById('deployment-environments-container');
    if (container) {
        setupRemoveButtons(container);
    }
}

/**
 * Initialize add/remove buttons for deployment components
 */
function initDeploymentComponentButtons() {
    // Add deployment component button
    document.getElementById('add-deployment-component-btn')?.addEventListener('click', function() {
        const container = document.getElementById('deployment-components-container');
        const componentCards = container.querySelectorAll('.deployment-component-card');
        const newCard = componentCards[0].cloneNode(true);
        
        // Clear some values but keep the environment dropdown
        newCard.querySelector('input[name="component_name"]').value = '';
        newCard.querySelector('input[name="component_host"]').value = '';
        
        // Show remove button
        const removeBtn = newCard.querySelector('.remove-deployment-component-btn');
        if (removeBtn) {
            removeBtn.style.display = 'inline-block';
            removeBtn.addEventListener('click', function() {
                newCard.remove();
            });
        }
        
        // Add new card to container
        container.appendChild(newCard);
        
        // Set up remove buttons on cloned card
        setupRemoveButtons(newCard);
    });
    
    // Set up existing remove buttons
    const container = document.getElementById('deployment-components-container');
    if (container) {
        setupRemoveButtons(container);
    }
}

/**
 * Initialize Mermaid editor
 */
function initMermaidEditor() {
    const mermaidEditor = document.getElementById('mermaid-editor');
    const mermaidPreview = document.getElementById('mermaid-preview');
    const updateMermaidBtn = document.getElementById('update-mermaid-btn');
    
    if (mermaidEditor && mermaidPreview && updateMermaidBtn) {
        // Set initial mermaid code
        if (!mermaidEditor.value) {
            mermaidEditor.value = `graph TD
    A[Frontend] --> B[API Gateway]
    B <--> C[(Database)]
    
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef database fill:#f5f5f5,stroke:#333,stroke-width:1px;
    class C database`;
        }
        
        // Update preview button
        updateMermaidBtn.addEventListener('click', function() {
            updateMermaidPreview();
        });
        
        // Initialize preview
        updateMermaidPreview();
    }
}

/**
 * Update Mermaid diagram preview
 */
function updateMermaidPreview() {
    const mermaidEditor = document.getElementById('mermaid-editor');
    const mermaidPreview = document.getElementById('mermaid-preview');
    
    if (mermaidEditor && mermaidPreview) {
        try {
            mermaidPreview.innerHTML = mermaidEditor.value;
            // Note: In a real implementation, you'd use mermaid.js to render the diagram
            // This is just a placeholder for the actual rendering logic
            if (typeof mermaid !== 'undefined') {
                mermaid.init(undefined, mermaidPreview);
            }
        } catch (error) {
            console.error('Error rendering mermaid diagram:', error);
            mermaidPreview.innerHTML = `<div class="alert alert-danger">Error rendering diagram: ${error.message}</div>`;
        }
    }
}

/**
 * Initialize generate diagram buttons
 */
function initGenerateDiagramButtons() {
    const generateButtons = document.querySelectorAll('.generate-diagram-btn');
    generateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const formId = button.getAttribute('data-form');
            const form = document.getElementById(formId);
            
            if (form) {
                // Show loading indicator
                const diagramContainer = document.getElementById('diagram-result');
                if (diagramContainer) {
                    diagramContainer.innerHTML = '<div class="d-flex justify-content-center my-5"><div class="spinner-border text-primary" role="status"></div></div>';
                }
                
                // Get form data
                const formData = new FormData(form);
                
                // Convert to JSON
                const jsonData = Object.fromEntries(formData.entries());
                
                // Additional processing based on form type
                if (formId === 'system-arch-form') {
                    // Process components
                    jsonData.components = getComponentsData('system-components-container');
                    
                    // Process connections
                    jsonData.connections = getConnectionsData();
                }
                else if (formId === 'deployment-form') {
                    // Process environments
                    jsonData.environments = getEnvironmentsData();
                    
                    // Process deployment components
                    jsonData.components = getDeploymentComponentsData();
                }
                
                // Submit to API
                generateDiagram(jsonData);
            }
        });
    });
}

/**
 * Generate diagram via API
 * @param {object} data - The diagram data
 */
function generateDiagram(data) {
    // Make API request
    fetch('/api/generate_diagram', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        const diagramContainer = document.getElementById('diagram-result');
        if (diagramContainer) {
            if (data.success) {
                // Display generated diagram
                diagramContainer.innerHTML = `
                    <div class="card">
                        <div class="card-header bg-light d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">Generated Diagram</h5>
                            <div>
                                <button type="button" class="btn btn-sm btn-outline-primary" id="download-diagram-btn">
                                    <i class="fas fa-download me-1"></i> Download
                                </button>
                            </div>
                        </div>
                        <div class="card-body text-center">
                            ${data.diagram_html}
                        </div>
                    </div>
                `;
                
                // Set up download button
                document.getElementById('download-diagram-btn')?.addEventListener('click', function() {
                    // Download logic would go here
                    alert('Download functionality would be implemented here');
                });
            } else {
                diagramContainer.innerHTML = `<div class="alert alert-danger">Error generating diagram: ${data.error || 'Unknown error'}</div>`;
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const diagramContainer = document.getElementById('diagram-result');
        if (diagramContainer) {
            diagramContainer.innerHTML = '<div class="alert alert-danger">Error communicating with server</div>';
        }
    });
}

/**
 * Get components data from form
 * @param {string} containerId - The ID of the container
 * @returns {Array} - Array of component objects
 */
function getComponentsData(containerId) {
    const components = [];
    const container = document.getElementById(containerId);
    
    if (container) {
        const componentCards = container.querySelectorAll('.component-card');
        componentCards.forEach(card => {
            const nameInput = card.querySelector('input[name="component_name"]');
            const typeSelect = card.querySelector('select[name="component_type"]');
            const descInput = card.querySelector('input[name="component_description"]');
            
            if (nameInput && typeSelect) {
                components.push({
                    name: nameInput.value,
                    type: typeSelect.value,
                    description: descInput ? descInput.value : ''
                });
            }
        });
    }
    
    return components;
}

/**
 * Get connections data from form
 * @returns {Array} - Array of connection objects
 */
function getConnectionsData() {
    const connections = [];
    const container = document.getElementById('system-connections-container');
    
    if (container) {
        const connectionCards = container.querySelectorAll('.connection-card');
        connectionCards.forEach(card => {
            const fromSelect = card.querySelector('select[name="connection_from"]');
            const toSelect = card.querySelector('select[name="connection_to"]');
            const typeSelect = card.querySelector('select[name="connection_type"]');
            const descInput = card.querySelector('input[name="connection_description"]');
            
            if (fromSelect && toSelect) {
                connections.push({
                    from: fromSelect.value,
                    to: toSelect.value,
                    type: typeSelect ? typeSelect.value : 'default',
                    description: descInput ? descInput.value : ''
                });
            }
        });
    }
    
    return connections;
}

/**
 * Get environments data from form
 * @returns {Array} - Array of environment objects
 */
function getEnvironmentsData() {
    const environments = [];
    const container = document.getElementById('deployment-environments-container');
    
    if (container) {
        const environmentCards = container.querySelectorAll('.environment-card');
        environmentCards.forEach(card => {
            const nameInput = card.querySelector('input[name="environment_name"]');
            const descInput = card.querySelector('input[name="environment_description"]');
            
            if (nameInput) {
                environments.push({
                    name: nameInput.value,
                    description: descInput ? descInput.value : ''
                });
            }
        });
    }
    
    return environments;
}

/**
 * Get deployment components data from form
 * @returns {Array} - Array of deployment component objects
 */
function getDeploymentComponentsData() {
    const components = [];
    const container = document.getElementById('deployment-components-container');
    
    if (container) {
        const componentCards = container.querySelectorAll('.deployment-component-card');
        componentCards.forEach(card => {
            const nameInput = card.querySelector('input[name="component_name"]');
            const typeSelect = card.querySelector('select[name="component_type"]');
            const envSelect = card.querySelector('select[name="component_env"]');
            const hostInput = card.querySelector('input[name="component_host"]');
            
            if (nameInput && envSelect) {
                components.push({
                    name: nameInput.value,
                    type: typeSelect ? typeSelect.value : 'component',
                    environment: envSelect.value,
                    host: hostInput ? hostInput.value : ''
                });
            }
        });
    }
    
    return components;
}

/**
 * Update component select options based on defined components
 */
function updateComponentSelects() {
    const components = getComponentsData('system-components-container');
    const selects = document.querySelectorAll('.component-select');
    
    selects.forEach(select => {
        // Save current value
        const currentValue = select.value;
        
        // Clear options
        select.innerHTML = '';
        
        // Add options for each component
        components.forEach(component => {
            const option = document.createElement('option');
            option.value = component.name;
            option.textContent = component.name;
            select.appendChild(option);
        });
        
        // Restore previous value if it exists in new options
        if (currentValue && [...select.options].some(option => option.value === currentValue)) {
            select.value = currentValue;
        }
    });
}

/**
 * Update environment select options based on defined environments
 */
function updateEnvironmentSelects() {
    const environments = getEnvironmentsData();
    const selects = document.querySelectorAll('.environment-select');
    
    selects.forEach(select => {
        // Save current value
        const currentValue = select.value;
        
        // Clear options
        select.innerHTML = '';
        
        // Add options for each environment
        environments.forEach(env => {
            const option = document.createElement('option');
            option.value = env.name;
            option.textContent = env.name;
            select.appendChild(option);
        });
        
        // Restore previous value if it exists in new options
        if (currentValue && [...select.options].some(option => option.value === currentValue)) {
            select.value = currentValue;
        }
    });
}

/**
 * Set up remove buttons within a container
 * @param {Element} container - The container element
 */
function setupRemoveButtons(container) {
    const removeButtons = container.querySelectorAll('.remove-component-btn, .remove-connection-btn, .remove-environment-btn, .remove-deployment-component-btn');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const card = button.closest('.card');
            if (card) {
                card.remove();
                
                // Update selects if needed
                if (button.classList.contains('remove-component-btn')) {
                    updateComponentSelects();
                } else if (button.classList.contains('remove-environment-btn')) {
                    updateEnvironmentSelects();
                }
            }
        });
    });
}

/**
 * Initialize flash messages with auto-dismiss
 */
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
        // Add close button if not already present
        if (!message.querySelector('.btn-close')) {
            const closeButton = document.createElement('button');
            closeButton.className = 'btn-close';
            closeButton.setAttribute('data-bs-dismiss', 'alert');
            closeButton.setAttribute('aria-label', 'Close');
            message.appendChild(closeButton);
        }
        
        // Auto-dismiss success and info messages after 5 seconds
        if (message.classList.contains('alert-success') || message.classList.contains('alert-info')) {
            setTimeout(function() {
                const alert = new bootstrap.Alert(message);
                alert.close();
            }, 5000);
        }
    });
}

/**
 * Helper function to ask architecture questions
 * @param {string} question - The question to ask
 * @param {number|null} appId - Optional application ID for context
 * @param {function} callback - Callback function for the response
 */
function askArchitectureQuestion(question, appId, callback) {
    if (!question || question.trim() === '') {
        callback({
            success: false,
            error: 'Please enter a question'
        });
        return;
    }
    
    // Prepare request data
    const requestData = {
        question: question,
        app_id: appId || null
    };
    
    // Make API request
    fetch('/api/ask_question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        callback(data);
    })
    .catch(error => {
        console.error('Error:', error);
        callback({
            success: false,
            error: 'Error communicating with server'
        });
    });
}




/**
 * Load ARB insights for application in review
 */
function loadArbInsights() {
    const arbInsightsElement = document.getElementById('arb-insights');
    const appIdElement = document.getElementById('application-id');
    
    if (arbInsightsElement && appIdElement) {
        const appId = appIdElement.value;
        
        fetch(`/arb/insights/${appId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    let insightsHtml = '';
                    
                    if (data.insights.length > 0) {
                        insightsHtml += '<div class="list-group">';
                        data.insights.forEach(insight => {
                            let bgClass = 'bg-light';
                            let iconClass = 'fa-info-circle';
                            
                            if (insight.type === 'warning') {
                                bgClass = 'bg-warning bg-opacity-25';
                                iconClass = 'fa-exclamation-triangle';
                            } else if (insight.type === 'positive') {
                                bgClass = 'bg-success bg-opacity-25';
                                iconClass = 'fa-check-circle';
                            }
                            
                            insightsHtml += `
                                <div class="list-group-item ${bgClass}">
                                    <div class="d-flex">
                                        <div class="me-3">
                                            <i class="fas ${iconClass} fa-lg mt-1"></i>
                                        </div>
                                        <div>
                                            ${insight.message}
                                        </div>
                                    </div>
                                </div>
                            `;
                        });
                        insightsHtml += '</div>';
                    } else {
                        insightsHtml = '<div class="alert alert-info">No insights available for this application.</div>';
                    }
                    
                    arbInsightsElement.innerHTML = insightsHtml;
                } else {
                    arbInsightsElement.innerHTML = '<div class="alert alert-danger">' + (data.error || 'Failed to load insights') + '</div>';
                }
            })
            .catch(error => {
                arbInsightsElement.innerHTML = '<div class="alert alert-danger">Error loading insights</div>';
                console.error('Error:', error);
            });
    }
}

/**
 * Generate a chart for application statuses
 * @param {string} canvasId - The ID of the canvas element
 * @param {object} data - The data for the chart
 */
function generateStatusChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: [
                    '#f1c40f', // PTI
                    '#3498db', // In Review
                    '#2ecc71', // PTO
                    '#e74c3c'  // Rejected
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}