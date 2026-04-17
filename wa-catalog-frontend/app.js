document.addEventListener("DOMContentLoaded", () => {
    const searchBtn = document.getElementById("searchBtn");
    const phoneInput = document.getElementById("phoneInput");
    const catalogGrid = document.getElementById("catalogGrid");
    const statusMessage = document.getElementById("statusMessage");

    const API_BASE_URL = "http://127.0.0.1:8001/api/v1/catalogs";

    fetchAllCatalogs();

    phoneInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            searchBtn.click();
        }
    });

    searchBtn.addEventListener("click", () => {
        const userId = phoneInput.value.trim();
        if(!userId) {
            fetchAllCatalogs();
            return;
        }
        fetchCatalogs(userId);
    });

    async function fetchAllCatalogs() {
        catalogGrid.innerHTML = '<div class="loader"></div>';
        statusMessage.style.color = "#0056b3";
        statusMessage.innerText = "☁️ Memuat seluruh surga kuliner nusantara...";

        try {
            const response = await fetch(API_BASE_URL + "/");
            if(!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const jsonResponse = await response.json();
            
            if(jsonResponse.status === "success") {
                const catalogs = jsonResponse.data;
                statusMessage.style.color = "#28a745";
                statusMessage.innerText = `✅ Tersedia ${catalogs.length} Toko F&B hari ini. (Ketik Nomor Whatsapp untuk menemukan!)`;
                
                renderCatalogs(catalogs);
            }
        } catch (error) {
            console.error("Error fetching all data:", error);
            catalogGrid.innerHTML = '';
            statusMessage.style.color = "red";
            statusMessage.innerText = "⚠️ Gagal terhubung ke server. Pastikan Uvicorn menyala!";
        }
    }

    async function fetchCatalogs(userId) {
        catalogGrid.innerHTML = '<div class="loader"></div>';
        statusMessage.style.color = "#0056b3";
        statusMessage.innerText = "☁️ Terbang mencari katalog warung Anda...";

        try {
            const response = await fetch(`${API_BASE_URL}/users/${userId}/catalogs`);
            
            if(response.status === 404) {
                catalogGrid.innerHTML = '';
                statusMessage.style.color = "#d9534f";
                statusMessage.innerHTML = "❌ <b>Maaf!</b> Tidak ada katalog yang ditemukan untuk nomor ini.";
                return;
            }

            if(!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const jsonResponse = await response.json();
            
            if(jsonResponse.status === "success") {
                const catalogs = jsonResponse.data;
                statusMessage.style.color = "#28a745";
                statusMessage.innerText = `✅ Terfilter spesifik untuk warung ini.`;
                
                renderCatalogs(catalogs);
            }
        } catch (error) {
            console.error("Error fetching user data:", error);
            catalogGrid.innerHTML = '';
            statusMessage.style.color = "red";
            statusMessage.innerText = "⚠️ Gagal terhubung ke server.";
        }
    }

    function renderCatalogs(catalogs) {
        catalogGrid.innerHTML = "";

        catalogs.forEach((item, index) => {
            let menuHtml = item.menus.map(menu => `<li>${menu}</li>`).join("");
            if(!menuHtml) menuHtml = "<li>No menu data available</li>";

            const card = document.createElement("div");
            card.className = "catalog-card";
            card.style.animationDelay = `${index * 0.1}s`;

            card.innerHTML = `
                <div class="card-header">
                    <h2 class="card-title">${item.product_name}</h2>
                    <p class="card-location">📍 ${item.location}</p>
                </div>
                <div class="card-body">
                    <h4>Daftar Menu:</h4>
                    <ul class="menu-list">
                        ${menuHtml}
                    </ul>
                    <div class="usp-box">
                        <strong>💡 Spesial:</strong>
                        <p>"${item.unique_selling_point}"</p>
                    </div>
                </div>
            `;
            catalogGrid.appendChild(card);
        });
    }
});