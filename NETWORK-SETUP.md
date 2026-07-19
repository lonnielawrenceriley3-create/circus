# Network Setup - Multi-Device Sync

Use this guide to set up the Flea Circus system for multiple devices (iPhone operator + TV display, or iPad + projector).

## The Problem

If you download the files onto your iPhone and desktop separately, they won't sync because they're using separate `localStorage` databases.

## The Solution

Run a simple server that both devices connect to.

---

## Step-by-Step Setup

### Step 1: Install Node.js
Download from https://nodejs.org (use LTS version)

Verify installation:
```bash
node --version
```

### Step 2: Start the Server

Open Terminal (Mac/Linux) or Command Prompt (Windows) and navigate to your circus folder:

```bash
# Navigate to the folder where index.html is located
cd /path/to/circus

# Start the server
node server.js
```

You should see:
```
🎪 Flea Circus Show Control System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Server running on port 8000

Access from:
  Local:       http://localhost:8000
  This device: http://127.0.0.1:8000
  ...
```

### Step 3: Find Your Computer's IP Address

The server told you your IP. Or find it manually:

**Windows Command Prompt:**
```
ipconfig
```
Look for "IPv4 Address" (usually `192.168.x.x`)

**Mac/Linux Terminal:**
```
ifconfig | grep "inet "
```
Look for your WiFi adapter's IP address

### Step 4: Connect Both Devices

All devices must be on the **same WiFi network**.

**On the Display (Projector/TV):**
```
http://<YOUR-IP>:8000/display.html
```
Press F11 or fullscreen button.

**On the Operator (iPad/Phone):**
```
http://<YOUR-IP>:8000/control.html
```

Example:
- Display: `http://192.168.1.42:8000/display.html`
- Operator: `http://192.168.1.42:8000/control.html`

### Step 5: Test It

Click a button on the operator console. The display should respond instantly.

---

## Common Issues

### "Can't reach this server"
- Check all devices are on the same WiFi
- Make sure server is still running (Terminal/Command Prompt)
- Try using different IP address (sometimes needs .1 or .254)
- Disable VPN on all devices
- Check firewall isn't blocking port 8000

### "Server won't start"
- Make sure you're in the correct folder (`cd /path/to/circus`)
- Try a different port: `node server.js 3000`
- Port 8000 might be in use. Try 8080 or 3000

### "iPhone still not syncing"
- Hard refresh: Safari → reload button (or Ctrl+R / Cmd+R)
- Make sure both URLs have the same IP address
- Check Safari privacy settings aren't blocking localStorage
- Try opening in incognito/private mode (and disable when using)

### Server keeps disconnecting
If your WiFi is unstable:
- Move devices closer to router
- Reduce number of other devices on network
- Try ethernet cable if available (for computer running server)

---

## Local Testing (Same Computer)

To test before going multi-device:

1. Start server: `node server.js`
2. Open two browser windows:
   - Window 1: `http://localhost:8000/display.html`
   - Window 2: `http://localhost:8000/control.html`
3. Buttons on Window 2 update Window 1 instantly

---

## Performance Tips

- Operator console (iPad) gets most use - good WiFi signal important
- Display (projector) can tolerate occasional lag
- 100ms sync is normal
- If lag is bad, check other WiFi usage on network
- Try reducing other device connections

---

## When to Use Each Mode

| Scenario | Mode | How |
|----------|------|-----|
| Testing on one computer | Local (localStorage) | Just open both files in same browser |
| Testing on same WiFi | Network | Run `node server.js` and connect via IP |
| iPhone + Projector in same room | Network | Definitely use server mode |
| Remote operation (different locations) | Network | Still works! Just use different IP |

---

## Security Note

This server is designed for local use only. It has no authentication.

For public networks or untrusted environments:
- Use firewall to restrict port 8000
- Only allow your specific devices
- Consider nginx/Apache with authentication for production

---

## Getting Help

1. Check browser console: F12 → Console tab
2. Check terminal where server is running
3. Try restarting server (`Ctrl+C` then `node server.js` again)
4. Make sure files are in the correct folder

---

## Need Node.js?

https://nodejs.org - Download LTS version

It's a small, simple tool - just one file to run your show.

No complicated setup needed. Just `node server.js` and go!
