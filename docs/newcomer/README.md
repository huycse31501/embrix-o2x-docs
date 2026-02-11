# Embrix O2X - HTML Documentation

## 📚 Available Documentation

This directory contains the complete Embrix O2X documentation in HTML format with professional styling and easy navigation.

### Files

1. **index.html** - Main landing page with navigation cards to all guides
2. **guide-index.html** - Complete Guide Index (Master Navigation & Reading Paths) ⭐ **START HERE**
3. **part1-business-architecture.html** - Business Overview & System Architecture (~50 pages)
4. **part2-technical-deep-dive.html** - Technical Deep Dive & Component Architecture (~60 pages)
5. **part3-services-development.html** - Core Services, Business Flows & Development Guide (~70 pages)
6. **multi-tenant-complete-guide.html** - Multi-Tenant Architecture Complete Guide (~120 pages) 🏢 **NEW**
7. **quick-reference.html** - Quick Reference Guide (~15 pages)

## 🎯 Documentation Types

### For New Developers
- Start with: **guide-index.html**
- Follow with: Parts 1 → 2 → 3
- Reference: **quick-reference.html**

### For DevOps & Solutions Architects
- Start with: **multi-tenant-complete-guide.html** 🏢
- Then: Part 1 (Architecture section)
- Reference: **quick-reference.html**

### For Business Analysts
- Start with: **guide-index.html**
- Focus on: Part 1 (full)
- Business flows: Part 3, Section 3

### For Technical Evaluators
- Start with: Part 1 (Sections 1, 4, 5, 6)
- Deep dive: Part 2 (full)
- Architecture: **multi-tenant-complete-guide.html**

## 🚀 How to View

### Option 1: Direct Open (Recommended)
Simply double-click `index.html` to open in your default browser.

### Option 2: GitLab Pages (Deployed)
```
https://<namespace>.gitlab.io/<project>/
```
Automatically updated on every push to main/master branch.

### Option 3: Local Web Server
```bash
# Using Python
cd docs/newcomer
python -m http.server 8000
# Open: http://localhost:8000

# Using Node.js
npx http-server

# Using PHP
php -S localhost:8000
```

### Option 4: VS Code Live Server
1. Install "Live Server" extension
2. Right-click on `index.html`
3. Select "Open with Live Server"

## ✨ Features

- **Professional Styling** - Beautiful gradient headers, clean typography
- **Easy Navigation** - Navigation bar on every page linking to all documents
- **Multi-Tenant Guide** - NEW! Comprehensive architecture guide for DevOps
- **Complete Guide Index** - Master document with all reading paths
- **Code Highlighting** - Syntax-highlighted code blocks
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Print-Friendly** - Optimized for printing
- **Search-Friendly** - Full-text search in browser

## 📖 Reading Paths

### New Developer (3-4 hours)
1. `guide-index.html` - Overview (15 min)
2. `part1-business-architecture.html` - Business context (45-60 min)
3. `part2-technical-deep-dive.html` - Technical details (60-90 min)
4. `part3-services-development.html` - Development (90-120 min)
5. `quick-reference.html` - Daily reference

### DevOps Engineer (2-3 hours) 🆕
1. `multi-tenant-complete-guide.html` - Full read (90-120 min)
2. `part1-business-architecture.html` - Section 4 (Architecture)
3. `quick-reference.html` - Infrastructure commands

### Solutions Architect (3-4 hours) 🆕
1. `guide-index.html` - Overview
2. `multi-tenant-complete-guide.html` - Full read
3. `part1-business-architecture.html` - Full read
4. `part2-technical-deep-dive.html` - Sections 1-2

### Business Analyst (2 hours)
1. `guide-index.html` - Overview
2. `part1-business-architecture.html` - Full read
3. `part3-services-development.html` - Section 3 (Flows)

## 🏢 What's New: Multi-Tenant Complete Guide

The **multi-tenant-complete-guide.html** is a comprehensive 120-page guide covering:

### Contents:
- ✅ **Architecture Overview** - Deployment-level multi-tenancy model
- ✅ **Current Tenant Inventory** - All production tenants documented
- ✅ **Infrastructure Components** - Kubernetes, databases, shared services
- ✅ **Tenant Onboarding Process** - Step-by-step procedures
- ✅ **Configuration Management** - Helm values, secrets, environment vars
- ✅ **Feature Customization** - Tenant-specific configurations
- ✅ **Monitoring & Observability** - Metrics, logs, alerts
- ✅ **Troubleshooting** - Common issues and solutions
- ✅ **Best Practices** - Security, performance, maintenance
- ✅ **Appendices** - Checklists, templates, references

### Target Audience:
- DevOps Engineers
- Solutions Architects
- Technical Account Managers
- Platform Engineers
- Site Reliability Engineers

## 🔄 Regenerating HTML

If you update the markdown files:

```bash
cd c:\Users\quang\IdeaProjects\embrix-o2x
python convert_to_html.py
```

This regenerates all HTML files including the new multi-tenant guide.

## 📱 Sharing

Options:
- ✅ GitLab Pages (automatic deployment)
- ✅ Share the `docs/newcomer` folder
- ✅ Host on internal documentation server
- ✅ Compress as ZIP and email
- ✅ Print to PDF from browser (Ctrl+P)

## 📊 Documentation Statistics

- **Total Files**: 7 HTML documents
- **Total Pages**: ~320 pages
- **Code Examples**: 60+
- **Diagrams**: 20+
- **Business Flows**: 3 complete end-to-end
- **Technologies Covered**: 25+
- **Hubs Explained**: 11
- **Services Documented**: 10+
- **Tenants Documented**: 7 production tenants

## 🎨 Customization

To customize styling:
1. Edit `CSS_TEMPLATE` in `convert_to_html.py`
2. Run `python convert_to_html.py`
3. Regenerated HTML will have new styles

## 💡 Tips

- **Multi-Tenant Guide**: Essential for DevOps and deployment
- **Start with Guide Index**: Master navigation document
- Use browser find (Ctrl+F) to search
- Bookmark important sections
- Print individual pages for reference
- View on mobile during commute
- Share specific page URLs with team

## 🆘 Troubleshooting

**Problem**: HTML file doesn't open  
**Solution**: Right-click → Open with → Choose browser

**Problem**: Styles not loading  
**Solution**: All styles are embedded, should work offline

**Problem**: Links don't work  
**Solution**: All files must be in same directory

**Problem**: Multi-tenant guide not showing  
**Solution**: Run `python convert_to_html.py` to regenerate

**Problem**: GitLab Pages not deploying  
**Solution**: Check `.gitlab-ci.yml` and pipeline logs

## 📝 Source Files

This HTML documentation is generated from:
- `NEWCOMER_GUIDE_INDEX.md`
- `NEWCOMER_GUIDE_PART1_BUSINESS_AND_ARCHITECTURE.md`
- `NEWCOMER_GUIDE_PART2_TECHNICAL_DEEP_DIVE.md`
- `NEWCOMER_GUIDE_PART3_SERVICES_AND_DEVELOPMENT.md`
- `QUICK_REFERENCE_GUIDE.md`
- `docs/MULTI_TENANT_COMPLETE_GUIDE.md` 🆕

## 🔐 GitLab Pages Deployment

Automatic deployment configured via `.gitlab-ci.yml`:
- Triggers on push to main/master
- Converts markdown to HTML
- Deploys to GitLab Pages
- URL: `https://<namespace>.gitlab.io/<project>/`

See `GITLAB_PAGES_SETUP.md` for detailed setup instructions.

## 📞 Getting Help

- **Pipeline Issues**: Check CI/CD → Pipelines in GitLab
- **Access Issues**: Check Settings → Pages in GitLab
- **Content Updates**: Edit markdown files and push
- **Technical Issues**: Contact development team

---

**Welcome to Embrix O2X! Happy Learning! 🎉**

**Latest Addition**: Multi-Tenant Architecture Complete Guide for DevOps teams! 🏢

**Last Updated**: February 2026 • Version 3.1.9-SNAPSHOT
