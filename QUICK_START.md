# Quick Start: Deploy to GitLab Pages

**Target**: https://gitlab.com/embrix-o2x

---

## 🚀 Fastest Way (3 Steps)

### Step 1: Run the Deployment Script

```powershell
# Open PowerShell in this directory
cd c:\Users\quang\IdeaProjects\embrix-o2x

# Run the deployment script
.\deploy-to-gitlab.ps1
```

The script will:
- ✅ Check prerequisites (git, python)
- ✅ Initialize git repository (if needed)
- ✅ Regenerate HTML files
- ✅ Add GitLab remote
- ✅ Commit all files
- ✅ Push to GitLab

### Step 2: Enter Project Name

When prompted, enter your GitLab project name:
- If URL is `https://gitlab.com/embrix-o2x/embrix-o2x` → Enter: `embrix-o2x`
- If URL is `https://gitlab.com/embrix-o2x/documentation` → Enter: `documentation`

### Step 3: Access Your Documentation

After pipeline completes (1-3 minutes):
```
https://embrix-o2x.gitlab.io/<project-name>/
```

---

## 📖 Manual Method (If Script Doesn't Work)

### Option A: Repository Already Exists

```bash
# 1. Clone repository
cd c:\Users\quang\IdeaProjects
git clone https://gitlab.com/embrix-o2x/<project-name>.git
cd <project-name>

# 2. Copy files from embrix-o2x
xcopy /E /I ..\embrix-o2x\docs\newcomer docs\newcomer
copy ..\embrix-o2x\.gitlab-ci.yml .
copy ..\embrix-o2x\convert_to_html.py .
copy ..\embrix-o2x\*.md .

# 3. Commit and push
git add .
git commit -m "Add documentation"
git push origin main
```

### Option B: New Repository

```bash
# 1. Initialize git
cd c:\Users\quang\IdeaProjects\embrix-o2x
git init

# 2. Add remote
git remote add origin https://gitlab.com/embrix-o2x/<project-name>.git

# 3. Add files
git add .gitlab-ci.yml convert_to_html.py docs/ *.md

# 4. Commit
git commit -m "Add documentation"

# 5. Push
git push -u origin main
```

---

## 🔐 Authentication

### Using Personal Access Token

1. Go to: https://gitlab.com/embrix-o2x
2. Click avatar → **Settings** → **Access Tokens**
3. Create token with scopes: `api`, `write_repository`
4. Copy token
5. When pushing, use token as password

### Using SSH (Recommended)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitLab: Settings → SSH Keys

# Change remote to SSH
git remote set-url origin git@gitlab.com:embrix-o2x/<project-name>.git
```

---

## ✅ Verification

### 1. Check Pipeline
Go to: `https://gitlab.com/embrix-o2x/<project-name>/-/pipelines`
- Should show green checkmark ✓

### 2. Check Pages
Go to: `https://gitlab.com/embrix-o2x/<project-name>/-/settings/pages`
- Should show Pages URL

### 3. Access Documentation
Open: `https://embrix-o2x.gitlab.io/<project-name>/`
- Should load the documentation

---

## 🆘 Troubleshooting

### "fatal: not a git repository"
**Solution**: Run `git init` first

### "Authentication failed"
**Solution**: Use Personal Access Token instead of password

### "Repository not found"
**Solution**: Create repository first on GitLab

### "Pipeline failed"
**Solution**: Check pipeline logs in GitLab

### "Pages not accessible"
**Solution**: Wait 5-10 minutes after first deployment

---

## 📞 Need More Help?

See detailed guides:
- **DEPLOYMENT_GUIDE.md** - Complete step-by-step instructions
- **GITLAB_PAGES_SETUP.md** - GitLab Pages configuration details

---

## 🎯 URLs After Deployment

Replace `<project-name>` with your actual project name:

```
Main Index:
https://embrix-o2x.gitlab.io/<project-name>/

Complete Guide:
https://embrix-o2x.gitlab.io/<project-name>/guide-index.html

Multi-Tenant Guide:
https://embrix-o2x.gitlab.io/<project-name>/multi-tenant-complete-guide.html

Quick Reference:
https://embrix-o2x.gitlab.io/<project-name>/quick-reference.html
```

---

**Ready? Run the script now!**

```powershell
.\deploy-to-gitlab.ps1
```
