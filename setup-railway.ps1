# Script para configurar variáveis de ambiente no Railway
# Rode este script UMA VEZ após criar os serviços no Railway

Write-Host "=== CONFIGURAÇÃO RAILWAY ===" -ForegroundColor Cyan
Write-Host ""

# Token do Railway
$RAILWAY_TOKEN = "8f6d3a48-3760-4b06-9c61-f6fe51f63367"

Write-Host "Instruções para configurar no Railway:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Acesse: https://railway.app" -ForegroundColor Green
Write-Host "2. Vá até seu projeto 'CRM Arcsat'" -ForegroundColor Green
Write-Host "3. Clique no serviço 'backend'" -ForegroundColor Green
Write-Host ""

Write-Host "=== VARIÁVEIS DO BACKEND ===" -ForegroundColor Cyan
$backendVars = @"
MONGODB_URL=mongodb+srv://nicolasrosaab_db_user:Gio4EAQhbEdQMISl@cluster0.npuhras.mongodb.net/arcsat_crm?retryWrites=true&w=majority
DATABASE_NAME=arcsat_crm
ENVIRONMENT=production
CORS_ORIGINS=https://frontend-production-5ae9.up.railway.app,http://arcsat.com.br,https://arcsat.com.br,http://www.arcsat.com.br,https://www.arcsat.com.br
"@

Write-Host $backendVars -ForegroundColor White
Write-Host ""
Write-Host "Copiando para área de transferência..." -ForegroundColor Yellow
$backendVars | Set-Clipboard
Write-Host "✓ Copiado! Cole no Railway (Variables > Raw Editor)" -ForegroundColor Green
Write-Host ""
Read-Host "Pressione ENTER quando terminar de configurar o backend"

Write-Host ""
Write-Host "4. Agora clique no serviço 'frontend'" -ForegroundColor Green
Write-Host ""

Write-Host "=== VARIÁVEIS DO FRONTEND ===" -ForegroundColor Cyan
$frontendVars = @"
VITE_API_URL=https://backend-production-7566.up.railway.app/api
"@

Write-Host $frontendVars -ForegroundColor White
Write-Host ""
Write-Host "Copiando para área de transferência..." -ForegroundColor Yellow
$frontendVars | Set-Clipboard
Write-Host "✓ Copiado! Cole no Railway (Variables > Raw Editor)" -ForegroundColor Green
Write-Host ""
Read-Host "Pressione ENTER quando terminar de configurar o frontend"

Write-Host ""
Write-Host "=== FINALIZAÇÃO ===" -ForegroundColor Cyan
Write-Host "5. Clique em 'Deploy' em cada serviço" -ForegroundColor Green
Write-Host "6. Aguarde o deploy finalizar" -ForegroundColor Green
Write-Host ""
Write-Host "✓ Configuração concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "URLs dos serviços:" -ForegroundColor Yellow
Write-Host "Backend:  https://backend-production-7566.up.railway.app" -ForegroundColor Cyan
Write-Host "Frontend: https://frontend-production-5ae9.up.railway.app" -ForegroundColor Cyan
Write-Host "Health:   https://backend-production-7566.up.railway.app/health" -ForegroundColor Cyan
