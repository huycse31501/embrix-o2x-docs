# Step-by-Step Deployment to GitLab Pages
## For: https://gitlab.com/embrix-o2x

---

## 🎯 Complete Process (15 minutes)

### STEP 1: Create Repository on GitLab (3 minutes)

#### 1.1 Go to GitLab
Open your browser and navigate to:
```
https://gitlab.com/embrix-o2x
```

#### 1.2 Create New Project
1. Click the **"New project"** button (top right)
2. Choose **"Create blank project"**

#### 1.3 Configure Project
Fill in the form:

- **Project name**: `embrix-documentation` (or `embrix-o2x-docs` or any name you prefer)
- **Project slug**: Will auto-fill (e.g., `embrix-documentation`)
- **Visibility Level**: 
  - Choose **Private** if you want only team members to access
  - Choose **Public** if you want anyone to view the docs
- **Initialize repository with a README**: ❌ **UNCHECK THIS** (we'll add our own files)

Click **"Create project"**

#### 1.4 Copy the Repository URL
After creation, you'll see:
```
git clone https://gitlab.com/embrix-o2x/embrix-documentation.git
```
**Copy this URL** - you'll need it in Step 2.

---

### STEP 2: Initialize Git in Your Project (2 minutes)

```powershell
# Navigate to your project directory
cd c:\Users\quang\IdeaProjects\embrix-o2x

# Initialize git repository
git init

# Add the GitLab remote (use YOUR URL from Step 1.4)
git remote add origin https://gitlab.com/embrix-o2x/embrix-documentation.git

# Verify remote was added
git remote -v
```

You should see:
```
origin  https://gitlab.com/embrix-o2x/embrix-documentation.git (fetch)
origin  https://gitlab.com/embrix-o2x/embrix-documentation.git (push)
```

---

### STEP 3: Regenerate HTML Files (1 minute)

```powershell
# Make sure all HTML files are up to date
python convert_to_html.py
```

You should see:
```
Converting NEWCOMER_GUIDE_INDEX.md to guide-index.html...
[OK] Created docs\newcomer\guide-index.html
...
[SUCCESS] All files converted successfully!
```

---

### STEP 4: Stage Documentation Files (1 minute)

```powershell
# Add all documentation files
git add .gitlab-ci.yml
git add convert_to_html.py
git add GITLAB_PAGES_SETUP.md
git add DEPLOYMENT_GUIDE.md
git add QUICK_START.md
git add STEP_BY_STEP_DEPLOYMENT.md
git add docs/newcomer/
git add NEWCOMER_GUIDE_INDEX.md
git add NEWCOMER_GUIDE_PART1_BUSINESS_AND_ARCHITECTURE.md
git add NEWCOMER_GUIDE_PART2_TECHNICAL_DEEP_DIVE.md
git add NEWCOMER_GUIDE_PART3_SERVICES_AND_DEVELOPMENT.md
git add QUICK_REFERENCE_GUIDE.md

# Check what will be committed
git status
```

---

### STEP 5: Commit Files (1 minute)

```powershell
git commit -m "Add comprehensive HTML documentation with GitLab Pages deployment"
```

---

### STEP 6: Push to GitLab (2 minutes)

```powershell
# Push to main branch
git push -u origin main
```

**If you get an authentication prompt:**

- **Username**: Your GitLab username
- **Password**: Use **Personal Access Token** (NOT your GitLab password)

#### How to Get Personal Access Token:

1. Go to: https://gitlab.com/-/profile/personal_access_tokens
2. Click **"Add new token"**
3. Fill in:
   - **Token name**: `Documentation Deployment`
   - **Expiration date**: 1 year from now
   - **Scopes**: Check these:
     - ✅ `api`
     - ✅ `read_repository`
     - ✅ `write_repository`
4. Click **"Create personal access token"**
5. **COPY THE TOKEN** (you won't see it again!)
6. When git asks for password, **paste this token**

---

### STEP 7: Monitor Pipeline (3 minutes)

#### 7.1 Go to Pipelines
```
https://gitlab.com/embrix-o2x/embrix-documentation/-/pipelines
```

#### 7.2 Watch the Pipeline
- You should see a pipeline running
- Click on it to see details
- Click on the **"pages"** job
- Watch the logs

#### 7.3 Wait for Success
The pipeline will:
1. Start Python container
2. Run `convert_to_html.py`
3. Copy files to `public/` directory
4. Deploy to GitLab Pages

**Status**: Should show ✓ (green checkmark) when done

---

### STEP 8: Access Your Documentation (1 minute)

#### 8.1 Get Your Pages URL

Go to:
```
https://gitlab.com/embrix-o2x/embrix-documentation/-/settings/pages
```

You'll see your Pages URL:
```
https://embrix-o2x.gitlab.io/embrix-documentation/
```

#### 8.2 Open Documentation

Click the URL or paste it in your browser.

You should see the beautiful landing page! 🎉

---

## 🎯 Quick Reference URLs

After deployment, your documentation will be at:

**Main Index:**
```
https://embrix-o2x.gitlab.io/embrix-documentation/
```

**Guide Index (Start Here):**
```
https://embrix-o2x.gitlab.io/embrix-documentation/guide-index.html
```

**Part 1 - Business & Architecture:**
```
https://embrix-o2x.gitlab.io/embrix-documentation/part1-business-architecture.html
```

**Part 2 - Technical Deep Dive:**
```
https://embrix-o2x.gitlab.io/embrix-documentation/part2-technical-deep-dive.html
```

**Part 3 - Services & Development:**
```
https://embrix-o2x.gitlab.io/embrix-documentation/part3-services-development.html
```

**Multi-Tenant Guide (DevOps):**
```
https://embrix-o2x.gitlab.io/embrix-documentation/multi-tenant-complete-guide.html
```

**Quick Reference:**
```
https://embrix-o2x.gitlab.io/embrix-documentation/quick-reference.html
```

---

## ✅ Verification Checklist

After completing all steps:

- [ ] Repository created on GitLab
- [ ] Git initialized locally
- [ ] Remote added (`git remote -v`)
- [ ] HTML files regenerated
- [ ] Files committed
- [ ] Files pushed to GitLab
- [ ] Pipeline running
- [ ] Pipeline succeeded (green ✓)
- [ ] Pages URL accessible
- [ ] Documentation loads correctly
- [ ] Navigation works
- [ ] Styles applied
- [ ] All 7 HTML files accessible

---

## 🚨 Troubleshooting Common Issues

### Issue 1: "Repository not found"

**Cause**: Repository doesn't exist on GitLab yet

**Solution**:
1. Go to https://gitlab.com/embrix-o2x
2. Click "New project"
3. Create the repository
4. Then run the git commands again

### Issue 2: "Authentication failed"

**Cause**: Using GitLab password instead of token

**Solution**:
1. Create Personal Access Token (see Step 6 above)
2. Use token as password when prompted

### Issue 3: "Pipeline not starting"

**Cause**: `.gitlab-ci.yml` not committed

**Solution**:
```powershell
git add .gitlab-ci.yml
git commit -m "Add GitLab CI configuration"
git push origin main
```

### Issue 4: "Pipeline failing"

**Cause**: Missing files or Python errors

**Solution**:
1. Check pipeline logs
2. Verify all markdown files exist
3. Test locally: `python convert_to_html.py`

### Issue 5: "Pages not accessible after 10 minutes"

**Cause**: Pages might be disabled or private

**Solution**:
1. Go to Settings → General → Visibility
2. Check if Pages is enabled
3. Check Pages access control settings

---

## 🔄 Updating Documentation Later

When you need to update:

```powershell
# 1. Edit markdown files
# (e.g., edit NEWCOMER_GUIDE_PART1_BUSINESS_AND_ARCHITECTURE.md)

# 2. Regenerate HTML
python convert_to_html.py

# 3. Commit and push
git add .
git commit -m "Update documentation: describe what changed"
git push origin main

# 4. Wait 1-3 minutes
# 5. Documentation automatically updates!
```

---

## 📱 Share with Team

Once deployed, send this message to your team:

```
📚 Embrix O2X Documentation Now Available!

Our comprehensive product documentation is now online:
https://embrix-o2x.gitlab.io/embrix-documentation/

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
• Technical evaluators assessing the platform

Bookmark it! 🔖
```

---

## 🎉 Success!

If you've completed all steps and can access your documentation at the GitLab Pages URL, you're done! 

**Congratulations!** Your documentation is now:
- ✅ Hosted on GitLab Pages
- ✅ Automatically deployed on every update
- ✅ Accessible to your team
- ✅ Professionally formatted
- ✅ Easy to maintain

---

## 📞 Need Help?

- **GitLab Issues**: Check project's Issues section
- **Pipeline Logs**: CI/CD → Pipelines → Click job → View logs
- **GitLab Support**: https://about.gitlab.com/support/
- **Documentation**: https://docs.gitlab.com/ee/user/project/pages/

**Good luck! 🚀**
