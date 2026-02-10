# Deploy to GitHub - Quick Start

## 🎯 3 Steps to Deploy (5 minutes)

### Step 1: Create Repository on GitHub (2 minutes)

**Open this link**: https://github.com/new

Fill in:
- **Repository name**: `embrix-o2x-docs`
- **Description**: "Embrix O2X comprehensive documentation"
- **Visibility**: Choose **Public** (so anyone can view)
- **❌ UNCHECK ALL** the initialize options (no README, no .gitignore, no license)

Click **"Create repository"**

---

### Step 2: Get Personal Access Token (2 minutes)

**Open this link**: https://github.com/settings/tokens/new

Fill in:
- **Note**: `Embrix Docs Deployment`
- **Expiration**: `90 days`
- **Scopes**: Check ✅ **`repo`** (Full control of private repositories)

Click **"Generate token"**

**COPY THE TOKEN** (looks like: `ghp_xxxxxxxxxxxx...`)

---

### Step 3: Deploy! (1 minute)

Open PowerShell in your project folder and run:

```powershell
.\deploy-to-github.ps1
```

When prompted:
- **Username**: `huycse31501`
- **Password**: Paste your token from Step 2

---

## 🎉 That's It!

After deployment:

1. **Enable GitHub Pages**:
   - Go to: https://github.com/huycse31501/embrix-o2x-docs/settings/pages
   - Under "Build and deployment" → Source: Select **"GitHub Actions"**
   - Click Save

2. **Monitor deployment** (2-3 minutes):
   - Go to: https://github.com/huycse31501/embrix-o2x-docs/actions
   - Wait for green checkmark ✓

3. **View your docs**:
   - https://huycse31501.github.io/embrix-o2x-docs/

---

## 🚨 Troubleshooting

**"Repository not found"**
→ Make sure you created the repository in Step 1

**"Authentication failed"**
→ Use your Personal Access Token (from Step 2), NOT your GitHub password

**"Permission denied"**
→ Make sure your token has `repo` scope checked

---

## 🔄 Updating Later

Just edit your markdown files and run:

```powershell
.\deploy-to-github.ps1
```

It will automatically update your live documentation!

---

**Need detailed help?** Check `GITHUB_PAGES_SETUP.md`
