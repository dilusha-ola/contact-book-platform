let allContacts = [];
let allCompanies = [];

document.addEventListener("DOMContentLoaded", () => {
    fetchPlatformData();
});

async function fetchPlatformData() {
    await fetchStats();
    await fetchContacts();
    await fetchCompanies();
}

async function fetchStats() {
    try {
        const resContacts = await fetch("/api/v1/contacts/stats");
        const dataContacts = await resContacts.json();
        document.getElementById("stat-total").innerText = dataContacts.total_contacts || 0;

        const resCompanies = await fetch("/api/v1/companies/stats");
        const dataCompanies = await resCompanies.json();
        document.getElementById("stat-companies").innerText = dataCompanies.total_companies || 0;
    } catch (err) {
        console.error("Error fetching stats:", err);
    }
}

async function fetchContacts() {
    try {
        const res = await fetch("/api/v1/contacts");
        allContacts = await res.json();
        renderDashboardTable(allContacts);
        renderContactsTable(allContacts);
    } catch (err) {
        console.error("Error fetching contacts:", err);
    }
}

async function fetchCompanies() {
    try {
        const res = await fetch("/api/v1/companies");
        allCompanies = await res.json();
        renderCompaniesTable(allCompanies);
    } catch (err) {
        console.error("Error fetching companies:", err);
    }
}

function renderDashboardTable(contacts) {
    const tbody = document.getElementById("dashboard-table-body");
    tbody.innerHTML = "";
    if (contacts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: var(--text-muted); padding: 20px;">No personal contacts stored. Click "+ Add Contact" to create one!</td></tr>`;
        return;
    }
    contacts.slice(0, 5).forEach(c => {
        tbody.appendChild(createContactRow(c));
    });
}

function renderContactsTable(contacts) {
    const tbody = document.getElementById("contacts-table-body");
    tbody.innerHTML = "";
    if (contacts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: var(--text-muted); padding: 20px;">No matching personal contacts found.</td></tr>`;
        return;
    }
    contacts.forEach(c => {
        tbody.appendChild(createContactRow(c));
    });
}

function createContactRow(c) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
        <td><strong>${escapeHtml(c.name)}</strong></td>
        <td>${escapeHtml(c.email)}</td>
        <td>${escapeHtml(c.phone)}</td>
        <td>
            <button class="btn btn-secondary btn-sm" onclick="openEditContactModal('${c.id}')">Edit</button>
            <button class="btn btn-danger btn-sm" onclick="deleteContact('${c.id}')">Delete</button>
        </td>
    `;
    return tr;
}

function renderCompaniesTable(companies) {
    const tbody = document.getElementById("companies-table-body");
    tbody.innerHTML = "";
    if (companies.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted); padding: 20px;">No company entries found. Click "+ Create Company Contact" to add one!</td></tr>`;
        return;
    }
    companies.forEach(comp => {
        tbody.appendChild(createCompanyRow(comp));
    });
}

function createCompanyRow(c) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
        <td><strong>🏢 ${escapeHtml(c.name)}</strong></td>
        <td>${escapeHtml(c.company_email)}</td>
        <td>${escapeHtml(c.phone)}</td>
        <td>${escapeHtml(c.location)}</td>
        <td>
            <button class="btn btn-secondary btn-sm" onclick="openEditCompanyModal('${c.id}')">Edit</button>
            <button class="btn btn-danger btn-sm" onclick="deleteCompany('${c.id}')">Delete</button>
        </td>
    `;
    return tr;
}

function filterContacts() {
    const q = document.getElementById("search-input").value.toLowerCase();
    const filtered = allContacts.filter(c => {
        return c.name.toLowerCase().includes(q) ||
               c.email.toLowerCase().includes(q) ||
               c.phone.toLowerCase().includes(q);
    });
    renderContactsTable(filtered);
}

function filterCompanies() {
    const q = document.getElementById("company-search-input").value.toLowerCase();
    const filtered = allCompanies.filter(c => {
        return c.name.toLowerCase().includes(q) ||
               c.company_email.toLowerCase().includes(q) ||
               c.phone.toLowerCase().includes(q) ||
               c.location.toLowerCase().includes(q);
    });
    renderCompaniesTable(filtered);
}

function switchNav(viewId, btn) {
    document.querySelectorAll(".view-section").forEach(s => s.classList.remove("active"));
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));

    document.getElementById("view-" + viewId).classList.add("active");
    btn.classList.add("active");

    const titles = {
        dashboard: "Dashboard Overview",
        contacts: "Personal Contacts Directory",
        companies: "Company Contacts Directory",
        settings: "Platform Settings"
    };
    document.getElementById("page-title").innerText = titles[viewId];
    document.getElementById("sidebar").classList.remove("open");
}

function toggleMobileMenu() {
    document.getElementById("sidebar").classList.toggle("open");
}

/* Personal Contact Modal Handlers */
function openContactModal() {
    document.getElementById("contact-modal-title").innerText = "Create Personal Contact";
    document.getElementById("form-contact-id").value = "";
    document.getElementById("contact-form").reset();
    document.getElementById("contact-modal").classList.add("active");
}

function openEditContactModal(id) {
    const c = allContacts.find(item => item.id === id);
    if (!c) return;

    document.getElementById("contact-modal-title").innerText = "Edit Personal Contact";
    document.getElementById("form-contact-id").value = c.id;
    document.getElementById("form-contact-name").value = c.name;
    document.getElementById("form-contact-email").value = c.email;
    document.getElementById("form-contact-phone").value = c.phone;
    document.getElementById("form-contact-notes").value = c.notes || "";

    document.getElementById("contact-modal").classList.add("active");
}

function closeContactModal() {
    document.getElementById("contact-modal").classList.remove("active");
}

async function handleContactSubmit(e) {
    e.preventDefault();
    const id = document.getElementById("form-contact-id").value;
    const payload = {
        name: document.getElementById("form-contact-name").value,
        email: document.getElementById("form-contact-email").value,
        phone: document.getElementById("form-contact-phone").value,
        notes: document.getElementById("form-contact-notes").value || null
    };

    try {
        let res;
        if (id) {
            res = await fetch(`/api/v1/contacts/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        } else {
            res = await fetch("/api/v1/contacts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        }

        if (res.ok) {
            closeContactModal();
            fetchPlatformData();
        } else {
            alert("Error saving contact");
        }
    } catch (err) {
        console.error("Submit error:", err);
    }
}

async function deleteContact(id) {
    if (!confirm("Are you sure you want to delete this personal contact?")) return;

    try {
        const res = await fetch(`/api/v1/contacts/${id}`, { method: "DELETE" });
        if (res.ok) {
            fetchPlatformData();
        } else {
            alert("Error deleting contact");
        }
    } catch (err) {
        console.error("Delete error:", err);
    }
}

/* Company Contact Modal Handlers */
function openCompanyModal() {
    document.getElementById("company-modal-title").innerText = "Create Company Contact";
    document.getElementById("form-company-id").value = "";
    document.getElementById("company-form").reset();
    document.getElementById("company-modal").classList.add("active");
}

function openEditCompanyModal(id) {
    const c = allCompanies.find(item => item.id === id);
    if (!c) return;

    document.getElementById("company-modal-title").innerText = "Edit Company Contact";
    document.getElementById("form-company-id").value = c.id;
    document.getElementById("form-company-name").value = c.name;
    document.getElementById("form-company-email").value = c.company_email;
    document.getElementById("form-company-phone").value = c.phone;
    document.getElementById("form-company-location").value = c.location;
    document.getElementById("form-company-notes").value = c.notes || "";

    document.getElementById("company-modal").classList.add("active");
}

function closeCompanyModal() {
    document.getElementById("company-modal").classList.remove("active");
}

async function handleCompanySubmit(e) {
    e.preventDefault();
    const id = document.getElementById("form-company-id").value;
    const payload = {
        name: document.getElementById("form-company-name").value,
        company_email: document.getElementById("form-company-email").value,
        phone: document.getElementById("form-company-phone").value,
        location: document.getElementById("form-company-location").value,
        notes: document.getElementById("form-company-notes").value || null
    };

    try {
        let res;
        if (id) {
            res = await fetch(`/api/v1/companies/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        } else {
            res = await fetch("/api/v1/companies", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        }

        if (res.ok) {
            closeCompanyModal();
            fetchPlatformData();
        } else {
            alert("Error saving company contact");
        }
    } catch (err) {
        console.error("Submit error:", err);
    }
}

async function deleteCompany(id) {
    if (!confirm("Are you sure you want to delete this company contact?")) return;

    try {
        const res = await fetch(`/api/v1/companies/${id}`, { method: "DELETE" });
        if (res.ok) {
            fetchPlatformData();
        } else {
            alert("Error deleting company");
        }
    } catch (err) {
        console.error("Delete error:", err);
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
