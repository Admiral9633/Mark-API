# PDF OCR Development Helper Script (PowerShell)

param(
    [Parameter(Position=0)]
    [string]$Command,

    [Parameter(Position=1)]
    [string]$Service
)

function Show-Usage {
    Write-Host "PDF OCR Development Helper" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\dev.ps1 {command} [service]"
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  start          Starte alle Container"
    Write-Host "  stop           Stoppe alle Container"
    Write-Host "  restart        Restarte alle Container"
    Write-Host "  logs [service] Zeige Logs (optional: backend|frontend|marker-api|db)"
    Write-Host "  shell [service] Shell im Container (backend|frontend|db)"
    Write-Host "  migrate        Django Migrationen ausführen"
    Write-Host "  rebuild [svc]  Container neu bauen"
    Write-Host "  clean          Räume Docker auf"
    Write-Host "  reset          Lösche alle Daten (VORSICHT!)"
    Write-Host "  status         Zeige Container Status"
    Write-Host "  test           Teste alle Services"
    Write-Host ""
    Write-Host "Beispiele:" -ForegroundColor Green
    Write-Host "  .\dev.ps1 start"
    Write-Host "  .\dev.ps1 logs backend"
    Write-Host "  .\dev.ps1 shell backend"
    Write-Host "  .\dev.ps1 migrate"
}

switch ($Command) {
    "start" {
        Write-Host "🚀 Starte Entwicklungsumgebung..." -ForegroundColor Green
        docker-compose up -d
        Write-Host "✅ Container gestartet" -ForegroundColor Green
        Write-Host "📊 Logs: docker-compose logs -f"
        Write-Host "🌐 Frontend: http://localhost:3000"
        Write-Host "🔧 Backend: http://localhost:8000"
    }

    "stop" {
        Write-Host "🛑 Stoppe Container..." -ForegroundColor Yellow
        docker-compose stop
    }

    "restart" {
        Write-Host "🔄 Restarte Container..." -ForegroundColor Yellow
        docker-compose restart
    }

    "logs" {
        if ($Service) {
            docker-compose logs -f $Service
        } else {
            docker-compose logs -f
        }
    }

    "shell" {
        switch ($Service) {
            "backend" {
                docker-compose exec backend sh
            }
            "frontend" {
                docker-compose exec frontend sh
            }
            "db" {
                docker-compose exec db psql -U postgres -d pdf_ocr
            }
            default {
                Write-Host "Usage: .\dev.ps1 shell [backend|frontend|db]" -ForegroundColor Red
            }
        }
    }

    "migrate" {
        Write-Host "🔄 Führe Migrationen aus..." -ForegroundColor Cyan
        docker-compose exec backend python manage.py makemigrations
        docker-compose exec backend python manage.py migrate
    }

    "rebuild" {
        Write-Host "🔨 Rebuilde Container..." -ForegroundColor Cyan
        if ($Service) {
            docker-compose build $Service
            docker-compose up -d $Service
        } else {
            docker-compose build
            docker-compose up -d
        }
    }

    "clean" {
        Write-Host "🧹 Räume auf..." -ForegroundColor Yellow
        docker-compose down
        docker system prune -f
    }

    "reset" {
        Write-Host "⚠️  WARNUNG: Löscht alle Daten!" -ForegroundColor Red
        $confirm = Read-Host "Wirklich fortfahren? (yes/no)"
        if ($confirm -eq "yes") {
            docker-compose down -v
            Write-Host "✅ Alle Volumes gelöscht" -ForegroundColor Green
        }
    }

    "status" {
        Write-Host "📊 Container Status:" -ForegroundColor Cyan
        docker-compose ps
        Write-Host ""
        Write-Host "💾 RAM Usage:" -ForegroundColor Cyan
        docker stats --no-stream --format "table {{.Name}}`t{{.MemUsage}}"
    }

    "test" {
        Write-Host "🧪 Teste Services..." -ForegroundColor Cyan

        Write-Host "1. Backend: " -NoNewline
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/api/documents/" -UseBasicParsing -TimeoutSec 5
            Write-Host "✅" -ForegroundColor Green
        } catch {
            Write-Host "❌" -ForegroundColor Red
        }

        Write-Host "2. Frontend: " -NoNewline
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
            Write-Host "✅" -ForegroundColor Green
        } catch {
            Write-Host "❌" -ForegroundColor Red
        }

        Write-Host "3. Marker-API: " -NoNewline
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 5
            Write-Host "✅" -ForegroundColor Green
        } catch {
            Write-Host "❌" -ForegroundColor Red
        }

        Write-Host "4. Database: " -NoNewline
        $dbCheck = docker-compose exec db pg_isready -U postgres
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅" -ForegroundColor Green
        } else {
            Write-Host "❌" -ForegroundColor Red
        }
    }

    default {
        Show-Usage
    }
}
