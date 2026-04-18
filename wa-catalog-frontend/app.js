document.addEventListener("DOMContentLoaded", () => {
    const searchBtn = document.getElementById("searchBtn");
    const showAllBtn = document.getElementById("showAllBtn");
    const phoneInput = document.getElementById("phoneInput");
    const catalogGrid = document.getElementById("catalogGrid");
    const statusMessage = document.getElementById("statusMessage");

    const API_BASE_URL = "http://127.0.0.1:8000/api/v1/catalogs";

    fetchAllCatalogs();

    phoneInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            searchBtn.click();
        }
    });

    searchBtn.addEventListener("click", () => {
        const userId = phoneInput.value.trim();

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

    async function fetchAllCatalogs() {
        catalogGrid.innerHTML = '<div class="loader"></div>';
        statusMessage.style.color = "#0056b3";
        statusMessage.innerText = "Memuat semua katalog dari database...";

        try {
            const response = await fetch(`${API_BASE_URL}/`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const jsonResponse = await response.json();

            if (jsonResponse.status === "success") {
                const catalogs = jsonResponse.data || [];
                statusMessage.style.color = "#28a745";
                statusMessage.innerText = `Menampilkan ${catalogs.length} katalog dari database. Masukkan nomor WhatsApp untuk memfilter katalog tertentu.`;
                renderCatalogs(catalogs);
            }
        } catch (error) {
            console.error("Error fetching all catalogs:", error);
            catalogGrid.innerHTML = "";
            statusMessage.style.color = "red";
            statusMessage.innerText = "Gagal terhubung ke server. Pastikan backend Docker sedang berjalan.";
        }
    }

    async function fetchCatalogsByUser(userId) {
        catalogGrid.innerHTML = '<div class="loader"></div>';
        statusMessage.style.color = "#0056b3";
        statusMessage.innerText = `Mencari katalog untuk nomor ${userId}...`;

        try {
            const response = await fetch(`${API_BASE_URL}/users/${userId}/catalogs`);

            if (response.status === 404) {
                statusMessage.style.color = "#d9534f";
                statusMessage.innerText = `Tidak ada katalog untuk nomor ${userId}. Menampilkan semua katalog yang tersedia.`;
                await fetchAllCatalogs();
                return;
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const jsonResponse = await response.json();

            if (jsonResponse.status === "success") {
                const catalogs = jsonResponse.data || [];
                statusMessage.style.color = "#28a745";
                statusMessage.innerText = `Menampilkan ${catalogs.length} katalog untuk nomor ${userId}. Klik "Tampilkan Semua" untuk kembali ke semua data.`;
                renderCatalogs(catalogs);
            }
        } catch (error) {
            console.error("Error fetching user catalogs:", error);
            catalogGrid.innerHTML = "";
            statusMessage.style.color = "red";
            statusMessage.innerText = "Gagal terhubung ke server.";
        }
    }

    function renderCatalogs(catalogs) {
        catalogGrid.innerHTML = "";

        if (!catalogs.length) {
            statusMessage.style.color = "#d9534f";
            statusMessage.innerText = "Belum ada katalog di database.";
            return;
        }

        catalogs.forEach((item, index) => {
            const menus = Array.isArray(item.menus) ? item.menus : [];
            let menuHtml = menus.map((menu) => `<li>${menu}</li>`).join("");

            if (!menuHtml) {
                menuHtml = "<li>Belum ada data menu</li>";
            }

            const card = document.createElement("div");
            card.className = "catalog-card";
            card.style.animationDelay = `${index * 0.1}s`;

            card.innerHTML = `
                <div class="card-header">
                    <h2 class="card-title">${item.product_name}</h2>
                    <p class="card-location">Lokasi: ${item.location}</p>
                    <p class="card-location">Nomor WA: ${item.user_id}</p>
                </div>
                <div class="card-body">
                    <h4>Daftar Menu:</h4>
                    <ul class="menu-list">
                        ${menuHtml}
                    </ul>
                    <div class="usp-box">
                        <strong>Keunggulan:</strong>
                        <p>"${item.unique_selling_point}"</p>
                    </div>
                </div>
            `;

            catalogGrid.appendChild(card);
        });
    }
});
