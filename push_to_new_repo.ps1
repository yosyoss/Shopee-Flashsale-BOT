# ==========================================================
# Push to NEW personal repo: yosyoss/Shopee-Flashsale-BOT
# ==========================================================
# Step 1: Buka https://github.com/new di browser Anda
#         - Repository name: Shopee-Flashsale-BOT
#         - Description:    Selenium-based bot untuk auto-beli flash sale Shopee
#         - Visibility:     Private (atau Public, sesuai keinginan)
#         - JANGAN centang "Add a README file", "Add .gitignore", "Choose a license"
#           (project ini sudah punya semuanya)
#         - Klik "Create repository"
#
# Step 2: Setelah repo dibuat, JANGAN close halaman GitHub-nya.
#         Copy URL HTTPS yang muncul (format: https://github.com/yosyoss/Shopee-Flashsale-BOT.git)
#
# Step 3: Jalankan script ini di PowerShell:
#         .\push_to_new_repo.ps1
#         (script akan prompt untuk paste URL)
# ==========================================================

# Prompt for repo URL
$repoUrl = Read-Host "Paste URL repo baru (https://github.com/yosyoss/Shopee-Flashsale-BOT.git)"

if (-not $repoUrl) {
    Write-Host "ERROR: URL tidak boleh kosong" -ForegroundColor Red
    exit 1
}

# Validate URL
if ($repoUrl -notmatch '^https://github\.com/.*\.git$') {
    Write-Host "ERROR: URL harus format https://github.com/username/repo.git" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Mengganti remote origin ===" -ForegroundColor Cyan
git remote remove origin 2>$null
git remote add origin $repoUrl
Write-Host "Remote sekarang: $(git remote get-url origin)"

Write-Host ""
Write-Host "=== Stage all files ===" -ForegroundColor Cyan
git add -A
Write-Host "Files staged: $(git diff --cached --name-only | Measure-Object).Count"

Write-Host ""
Write-Host "=== Commit ===" -ForegroundColor Cyan
$commitMsg = "Initial commit: Shopee Flashsale BOT for YOS (@yosyoss)" + [char]10 + [char]10 + "- Fixed all known bugs from original repo" + [char]10 + "- Migrated to Chrome for Testing portable + CDP" + [char]10 + "- Added manual login flow to bypass Shopee captcha" + [char]10 + "- Added multiple selector fallback for Shopee buttons" + [char]10 + "- Added manual GO trigger (press Enter) for flash sale" + [char]10 + "- Added auto-checkout for cart + Buat Pesanan"
git commit -m $commitMsg

Write-Host ""
Write-Host "=== Push to $repoUrl ===" -ForegroundColor Cyan
git branch -M main
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "  Push berhasil!" -ForegroundColor Green
    Write-Host "  Repo baru: $repoUrl" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Push gagal. Cek error di atas." -ForegroundColor Red
    Write-Host "Kalau 'authentication failed':" -ForegroundColor Yellow
    Write-Host "  - Pastikan Anda sudah setup SSH key atau Personal Access Token" -ForegroundColor Yellow
    Write-Host "  - https://docs.github.com/en/authentication" -ForegroundColor Yellow
}
