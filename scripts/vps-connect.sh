#!/bin/bash
# Script para conectarse al VPS de gvSIG Online
# Uso: ./vps-connect.sh [comando]

VPS_HOST="gvsig-vps"
VPS_IP="72.62.31.223"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_help() {
    echo -e "${GREEN}=== gvSIG Online VPS Connection Script ===${NC}"
    echo ""
    echo "Uso: $0 [opción]"
    echo ""
    echo "Opciones:"
    echo "  (sin args)    Conectar al VPS via SSH"
    echo "  status        Ver estado de los servicios"
    echo "  restart       Reiniciar servicios (gvsigonline, celery)"
    echo "  logs          Ver logs de gvsigonline"
    echo "  celery-logs   Ver logs de celery"
    echo "  db            Conectar a PostgreSQL"
    echo "  fix-perms     Corregir permisos de archivos"
    echo "  project       Conectar al directorio del proyecto (/var/www/gvsig-online/gvsigol)"
    echo "  git           Ver estado de git y últimos commits"
    echo "  pull          Actualizar código desde origin/staging"
    echo "  help          Mostrar esta ayuda"
    echo ""
    echo -e "${YELLOW}URLs útiles:${NC}"
    echo "  - App:        http://$VPS_IP/gvsigonline/"
    echo "  - GeoServer:  http://$VPS_IP/geoserver/"
    echo "  - Layers:     http://$VPS_IP/gvsigonline/services/layer_list/"
}

case "$1" in
    "")
        echo -e "${GREEN}Conectando al VPS...${NC}"
        ssh $VPS_HOST
        ;;
    "status")
        echo -e "${GREEN}Estado de servicios:${NC}"
        ssh $VPS_HOST "systemctl status gvsigonline celery --no-pager | head -20"
        ;;
    "restart")
        echo -e "${YELLOW}Reiniciando servicios...${NC}"
        ssh $VPS_HOST "systemctl restart gvsigonline celery && echo 'Servicios reiniciados'"
        ;;
    "logs")
        echo -e "${GREEN}Logs de gvsigonline:${NC}"
        ssh $VPS_HOST "journalctl -u gvsigonline -f"
        ;;
    "celery-logs")
        echo -e "${GREEN}Logs de celery:${NC}"
        ssh $VPS_HOST "tail -f /var/log/celery/celery.service.log"
        ;;
    "db")
        echo -e "${GREEN}Conectando a PostgreSQL...${NC}"
        ssh $VPS_HOST "sudo -u postgres psql -d gvsigonline"
        ;;
    "fix-perms")
        echo -e "${YELLOW}Corrigiendo permisos...${NC}"
        ssh $VPS_HOST "chown -R www-data:www-data /opt/gvsigol_data/thumbnails /opt/gvsigol_data/images && chmod 644 /opt/gvsigol_data/thumbnails/*.png /opt/gvsigol_data/images/*.png 2>/dev/null && echo 'Permisos corregidos'"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "project"|"gvsigol")
        echo -e "${GREEN}Conectando al directorio del proyecto...${NC}"
        ssh -t $VPS_HOST "cd /var/www/gvsig-online/gvsigol && bash"
        ;;
    "git")
        echo -e "${GREEN}Estado de git en el proyecto:${NC}"
        ssh $VPS_HOST "cd /var/www/gvsig-online && git status --short && git log --oneline -5"
        ;;
    "pull")
        echo -e "${YELLOW}Actualizando código desde origin...${NC}"
        ssh $VPS_HOST "cd /var/www/gvsig-online && git pull origin staging"
        ;;
    *)
        echo -e "${GREEN}Ejecutando comando en VPS:${NC} $@"
        ssh $VPS_HOST "$@"
        ;;
esac
