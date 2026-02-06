#!/bin/bash

# Development Helper Script

case "$1" in
    start)
        echo "🚀 Starte Entwicklungsumgebung..."
        docker-compose up -d
        echo "✅ Container gestartet"
        echo "📊 Logs: docker-compose logs -f"
        echo "🌐 Frontend: http://localhost:3000"
        echo "🔧 Backend: http://localhost:8000"
        ;;

    stop)
        echo "🛑 Stoppe Container..."
        docker-compose stop
        ;;

    restart)
        echo "🔄 Restarte Container..."
        docker-compose restart
        ;;

    logs)
        docker-compose logs -f ${2:-}
        ;;

    shell)
        if [ "$2" = "backend" ]; then
            docker-compose exec backend sh
        elif [ "$2" = "frontend" ]; then
            docker-compose exec frontend sh
        elif [ "$2" = "db" ]; then
            docker-compose exec db psql -U postgres -d pdf_ocr
        else
            echo "Usage: $0 shell [backend|frontend|db]"
        fi
        ;;

    migrate)
        echo "🔄 Führe Migrationen aus..."
        docker-compose exec backend python manage.py makemigrations
        docker-compose exec backend python manage.py migrate
        ;;

    rebuild)
        echo "🔨 Rebuilde Container..."
        docker-compose build ${2:-}
        docker-compose up -d ${2:-}
        ;;

    clean)
        echo "🧹 Räume auf..."
        docker-compose down
        docker system prune -f
        ;;

    reset)
        echo "⚠️  WARNUNG: Löscht alle Daten!"
        read -p "Wirklich fortfahren? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            docker-compose down -v
            echo "✅ Alle Volumes gelöscht"
        fi
        ;;

    status)
        echo "📊 Container Status:"
        docker-compose ps
        echo ""
        echo "💾 RAM Usage:"
        docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"
        ;;

    test)
        echo "🧪 Teste Services..."
        echo "1. Backend:"
        curl -f http://localhost:8000/api/documents/ && echo "✅" || echo "❌"
        echo "2. Frontend:"
        curl -f http://localhost:3000 && echo "✅" || echo "❌"
        echo "3. Marker-API:"
        curl -f http://localhost:8001/health && echo "✅" || echo "❌"
        echo "4. Database:"
        docker-compose exec db pg_isready -U postgres && echo "✅" || echo "❌"
        ;;

    *)
        echo "PDF OCR Development Helper"
        echo ""
        echo "Usage: $0 {command}"
        echo ""
        echo "Commands:"
        echo "  start          Starte alle Container"
        echo "  stop           Stoppe alle Container"
        echo "  restart        Restarte alle Container"
        echo "  logs [service] Zeige Logs (optional: backend|frontend|marker-api|db)"
        echo "  shell [service] Shell im Container (backend|frontend|db)"
        echo "  migrate        Django Migrationen ausführen"
        echo "  rebuild [svc]  Container neu bauen"
        echo "  clean          Räume Docker auf"
        echo "  reset          Lösche alle Daten (VORSICHT!)"
        echo "  status         Zeige Container Status"
        echo "  test           Teste alle Services"
        echo ""
        echo "Beispiele:"
        echo "  $0 start"
        echo "  $0 logs backend"
        echo "  $0 shell backend"
        echo "  $0 migrate"
        ;;
esac
