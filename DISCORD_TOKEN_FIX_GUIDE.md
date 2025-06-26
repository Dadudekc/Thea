# Discord Bot Token Fix Guide

## 🚨 Current Issue
The Discord bot token is invalid. This needs to be fixed before we can proceed with Day 2.

## 🔧 How to Fix

### Step 1: Get Your Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application (ID: `1369955853536464916`)
3. Click on **"Bot"** in the left sidebar
4. Click **"Reset Token"** to generate a new token
5. Copy the new token (it will look like: `MTM2OTk1NTg1MzUzNjQ2NDkxNi5H...`)

### Step 2: Update Your Configuration
1. Open your `.env` file
2. Update the `DISCORD_BOT_TOKEN` line with your new token:
   ```
   DISCORD_BOT_TOKEN=your_new_token_here
   ```
3. Save the file

### Step 3: Get Guild and Channel IDs
1. **Enable Developer Mode** in Discord:
   - Open Discord
   - Go to User Settings → Advanced
   - Turn on "Developer Mode"

2. **Get Guild (Server) ID**:
   - Right-click on your server name
   - Click "Copy Server ID"
   - Add to `.env`: `DISCORD_GUILD_ID=your_server_id`

3. **Get Channel ID**:
   - Right-click on the channel where you want the bot to work
   - Click "Copy Channel ID"
   - Add to `.env`: `DISCORD_CHANNEL_ID=your_channel_id`

### Step 4: Test the Fix
Run the test script to verify everything works:
```bash
python test_bot_token.py
```

## 🎯 Expected Result
After fixing the token, you should see:
```
✅ Successfully connected as YourBotName#1234
   Bot ID: 1369955853536464916
   Application ID: 1369955853536464916
🎉 Token is valid! Ready to proceed with Day 2.
```

## 🚀 Next Steps
Once the token is fixed:
1. Run `python test_discord_connection.py` to test full integration
2. Start the bot with `python start_discord_bot.py`
3. Test slash commands in Discord: `/ping`, `/dreamscape`, `/quests`, etc.

## 📋 Day 2 Commands Ready
The following slash commands are already implemented and ready to test:

- `/ping` - Test bot connectivity
- `/dreamscape` - Get current dreamscape status
- `/quests` - Show available and completed quests
- `/skills` - Show player skills and progression
- `/domains` - Show empire domains and territories
- `/process` - Manually trigger conversation processing
- `/stats` - Show detailed processing statistics

## 🔍 Troubleshooting
- **"Invalid token"**: Make sure you copied the entire token from the Bot section
- **"Missing permissions"**: Ensure the bot has the required permissions in your server
- **"Commands not showing"**: Wait up to 1 hour for global command sync, or use guild-specific sync

## 📞 Need Help?
If you're still having issues:
1. Check that the bot is added to your server with proper permissions
2. Verify the application ID matches your Discord application
3. Ensure the bot has the "applications.commands" scope when invited 