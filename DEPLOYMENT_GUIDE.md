# Deploy Documentation to GitLab Pages
## https://gitlab.com/embrix-o2x

This guide will help you deploy the Embrix O2X HTML documentation to GitLab Pages.

---

## 📋 Prerequisites Checklist

- [x] HTML documentation files generated in `docs/newcomer/`
- [x] `.gitlab-ci.yml` file created
- [x] `convert_to_html.py` script ready
- [ ] GitLab repository exists
- [ ] Git configured locally
- [ ] GitLab authentication set up

---

## 🎯 Option 1: If GitLab Repository Already Exists

### Step 1A: Clone the Repository

```bash
# Navigate to your projects directory
cd c:\Users\quang\IdeaProjects

# Clone the repository (replace <project-name> with actual project name)
git clone https://gitlab.com/embrix-o2x/<project-name>.git

# Example:
# git clone https://gitlab.com/embrix-o2x/embrix-o2x.git
```

### Step 1B: Copy Documentation Files

```bash
# Copy all your documentation files to the cloned repository
cd c:\Users\quang\IdeaProjects\<project-name>

# Copy the files
xcopy /E /I c:\Users\quang\IdeaProjects\embrix-o2x\docs\newcomer docs\newcomer
copy c:\Users\quang\IdeaProjects\embrix-o2x\.gitlab-ci.yml .
copy c:\Users\quang\IdeaProjects\embrix-o2x\convert_to_html.py .
copy c:\Users\quang\IdeaProjects\embrix-o2x\NEWCOMER_GUIDE_*.md .
copy c:\Users\quang\IdeaProjects\embrix-o2x\QUICK_REFERENCE_GUIDE.md .
copy c:\Users\quang\IdeaProjects\embrix-o2x\GITLAB_PAGES_SETUP.md .
```

### Step 1C: Commit and Push

```bash
# Add all files
git add .

# Commit with descriptive message
git commit -m "Add comprehensive HTML documentation with GitLab Pages deployment

- Added newcomer guides (Parts 1-3) in HTML format
- Added multi-tenant architecture complete guide
- Added quick reference guide
- Added complete guide index with reading paths
- Configured GitLab CI/CD for automatic deployment
- Included Python converter script for markdown to HTML
- Added setup documentation and troubleshooting"

# Push to GitLab
git push origin main
# Or if your default branch is master:
# git push origin master
```

---

## 🎯 Option 2: If This IS Your GitLab Repository

### Step 2A: Initialize Git Repository

```bash
# Navigate to your project
cd c:\Users\quang\IdeaProjects\embrix-o2x

# Initialize git repository
git init

# Add GitLab remote (replace <project-name> with actual project name)
git remote add origin https://gitlab.com/embrix-o2x/<project-name>.git

# Verify remote was added
git remote -v
```

### Step 2B: Create .gitignore File

```bash
# Create .gitignore to exclude unnecessary files
# This file should already exist, but if not:
```

Create `.gitignore` with this content:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# IDE
.idea/
*.iml
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Build artifacts
target/
*.class
*.jar
*.war
*.ear

# Logs
*.log

# Temp files
*.tmp
*.bak
*.backup

# Don't ignore docs
!docs/
```

### Step 2C: Add and Commit All Files

```bash
# Check what will be committed
git status

# Add all documentation files
git add .gitlab-ci.yml
git add convert_to_html.py
git add GITLAB_PAGES_SETUP.md
git add DEPLOYMENT_GUIDE.md
git add docs/
git add NEWCOMER_GUIDE_*.md
git add QUICK_REFERENCE_GUIDE.md
git add NEWCOMER_GUIDE_INDEX.md

# If you want to commit everything (be careful!):
# git add .

# Commit
git commit -m "Initial commit: Add comprehensive documentation with GitLab Pages

- Complete newcomer guides (3 parts)
- Multi-tenant architecture guide
- Quick reference guide
- GitLab Pages CI/CD configuration
- Python HTML converter
- Setup and deployment documentation"

# Push to GitLab (first time)
git push -u origin main
# Or for master branch:
# git push -u origin master
```

---

## 🔐 GitLab Authentication

### If you need to authenticate:

**Option A: HTTPS with Personal Access Token**

1. Go to GitLab: https://gitlab.com/embrix-o2x
2. Click your avatar → **Settings** → **Access Tokens**
3. Create token with scopes: `api`, `read_repository`, `write_repository`
4. Copy the token
5. When prompted for password during `git push`, use the token

**Option B: SSH Key**

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy the public key
cat ~/.ssh/id_ed25519.pub

# Add to GitLab:
# 1. Go to GitLab → Settings → SSH Keys
# 2. Paste the public key
# 3. Click "Add key"

# Change remote to SSH
git remote set-url origin git@gitlab.com:embrix-o2x/<project-name>.git
```

---

## 🚀 After Pushing to GitLab

### Step 3: Monitor Pipeline

1. **Go to your GitLab project**: https://gitlab.com/embrix-o2x/<project-name>

2. **Navigate to CI/CD → Pipelines**
   - You should see a pipeline running
   - Click on the pipeline to see details

3. **Check the `pages` job**
   - Click on the `pages` job in the pipeline
   - View the logs to ensure conversion succeeded
   - Look for: `[SUCCESS] All files converted successfully!`

4. **Wait for completion**
   - Pipeline should take 1-3 minutes
   - Status will show ✓ (passed) or ✗ (failed)

### Step 4: Access Your Documentation

1. **Get your Pages URL**:
   - Go to **Settings → Pages**
   - Your URL will be displayed there

2. **Your documentation will be at**:
   ```
   https://embrix-o2x.gitlab.io/<project-name>/
   ```

   **For example**:
   - If project name is `embrix-o2x`: https://embrix-o2x.gitlab.io/embrix-o2x/
   - If project name is `documentation`: https://embrix-o2x.gitlab.io/documentation/

3. **Direct links to guides**:
   ```
   Main Index:
   https://embrix-o2x.gitlab.io/<project-name>/

   Complete Guide Index:
   https://embrix-o2x.gitlab.io/<project-name>/guide-index.html

   Part 1:
   https://embrix-o2x.gitlab.io/<project-name>/part1-business-architecture.html

   Part 2:
   https://embrix-o2x.gitlab.io/<project-name>/part2-technical-deep-dive.html

   Part 3:
   https://embrix-o2x.gitlab.io/<project-name>/part3-services-development.html

   Multi-Tenant Guide:
   https://embrix-o2x.gitlab.io/<project-name>/multi-tenant-complete-guide.html

   Quick Reference:
   https://embrix-o2x.gitlab.io/<project-name>/quick-reference.html
   ```

---

## ✅ Verification Steps

### After deployment, verify:

```bash
# 1. Check pipeline status
# Go to: https://gitlab.com/embrix-o2x/<project-name>/-/pipelines

# 2. Check Pages settings
# Go to: https://gitlab.com/embrix-o2x/<project-name>/-/settings/pages

# 3. Access documentation
# Open: https://embrix-o2x.gitlab.io/<project-name>/

# 4. Test navigation
# Click through all the links on the index page
# Verify all pages load correctly
# Check that styles are applied
```

### Checklist:

- [ ] Pipeline ran successfully (green checkmark)
- [ ] Pages URL is accessible
- [ ] Index page loads correctly
- [ ] All navigation links work
- [ ] Styles are applied correctly
- [ ] All 7 HTML files are accessible
- [ ] Mobile view works (test on phone)

---

## 🔄 Updating Documentation

When you update the markdown files:

```bash
# 1. Edit your markdown files
# Example: NEWCOMER_GUIDE_PART1_BUSINESS_AND_ARCHITECTURE.md

# 2. (Optional) Test locally
python convert_to_html.py
# Open docs/newcomer/index.html in browser to verify

# 3. Commit changes
git add .
git commit -m "Update documentation: [describe what changed]"

# 4. Push to GitLab
git push origin main

# 5. Wait for automatic deployment (1-3 minutes)
# Documentation will automatically update!
```

---

## 🎯 Project Name Discovery

If you're not sure what your project name is:

**Method 1: Check GitLab Web Interface**
1. Go to https://gitlab.com/embrix-o2x
2. Look at the list of projects
3. The project name will be in the URL: `https://gitlab.com/embrix-o2x/<PROJECT-NAME>`

**Method 2: If you have GitLab CLI**
```bash
# List all projects in embrix-o2x group
glab repo list
```

**Method 3: Check with Git**
```bash
# If already cloned
git remote -v
# Will show: origin  https://gitlab.com/embrix-o2x/<PROJECT-NAME>.git
```

---

## 🚨 Troubleshooting

### Issue: "Repository not found"

**Solution**:
1. Verify repository exists at https://gitlab.com/embrix-o2x/<project-name>
2. Check you have access (you should see the project when logged in)
3. Verify the remote URL: `git remote -v`

### Issue: "Authentication failed"

**Solution**:
1. Use Personal Access Token instead of password
2. Or set up SSH keys (see authentication section above)

### Issue: "Pipeline failed"

**Solution**:
1. Check pipeline logs: CI/CD → Pipelines → Click failed pipeline
2. Common issues:
   - Missing `convert_to_html.py` file
   - Missing markdown source files
   - Python syntax errors

**Fix**: Ensure all files are committed and pushed

### Issue: "Pages not accessible"

**Solution**:
1. Wait 5-10 minutes after first deployment
2. Check Settings → Pages to ensure Pages is enabled
3. Verify pipeline succeeded (green checkmark)
4. Check if project is private (Pages may be private too)

### Issue: "Styles not loading"

**Solution**:
- All styles are embedded in HTML, so this shouldn't happen
- Clear browser cache (Ctrl+F5)
- Check browser console for errors (F12)

---

## 📞 Need Help?

### Resources:

- **GitLab Pages Docs**: https://docs.gitlab.com/ee/user/project/pages/
- **This Project's Setup Guide**: `GITLAB_PAGES_SETUP.md`
- **GitLab Support**: https://about.gitlab.com/support/

### Common Commands Reference:

```bash
# Check status
git status

# Check remotes
git remote -v

# Check current branch
git branch

# Pull latest changes
git pull origin main

# Push changes
git push origin main

# View commit history
git log --oneline

# See what changed
git diff
```

---

## 🎉 Success Indicators

When everything is working:

✅ Pipeline shows green checkmark  
✅ Pages URL is accessible  
✅ All 7 HTML documents load  
✅ Navigation between pages works  
✅ Styles render correctly  
✅ Mobile responsive  
✅ Can share URL with team  

**Your documentation is now live!** 🚀

---

## 📱 Sharing with Team

Once deployed, share these links:

**For Everyone**:
```
Main Documentation: https://embrix-o2x.gitlab.io/<project-name>/
```

**For New Developers**:
```
Start here: https://embrix-o2x.gitlab.io/<project-name>/guide-index.html
```

**For DevOps/Architects**:
```
Multi-Tenant Guide: https://embrix-o2x.gitlab.io/<project-name>/multi-tenant-complete-guide.html
```

**For Quick Reference**:
```
Cheat Sheet: https://embrix-o2x.gitlab.io/<project-name>/quick-reference.html
```

---

**Good luck with your deployment! 🎊**

If you encounter any issues, check the troubleshooting section or refer to `GITLAB_PAGES_SETUP.md`.
