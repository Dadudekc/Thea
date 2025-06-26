# Discord Bot Setup Guide
## Getting All Required IDs

### Step 1: Create Discord Application
1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Name it (e.g., "Dream.OS Bot")
4. **Copy the Application ID** (you'll see it in the General Information)

### Step 2: Add Bot to Application
1. In your application, go to "Bot" section
2. Click "Add Bot"
3. **Copy the Bot Token** (click "Reset Token" if needed)
4. Enable these options:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent

### Step 3: Get Server (Guild) ID
1. In Discord, enable Developer Mode:
   - User Settings → Advanced → Developer Mode
2. Right-click on your server name
3. Click "Copy Server ID"
4. **This is your Guild ID**

### Step 4: Get Channel ID
1. Right-click on the channel where you want the bot to send messages
2. Click "Copy Channel ID"
3. **This is your Channel ID**

### Step 5: Invite Bot to Server
1. Go back to Discord Developer Portal
2. Select your application
3. Go to "OAuth2" → "URL Generator"
4. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
5. Select permissions:
   - ✅ Send Messages
   - ✅ Use Slash Commands
   - ✅ Embed Links
   - ✅ Read Message History
6. Copy the generated URL
7. Open URL in browser and select your server

### Step 6: Configure Dream.OS
Update your `config/discord_config.json`:

```json
{
  "enabled": true,
  "bot_token": "YOUR_BOT_TOKEN_HERE",
  "guild_id": "YOUR_SERVER_ID_HERE",
  "channel_id": "YOUR_CHANNEL_ID_HERE",
  "prefix": "/",
  "auto_connect": true
}
```

### Step 7: Test Connection
Run: `python core/discord_manager.py`

### ID Summary:
- **Application ID**: Your bot's application identifier
- **Bot Token**: Your bot's secret authentication token
- **Guild ID**: Your Discord server's ID
- **Channel ID**: Specific channel where bot sends messages

### Quick Reference:
```
Application ID: 1234567890123456789 (from Developer Portal)
Bot Token: ABC123.XYZ789.DEF456 (from Bot section)
Guild ID: 9876543210987654321 (right-click server → Copy ID)
Channel ID: 111222333444555666 (right-click channel → Copy ID)
``` 