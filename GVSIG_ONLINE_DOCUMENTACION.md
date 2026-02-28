# 📚 gvSIG Online - Documentación Completa

> **Fuente**: [DeepWiki - gvSIG Online](https://deepwiki.com/gvSIGAssociation/gvsig-online)
> **Repositorio**: [GitHub - gvSIGAssociation/gvsig-online](https://github.com/gvSIGAssociation/gvsig-online)

---

## 📋 Índice

1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Aplicaciones Django Core](#aplicaciones-django-core)
4. [Sistema de Configuración](#sistema-de-configuración)
5. [Gestión de Servicios](#gestión-de-servicios)
6. [Integración con GeoServer](#integración-con-geoserver)
7. [Base de Datos PostGIS](#base-de-datos-postgis)
8. [Sistema de Plugins](#sistema-de-plugins)
9. [Autenticación y Autorización](#autenticación-y-autorización)
10. [Variables de Configuración](#variables-de-configuración)
11. [Estructura de URLs](#estructura-de-urls)
12. [Comandos Útiles](#comandos-útiles)
13. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 Descripción General

**gvSIG Online** es una plataforma GIS (Sistema de Información Geográfica) basada en web, construida sobre Django, que proporciona:

- ✅ Gestión integral de datos geoespaciales
- ✅ Visualización de mapas interactivos
- ✅ Publicación de servicios OGC (WMS, WFS, WCS, WMTS)
- ✅ Edición de capas vectoriales
- ✅ Gestión de usuarios y permisos
- ✅ Sistema de plugins extensible

### Componentes Principales

| Componente | Puerto | Descripción |
|------------|--------|-------------|
| **Django** | 8000 | Aplicación web principal |
| **GeoServer** | 8080 | Servidor de mapas OGC |
| **PostgreSQL/PostGIS** | 5432 | Base de datos espacial |
| **RabbitMQ** | 5672 | Cola de mensajes (Celery) |

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (JavaScript)                     │
│              OpenLayers / Visor de Mapas                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  DJANGO APPLICATION SERVER                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│
│  │ gvsigol_core│ │gvsigol_auth │ │   gvsigol_services      ││
│  │  Projects   │ │   Users     │ │ Workspaces/Datastores   ││
│  │ LayerGroups │ │   Roles     │ │   Layers/LayerGroups    ││
│  └─────────────┘ └─────────────┘ └─────────────────────────┘│
│  ┌─────────────────────────┐ ┌─────────────────────────────┐│
│  │   gvsigol_symbology     │ │      gvsigol_plugins        ││
│  │   Styles/Rules          │ │   Edition/Catalog/ETL       ││
│  └─────────────────────────┘ └─────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                    │                       │
                    ▼                       ▼
┌───────────────────────────┐   ┌─────────────────────────────┐
│       GEOSERVER           │   │    POSTGRESQL/POSTGIS       │
│   (REST API + OGC)        │   │    (Datos + Metadatos)      │
│  - WMS/WFS/WCS/WMTS       │   │    - Capas vectoriales      │
│  - Workspaces/Stores      │   │    - Configuración Django   │
│  - Estilos SLD            │   │    - Usuarios/Permisos      │
└───────────────────────────┘   └─────────────────────────────┘
```

### Arquitectura de Tres Capas

1. **Frontend JavaScript**: Visor de mapas con OpenLayers
2. **Django Application Server**: Lógica de negocio y API REST
3. **Backend Services**: GeoServer + PostGIS + RabbitMQ

---

## 📦 Aplicaciones Django Core

### `gvsigol_core`
Gestión de proyectos y grupos de capas.

| Modelo | Descripción |
|--------|-------------|
| `Project` | Proyecto de mapa con configuración |
| `ProjectLayerGroup` | Relación proyecto-grupo de capas |
| `TilingProcessStatus` | Estado de procesos de tileado |

### `gvsigol_services`
Gestión de recursos GeoServer.

| Modelo | Descripción |
|--------|-------------|
| `Server` | Servidor GeoServer configurado |
| `Node` | Nodo de cluster GeoServer |
| `Workspace` | Espacio de trabajo en GeoServer |
| `Connection` | Conexión centralizada a BD |
| `Datastore` | Almacén de datos (PostGIS, SHP, etc.) |
| `Layer` | Capa publicada |
| `LayerGroup` | Grupo de capas |

### `gvsigol_auth`
Autenticación y autorización.

| Modelo | Descripción |
|--------|-------------|
| `User` | Usuario del sistema |
| `Role` | Rol/Grupo de permisos |
| `UserGroup` | Grupo de usuarios |

### `gvsigol_symbology`
Gestión de estilos de capas.

| Modelo | Descripción |
|--------|-------------|
| `Style` | Estilo SLD |
| `Rule` | Regla de estilo |
| `Symbolizer` | Simbolizador (punto, línea, polígono) |
| `StyleLayer` | Relación estilo-capa |

---

## ⚙️ Sistema de Configuración

### Dos Enfoques de Configuración

#### 1. Template-based (Producción)
```bash
# configure.sh reemplaza tokens ##VARIABLE## en settings_tpl.py
./configure.sh
```

Tokens de ejemplo:
- `##DEBUG##`
- `##DB_NAME##`
- `##GEOSERVER_BASE_URL##`

#### 2. Environment-based (Desarrollo)
```bash
# Usa django-environ para leer .env
cp .env.example .env
nano .env
```

### Archivo `.env` Ejemplo

```bash
# Debug
DEBUG=True

# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gvsigonline
DB_USER=gvsiguser
DB_PASS=password123

# URLs
BASE_URL=https://tudominio.com
GVSIGOL_URL_PREFIX=

# GeoServer
GEOSERVER_BASE_URL=http://localhost:8080/geoserver
GEOSERVER_USER=admin
GEOSERVER_PASSWORD=geoserver

# Celery
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//

# Plugins
GVSIGOL_PLUGINS=gvsigol_plugin_edition,gvsigol_plugin_catalog

# Seguridad
SECRET_KEY=tu-clave-secreta-muy-larga
ALLOWED_HOSTS=localhost,127.0.0.1,tudominio.com

# Idioma
LANGUAGE_CODE=es
LANGUAGES=es,en

# CRS
VIEWER_DEFAULT_CRS=EPSG:3857
```

---

## 🗂️ Gestión de Servicios

### Jerarquía de Recursos

```
Server (GeoServer)
└── Workspace (Espacio de trabajo)
    └── Datastore (Almacén de datos)
        └── Layer (Capa)
            └── LayerGroup (Grupo de capas)
```

### Tipos de Datastore Soportados

| Tipo | Código | Descripción |
|------|--------|-------------|
| PostGIS Vectorial | `v_PostGIS` | Capas vectoriales en PostgreSQL |
| Shapefile | `v_SHP` | Archivos .shp |
| GeoTIFF | `c_GeoTIFF` | Raster GeoTIFF |
| ImageMosaic | `c_ImageMosaic` | Mosaico de imágenes |
| WMS Externo | `e_WMS` | Servicio WMS externo |

### Modelo Connection (Nuevo)

Centraliza credenciales de conexión:

```python
# Parámetros de conexión PostGIS
{
    "host": "localhost",
    "port": "5432",
    "database": "gvsigonline",
    "schema": "public",
    "user": "gvsiguser",
    "passwd": "password123",
    "dbtype": "postgis"
}
```

Métodos útiles:
- `get_connection_params()` - Obtener parámetros
- `test_connection()` - Probar conexión
- `create_schema_if_not_exists(schema_name)` - Crear schema

---

## 🌐 Integración con GeoServer

### Clase `Geoserver` Backend

Ubicación: `gvsigol_services/backend_geoserver.py`

```python
# Métodos principales
createWorkspace(name, uri)           # POST /rest/workspaces
createDatastore(ws, type, name, ...) # POST /rest/workspaces/{ws}/datastores
createFeaturetype(ws, ds, fields)    # POST /rest/.../featuretypes
createDefaultStyle(layer, name)      # POST /rest/styles
reload_featuretype(layer, ...)       # PUT /rest/.../featuretypes/{name}
```

### REST API GeoServer

```python
# Clase rest_geoserver.Geoserver
from gvsigol_services.rest_geoserver import Geoserver

gs = Geoserver(url, user, password)
gs.get_workspaces()
gs.create_workspace(name, uri)
gs.get_datastores(workspace)
```

### Singleton Geographic Servers

```python
from gvsigol_services import geographic_servers

# Obtener instancia de GeoServer
gs_instance = geographic_servers.get_instance()
```

---

## 🗄️ Base de Datos PostGIS

### Introspección de Esquemas

Clase: `backend_postgis.Introspect`

```python
from gvsigol_services.backend_postgis import Introspect

introspect = Introspect(database, host, port, user, password)
tables = introspect.get_tables(schema)
geom_info = introspect.get_geometry_columns_info(schema, table)
table_info = introspect.get_table_info(schema, table)
```

### Bases de Datos Adicionales

| Variable | Uso |
|----------|-----|
| `GVSIGOL_USERS_CARTODB` | BD para datos de usuarios |
| `MOSAIC_DB` | BD para mosaicos de imágenes |
| `GEOETL_DB` | BD para procesos ETL |

---

## 🔌 Sistema de Plugins

### Estructura de un Plugin

```
gvsigol_plugin_nombre/
├── __init__.py
├── models.py      # Modelos Django
├── views.py       # Vistas
├── urls.py        # Rutas URL
├── settings.py    # Configuración del plugin
├── templates/     # Plantillas HTML
└── static/        # Archivos estáticos
```

### Plugins Oficiales

| Plugin | Descripción |
|--------|-------------|
| `gvsigol_plugin_edition` | Edición de capas vectoriales |
| `gvsigol_plugin_catalog` | Catálogo de metadatos |
| `gvsigol_plugin_etl` | Procesos ETL geoespaciales |
| `gvsigol_plugin_print` | Impresión de mapas |
| `gvsigol_plugin_worldwind` | Visor 3D |
| `gvsigol_plugin_oidc_mozilla` | Autenticación OIDC |

### Activar Plugins

```bash
# En .env
GVSIGOL_PLUGINS=gvsigol_plugin_edition,gvsigol_plugin_catalog,gvsigol_plugin_etl
```

---

## 🔐 Autenticación y Autorización

### Proveedores de Autenticación

| Proveedor | Variable |
|-----------|----------|
| Django (default) | `GVSIGOL_AUTH_PROVIDER=gvsigol_auth` |
| LDAP | `GVSIGOL_AUTH_PROVIDER=gvsigol_plugin_ldap` |
| OIDC/Keycloak | `GVSIGOL_AUTH_PROVIDER=gvsigol_plugin_oidc_mozilla` |

### Niveles de Autorización

1. **Nivel de Capa**: read/write/manage
2. **Nivel de Feature**: Filtros CQL
3. **Nivel de Proyecto**: ProjectRole

### Configuración LDAP

```bash
LDAP_HOST=ldap://ldap.empresa.com
LDAP_PORT=389
LDAP_BASE_DN=dc=empresa,dc=com
LDAP_BIND_DN=cn=admin,dc=empresa,dc=com
LDAP_BIND_PASSWORD=password
```

---

## 📝 Variables de Configuración

### Variables Críticas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DEBUG` | Modo debug | `False` |
| `SECRET_KEY` | Clave secreta Django | `abc123...` |
| `BASE_URL` | URL base del sitio | `https://gis.empresa.com` |
| `ALLOWED_HOSTS` | Hosts permitidos | `gis.empresa.com,localhost` |
| `DB_*` | Configuración PostgreSQL | Ver arriba |
| `GEOSERVER_*` | Configuración GeoServer | Ver arriba |
| `CELERY_BROKER_URL` | URL broker Celery | `amqp://...` |
| `GVSIGOL_PLUGINS` | Plugins activos | `plugin1,plugin2` |

### Variables Geoespaciales

| Variable | Descripción | Default |
|----------|-------------|---------|
| `VIEWER_DEFAULT_CRS` | CRS por defecto | `EPSG:3857` |
| `SUPPORTED_CRS` | CRS soportados | Lista de EPSG |
| `DEFAULT_VIEWER_UI` | UI del visor | `ol` |

### Variables de Seguridad

| Variable | Descripción |
|----------|-------------|
| `CORS_ALLOWED_ORIGINS` | Orígenes CORS permitidos |
| `CSRF_TRUSTED_ORIGINS` | Orígenes CSRF confiables |
| `USE_X_FORWARDED_HOST` | Usar header X-Forwarded-Host |

---

## 🔗 Estructura de URLs

### URLs Principales

```
/                           # Índice/Dashboard
/admin/                     # Admin Django
/core/                      # Gestión de proyectos
  ├── load/<project_name>/  # Cargar proyecto
  ├── project_list/         # Lista de proyectos
  └── project_get_conf/     # Configuración JSON
/services/                  # Gestión de servicios
  ├── server_list/          # Servidores
  ├── workspace_list/       # Workspaces
  ├── workspace_add/        # Añadir workspace
  ├── datastore_list/       # Datastores
  ├── datastore_add/        # Añadir datastore
  ├── layer_list/           # Capas
  ├── layer_create/         # Crear capa
  ├── layer_update/<id>/    # Editar capa
  └── layergroup_list/      # Grupos de capas
/auth/                      # Autenticación
  ├── login/                # Iniciar sesión
  ├── logout/               # Cerrar sesión
  └── user_list/            # Lista de usuarios
/symbology/                 # Gestión de estilos
/filemanager/               # Gestor de archivos
```

### Plantillas Base

```
base.html
├── dashboard.html
├── layer_list.html
├── layer_add.html
├── layer_update.html
├── layer_create.html
├── layer_config.html
├── layergroup_add.html
└── layergroup_update.html
```

---

## 💻 Comandos Útiles

### Django

```bash
# Activar entorno virtual
source venv/bin/activate

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar estáticos
python manage.py collectstatic --noinput

# Servidor de desarrollo
python manage.py runserver 0.0.0.0:8000

# Shell Django
python manage.py shell
```

### Base de Datos

```bash
# Conectar a PostgreSQL
psql -h localhost -U gvsiguser -d gvsigonline

# Backup
pg_dump -h localhost -U gvsiguser gvsigonline > backup.sql

# Restore
psql -h localhost -U gvsiguser gvsigonline < backup.sql
```

### GeoServer

```bash
# Iniciar GeoServer
./geoserver/bin/startup.sh

# Detener GeoServer
./geoserver/bin/shutdown.sh

# Verificar estado
curl -u admin:geoserver http://localhost:8080/geoserver/rest/about/version.json
```

### Celery

```bash
# Iniciar worker
celery -A gvsigol worker -l info

# Iniciar beat (tareas programadas)
celery -A gvsigol beat -l info
```

---

## 🔧 Solución de Problemas

### Error: "Connection refused" a GeoServer

```bash
# Verificar que GeoServer está corriendo
curl http://localhost:8080/geoserver/web/

# Verificar URL en base de datos
python manage.py shell
>>> from gvsigol_services.models import Server
>>> s = Server.objects.get(id=1)
>>> print(s.frontend_url)  # Debe ser http://localhost:8080/geoserver
```

### Error: "Workspace no puede ser creado"

1. Verificar que GeoServer está corriendo
2. Verificar credenciales en `.env`:
   ```bash
   GEOSERVER_USER=admin
   GEOSERVER_PASSWORD=geoserver
   ```
3. Verificar URL del servidor en BD:
   ```python
   from gvsigol_services.models import Server
   s = Server.objects.get(id=1)
   s.frontend_url = 'http://localhost:8080/geoserver'
   s.user = 'admin'
   s.password = 'geoserver'
   s.save()
   ```

### Error: 404 en URLs

Verificar que no hay URLs hardcodeadas con `/gvsigonline/`:
```bash
grep -r "/gvsigonline/" gvsigol/*/templates/
```

Usar Django URL tags:
```html
<!-- Incorrecto -->
<a href="/gvsigonline/services/workspace_add/">

<!-- Correcto -->
<a href="{% url 'workspace_add' %}">
```

### Error: Base de datos no accesible

```bash
# Verificar PostgreSQL
sudo systemctl status postgresql

# Verificar conexión
psql -h localhost -U gvsiguser -d gvsigonline -c "SELECT 1;"

# Verificar extensión PostGIS
psql -h localhost -U gvsiguser -d gvsigonline -c "SELECT PostGIS_Version();"
```

### Error: Celery no procesa tareas

```bash
# Verificar RabbitMQ
sudo systemctl status rabbitmq-server

# Verificar conexión
python -c "import pika; pika.BlockingConnection(pika.ConnectionParameters('localhost'))"

# Reiniciar Celery
pkill -f "celery worker"
celery -A gvsigol worker -l info
```

---

## 📚 Referencias

- **DeepWiki**: https://deepwiki.com/gvSIGAssociation/gvsig-online
- **GitHub**: https://github.com/gvSIGAssociation/gvsig-online
- **Documentación Oficial**: https://www.gvsig.com/es/productos/gvsig-online
- **GeoServer Docs**: https://docs.geoserver.org/
- **PostGIS Docs**: https://postgis.net/documentation/

---

## 📅 Última Actualización

**Fecha**: Febrero 2026
**Versión gvSIG Online**: 4.0.x

---

*Documento generado automáticamente desde DeepWiki*
