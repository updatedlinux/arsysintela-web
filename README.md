# Arsys Intela – SaaS Landing (Flask)

Landing page de marketing para **Arsys Intela** (infraestructura privada, IA y automatización), basada en el template eSoft y desarrollada con Flask.

## Descripción

Este proyecto es una aplicación web Flask que sirve como landing page para presentar las soluciones de Arsys Intela: infraestructura privada con Intela Grid, agentes de IA con Assistant360, y gestión y automatización de espacios con Condominio360 e Intela Smart.

## Requisitos previos

- **Python 3.9+** (recomendado 3.9 o superior)
- **git** para clonar el repositorio
- **Entorno virtual** (venv) - recomendado
- **PM2** (para modo producción) - opcional pero recomendado
- **npm** (para instalar PM2 globalmente)

## Instalación (modo manual, sin Docker)

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd arsysintela-web
```

### 2. Crear y activar entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En Linux/macOS:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp env.sample .env

# Editar .env con tus valores
nano .env  # o usar tu editor preferido
```

Variables mínimas requeridas en `.env`:

```env
DEBUG=True
FLASK_APP=run.py
FLASK_ENV=development
ASSETS_ROOT=/static
```

### 5. Ejecutar en modo desarrollo

```bash
flask run --host=0.0.0.0 --port=8000
```

La aplicación estará disponible en `http://localhost:8000`

## Despliegue en producción (sin Docker - recomendado)

### Opción 1: Usando Gunicorn con PM2 (recomendado)

#### Instalar PM2

```bash
npm install -g pm2
```

#### Crear script de inicio (opcional)

Puedes crear un archivo `start.sh` en la raíz del proyecto:

```bash
#!/bin/bash
source venv/bin/activate
gunicorn --config gunicorn-cfg.py run:app
```

Hacer ejecutable:

```bash
chmod +x start.sh
```

#### Iniciar con PM2

**Opción A: Usando gunicorn directamente**

```bash
pm2 start "venv/bin/gunicorn --config gunicorn-cfg.py run:app" --name arsysintela
```

**Opción B: Usando el script shell**

```bash
pm2 start start.sh --name arsysintela --interpreter bash
```

**Opción C: Configuración con variables de entorno en PM2**

Crear un archivo `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: 'arsysintela',
    script: 'venv/bin/gunicorn',
    args: '--config gunicorn-cfg.py run:app',
    cwd: '/ruta/completa/al/proyecto',
    env: {
      FLASK_APP: 'run.py',
      FLASK_ENV: 'production',
      DEBUG: 'False',
      ASSETS_ROOT: '/static'
    }
  }]
};
```

Luego iniciar con:

```bash
pm2 start ecosystem.config.js
```

#### Comandos útiles de PM2

```bash
# Ver logs en tiempo real
pm2 logs arsysintela

# Ver estado
pm2 status

# Reiniciar aplicación
pm2 restart arsysintela

# Detener aplicación
pm2 stop arsysintela

# Eliminar aplicación de PM2
pm2 delete arsysintela

# Guardar configuración actual
pm2 save

# Configurar arranque automático al reiniciar el sistema
pm2 startup
# (sigue las instrucciones que muestra el comando)
```

### Opción 2: Gunicorn detrás de un reverse proxy (nginx)

Si prefieres usar nginx como reverse proxy:

1. Configurar nginx para hacer proxy a `localhost:5005` (puerto configurado en `gunicorn-cfg.py`)
2. Ejecutar gunicorn directamente o con PM2 como se muestra arriba

Ejemplo de configuración nginx (`/etc/nginx/sites-available/arsysintela`):

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /ruta/al/proyecto/apps/static;
    }
}
```

## Despliegue con Docker (opcional)

Aunque el método recomendado para este proyecto es **sin Docker usando PM2**, también puedes usar Docker si lo prefieres.

### Construir la imagen

```bash
docker build -t arsysintela .
```

### Ejecutar el contenedor

```bash
docker run -d -p 8000:5005 --name arsysintela arsysintela
```

### Usar docker-compose

```bash
docker-compose up -d
```

**Nota:** Esta opción es opcional. Para producción en Intela Grid, se recomienda usar PM2 sin Docker.

## Estructura del proyecto

```
arsysintela-web/
├── apps/
│   ├── __init__.py          # Inicialización de la aplicación Flask
│   ├── config.py            # Configuración de la aplicación
│   ├── pages/
│   │   ├── routes.py        # Rutas principales de la aplicación
│   │   └── __init__.py
│   ├── static/              # Archivos estáticos (CSS, JS, imágenes)
│   │   ├── css/
│   │   ├── js/
│   │   ├── img/
│   │   └── scss/
│   └── templates/           # Plantillas Jinja2
│       ├── layouts/         # Layouts base
│       ├── pages/           # Páginas principales (index6.html es la home)
│       └── partials/        # Componentes reutilizables (navbar, footer, etc.)
├── run.py                   # Punto de entrada de la aplicación
├── requirements.txt         # Dependencias de Python
├── .env                    # Variables de entorno (no versionado)
├── env.sample              # Plantilla de variables de entorno
├── gunicorn-cfg.py         # Configuración de Gunicorn
├── Dockerfile              # Configuración Docker (opcional)
├── docker-compose.yml      # Configuración Docker Compose (opcional)
└── README.md               # Este archivo
```

### Descripción de carpetas principales

- **`apps/`**: Contiene toda la lógica de la aplicación Flask
  - **`pages/routes.py`**: Define las rutas de la aplicación (la ruta `/` renderiza `index6.html`)
  - **`templates/`**: Plantillas HTML usando Jinja2
  - **`static/`**: Archivos estáticos servidos directamente
- **`run.py`**: Punto de entrada que inicializa la aplicación Flask
- **`gunicorn-cfg.py`**: Configuración para Gunicorn (puerto, workers, logs)

## Flujos típicos de trabajo

### Desarrollo local

1. Activar entorno virtual: `source venv/bin/activate`
2. Ejecutar en modo desarrollo: `flask run --host=0.0.0.0 --port=8000`
3. Realizar cambios en templates, rutas o estáticos
4. Los cambios se reflejan automáticamente (modo debug activado)

### Despliegue en servidor (Intela Grid)

1. **Push a GitHub**: Subir cambios al repositorio
   ```bash
   git add .
   git commit -m "Descripción de cambios"
   git push origin main
   ```

2. **Pull en el servidor**: Actualizar código en el servidor
   ```bash
   cd /ruta/al/proyecto
   git pull origin main
   ```

3. **Actualizar dependencias** (si hay cambios en `requirements.txt`):
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Reiniciar aplicación con PM2**:
   ```bash
   pm2 restart arsysintela
   ```

5. **Verificar logs**:
   ```bash
   pm2 logs arsysintela
   ```

### Actualización rápida (solo código, sin cambios de dependencias)

```bash
git pull origin main
pm2 restart arsysintela
```

## Configuración de producción

Asegúrate de configurar las siguientes variables en tu `.env` para producción:

```env
DEBUG=False
FLASK_ENV=production
ASSETS_ROOT=/static
SECRET_KEY=<tu-clave-secreta-generada>
```

## Notas adicionales

- La página principal (`/`) renderiza la plantilla `pages/index6.html`
- Los archivos estáticos se sirven desde `apps/static/`
- El proyecto usa SQLite por defecto (configurable en `.env` para MySQL/PostgreSQL)
- La compresión HTML está habilitada en modo producción

## Soporte

Para más información sobre Arsys Intela, visita [tu-sitio-web.com](https://tu-sitio-web.com)

---

**Desarrollado para Arsys Intela** - Infraestructura, IA y Automatización

