param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [switch]$SkipAI
)

$ErrorActionPreference = "Stop"
$RunId = Get-Date -Format "yyyyMMdd-HHmmssfff"
$UniverseName = "Arunika-Smoke-$RunId"

function Invoke-JsonPost {
    param([string]$Uri, [hashtable]$Payload)
    return Invoke-RestMethod -Uri $Uri -Method Post -ContentType "application/json" -Body ($Payload | ConvertTo-Json -Depth 20)
}

function Show-Step {
    param([string]$Name, $Value)
    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    $Value | ConvertTo-Json -Depth 30
}

Write-Host "Bot Cerita Smoke Test - $RunId" -ForegroundColor Green

$health = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get
Show-Step "HEALTH" $health
if ($health.status -ne "ok") { throw "Health check failed" }

$universe = Invoke-JsonPost "$BaseUrl/universes" @{
    name = $UniverseName
    description = "Ephemeral smoke-test universe. RunId=$RunId"
}
Show-Step "UNIVERSE" $universe
$UniverseId = $universe.id
if (-not $UniverseId) { throw "Universe ID missing" }

$character = Invoke-JsonPost "$BaseUrl/universes/$UniverseId/characters" @{
    name = "Arka"
    description = "Anak pemberani yang suka menjelajah hutan."
    personality = "penasaran, pemberani, sedikit usil"
}
Show-Step "CHARACTER" $character
$CharacterId = $character.id
if (-not $CharacterId) { throw "Character ID missing" }

$canon = Invoke-JsonPost "$BaseUrl/universes/$UniverseId/canon" @{
    title = "Aturan Dunia Arunika"
    content = "Hutan Arunika memiliki makhluk-makhluk kecil yang muncul ketika matahari terbenam."
    category = "world_rule"
    importance = 5
}
Show-Step "CANON" $canon

$context = Invoke-JsonPost "$BaseUrl/universes/$UniverseId/context" @{
    query = "Arka menemukan makhluk kecil di hutan pada sore hari."
    character_ids = @($CharacterId)
    max_items = 40
}
Show-Step "CONTEXT" $context

if ($SkipAI) {
    Write-Host "`nAI step skipped (-SkipAI)." -ForegroundColor Yellow
    Write-Host "SMOKE TEST PASSED" -ForegroundColor Green
    exit 0
}

$story = Invoke-JsonPost "$BaseUrl/stories" @{
    idea = "Arka menemukan seekor anak burung yang terluka di hutan. Ia ingin menolongnya, tetapi suara aneh dari balik pepohonan membuatnya ragu untuk melanjutkan."
    universe_id = $UniverseId
    character_ids = @($CharacterId)
    target_age = "7-10"
    genre = "fantasy adventure"
    tone = @("warm", "funny", "adventurous")
    language = "Indonesian"
    length = "short"
    what_if_count = 3
}
Show-Step "STORY RESULT" $story

New-Item -ItemType Directory -Force -Path "test-results" | Out-Null
$result = @{
    run_id = $RunId
    universe_id = $UniverseId
    universe_name = $UniverseName
    character_id = $CharacterId
    story = $story
}
$result | ConvertTo-Json -Depth 50 | Set-Content "test-results/story-$RunId.json" -Encoding UTF8

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "SMOKE TEST PASSED" -ForegroundColor Green
Write-Host "Universe : $UniverseName"
Write-Host "Universe ID: $UniverseId"
Write-Host "Character: $CharacterId"
Write-Host "Result   : test-results/story-$RunId.json"
Write-Host "======================================" -ForegroundColor Green
