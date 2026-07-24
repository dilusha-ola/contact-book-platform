let allContacts = [];

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
        const res = await fetch("/api/v1/contacts/stats");
        const data = await res.json();
        document.getElementById("stat-total").innerText = data.total_contacts || 0;
        document.getElementById("stat-companies").innerText = data.total_companies || 0;
        document.getElementById("stat-work").innerText = data.work_contacts || 0;
        document.getElementById("stat-personal").innerText = data.personal_contacts || 0;
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
        const companies = await res.json();
        renderCompaniesGrid(companies);
    } catch (err) {
        console.error("Error fetching companies:", err);
    }
}

function renderDashboardTable(contacts) {
    const tbody = document.getElementById("dashboard-table-body");
    tbody.innerHTML = "";
    if (contacts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--text-muted); padding: 20px;">No contacts stored in MongoDB. Click "+ Add Contact" to create one!</td></tr>`;
        return;
    }
    contacts.slice(0, 5).forEach(c => {
        tbody.appendChild(createRow(c));
    });
}

function renderContactsTable(contacts) {
    const tbody = document.getElementById("contacts-table-body");
    tbody.innerHTML = "";
    if (contacts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--text-muted); padding: 20px;">No matching contacts found.</td></tr>`;
        return;
    }
    contacts.forEach(c => {
        tbody.appendChild(createRow(c));
    });
}

function createRow(c) {
    const tr = document.createElement("tr");
    const badgeClass = (c.category && c.category.toLowerCase() === "work") ? "badge-work" : "badge-personal";
    tr.innerHTML = `
        <td><strong>${escapeHtml(c.name)}</strong></td>
        <td>${escapeHtml(c.email)}</td>
        <td>${escapeHtml(c.phone)}</td>
        <td>${escapeHtml(c.company || '-')}</td>
        <td><span class="badge ${badgeClass}">${escapeHtml(c.category)}</span></td>
        <td>
            <button class="btn btn-secondary btn-sm" onclick="openEditModal('${c.id}')">Edit</button>
            <button class="btn btn-danger btn-sm" onclick="deleteContact('${c.id}')">Delete</button>
        </td>
    `;
    return tr;
}

function renderCompaniesGrid(companies) {
    const grid = document.getElementById("companies-grid");
    grid.innerHTML = "";

    if (!companies || companies.length === 0) {
        grid.innerHTML = `<p style="color: var(--text-muted);">No company records found.</p>`;
        return;
    }

    companies.forEach(item => {
        const card = document.createElement("div");
        card.className = "company-card";
        const membersList = (item.members || []).map(m => `<li>👤 ${escapeHtml(m.name)} (${escapeHtml(m.email)})</li>`).join("");
        card.innerHTML = `
            <h3>🏢 ${escapeHtml(item.company)}</h3>
            <p style="color: var(--text-secondary); font-size: 13px; margin-top: 6px; font-weight: 600;">${item.contact_count} Contact(s)</p>
            <ul style="font-size: 12px; color: var(--text-secondary); margin-top: 8px; list-style: none; padding: 0;">
                ${membersList}
            </ul>
        `;
        grid.appendChild(card);
    });
}

function filterContacts() {
    const q = document.getElementById("search-input").value.toLowerCase();
    const cat = document.getElementById("category-filter").value;

    const filtered = allContacts.filter(c => {
        const matchesQuery = c.name.toLowerCase().includes(q) ||
                             c.email.toLowerCase().includes(q) ||
                             (c.company && c.company.toLowerCase().includes(q));
        const matchesCat = cat === "All" || c.category.toLowerCase() === cat.toLowerCase();
        return matchesQuery && matchesCat;
    });

    renderContactsTable(filtered);
}

function switchNav(viewId, btn) {
    document.querySelectorAll(".view-section").forEach(s => s.classList.remove("active"));
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));

    document.getElementById("view-" + viewId).classList.add("active");
    btn.classList.add("active");

    const titles = {
        dashboard: "Dashboard Overview",
        contacts: "All Contacts Directory",
        companies: "Companies Directory",
        settings: "Platform Settings"
    };
    document.getElementById("page-title").innerText = titles[viewId];

    // Close mobile menu if open
    document.getElementById("sidebar").classList.remove("open");
}

function toggleMobileMenu() {
    document.getElementById("sidebar").classList.toggle("open");
}

function openCreateModal() {
    document.getElementById("modal-title").innerText = "Create New Contact";
    document.getElementById("form-contact-id").value = "";
    document.getElementById("contact-form").reset();
    document.getElementById("contact-modal").classList.add("active");
}

function openEditModal(id) {
    const c = allContacts.find(item => item.id === id);
    if (!c) return;

    document.getElementById("modal-title").innerText = "Edit Contact";
    document.getElementById("form-contact-id").value = c.id;
    document.getElementById("form-name").value = c.name;
    document.getElementById("form-email").value = c.email;
    document.getElementById("form-phone").value = c.phone;
    document.getElementById("form-company").value = c.company || "";
    document.getElementById("form-category").value = c.category;
    document.getElementById("form-notes").value = c.notes || "";

    document.getElementById("contact-modal").classList.add("active");
}

function closeModal() {
    document.getElementById("contact-modal").classList.remove("active");
}

async function handleFormSubmit(e) {
    e.preventDefault();
    const id = document.getElementById("form-contact-id").value;
    const payload = {
        name: document.getElementById("form-name").value,
        email: document.getElementById("form-email").value,
        phone: document.getElementById("form-phone").value,
        company: document.getElementById("form-company").value || null,
        category: document.getElementById("form-category").value,
        notes: document.getElementById("form-notes").value || null
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
            closeModal();
            fetchPlatformData();
        } else {
            alert("Error saving contact");
        }
    } catch (err) {
        console.error("Submit error:", err);
    }
}

async function deleteContact(id) {
    if (!confirm("Are you sure you want to delete this contact?")) return;

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

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
