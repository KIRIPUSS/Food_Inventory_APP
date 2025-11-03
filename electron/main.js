// electron/main.js
const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let backendProc = null;

function startBackend() {
  // Example path: packaged api executable; adjust path for your build
  const exePath = process.platform === "win32"
    ? path.join(process.resourcesPath, "api.exe")
    : path.join(process.resourcesPath, "api"); // mac/linux name

  backendProc = spawn(exePath, [], { stdio: "ignore" });
}

function stopBackend() {
  if (backendProc) {
    backendProc.kill();
    backendProc = null;
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: { preload: path.join(__dirname, 'preload.js'),
                      contextIsolation: true }
  });

  // Dev: load Vite
  const dev = process.env.ELECTRON_DEV === "1";
  if (dev) {
    win.loadURL("http://localhost:5173");
    win.webContents.openDevTools();
  } else {
    // Prod: load built index.html
    win.loadFile(path.join(__dirname, "../frontend/dist/index.html"));
  }
}

app.whenReady().then(() => {
  if (process.env.ELECTRON_DEV !== "1") startBackend();
  createWindow();
});
app.on("window-all-closed", () => { stopBackend(); if (process.platform !== "darwin") app.quit(); });
app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
// Expose system theme to frontend
ipcMain.handle('get-system-theme', () => {
  return nativeTheme.shouldUseDarkColors ? 'dark' : 'light';
});

nativeTheme.on('updated', () => {
  // Notify renderer when theme changes
  BrowserWindow.getAllWindows().forEach(win => {
    win.webContents.send('theme-changed', nativeTheme.shouldUseDarkColors ? 'dark' : 'light');
  });
});
