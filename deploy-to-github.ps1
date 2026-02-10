#!/usr/bin/env pwsh
#
# GitHub Pages Deployment Script for Embrix O2X Documentation
# This script automates the deployment process to GitHub Pages
#

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================"
Write-Host "Embrix O2X Documentation Deployment"
Write-Host "Target: GitHub Pages"
Write-Host "========================================"
Write-Host ""

# Step 1: Check prerequisites
Write-Host "Step 1: Checking prerequisites..."
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "[OK] Git found: $gitVersion"
} catch {
    Write-Host "[ERROR] Git is not installed or not in PATH"
    Write-Host "Please install Git from: https://git-scm.com/download/win"
    exit 1
}

# Check if python is installed
try {
    $pythonVersion = python --version
    Write-Host "[OK] Python found: $pythonVersion"
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH"
    Write-Host "Please install Python from: https://www.python.org/downloads/"
    exit 1
}

Write-Host ""

# Step 2: Verify git repository
Write-Host "Step 2: Verifying git repository..."
Write-Host ""

if (-not (Test-Path ".git")) {
    Write-Host "[ERROR] Not a git repository"
    Write-Host "Initializing git repository..."
    git init
    Write-Host "[OK] Git repository initialized"
}

# Check current remote
$currentRemote = git remote get-url origin 2>$null
if ($currentRemote) {
    Write-Host "[OK] Git remote configured: $currentRemote"
} else {
    Write-Host "[ERROR] No git remote configured"
    Write-Host "Setting up GitHub remote..."
    git remote add origin https://github.com/huycse31501/embrix-o2x-docs.git
    Write-Host "[OK] Remote added"
}

Write-Host ""

# Step 3: Regenerate HTML files
Write-Host "Step 3: Regenerating HTML documentation..."
Write-Host ""

try {
    python convert_to_html.py
    Write-Host ""
    Write-Host "[OK] HTML files generated successfully"
} catch {
    Write-Host "[ERROR] Failed to generate HTML files"
    Write-Host "Error: $_"
    exit 1
}

Write-Host ""

# Step 4: Stage documentation files
Write-Host "Step 4: Staging documentation files..."
Write-Host ""

$filesToAdd = @(
    ".github/workflows/deploy-docs.yml",
    "convert_to_html.py",
    "NEWCOMER_GUIDE_INDEX.md",
    "NEWCOMER_GUIDE_PART1_BUSINESS_AND_ARCHITECTURE.md",
    "NEWCOMER_GUIDE_PART2_TECHNICAL_DEEP_DIVE.md",
    "NEWCOMER_GUIDE_PART3_SERVICES_AND_DEVELOPMENT.md",
    "QUICK_REFERENCE_GUIDE.md",
    "docs/MULTI_TENANT_COMPLETE_GUIDE.md",
    "docs/newcomer/",
    "GITHUB_PAGES_SETUP.md",
    "deploy-to-github.ps1"
)

foreach ($file in $filesToAdd) {
    if (Test-Path $file) {
        git add $file 2>$null
        Write-Host "[OK] Added: $file"
    }
}

Write-Host ""

# Step 5: Check if there are changes to commit
Write-Host "Step 5: Checking for changes..."
Write-Host ""

$status = git status --porcelain
if (-not $status) {
    Write-Host "[INFO] No changes to commit"
    Write-Host "Documentation is already up to date!"
    Write-Host ""
    Write-Host "Your documentation is available at:"
    Write-Host "https://huycse31501.github.io/embrix-o2x-docs/"
    exit 0
}

Write-Host "[OK] Found changes to commit"
Write-Host ""

# Step 6: Commit changes
Write-Host "Step 6: Committing changes..."
Write-Host ""

$commitMessage = "Deploy comprehensive documentation to GitHub Pages

- Newcomer guide (3 parts covering business, architecture, and development)
- Multi-tenant architecture complete guide
- Quick reference guide
- Automated GitHub Pages deployment"

try {
    git commit -m $commitMessage
    Write-Host "[OK] Changes committed"
} catch {
    Write-Host "[ERROR] Commit failed"
    Write-Host "Error: $_"
    exit 1
}

Write-Host ""

# Step 7: Push to GitHub
Write-Host "Step 7: Pushing to GitHub..."
Write-Host ""
Write-Host "You may be prompted for your GitHub credentials."
Write-Host "Username: huycse31501"
Write-Host "Password: Use your Personal Access Token (NOT your GitHub password)"
Write-Host ""
Write-Host "Don't have a token? Create one at:"
Write-Host "https://github.com/settings/tokens/new"
Write-Host ""
Write-Host "Token permissions needed: 'repo' (Full control of private repositories)"
Write-Host ""

try {
    git push -u origin master
    Write-Host ""
    Write-Host "[OK] Successfully pushed to GitHub"
} catch {
    Write-Host ""
    Write-Host "========================================"
    Write-Host "PUSH FAILED"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "Common issues:"
    Write-Host "- Authentication failed: Use Personal Access Token as password"
    Write-Host "- Repository does not exist: Create it first on GitHub"
    Write-Host "- No write access: Check your permissions"
    Write-Host ""
    Write-Host "See GITHUB_PAGES_SETUP.md for detailed help"
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "DEPLOYMENT SUCCESSFUL!"
Write-Host "========================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host ""
Write-Host "1. Go to your repository settings:"
Write-Host "   https://github.com/huycse31501/embrix-o2x-docs/settings/pages"
Write-Host ""
Write-Host "2. Under 'Build and deployment':"
Write-Host "   - Source: GitHub Actions"
Write-Host "   - The workflow will automatically deploy your documentation"
Write-Host ""
Write-Host "3. Wait 2-3 minutes for deployment to complete"
Write-Host ""
Write-Host "4. Access your documentation at:"
Write-Host "   https://huycse31501.github.io/embrix-o2x-docs/"
Write-Host ""
Write-Host "Monitor deployment at:"
Write-Host "https://github.com/huycse31501/embrix-o2x-docs/actions"
Write-Host ""
Write-Host "Done! Your documentation will be live shortly."
Write-Host ""
