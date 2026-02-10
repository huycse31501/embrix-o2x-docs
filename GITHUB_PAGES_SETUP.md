# GitHub Pages Setup Guide

Complete guide for deploying Embrix O2X documentation to GitHub Pages.

---

## 🎯 Quick Start (5 minutes)

### Prerequisites
- Git installed
- Python 3.9+ installed
- GitHub account (you have: `huycse31501`)
- GitHub Personal Access Token

### Option 1: Automated Deployment (Recommended)

```powershell
# Just run this:
.\deploy-to-github.ps1
```

When prompted for password, use your **Personal Access Token** (not GitHub password).

### Option 2: Manual Deployment

```powershell
# 1. Create repository on GitHub
# Go to: https://github.com/new
# Repository name: embrix-o2x-docs
# Public or Private (your choice)
# Don't initialize with README

# 2. Generate HTML files
python convert_to_html.py

# 3. Add and commit files
git add .github/ convert_to_html.py docs/ NEWCOMER_GUIDE*.md QUICK_REFERENCE_GUIDE.md
git commit -m "Deploy documentation to GitHub Pages"

# 4. Push to GitHub
git push -u origin master
```

---

## 📋 Step-by-Step Setup

### Step 1: Create GitHub Repository (2 minutes)

1. Go to: https://github.com/new

2. Fill in:
   - **Repository name**: `embrix-o2x-docs`
   - **Description**: "Comprehensive documentation for Embrix O2X platform"
   - **Visibility**: 
     - Choose **Private** if only for your team
     - Choose **Public** if anyone can view
   - **❌ UNCHECK** "Add a README file"
   - **❌ UNCHECK** "Add .gitignore"
   - **❌ UNCHECK** "Choose a license"

3. Click **"Create repository"**

### Step 2: Get Personal Access Token (3 minutes)

1. Go to: https://github.com/settings/tokens/new

2. Fill in:
   - **Note**: `Embrix O2X Documentation Deployment`
   - **Expiration**: 90 days (or custom)
   - **Select scopes**:
     - ✅ `repo` (Full control of private repositories)

3. Click **"Generate token"**

4. **COPY THE TOKEN** - you won't see it again!
   - Format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 3: Enable GitHub Pages (1 minute)

1. Go to repository settings:
   ```
   https://github.com/huycse31501/embrix-o2x-docs/settings/pages
   ```

2. Under **"Build and deployment"**:
   - **Source**: Select `GitHub Actions`

3. Click **"Save"**

### Step 4: Deploy Documentation (2 minutes)

```powershell
# Run the deployment script
.\deploy-to-github.ps1
```

**When prompted for credentials:**
- **Username**: `huycse31501`
- **Password**: Paste your Personal Access Token

### Step 5: Verify Deployment (2 minutes)

1. **Check Actions (Workflow):**
   ```
   https://github.com/huycse31501/embrix-o2x-docs/actions
   ```
   - You should see "Deploy Documentation" workflow running
   - Wait for green checkmark ✓

2. **Access Documentation:**
   ```
   https://huycse31501.github.io/embrix-o2x-docs/
   ```

---

## 🌐 Your Documentation URLs

After deployment, your documentation will be available at:

### Main Landing Page
```
https://huycse31501.github.io/embrix-o2x-docs/
```

### Individual Guides

**Guide Index (Start Here):**
```
https://huycse31501.github.io/embrix-o2x-docs/guide-index.html
```

**Part 1 - Business & Architecture:**
```
https://huycse31501.github.io/embrix-o2x-docs/part1-business-architecture.html
```

**Part 2 - Technical Deep Dive:**
```
https://huycse31501.github.io/embrix-o2x-docs/part2-technical-deep-dive.html
```

**Part 3 - Services & Development:**
```
https://huycse31501.github.io/embrix-o2x-docs/part3-services-development.html
```

**Multi-Tenant Guide:**
```
https://huycse31501.github.io/embrix-o2x-docs/multi-tenant-complete-guide.html
```

**Quick Reference:**
```
https://huycse31501.github.io/embrix-o2x-docs/quick-reference.html
```

---

## 🔄 Updating Documentation

When you need to update the documentation:

```powershell
# 1. Edit markdown files
# (e.g., edit NEWCOMER_GUIDE_PART1_BUSINESS_AND_ARCHITECTURE.md)

# 2. Run deployment script
.\deploy-to-github.ps1

# 3. Wait 2-3 minutes
# 4. Documentation automatically updates!
```

The GitHub Actions workflow will:
1. Detect your push
2. Regenerate HTML files
3. Deploy to GitHub Pages
4. Update live site

---

## 🚨 Troubleshooting

### Issue 1: "Repository not found"

**Problem**: Repository doesn't exist on GitHub

**Solution**:
1. Go to https://github.com/new
2. Create repository named `embrix-o2x-docs`
3. Run `.\deploy-to-github.ps1` again

### Issue 2: "Authentication failed"

**Problem**: Using GitHub password instead of Personal Access Token

**Solution**:
1. Create token at: https://github.com/settings/tokens/new
2. Give it `repo` scope
3. Use token as password when prompted

### Issue 3: "GitHub Actions workflow not running"

**Problem**: GitHub Pages not configured or workflow file missing

**Solution**:
1. Check workflow file exists: `.github/workflows/deploy-docs.yml`
2. Go to Settings → Pages → Source → Select "GitHub Actions"
3. Push changes again

### Issue 4: "404 Page Not Found"

**Problem**: GitHub Pages not enabled or site not deployed yet

**Solution**:
1. Go to: https://github.com/huycse31501/embrix-o2x-docs/settings/pages
2. Check if Pages is enabled
3. Wait 2-3 minutes after workflow completes
4. Check Actions tab for deployment status

### Issue 5: "Permission denied"

**Problem**: Token doesn't have correct permissions

**Solution**:
1. Create new token with `repo` scope
2. Delete old remote: `git remote remove origin`
3. Add new remote: `git remote add origin https://github.com/huycse31501/embrix-o2x-docs.git`
4. Try pushing again with new token

---

## 🔒 Security Best Practices

### Store Token Securely

**❌ DO NOT:**
- Commit tokens to git
- Share tokens with others
- Store tokens in plain text files in repository

**✅ DO:**
- Use Git Credential Manager (Windows handles this automatically)
- Rotate tokens every 90 days
- Use minimum required permissions

### Using Git Credential Manager

Windows automatically stores your credentials securely:

```powershell
# First time - you'll be prompted for token
git push -u origin master

# Windows will remember it in Credential Manager
# No need to enter again!
```

To clear stored credentials:
```powershell
# Open Credential Manager
# Windows Key → Search "Credential Manager"
# Remove "git:https://github.com"
```

---

## ⚙️ GitHub Actions Workflow

The `.github/workflows/deploy-docs.yml` file automates deployment:

```yaml
# What it does:
1. Triggers on push to main/master branch
2. Sets up Python environment
3. Runs convert_to_html.py
4. Uploads generated HTML to GitHub Pages
5. Deploys to live site

# You can monitor it at:
https://github.com/huycse31501/embrix-o2x-docs/actions
```

---

## 📱 Share with Team

Once deployed, share with your team:

```
📚 Embrix O2X Documentation is Live!

Our comprehensive documentation is now available:
https://huycse31501.github.io/embrix-o2x-docs/

What's included:
✓ Complete newcomer's guide (3 parts)
✓ Multi-tenant architecture guide
✓ Quick reference cheat sheet
✓ Business flows and use cases
✓ Development setup instructions

Perfect for:
• New developers joining the team
• DevOps engineers managing deployments
• Business analysts understanding the product
• Technical evaluators

Bookmark it! 🔖
```

---

## 🎨 Customization

### Custom Domain (Optional)

Want to use your own domain instead of `github.io`?

1. Add a file named `CNAME` to `docs/newcomer/`:
   ```
   docs.embrix-o2x.com
   ```

2. Configure DNS:
   - Add CNAME record pointing to: `huycse31501.github.io`

3. Go to Settings → Pages → Custom domain
4. Enter your domain and save

### Update Styles

Edit the CSS in `convert_to_html.py`:

```python
# Find the CSS_TEMPLATE section
# Modify colors, fonts, layouts
# Run: python convert_to_html.py
# Commit and push
```

---

## 📊 Monitoring

### View Page Analytics

GitHub doesn't provide built-in analytics, but you can add:

1. **Google Analytics**: Add tracking code to `convert_to_html.py`
2. **GitHub Traffic**: Check Insights → Traffic (last 14 days)

### Check Deployment Status

```powershell
# View recent workflows
gh workflow list

# View workflow runs
gh run list

# View specific run logs
gh run view <run-id>
```

Or visit: https://github.com/huycse31501/embrix-o2x-docs/actions

---

## 🆚 GitHub Pages vs GitLab Pages

| Feature | GitHub Pages | GitLab Pages |
|---------|-------------|--------------|
| Setup | Simple (Actions workflow) | Requires `.gitlab-ci.yml` |
| Build Time | 2-3 minutes | 1-3 minutes |
| URL Format | `username.github.io/repo` | `group.gitlab.io/repo` |
| Private Repos | ✓ (with Pro) | ✓ (Free) |
| Custom Domains | ✓ Free | ✓ Free |
| Analytics | External only | External only |

---

## ✅ Success Checklist

After deployment, verify:

- [ ] Repository created on GitHub
- [ ] Personal Access Token created and saved
- [ ] Documentation files committed
- [ ] Files pushed to GitHub successfully
- [ ] GitHub Actions workflow triggered
- [ ] Workflow completed successfully (green ✓)
- [ ] GitHub Pages enabled in settings
- [ ] Main page loads: `https://huycse31501.github.io/embrix-o2x-docs/`
- [ ] All navigation links work
- [ ] All 7 HTML pages accessible
- [ ] Styles applied correctly
- [ ] Mobile responsive design works

---

## 📞 Support Resources

- **GitHub Pages Docs**: https://docs.github.com/en/pages
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **GitHub Community**: https://github.community/
- **Status Page**: https://www.githubstatus.com/

---

## 🎉 You're All Set!

Your documentation is now:
- ✅ Hosted on GitHub Pages
- ✅ Automatically deployed via GitHub Actions
- ✅ Accessible to anyone with the link
- ✅ Professionally formatted with navigation
- ✅ Easy to update (just push changes)

**Next time you update**: Just run `.\deploy-to-github.ps1` and you're done!

Good luck! 🚀
