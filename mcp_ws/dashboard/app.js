const socket = new WebSocket("ws://localhost:8765");

const statusEl = document.getElementById("server-status");
const logEl = document.getElementById("log");
const toolListEl = document.getElementById("tool-list");
const clientListEl = document.getElementById("client-list");

// CONNECTED
socket.addEventListener("open", () => {
    statusEl.textContent = "Connected";
});

// DISCONNECTED
socket.addEventListener("close", () => {
    statusEl.textContent = "Disconnected";
});

// LOG MESSAGES
socket.addEventListener("message", (event) => {
    logEl.textContent += event.data + "\n";

    try {
        const msg = JSON.parse(event.data);

        // Populate tools
        if (msg?.result?.tools) {
            toolListEl.innerHTML = "";
            msg.result.tools.forEach(t => {
                toolListEl.innerHTML += `<li>${t.name}</li>`;
            });
        }

    } catch {}
});
