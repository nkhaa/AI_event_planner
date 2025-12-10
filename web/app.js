// Tab switching
document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

        tab.classList.add("active");
        document.getElementById(tab.dataset.tab).classList.add("active");
    });
});

// Register
document.getElementById("register-btn").addEventListener("click", async () => {
    let email = document.getElementById("register-email").value;
    let pass = document.getElementById("register-password").value;

    let res = await fetch("http://localhost:5000/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ email, password: pass })
    });

    let data = await res.json();
    alert(data.message);
});

// Login
document.getElementById("login-btn").addEventListener("click", async () => {
    let email = document.getElementById("login-email").value;
    let pass = document.getElementById("login-password").value;

    let res = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ email, password: pass })
    });

    let data = await res.json();

    if (data.status === "logged_in") {
        document.getElementById("dashboard").classList.remove("hidden");
        document.getElementById("user-email").innerText = data.email;

        // Load login history
        let h = await fetch(`http://localhost:5000/history/${data.email}`);
        let list = await h.json();

        document.getElementById("history").innerHTML =
            list.map(item => `<li>${item.timestamp} — ${item.success}</li>`).join("");
    } else {
        alert(data.error);
    }
});
