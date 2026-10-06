document.addEventListener("DOMContentLoaded", () => {
    // --- DOM Elements ---
    const searchBtn = document.getElementById("searchBtn");
    const showAllBtn = document.getElementById("showAllBtn");
    const phoneInput = document.getElementById("phoneInput");
    const catalogGrid = document.getElementById("catalogGrid");
    const statusMessage = document.getElementById("statusMessage");

    // --- Constants ---
    const API_BASE_URL = "/api/v1/catalogs";
    const STATUS_COLORS = {
        info: "#0056b3",
        success: "#28a745",
        error: "#d9534f"
    };

    // --- Helper Functions ---

    /**
     * Updates the status message text and styling.
     * @param {string} text - Message to display to the user.
     * @param {'info' | 'success' | 'error'} tone - Tone determining the text color.
     */
    function setStatus(text, tone = "info") {
        statusMessage.style.color = STATUS_COLORS[tone] || STATUS_COLORS.info;
        statusMessage.textContent = text;
    }

    /**
     * Escapes HTML entities to prevent Stored XSS when rendering into the DOM.
     * @param {string|null|undefined} str - The raw text input.
     * @returns {string} Sanitized string safe for HTML rendering.
     */
    function escapeHtml(str) {
        if (str === null || str === undefined) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    /**
     * Masks phone number to protect merchant privacy across 8-16 digit formats.
     * @param {string} phone - Raw phone number digits.
     * @returns {string} Partially masked phone number.
     */
    function maskPhoneNumber(phone) {
        if (!phone) return "";
        const str = String(phone).trim();
        if (str.length <= 4) return str;
        if (str.length <= 8) {
            return `${str.slice(0, 3)}****${str.slice(-2)}`;
        }
        return `${str.slice(0, 4)}****${str.slice(-3)}`;
    }

    /**
     * Extracts initial user phone number from URL path or query string.
     * @returns {string} Sanitized initial phone number without leading '+'.
     */
    function getInitialUserId() {
        const pathParts = window.location.pathname.split("/").filter(Boolean);
        if (pathParts.length >= 3 && pathParts[0] === "users" && pathParts[2] === "catalogs") {
            return decodeURIComponent(pathParts[1]).replace(/^\+/, "");
        }
        const urlParams = new URLSearchParams(window.location.search);
        const queryUser = urlParams.get("user") || urlParams.get("phone");
        return queryUser ? queryUser.trim().replace(/^\+/, "") : "";
    }

    // --- API / Fetch Functions ---

    /**
     * Fetches all catalogs from the backend and renders them.
     * @param {boolean} preserveStatus - When true, keeps existing status text intact.
     */
    async function fetchAllCatalogs(preserveStatus = false) {
        catalogGrid.innerHTML = '<div class="loader"></div>';
        if (!preserveStatus) {
            setStatus("Memuat semua katalog...", "info");
        }

        try {
            const response = await fetch(`${API_BASE_URL}/`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const jsonResponse = await response.json();

            if (jsonResponse.status === "success") {
                const catalogs = jsonResponse.data || [];
                if (!preserveStatus) {
                    setStatus(
                        `Menampilkan ${catalogs.length} katalog. Masukkan nomor WhatsApp untuk memfilter katalog tertentu.`,
                        "success"
                    );
                }
                renderCatalogs(catalogs, preserveStatus);
            }
        } catch (error) {
            console.error("Error fetching all catalogs:", error);
            catalogGrid.innerHTML = "";
            setStatus("Gagal terhubung ke server. Silakan coba beberapa saat lagi.", "error");
        }
    }

    /**
     * Fetches catalogs belonging to a specific WhatsApp phone number.
     * @param {string} userId - Sanitized WhatsApp phone number.
     */
    async function fetchCatalogsByUser(userId) {
        catalogGrid.innerHTML = '<div class="loader"></div>';
        setStatus(`Mencari katalog untuk nomor WhatsApp ${userId}...`, "info");

        try {
            const response = await fetch(`${API_BASE_URL}/users/${encodeURIComponent(userId)}/catalogs`);

            if (response.status === 404) {
                setStatus(
                    `Tidak ada katalog untuk nomor WhatsApp ${userId}. Menampilkan semua katalog yang tersedia.`,
                    "error"
                );
                await fetchAllCatalogs(true);
                return;
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const jsonResponse = await response.json();

            if (jsonResponse.status === "success") {
                const catalogs = jsonResponse.data || [];
                setStatus(
                    `Menampilkan ${catalogs.length} katalog untuk nomor WhatsApp ${userId}. Klik "Tampilkan Semua" untuk kembali ke semua data.`,
                    "success"
                );
                renderCatalogs(catalogs);
            }
        } catch (error) {
            console.error("Error fetching user catalogs:", error);
            catalogGrid.innerHTML = "";
            setStatus("Gagal terhubung ke server. Silakan coba beberapa saat lagi.", "error");
        }
    }

    // --- Render Functions ---

    /**
     * Renders an array of catalog items into card components.
     * @param {Array<Object>} catalogs - List of catalog objects.
     * @param {boolean} preserveStatus - Whether to preserve the current status message.
     */
    function renderCatalogs(catalogs, preserveStatus = false) {
        catalogGrid.innerHTML = "";

        if (!catalogs.length) {
            if (!preserveStatus) {
                setStatus("Belum ada katalog yang tersedia.", "error");
            }
            return;
        }

        catalogs.forEach((item, index) => {
            const menus = Array.isArray(item.menus) ? item.menus : [];
            let menuHtml = menus.map((menu) => `<li>${escapeHtml(menu)}</li>`).join("");

            if (!menuHtml) {
                menuHtml = "<li>Belum ada data menu</li>";
            }

            // Note: product_name stores the business / shop name
            const safeName = escapeHtml(item.product_name);
            const safeLocation = escapeHtml(item.location);
            const safeUserId = escapeHtml(maskPhoneNumber(item.user_id));
            const safeUsp = escapeHtml(item.unique_selling_point);

            const card = document.createElement("div");
            card.className = "catalog-card";
            card.style.animationDelay = `${index * 0.1}s`;

            card.innerHTML = `
                <div class="card-header">
                    <h2 class="card-title">${safeName}</h2>
                    <p class="card-location">Lokasi: ${safeLocation}</p>
                    <p class="card-location">Nomor WhatsApp: ${safeUserId}</p>
                </div>
                <div class="card-body">
                    <h4>Daftar Menu:</h4>
                    <ul class="menu-list">
                        ${menuHtml}
                    </ul>
                    <div class="usp-box">
                        <strong>Keunggulan:</strong>
                        <p>"${safeUsp}"</p>
                    </div>
                </div>
            `;

            catalogGrid.appendChild(card);
        });
    }

    // --- Event Listeners ---

    phoneInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            searchBtn.click();
        }
    });

    searchBtn.addEventListener("click", () => {
        const userId = phoneInput.value.trim().replace(/^\+/, "");

        if (!userId) {
            fetchAllCatalogs();
            return;
        }

        fetchCatalogsByUser(userId);
    });

    showAllBtn.addEventListener("click", () => {
        phoneInput.value = "";
        fetchAllCatalogs();
    });

    // --- Bootstrap / Initialization ---

    const initialUserId = getInitialUserId();
    if (initialUserId) {
        phoneInput.value = initialUserId;
        fetchCatalogsByUser(initialUserId);
    } else {
        fetchAllCatalogs();
    }
});
