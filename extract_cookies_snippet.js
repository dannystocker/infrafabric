/**
 * BING CHAT COOKIE EXTRACTOR
 *
 * INSTRUCTIONS:
 * 1. Open https://bing.com/chat in your browser
 * 2. Make sure you're logged in
 * 3. Open Developer Console (F12 or Ctrl+Shift+J)
 * 4. Paste this entire script and press Enter
 * 5. Script will download cookies.json automatically
 *
 * ALTERNATIVE: Copy the output from console and save manually
 */

(async function() {
    console.log("🔍 Extracting Bing Chat cookies...");

    try {
        // Get all cookies for bing.com
        const cookies = await cookieStore.getAll({
            domain: '.bing.com'
        });

        if (cookies.length === 0) {
            console.error("❌ No cookies found. Are you logged in?");
            return;
        }

        // Format cookies for EdgeGPT
        const formattedCookies = cookies.map(cookie => ({
            name: cookie.name,
            value: cookie.value,
            domain: cookie.domain,
            path: cookie.path,
            expires: cookie.expires,
            httpOnly: cookie.httpOnly || false,
            secure: cookie.secure || false,
            sameSite: cookie.sameSite || "None"
        }));

        const cookiesJSON = JSON.stringify(formattedCookies, null, 2);

        // Create download link
        const blob = new Blob([cookiesJSON], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'cookies.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log("✅ cookies.json downloaded!");
        console.log(`📊 Extracted ${cookies.length} cookies`);
        console.log("\n📋 Cookie preview:");
        console.log(cookiesJSON);
        console.log("\n💾 Next steps:");
        console.log("1. Move cookies.json to /home/setup/infrafabric/");
        console.log("2. Run: .venv-copilot/bin/python3 copilot_shard.py \"test\"");

    } catch (error) {
        console.error("❌ Error:", error);
        console.log("\n🔄 FALLBACK METHOD:");
        console.log("If Cookie Store API failed, use this manual method:");
        console.log("\n// Copy this output and save as cookies.json:");

        // Fallback: Parse document.cookie
        const cookieStrings = document.cookie.split('; ');
        const manualCookies = cookieStrings.map(str => {
            const [name, value] = str.split('=');
            return {
                name: name,
                value: value,
                domain: '.bing.com',
                path: '/',
                secure: true,
                httpOnly: false,
                sameSite: "None"
            };
        });

        console.log(JSON.stringify(manualCookies, null, 2));
    }
})();
