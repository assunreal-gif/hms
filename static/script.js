/**
 * HMS EcoClean - Hostel Waste Management System
 * Interactive Client Script
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Menu Navigation Toggle
    const mobileBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    if (mobileBtn && navLinks) {
        mobileBtn.addEventListener('click', () => {
            navLinks.classList.toggle('show');
        });
    }

    // 2. Auto Dismiss Flash Alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });

    // 3. Admin Table Client-Side Quick Filter (enhances UX alongside server-side search)
    const adminSearchInput = document.getElementById('adminSearchInput');
    const requestsTable = document.getElementById('requestsTable');
    if (adminSearchInput && requestsTable) {
        adminSearchInput.addEventListener('keyup', (e) => {
            // When Enter is pressed, allow standard form submission for server query
            if (e.key === 'Enter') return;

            const query = adminSearchInput.value.toLowerCase().trim();
            const rows = requestsTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                // Skip empty state placeholder row if present
                if (row.querySelector('.empty-table-cell')) return;

                const text = row.innerText.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // 4. Client-side Form Validation & Submission Loading State
    const reportForm = document.getElementById('wasteReportForm');
    const submitBtn = document.getElementById('submitBtn');
    if (reportForm && submitBtn) {
        reportForm.addEventListener('submit', (e) => {
            const wasteType = document.getElementById('waste_type');
            const location = document.getElementById('location');
            const desc = document.getElementById('description');

            if (!wasteType.value) {
                alert('Please select a waste category.');
                wasteType.focus();
                e.preventDefault();
                return;
            }

            if (location.value.trim().length < 3) {
                alert('Please enter a specific hostel location (at least 3 characters).');
                location.focus();
                e.preventDefault();
                return;
            }

            if (desc.value.trim().length < 5) {
                alert('Please provide a short description of the waste (at least 5 characters).');
                desc.focus();
                e.preventDefault();
                return;
            }

            // Visual feedback on submission
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>⏳</span> Submitting Request...';
        });
    }

    // 5. Confirmation prompt on critical admin status update (e.g. marking completed)
    const statusSelects = document.querySelectorAll('.status-select');
    statusSelects.forEach(select => {
        const originalVal = select.value;
        select.addEventListener('change', function(e) {
            const chosen = this.value;
            if (chosen === 'Completed') {
                const confirmed = confirm(`Are you sure you want to mark this request as COMPLETED?`);
                if (!confirmed) {
                    this.value = originalVal;
                    e.preventDefault();
                    return;
                }
            }
            this.form.submit();
        });
    });
});
