const MCP_HOST = "ws://localhost:8765";
let ws = null;

function connectMCP() {
    ws = new WebSocket(MCP_HOST);

    ws.onopen = () => {
        console.log("[Dashboard] Connected to MCP server");
        initialize();
    };

    ws.onmessage = (msg) => {
        const data = JSON.parse(msg.data);
        handleMessage(data);
    };

    ws.onclose = () => {
        console.log("[Dashboard] Disconnected. Reconnecting...");
        setTimeout(connectMCP, 2000);
    };
}

function sendRPC(method, params = {}, id = Date.now()) {
    ws.send(JSON.stringify({ jsonrpc: "2.0", method, params, id }));
}

function initialize() {
    sendRPC("initialize", { clientType: "dashboard" });
}

function handleMessage(msg) {
    if (msg.method === "notifications/initialized") {
        console.log("[Dashboard] MCP initialized");
        fetchAll();
    } else if (msg.method === "logging/logMessage") {
        displayLog(msg.params.level, msg.params.message);
    } else if (msg.id) {
        if (msg.result) {
            if (msg.result.tools) displayTools(msg.result.tools);
            if (msg.result.resources) displayResources(msg.result.resources);
            if (msg.result.prompts) displayPrompts(msg.result.prompts);
        }
    }
}

function fetchAll() {
    sendRPC("tools/list");
    sendRPC("resources/list");
    sendRPC("prompts/list");
}

function displayTools(tools) {
    const container = document.getElementById("tools");
    container.innerHTML = "";
    tools.forEach(t => {
        const div = document.createElement("div");
        div.className = "tool-item";

        const title = document.createElement("div");
        title.textContent = `${t.name} — ${t.description}`;
        div.appendChild(title);

        // Execute Button
        const btn = document.createElement("button");
        btn.textContent = "Execute";
        btn.onclick = () => showExecuteForm(t, div);
        div.appendChild(btn);

        container.appendChild(div);
    });
}

function showExecuteForm(tool, parentDiv) {
    // Remove existing form
    const existing = parentDiv.querySelector(".tool-form");
    if (existing) existing.remove();

    const form = document.createElement("div");
    form.className = "tool-form";

    const table = document.createElement("table");
    const schema = tool.inputSchema;
    const props = schema.properties;
    const required = schema.required || [];

    for (const key in props) {
        const row = document.createElement("tr");

        const labelTd = document.createElement("td");
        labelTd.textContent = `${key} (${props[key].type})${required.includes(key) ? " *" : ""}`;
        row.appendChild(labelTd);

        const inputTd = document.createElement("td");
        const input = document.createElement("input");
        input.name = key;
        input.dataset.type = props[key].type;
        input.required = required.includes(key);
        inputTd.appendChild(input);
        row.appendChild(inputTd);

        table.appendChild(row);
    }

    form.appendChild(table);

    const submitBtn = document.createElement("button");
    submitBtn.textContent = "Call Tool";
    submitBtn.onclick = () => callTool(tool.name, form);
    form.appendChild(submitBtn);

    const resultDiv = document.createElement("div");
    resultDiv.className = "tool-result";
    form.appendChild(resultDiv);

    parentDiv.appendChild(form);
}

function callTool(toolName, form) {
    const inputs = form.querySelectorAll("input");
    const args = {};
    inputs.forEach(input => {
        let val = input.value;
        switch (input.dataset.type) {
            case "integer": val = parseInt(val); break;
            case "number": val = parseFloat(val); break;
            case "boolean": val = (val.toLowerCase() === "true"); break;
        }
        args[input.name] = val;
    });

    const id = Date.now();
    sendRPC("tools/call", { name: toolName, arguments: args }, id);

    // Listen for response once
    const handler = (msg) => {
        const data = JSON.parse(msg.data);
        if (data.id === id) {
            const resDiv = form.querySelector(".tool-result");
            if (data.result) {
                resDiv.textContent = JSON.stringify(data.result, null, 2);
            } else if (data.error) {
                resDiv.textContent = "Error: " + data.error.message;
            }
            ws.removeEventListener("message", handler);
        }
    };
    ws.addEventListener("message", handler);
}

function displayResources(resources) {
    const container = document.getElementById("resources");
    container.innerHTML = "";
    resources.forEach(r => {
        const div = document.createElement("div");
        div.className = "resource-item";
        div.textContent = `${r.name} — ${r.title || ""} (${r.mimeType})`;
        container.appendChild(div);
    });
}

function displayPrompts(prompts) {
    const container = document.getElementById("prompts");
    container.innerHTML = "";
    prompts.forEach(p => {
        const div = document.createElement("div");
        div.className = "prompt-item";
        div.textContent = `${p.name} — ${p.description || ""}`;
        container.appendChild(div);
    });
}

function displayLog(level, message) {
    const container = document.getElementById("logs");
    const div = document.createElement("div");
    div.className = `log-${level}`;
    div.textContent = `[${level}] ${message}`;
    container.appendChild(div);
}

window.onload = connectMCP;
