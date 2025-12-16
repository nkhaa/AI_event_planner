
function activateTab(tabName) {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    const btn = document.querySelector(`.tab[data-tab='${tabName}']`);
    const pane = document.getElementById(tabName);
    if (btn) btn.classList.add("active");
    if (pane) pane.classList.add("active");
}

document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => activateTab(tab.dataset.tab));
});

// Quick-jump buttons on the hero
document.querySelectorAll("[data-tab-jump]").forEach(btn => {
    btn.addEventListener("click", () => activateTab(btn.dataset.tabJump));
});

function showMessage(elementId, message, isError = false) {
    const messageEl = document.getElementById(elementId);
    if (messageEl) {
        messageEl.textContent = message;
        const base = "message text-sm rounded-md px-4 py-2";
        messageEl.className = isError
            ? `${base} text-red-200 bg-red-500/20 border border-red-400/40`
            : `${base} text-emerald-200 bg-emerald-500/20 border border-emerald-400/40`;
        messageEl.classList.remove("hidden");
        setTimeout(() => {
            messageEl.classList.add("hidden");
        }, 5000);
    } else {
       
        alert(message);
    }
}

async function fetchJSON(url, options = {}) {
    try {
        const res = await fetch(url, options);
        let data;
        
        // Try to parse JSON, but handle non-JSON responses
        const contentType = res.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            data = await res.json();
        } else {
            const text = await res.text();
            throw new Error(`Server returned: ${text || res.statusText}`);
        }
        
        return { ok: res.ok, status: res.status, data };
    } catch (error) {
        // Network error or JSON parse error
        throw error;
    }
}

// Register
document.getElementById("register-btn").addEventListener("click", async () => {
    let identifier = document.getElementById("register-identifier").value;
    let pass = document.getElementById("register-password").value;

    if (!identifier || !pass) {
        showMessage("register-message", "Имэйл эсвэл утас, нууц үг оруулна уу", true);
        return;
    }

    try {
        const base = window.location.origin;
        const { ok, status, data } = await fetchJSON(`${base}/register`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ identifier, password: pass })
        });
        
        if (ok && data.status === "ok") {
            showMessage("register-message", data.message, false);
            // Clear form
            document.getElementById("register-identifier").value = "";
            document.getElementById("register-password").value = "";
        } else {
            showMessage("register-message", data.message || data.error || "Алдаа гарлаа", true);
        }
    } catch (error) {
        console.error("Register error:", error);
        showMessage("register-message", "Холболтын алдаа: " + (error.message || "Сервертэй холбогдох боломжгүй"), true);
    }
});

// Login
document.getElementById("login-btn").addEventListener("click", async () => {
    let identifier = document.getElementById("login-identifier").value;
    let pass = document.getElementById("login-password").value;

    if (!identifier || !pass) {
        showMessage("login-message", "Имэйл эсвэл утас, нууц үг оруулна уу", true);
        return;
    }

    try {
        const base = window.location.origin;
        const { ok, status, data } = await fetchJSON(`${base}/login`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ identifier, password: pass })
        });

        if (ok && data.status === "logged_in") {
            document.getElementById("dashboard").classList.remove("hidden");
            document.getElementById("user-identifier").innerText = data.identifier;
            
            // Hide login/register tabs
            document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
            document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));

            // Load login history
            try {
                const base = window.location.origin;
                const historyResult = await fetchJSON(`${base}/history/${encodeURIComponent(data.identifier)}`);
                if (historyResult.ok) {
                    const list = historyResult.data;
                    document.getElementById("history").innerHTML =
                        list.map(item => `<li>${item.timestamp} — ${item.success}</li>`).join("");
                } else {
                    document.getElementById("history").innerHTML = "<li>Түүх ачаалахад алдаа гарлаа</li>";
                }
            } catch (error) {
                console.error("History error:", error);
                document.getElementById("history").innerHTML = "<li>Түүх ачаалахад алдаа гарлаа</li>";
            }
        } else {
            showMessage("login-message", data.message || data.error || "Нэвтрэхэд алдаа гарлаа", true);
        }
    } catch (error) {
        console.error("Login error:", error);
        showMessage("login-message", "Холболтын алдаа: " + (error.message || "Сервертэй холбогдох боломжгүй"), true);
    }
});

// Provider register
document.getElementById("provider-btn").addEventListener("click", async () => {
    const name = document.getElementById("p-name").value.trim();
    const capacity = parseInt(document.getElementById("p-capacity").value, 10);
    const price = parseInt(document.getElementById("p-price").value, 10);
    const packages = document.getElementById("p-packages").value;
    const image_url = document.getElementById("p-image").value;
    const available_dates = document.getElementById("p-dates").value;
    const location = document.getElementById("p-location").value.trim();

    if (!name || Number.isNaN(capacity) || Number.isNaN(price) || !location) {
        showMessage("provider-message", "Нэр, хүчин чадал, үнэ, байршил шаардлагатай", true);
        return;
    }

    try {
        const base = window.location.origin;
        const { ok, data } = await fetchJSON(`${base}/api/providers/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name,
                capacity,
                price,
                packages,
                image_url,
                available_dates,
                location
            })
        });

        if (ok) {
            showMessage("provider-message", data.message || "Амжилттай бүртгэгдлээ", false);
            ["p-name","p-capacity","p-price","p-packages","p-image","p-dates","p-location"].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.value = "";
            });
        } else {
            showMessage("provider-message", data.message || "Алдаа гарлаа", true);
        }
    } catch (error) {
        console.error("Provider register error:", error);
        showMessage("provider-message", "Холболтын алдаа: " + (error.message || "Сервертэй холбогдох боломжгүй"), true);
    }
});


// Logout
document.getElementById("logout-btn").addEventListener("click", () => {
    // Hide dashboard
    document.getElementById("dashboard").classList.add("hidden");
    
    // Show login tab
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    document.querySelector('[data-tab="login"]').classList.add("active");
    document.getElementById("login").classList.add("active");
    
    // Clear form fields
    document.getElementById("login-identifier").value = "";
    document.getElementById("login-password").value = "";
    document.getElementById("register-identifier").value = "";
    document.getElementById("register-password").value = "";
    ["p-name","p-capacity","p-price","p-packages","p-image","p-dates","p-location"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
    
    // Clear history
    document.getElementById("history").innerHTML = "";
    document.getElementById("user-identifier").innerText = "";
});
