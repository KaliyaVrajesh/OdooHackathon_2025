
/**
 * SkillSwap Admin Dashboard JS
 * Contains all interactive functionality for the admin panel
 */

document.addEventListener('DOMContentLoaded', function() {
    // ======================
    // Dashboard Initialization
    // ======================
    initAdminDashboard();

    // ======================
    // Core Functions
    // ======================
    function initAdminDashboard() {
        initCharts();
        setupDataTables();
        initTooltips();
        setupEventListeners();
        handleStatusToggles();
        setupAjaxCSRF();
    }

    // ======================
    // Chart Initialization
    // ======================
    function initCharts() {
        // User Growth Chart
        const userGrowthCtx = document.getElementById('userGrowthChart');
        if (userGrowthCtx) {
            new Chart(userGrowthCtx, {
                type: 'line',
                data: {
                    labels: JSON.parse(userGrowthCtx.dataset.labels || '[]'),
                    datasets: [{
                        label: 'New Users',
                        data: JSON.parse(userGrowthCtx.dataset.values || '[]'),
                        backgroundColor: 'rgba(13, 110, 253, 0.2)',
                        borderColor: 'rgba(13, 110, 253, 1)',
                        borderWidth: 2,
                        tension: 0.1,
                        fill: true
                    }]
                },
                options: getChartOptions('User Registration Trends')
            });
        }

        // Skill Distribution Chart
        const skillDistCtx = document.getElementById('skillDistributionChart');
        if (skillDistCtx) {
            new Chart(skillDistCtx, {
                type: 'doughnut',
                data: {
                    labels: JSON.parse(skillDistCtx.dataset.labels || '[]'),
                    datasets: [{
                        data: JSON.parse(skillDistCtx.dataset.values || '[]'),
                        backgroundColor: [
                            '#0d6efd', '#198754', '#ffc107', 
                            '#dc3545', '#6610f2', '#fd7e14'
                        ],
                        borderWidth: 1
                    }]
                },
                options: getChartOptions('Skill Distribution', true)
            });
        }
    }

    function getChartOptions(title, showLegend = false) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: showLegend,
                    position: 'right'
                },
                title: {
                    display: !!title,
                    text: title,
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    backgroundColor: '#212529',
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 12
                    },
                    padding: 12,
                    usePointStyle: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        };
    }

    // ======================
    // Data Tables Setup
    // ======================
    function setupDataTables() {
        const tables = document.querySelectorAll('.admin-datatable');
        tables.forEach(table => {
            new simpleDatatables.DataTable(table, {
                perPage: 10,
                perPageSelect: [5, 10, 15, 20],
                labels: {
                    placeholder: "Search...",
                    searchTitle: "Search within table",
                    perPage: "entries per page",
                    noRows: "No entries found",
                    info: "Showing {start} to {end} of {rows} entries"
                },
                columns: getColumnConfig(table)
            });
        });
    }

    function getColumnConfig(table) {
        // Customize sorting for specific columns
        const configs = [];
        const headers = table.querySelectorAll('thead th');
        
        headers.forEach(header => {
            if (header.classList.contains('no-sort')) {
                configs.push({ select: Array.from(headers).indexOf(header), sortable: false });
            }
            if (header.classList.contains('date-column')) {
                configs.push({
                    select: Array.from(headers).indexOf(header),
                    type: 'date',
                    format: 'YYYY-MM-DD'
                });
            }
        });
        
        return configs;
    }

    // ======================
    // UI Enhancements
    // ======================
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                boundary: document.body
            });
        });
    }

    function setupEventListeners() {
        // Bulk action handlers
        document.querySelectorAll('.bulk-action-btn').forEach(btn => {
            btn.addEventListener('click', handleBulkActions);
        });

        // Status toggles
        document.querySelectorAll('.status-toggle').forEach(toggle => {
            toggle.addEventListener('change', handleStatusChange);
        });

        // Confirmation modals
        document.querySelectorAll('[data-confirm]').forEach(btn => {
            btn.addEventListener('click', confirmAction);
        });

        // Quick filter buttons
        document.querySelectorAll('.quick-filter').forEach(filter => {
            filter.addEventListener('click', applyQuickFilter);
        });
    }

    // ======================
    // Action Handlers
    // ======================
    function handleBulkActions(e) {
        const action = e.target.dataset.action;
        const selected = Array.from(document.querySelectorAll('.bulk-select:checked'))
                            .map(checkbox => checkbox.value);
        
        if (selected.length === 0) {
            showAlert('Please select at least one item', 'warning');
            return;
        }

        if (action === 'delete') {
            showConfirmModal(
                `Delete ${selected.length} selected items?`,
                'This action cannot be undone.',
                () => performBulkAction(action, selected)
            );
        } else {
            performBulkAction(action, selected);
        }
    }

    function handleStatusChange(e) {
        const targetId = e.target.dataset.id;
        const newStatus = e.target.checked;
        const model = e.target.dataset.model;
        
        fetch(`/admin/${model}/${targetId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ active: newStatus })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(`Status updated successfully`, 'success');
            } else {
                e.target.checked = !newStatus; // Revert toggle
                showAlert(data.message || 'Update failed', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            e.target.checked = !newStatus; // Revert toggle
            showAlert('An error occurred', 'danger');
        });
    }

    function confirmAction(e) {
        e.preventDefault();
        const message = e.target.dataset.confirm || 'Are you sure you want to perform this action?';
        const formId = e.target.dataset.form;

        showConfirmModal(
            'Please confirm',
            message,
            () => {
                if (formId) {
                    document.getElementById(formId).submit();
                } else if (e.target.href) {
                    window.location = e.target.href;
                }
            }
        );
    }

    // ======================
    // Helper Functions
    // ======================
    function performBulkAction(action, ids) {
        fetch('/admin/bulk-action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ action, ids })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(data.message || 'Action completed successfully', 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showAlert(data.message || 'Action failed', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('An error occurred', 'danger');
        });
    }

    function showAlert(message, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.role = 'alert';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.getElementById('alert-container') || document.body;
        container.prepend(alert);
        
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    }

    function showConfirmModal(title, message, callback) {
        const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
        document.getElementById('confirmModalTitle').textContent = title;
        document.getElementById('confirmModalBody').textContent = message;
        
        const confirmBtn = document.getElementById('confirmModalBtn');
        const oldHandler = confirmBtn.onclick;
        confirmBtn.onclick = function() {
            if (oldHandler) oldHandler();
            callback();
            modal.hide();
        };
        
        modal.show();
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrf_token]')?.value || '';
    }

    function setupAjaxCSRF() {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                    xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
                }
            }
        });
    }

    // ======================
    // Utility Functions
    // ======================
    function applyQuickFilter(e) {
        e.preventDefault();
        const filter = e.target.dataset.filter;
        const table = e.target.closest('.card').querySelector('table');
        
        if (table) {
            const datatable = table.DataTable;
            datatable.search(filter).draw();
        }
    }

    function handleStatusToggles() {
        document.querySelectorAll('.status-toggle').forEach(toggle => {
            toggle.addEventListener('change', function() {
                const statusText = this.nextElementSibling;
                if (this.checked) {
                    statusText.textContent = 'Active';
                    statusText.classList.remove('text-danger');
                    statusText.classList.add('text-success');
                } else {
                    statusText.textContent = 'Inactive';
                    statusText.classList.remove('text-success');
                    statusText.classList.add('text-danger');
                }
            });
        });
    }
});
