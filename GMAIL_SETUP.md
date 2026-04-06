# 📧 Gmail SMTP Setup Guide

## Step 1: Enable Gmail App Password

1. **Go to Gmail Security Settings**
   - Visit: https://myaccount.google.com/security
   - Make sure 2-Factor Authentication is enabled first

2. **Generate App Password**
   - Go to "App passwords" section
   - Select "Other (Custom name)"
   - Name it: "Property Tracker Bot"
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

## Step 2: Configure GitHub Secrets

Go to your repository: **Settings** → **Secrets and variables** → **Actions**

Add these **4 secrets**:

```
GMAIL_USER = your-gmail-address@gmail.com
GMAIL_APP_PASSWORD = your-16-character-app-password
FROM_EMAIL = your-gmail-address@gmail.com  (same as GMAIL_USER)
TO_EMAIL = recipient-email@gmail.com       (where you want notifications)
```

### Example:
```
GMAIL_USER = john.doe@gmail.com
GMAIL_APP_PASSWORD = abcd efgh ijkl mnop
FROM_EMAIL = john.doe@gmail.com
TO_EMAIL = john.doe@gmail.com
```

## Step 3: Test the Setup

1. **Manual Test** - Go to **Actions** tab → **Daily Kraimorie Property Tracker** → **Run workflow**

2. **Check for Success**
   - Workflow should complete without errors
   - You should receive an email if new properties are found
   - Check logs for: `✅ Gmail email sent successfully`

## Step 4: Verify Daily Schedule

The tracker runs automatically at **23:57 UTC** daily (1:57 AM Bulgarian time).

## 🔧 Troubleshooting

### "Gmail authentication failed"
- Double-check GMAIL_USER and GMAIL_APP_PASSWORD in GitHub Secrets
- Make sure you're using App Password, not regular Gmail password
- Verify 2FA is enabled on your Gmail account

### "Gmail not configured"
- Check that all 4 secrets are properly set in GitHub
- Secret names are case-sensitive

### No Email Received
- Check spam/junk folder
- Verify TO_EMAIL is correct
- Look for Gmail sending logs in GitHub Actions

## 🔒 Security Notes

- ✅ App passwords are safer than regular passwords
- ✅ GitHub Secrets are encrypted and hidden
- ✅ Only authorized GitHub Actions can access them
- ❌ Never put passwords in code or commit them

## 📧 What You'll Receive

When new properties are found, you'll get a beautiful HTML email with:

- 🏠 **Property images and details**
- 💰 **Prices and locations**
- ⭐ **Special Argosdom property highlights**
- 🔗 **Direct links to view properties**
- 📊 **Daily summary statistics**

---

**Ready to track properties!** 🏠✨