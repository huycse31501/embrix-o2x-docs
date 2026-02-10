# GitLab Pages Setup Guide - Embrix O2X Documentation

## 🌐 What is GitLab Pages?

GitLab Pages allows you to host static websites directly from your GitLab repository. Your documentation will be accessible at:

```
https://<namespace>.gitlab.io/<project-name>/
```

For example:
- If namespace is `embrix` and project is `embrix-o2x`
- URL will be: `https://embrix.gitlab.io/embrix-o2x/`

## 📋 Prerequisites

- [x] GitLab repository for embrix-o2x project
- [x] Access to repository settings (Maintainer or Owner role)
- [x] Documentation files committed to repository

## 🚀 Quick Setup (3 Steps)

### Step 1: Commit Documentation Files

```bash
# Make sure you're in the project root
cd c:\Users\quang\IdeaProjects\embrix-o2x

# Add all documentation files
git add .gitlab-ci.yml
git add convert_to_html.py
git add docs/newcomer/
git add NEWCOMER_GUIDE_*.md
git add QUICK_REFERENCE_GUIDE.md
git add NEWCOMER_GUIDE_INDEX.md

# Commit
git commit -m "Add HTML documentation and GitLab Pages configuration"

# Push to GitLab
git push origin main
```

### Step 2: Enable GitLab Pages

1. Go to your GitLab project
2. Navigate to **Settings** → **Pages**
3. GitLab Pages should automatically be enabled after the first pipeline runs
4. Wait for the pipeline to complete (check **CI/CD** → **Pipelines**)

### Step 3: Access Your Documentation

Once the pipeline succeeds:

1. Go to **Settings** → **Pages**
2. Copy your Pages URL (e.g., `https://embrix.gitlab.io/embrix-o2x/`)
3. Open the URL in your browser
4. Share with your team! 🎉

## 📁 Repository Structure

```
embrix-o2x/
├── .gitlab-ci.yml                              # GitLab CI/CD configuration
├── convert_to_html.py                          # Python converter script
├── docs/
│   └── newcomer/                               # Generated HTML files
│       ├── index.html
│       ├── guide-index.html
│       ├── part1-business-architecture.html
│       ├── part2-technical-deep-dive.html
│       ├── part3-services-development.html
│       └── quick-reference.html
├── NEWCOMER_GUIDE_INDEX.md                     # Source markdown files
├── NEWCOMER_GUIDE_PART1_*.md
├── NEWCOMER_GUIDE_PART2_*.md
├── NEWCOMER_GUIDE_PART3_*.md
└── QUICK_REFERENCE_GUIDE.md
```

## 🔄 How It Works

### Automatic Deployment

The `.gitlab-ci.yml` file is configured to:

1. **Trigger**: On every push to `main` or `master` branch
2. **Convert**: Run `python convert_to_html.py` to generate HTML from markdown
3. **Deploy**: Copy HTML files to `public/` directory
4. **Publish**: GitLab automatically serves content from `public/`

### Pipeline Process

```
Push to main/master
    ↓
GitLab CI/CD Triggered
    ↓
Python Script Runs
    ↓
Markdown → HTML Conversion
    ↓
Files Copied to public/
    ↓
GitLab Pages Deployed
    ↓
Documentation Live! 🎉
```

## 🎯 GitLab Pages URL Structure

Your documentation will be accessible at these URLs:

```
Main Landing Page:
https://<namespace>.gitlab.io/<project>/

Complete Guide Index:
https://<namespace>.gitlab.io/<project>/guide-index.html

Part 1:
https://<namespace>.gitlab.io/<project>/part1-business-architecture.html

Part 2:
https://<namespace>.gitlab.io/<project>/part2-technical-deep-dive.html

Part 3:
https://<namespace>.gitlab.io/<project>/part3-services-development.html

Quick Reference:
https://<namespace>.gitlab.io/<project>/quick-reference.html
```

## 🔧 Configuration Options

### Option 1: Deploy Only on Documentation Changes

Edit `.gitlab-ci.yml`:

```yaml
pages:
  only:
    changes:
      - docs/**/*
      - "*.md"
      - convert_to_html.py
```

This will only trigger deployment when documentation files change.

### Option 2: Manual Deployment

Edit `.gitlab-ci.yml`:

```yaml
pages:
  when: manual  # Add this line
```

This requires manual approval to deploy.

### Option 3: Custom Domain

If you want a custom domain (e.g., `docs.embrix.com`):

1. Go to **Settings** → **Pages**
2. Click **New Domain**
3. Add your domain and configure DNS
4. GitLab will provide DNS records to configure

## 📊 Monitoring Deployment

### Check Pipeline Status

1. Go to **CI/CD** → **Pipelines**
2. Click on the latest pipeline
3. View the `pages` job
4. Check logs for any errors

### View Deployment History

1. Go to **Deployments** → **Environments**
2. See all Pages deployments
3. Rollback if needed

## 🔐 Access Control

### Public Access (Default)

Documentation is publicly accessible to anyone with the URL.

### Private Access

If your GitLab project is private, Pages will be:
- ✅ Accessible to project members
- ❌ Not accessible to public

To make Pages public while keeping repo private:
1. Go to **Settings** → **General**
2. Expand **Visibility, project features, permissions**
3. Enable **Pages** under project features
4. Set Pages access level

## 🚨 Troubleshooting

### Issue: Pipeline Fails

**Check:**
- Python 3.9 is available
- `convert_to_html.py` script has no errors
- All markdown files exist

**Solution:**
```bash
# Test locally first
python convert_to_html.py
```

### Issue: Pages Not Accessible

**Check:**
- Pipeline completed successfully
- `public/` directory was created
- Files are in `public/` (check pipeline artifacts)

**Solution:**
- Wait 5-10 minutes after first deployment
- Check **Settings** → **Pages** for status

### Issue: 404 Error

**Check:**
- `index.html` exists in `public/` directory
- File paths are correct in HTML

**Solution:**
```bash
# Verify files in pipeline artifacts
# Go to pipeline → pages job → Browse artifacts
```

### Issue: Styles Not Loading

**Check:**
- CSS is embedded in HTML (not external files)
- HTML files are in same directory

**Solution:**
- All styles are embedded, so this shouldn't happen
- Check browser console for errors

## 📱 Sharing Documentation

### Internal Team

Share the GitLab Pages URL:
```
https://embrix.gitlab.io/embrix-o2x/
```

### External Partners

Options:
1. Make Pages public (if allowed)
2. Export as ZIP and email
3. Print to PDF and share
4. Set up temporary access

### Mobile Access

The documentation is responsive and works perfectly on:
- 📱 Mobile phones
- 📱 Tablets
- 💻 Desktops
- 🖨️ Print

## 🔄 Updating Documentation

### Update Process

```bash
# 1. Edit markdown files
vim NEWCOMER_GUIDE_PART1_BUSINESS_AND_ARCHITECTURE.md

# 2. (Optional) Test locally
python convert_to_html.py
# Open docs/newcomer/index.html in browser

# 3. Commit and push
git add .
git commit -m "Update documentation: [description]"
git push origin main

# 4. Wait for pipeline to complete
# 5. Changes are live!
```

### Automatic Updates

Every push to `main`/`master` automatically:
- ✅ Converts markdown to HTML
- ✅ Deploys to GitLab Pages
- ✅ Updates live documentation

## 📈 Analytics (Optional)

### Add Google Analytics

Edit `convert_to_html.py` and add to `CSS_TEMPLATE`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🎯 Best Practices

1. **Keep Markdown Updated** - Edit markdown, not HTML directly
2. **Test Locally First** - Run converter before committing
3. **Descriptive Commits** - Clear commit messages for documentation changes
4. **Review Before Merge** - Use merge requests for major updates
5. **Monitor Pipelines** - Ensure deployments succeed

## 📞 Getting Help

### GitLab Support

- **Documentation**: https://docs.gitlab.com/ee/user/project/pages/
- **Forum**: https://forum.gitlab.com/
- **Support**: Help → Support (in GitLab)

### Team Resources

- Pipeline logs: **CI/CD** → **Pipelines** → Select pipeline → `pages` job
- Artifacts: Pipeline → `pages` job → **Browse**
- Settings: **Settings** → **Pages**

## ✅ Verification Checklist

Before considering setup complete:

- [ ] `.gitlab-ci.yml` committed to repository
- [ ] `convert_to_html.py` committed
- [ ] All markdown files committed
- [ ] HTML files generated in `docs/newcomer/`
- [ ] Pipeline ran successfully
- [ ] GitLab Pages enabled in settings
- [ ] Documentation accessible via URL
- [ ] All navigation links work
- [ ] Styles load correctly
- [ ] Mobile responsive
- [ ] Team can access

## 🎉 Success!

Once setup is complete, your team can access the documentation at:

**Main URL**: `https://<namespace>.gitlab.io/<project>/`

Share this URL with:
- ✅ New developers for onboarding
- ✅ Business analysts for product understanding
- ✅ Technical evaluators for architecture review
- ✅ QA engineers for test scenarios
- ✅ Project managers for scope understanding

---

**Last Updated**: February 2026  
**Maintained By**: Development Team  
**Version**: 3.1.9-SNAPSHOT

**Questions?** Contact the development team or check GitLab Pages documentation.
