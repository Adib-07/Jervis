const conversation = document.querySelector("#conversation");
const commandForm = document.querySelector("#commandForm");
const commandInput = document.querySelector("#commandInput");
const micButton = document.querySelector("#micButton");
const muteButton = document.querySelector("#muteButton");
const listenState = document.querySelector("#listenState");
const voiceHint = document.querySelector("#voiceHint");
const serverStatus = document.querySelector("#serverStatus");
const serverDot = document.querySelector("#serverDot");
const voiceStatus = document.querySelector("#voiceStatus");
const aiStatus = document.querySelector("#aiStatus");
const clearButton = document.querySelector("#clearButton");
const turnCount = document.querySelector("#turnCount");
const canvas = document.querySelector("#waveform");
const ctx = canvas.getContext("2d");

let listening = false;
let spokenResponses = true;
let pulse = 0;
let turns = 1;

function addMessage(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const meta = document.createElement("div");
  meta.className = "message-meta";
  meta.textContent = role === "user" ? "You" : "Jarvis";
  const paragraph = document.createElement("p");
  paragraph.textContent = text;
  article.append(meta, paragraph);
  conversation.append(article);
  article.scrollIntoView({ behavior: "smooth", block: "end" });
  turns += 1;
  turnCount.textContent = `${turns} messages`;
}

async function runCommand(command) {
  const trimmed = command.trim();
  if (!trimmed) return;

  addMessage("user", trimmed);
  commandInput.value = "";
  listenState.textContent = "Working";

  try {
    const response = await fetch("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command: trimmed }),
    });
    const result = await response.json();
    const text = result.response || "No response.";
    addMessage("assistant", text);
    await speak(text);
    listenState.textContent = "Ready";
  } catch (error) {
    addMessage("assistant", `Could not reach Jarvis server: ${error.message}`);
    listenState.textContent = "Offline";
  }
}

async function listenFromServer() {
  if (listening) return;
  listening = true;
  micButton.disabled = true;
  micButton.classList.add("listening");
  listenState.textContent = "Listening";
  voiceStatus.textContent = "Listening";
  voiceHint.textContent = "Speak now. Jarvis will stop automatically.";

  try {
    const response = await fetch("/api/listen", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    const result = await response.json();
    if (!result.ok) {
      throw new Error(result.error || "Voice recognition failed.");
    }

    const command = result.command || "";
    const answer = result.response || "No response.";
    commandInput.value = command;
    addMessage("user", command);
    addMessage("assistant", answer);
    await speak(answer);
    voiceStatus.textContent = "Voice ready";
    listenState.textContent = "Ready";
  } catch (error) {
    addMessage("assistant", `Voice error: ${error.message}`);
    voiceStatus.textContent = "Voice needs attention";
    listenState.textContent = "Ready";
    voiceHint.textContent = "Check microphone permission for Terminal, then try again.";
  } finally {
    listening = false;
    micButton.disabled = false;
    micButton.classList.remove("listening");
  }
}

async function speak(text) {
  if (!spokenResponses) return;

  try {
    await fetch("/api/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
  } catch {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text.replace(/`/g, ""));
    utterance.rate = 1;
    utterance.pitch = 0.95;
    window.speechSynthesis.speak(utterance);
  }
}

function drawWaveform() {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const dpr = window.devicePixelRatio || 1;
  if (canvas.width !== Math.floor(width * dpr) || canvas.height !== Math.floor(height * dpr)) {
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
  }
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, width, height);
  ctx.lineWidth = 2;
  ctx.strokeStyle = listening ? "rgba(180, 63, 82, 0.78)" : "rgba(15, 143, 122, 0.46)";
  ctx.beginPath();
  const amplitude = listening ? 46 : 18;
  const center = height / 2;
  for (let x = 0; x <= width; x += 6) {
    const y = center + Math.sin((x + pulse) / 34) * amplitude + Math.sin((x + pulse) / 15) * 8;
    if (x === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();
  pulse += listening ? 4 : 1;
  requestAnimationFrame(drawWaveform);
}

async function checkServer() {
  try {
    const response = await fetch("/health");
    const result = await response.json();
    if (!response.ok) throw new Error("bad status");
    serverStatus.textContent = "Connected";
    voiceStatus.textContent = result.voice ? "Ready" : "Unavailable";
    aiStatus.textContent = result.ai ? "Ready" : "Setup Needed";
    micButton.disabled = !result.voice;
    voiceHint.textContent = result.voice
      ? "Press the mic and speak one command."
      : "Microphone backend is unavailable. Typed commands still work.";
  } catch {
    serverStatus.textContent = "Disconnected";
    voiceStatus.textContent = "Offline";
    aiStatus.textContent = "Offline";
  }
}

commandForm.addEventListener("submit", (event) => {
  event.preventDefault();
  runCommand(commandInput.value);
});

micButton.addEventListener("click", () => {
  listenFromServer();
});

muteButton.addEventListener("click", () => {
  spokenResponses = !spokenResponses;
  muteButton.textContent = spokenResponses ? "Sound On" : "Muted";
  muteButton.title = spokenResponses ? "Spoken responses on" : "Spoken responses off";
  if (!spokenResponses) window.speechSynthesis?.cancel();
});

clearButton.addEventListener("click", () => {
  conversation.innerHTML = "";
  turns = 0;
  addMessage("assistant", "Conversation cleared. I am ready.");
});

document.querySelectorAll(".quick-command").forEach((button) => {
  button.addEventListener("click", () => runCommand(button.dataset.command || ""));
});

checkServer();
drawWaveform();
setInterval(checkServer, 5000);
