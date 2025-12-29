# Arsys Intela – Blog API

## Descripción General

API REST backend para el Blog de Arsys Intela. Esta API proporciona endpoints para gestionar posts del blog, permitiendo lectura pública de posts y gestión administrativa mediante autenticación JWT.

**Propósito**: Servir como backend para el blog de Arsys Intela, permitiendo:
- Lectura pública de posts (para el frontend Flask y cualquier consumidor)
- Gestión administrativa de posts (crear, editar, eliminar) desde el Portal de Clientes o interfaces de administración

**URLs**:
- **Producción**: `https://blog.arsystech.net/api`
- **Desarrollo**: `http://localhost:3001/api`

---

## Autenticación

### Tipo de Autenticación

La API utiliza **JWT (JSON Web Token)** con esquema **Bearer Token**. El mismo sistema de autenticación que el Portal de Clientes.

### ⚠️ Importante: Obtener el Token desde Portal de Clientes

**El Blog API NO tiene su propio endpoint de login**. Para obtener un token JWT, debes autenticarte en el **Portal de Clientes API**:

#### Endpoint de Login (Portal de Clientes)

**POST** `https://clientes.arsystech.net/api/auth/login` (Producción)  
**POST** `http://localhost:3000/api/auth/login` (Desarrollo)

#### Request

```json
{
  "email": "admin@arsysintela.com",
  "password": "tu_password"
}
```

#### Response (200 OK)

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiZW1haWwiOiJhZG1pbkBhcnN5c2ludGVsYS5jb20iLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3MDUzMjE2NDYsImV4cCI6MTcwNTQwODA0Nn0.example",
  "user": {
    "id": 1,
    "email": "admin@arsysintela.com",
    "name": "Administrador",
    "role": "admin"
  }
}
```

#### Requisitos para Gestión de Posts

- **Rol requerido**: `admin`
- Solo usuarios con rol `admin` pueden crear, editar o eliminar posts
- Los endpoints de lectura (GET) son **públicos** y no requieren autenticación

### Uso del Token en Blog API

Una vez obtenido el token del Portal de Clientes, úsalo en el Blog API incluyéndolo en el header `Authorization`:

```
Authorization: Bearer <tu_token_jwt>
```

**Ejemplo**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Expiración del Token

El token JWT tiene un tiempo de expiración configurable. Por defecto es `1d` (1 día). Cuando el token expire, deberás obtener uno nuevo desde el Portal de Clientes.

---

## Healthcheck

### GET `/api/health`

Verifica el estado de la API y retorna información básica del servicio.

**Autenticación**: No requerida

#### Response (200 OK)

```json
{
  "status": "ok",
  "uptime": 12345.67,
  "timestamp": "2025-01-30T00:00:00.000Z",
  "service": "arsys-blog-api"
}
```

**Campos**:
- `status`: Estado del servicio (siempre "ok" si responde)
- `uptime`: Tiempo de actividad del proceso en segundos
- `timestamp`: Fecha y hora actual en formato ISO 8601
- `service`: Nombre del servicio

---

## Endpoints Principales

### Posts

#### GET `/api/posts`

Lista posts publicados con paginación y filtrado opcional por tag.

**Autenticación**: No requerida (público)

**Query Parameters**:
- `page` (opcional, default: 1): Número de página
- `limit` (opcional, default: 6): Cantidad de posts por página
- `tag` (opcional): Filtrar posts por tag (ej: "Infraestructura", "IA", "Condominio")

**Ejemplo de Request**:
```http
GET /api/posts?page=1&limit=6&tag=Infraestructura
```

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": 1,
      "title": "Cómo combinar infraestructura privada e IA para tu negocio",
      "slug": "como-combinar-infraestructura-privada-ia-negocio",
      "excerpt": "Descubre cómo la combinación de infraestructura privada e inteligencia artificial puede transformar tu negocio.",
      "author": "Rabby Mahmud",
      "tag": "Infraestructura",
      "publishedAt": "2025-01-15T10:00:00.000Z",
      "headerImageUrl": "https://placehold.co/800x400/0066CC/FFFFFF?text=Infraestructura+Privada+e+IA"
    },
    {
      "id": 2,
      "title": "Automatización de condominios y edificios con Intela Smart",
      "slug": "automatizacion-condominios-edificios-intela-smart",
      "excerpt": "Intela Smart revoluciona la gestión de condominios mediante automatización inteligente.",
      "author": "María González",
      "tag": "Condominio",
      "publishedAt": "2025-01-20T14:30:00.000Z",
      "headerImageUrl": "https://placehold.co/800x400/00AA44/FFFFFF?text=Intela+Smart+Condominios"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 6,
    "total": 20,
    "totalPages": 4
  }
}
```

**Campos de respuesta**:
- `data`: Array de posts (solo campos resumidos, sin `contentHtml`)
- `pagination`: Información de paginación
  - `page`: Página actual
  - `limit`: Elementos por página
  - `total`: Total de posts que cumplen los filtros
  - `totalPages`: Total de páginas

**Códigos de Estado**:
- **200**: Lista obtenida exitosamente
- **500**: Error interno del servidor

---

#### GET `/api/posts/:slug`

Obtiene el post completo por su slug (incluyendo el contenido HTML completo).

**Autenticación**: No requerida (público)

**Path Parameters**:
- `slug` (requerido): Slug único del post (ej: "como-combinar-infraestructura-privada-ia-negocio")

**Ejemplo de Request**:
```http
GET /api/posts/como-combinar-infraestructura-privada-ia-negocio
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "title": "Cómo combinar infraestructura privada e IA para tu negocio",
  "slug": "como-combinar-infraestructura-privada-ia-negocio",
  "excerpt": "Descubre cómo la combinación de infraestructura privada e inteligencia artificial puede transformar tu negocio, mejorando la eficiencia y reduciendo costos operativos.",
  "author": "Rabby Mahmud",
  "tag": "Infraestructura",
  "publishedAt": "2025-01-15T10:00:00.000Z",
  "headerImageUrl": "https://placehold.co/800x400/0066CC/FFFFFF?text=Infraestructura+Privada+e+IA",
  "contentHtml": "<h2>Introducción</h2><p>En el mundo empresarial actual, la combinación de infraestructura privada e inteligencia artificial se ha convertido en una estrategia clave...</p><h2>Beneficios de la Infraestructura Privada</h2><p>La infraestructura privada ofrece control total sobre los recursos...</p>",
  "isPublished": true,
  "createdAt": "2025-01-15T10:00:00.000Z",
  "updatedAt": "2025-01-15T10:00:00.000Z"
}
```

**Campos de respuesta**:
- Todos los campos del post, incluyendo `contentHtml` (contenido completo en HTML)

**Códigos de Estado**:
- **200**: Post encontrado
- **404**: Post no encontrado o no publicado
- **500**: Error interno del servidor

---

#### POST `/api/posts`

Crea un nuevo post en el blog.

**Autenticación**: Requerida (JWT Bearer Token)  
**Rol requerido**: `admin`

**Request Body**:
```json
{
  "title": "Nuevo Post del Blog",
  "excerpt": "Resumen corto del post que aparecerá en listados y cards",
  "author": "Nombre del Autor",
  "tag": "Infraestructura",
  "publishedAt": "2025-01-30T12:00:00.000Z",
  "headerImageUrl": "https://example.com/imagen-cabecera.jpg",
  "contentHtml": "<h2>Título Sección</h2><p>Contenido del post en HTML...</p>",
  "isPublished": true
}
```

**Campos requeridos**:
- `title` (string): Título del post
- `excerpt` (string): Resumen del post
- `author` (string): Nombre del autor
- `publishedAt` (string, ISO 8601): Fecha de publicación
- `headerImageUrl` (string, URL): URL de la imagen de cabecera
- `contentHtml` (string): Contenido completo en HTML

**Campos opcionales**:
- `tag` (string): Tag del post (ej: "Infraestructura", "IA", "Condominio")
- `isPublished` (boolean, default: true): Si el post está publicado

**Nota**: El `slug` se genera automáticamente desde el `title`. Si el slug ya existe, se añade un sufijo numérico (ej: "titulo-post-1").

**Response (201 Created)**:
```json
{
  "id": 7,
  "title": "Nuevo Post del Blog",
  "slug": "nuevo-post-del-blog",
  "excerpt": "Resumen corto del post que aparecerá en listados y cards",
  "author": "Nombre del Autor",
  "tag": "Infraestructura",
  "publishedAt": "2025-01-30T12:00:00.000Z",
  "headerImageUrl": "https://example.com/imagen-cabecera.jpg",
  "contentHtml": "<h2>Título Sección</h2><p>Contenido del post en HTML...</p>",
  "isPublished": true,
  "createdAt": "2025-01-30T12:00:00.000Z",
  "updatedAt": "2025-01-30T12:00:00.000Z"
}
```

**Códigos de Estado**:
- **201**: Post creado exitosamente
- **400**: Error de validación (campos requeridos faltantes o inválidos)
- **401**: No autenticado (token faltante o inválido)
- **403**: No autorizado (usuario no es admin)
- **409**: Conflicto (slug duplicado, aunque esto es raro ya que se genera automáticamente)
- **500**: Error interno del servidor

---

#### PUT `/api/posts/:id`

Actualiza un post existente.

**Autenticación**: Requerida (JWT Bearer Token)  
**Rol requerido**: `admin`

**Path Parameters**:
- `id` (requerido): ID del post a actualizar

**Request Body** (todos los campos son opcionales, solo envía los que quieras actualizar):
```json
{
  "title": "Título Actualizado",
  "excerpt": "Nuevo resumen",
  "author": "Nuevo Autor",
  "tag": "IA",
  "publishedAt": "2025-02-01T10:00:00.000Z",
  "headerImageUrl": "https://example.com/nueva-imagen.jpg",
  "contentHtml": "<h2>Contenido Actualizado</h2><p>Nuevo contenido...</p>",
  "isPublished": false
}
```

**Nota**: Si actualizas el `title`, el `slug` se regenerará automáticamente. Si el nuevo slug ya existe (para otro post), se añadirá un sufijo numérico.

**Response (200 OK)**:
```json
{
  "id": 1,
  "title": "Título Actualizado",
  "slug": "titulo-actualizado",
  "excerpt": "Nuevo resumen",
  "author": "Nuevo Autor",
  "tag": "IA",
  "publishedAt": "2025-02-01T10:00:00.000Z",
  "headerImageUrl": "https://example.com/nueva-imagen.jpg",
  "contentHtml": "<h2>Contenido Actualizado</h2><p>Nuevo contenido...</p>",
  "isPublished": false,
  "createdAt": "2025-01-15T10:00:00.000Z",
  "updatedAt": "2025-02-01T10:00:00.000Z"
}
```

**Códigos de Estado**:
- **200**: Post actualizado exitosamente
- **400**: Error de validación
- **401**: No autenticado
- **403**: No autorizado (usuario no es admin)
- **404**: Post no encontrado
- **500**: Error interno del servidor

---

#### DELETE `/api/posts/:id`

Elimina un post del blog (borrado físico).

**Autenticación**: Requerida (JWT Bearer Token)  
**Rol requerido**: `admin`

**Path Parameters**:
- `id` (requerido): ID del post a eliminar

**Response (200 OK)**:
```json
{
  "message": "Post eliminado correctamente",
  "id": 1
}
```

**Códigos de Estado**:
- **200**: Post eliminado exitosamente
- **401**: No autenticado
- **403**: No autorizado (usuario no es admin)
- **404**: Post no encontrado
- **500**: Error interno del servidor

---

## Modelos de Datos

### Post

| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| `id` | INTEGER | ID único (PK, autoincrement) | Sí (auto) |
| `title` | STRING(255) | Título del post | Sí |
| `slug` | STRING(255) | Slug único generado desde el título | Sí (auto) |
| `excerpt` | TEXT | Resumen del post (para cards/listados) | Sí |
| `author` | STRING(100) | Nombre del autor | Sí |
| `tag` | STRING(50) | Tag del post (ej: "Infraestructura", "IA") | No |
| `publishedAt` | DATE | Fecha de publicación | Sí |
| `headerImageUrl` | STRING(500) | URL de la imagen de cabecera | Sí |
| `contentHtml` | TEXT | Contenido completo en HTML | Sí |
| `isPublished` | BOOLEAN | Si el post está publicado | No (default: true) |
| `createdAt` | DATE | Fecha de creación | Sí (auto) |
| `updatedAt` | DATE | Fecha de última actualización | Sí (auto) |

**Notas**:
- El `slug` se genera automáticamente desde el `title`, convirtiendo a minúsculas, eliminando acentos y caracteres especiales, y reemplazando espacios por guiones.
- Si un slug ya existe, se añade un sufijo numérico (ej: "titulo-post-1").
- Solo posts con `isPublished: true` aparecen en los endpoints públicos de lectura.

---

## Errores y Formato de Respuesta de Error

### Estructura de Error

Todos los errores siguen el mismo formato JSON:

```json
{
  "message": "Descripción del error",
  "details": "Información adicional (opcional)"
}
```

### Ejemplos de Errores

#### 400 Bad Request (Validación)
```json
{
  "message": "Error de validación",
  "details": [
    {
      "field": "title",
      "message": "title no puede estar vacío"
    },
    {
      "field": "headerImageUrl",
      "message": "headerImageUrl debe ser una URL válida"
    }
  ]
}
```

#### 401 Unauthorized (No autenticado)
```json
{
  "message": "Token de autenticación requerido",
  "details": "Debe proporcionar un token JWT válido en el header Authorization: Bearer <token>"
}
```

#### 403 Forbidden (No autorizado)
```json
{
  "message": "Acceso denegado",
  "details": "Solo los administradores pueden realizar esta acción"
}
```

#### 404 Not Found
```json
{
  "message": "Post no encontrado",
  "details": "No se encontró un post publicado con el slug: post-inexistente"
}
```

#### 409 Conflict (Duplicado)
```json
{
  "message": "Conflicto: el recurso ya existe",
  "details": [
    {
      "field": "slug",
      "message": "slug must be unique"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "message": "Error interno del servidor",
  "details": "Mensaje detallado (solo en desarrollo)"
}
```

---

## Configuración y Entorno

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `NODE_ENV` | Entorno de ejecución (development/production) | `development` |
| `PORT` | Puerto del servidor | `3001` |
| `DB_HOST` | Host de MariaDB | `localhost` |
| `DB_PORT` | Puerto de MariaDB | `3306` |
| `DB_USER` | Usuario de MariaDB | `arsys_blog` |
| `DB_PASSWORD` | Contraseña de MariaDB | - |
| `DB_NAME` | Nombre de la base de datos | `arsys_blog_db` |
| `JWT_SECRET` | Secreto para firmar tokens JWT | - |
| `JWT_EXPIRES_IN` | Tiempo de expiración del token | `1d` |
| `LOG_LEVEL` | Nivel de logging (error/warn/info/debug) | `info` |

### URLs Base

- **Producción**: `https://blog.arsystech.net/api`
- **Desarrollo**: `http://localhost:3001/api`

---

## Swagger / OpenAPI

La documentación interactiva de la API está disponible en:

- **Producción**: `https://blog.arsystech.net/api/docs`
- **Desarrollo**: `http://localhost:3001/api/docs`

En Swagger UI puedes:
- Ver todos los endpoints disponibles
- Probar los endpoints directamente desde el navegador
- Ver ejemplos de request/response
- Autenticarte con tu token JWT (botón "Authorize")

---

## Ejemplos de Integración para Frontend

### JavaScript/Fetch

#### 1. Obtener Token desde Portal de Clientes

```javascript
async function obtenerToken(email, password) {
  const response = await fetch('https://clientes.arsystech.net/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error('Error al autenticarse');
  }

  const data = await response.json();
  return data.token; // Guardar este token para usar en Blog API
}

// Uso
const token = await obtenerToken('admin@arsysintela.com', 'password123');
localStorage.setItem('blogToken', token);
```

#### 2. Listar Posts (Público)

```javascript
async function listarPosts(page = 1, limit = 6, tag = null) {
  let url = `https://blog.arsystech.net/api/posts?page=${page}&limit=${limit}`;
  if (tag) {
    url += `&tag=${encodeURIComponent(tag)}`;
  }

  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error('Error al obtener posts');
  }

  return await response.json();
}

// Uso
const { data: posts, pagination } = await listarPosts(1, 6, 'Infraestructura');
console.log('Posts:', posts);
console.log('Total páginas:', pagination.totalPages);
```

#### 3. Obtener Post por Slug (Público)

```javascript
async function obtenerPostPorSlug(slug) {
  const response = await fetch(`https://blog.arsystech.net/api/posts/${slug}`);
  
  if (response.status === 404) {
    return null; // Post no encontrado
  }

  if (!response.ok) {
    throw new Error('Error al obtener post');
  }

  return await response.json();
}

// Uso
const post = await obtenerPostPorSlug('como-combinar-infraestructura-privada-ia-negocio');
if (post) {
  console.log('Título:', post.title);
  console.log('Contenido HTML:', post.contentHtml);
}
```

#### 4. Crear Post (Admin)

```javascript
async function crearPost(postData, token) {
  const response = await fetch('https://blog.arsystech.net/api/posts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(postData),
  });

  if (response.status === 401) {
    throw new Error('Token inválido o expirado');
  }

  if (response.status === 403) {
    throw new Error('No tienes permisos de administrador');
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Error al crear post');
  }

  return await response.json();
}

// Uso
const token = localStorage.getItem('blogToken');
const nuevoPost = await crearPost({
  title: 'Nuevo Post',
  excerpt: 'Resumen del post',
  author: 'Autor',
  tag: 'Infraestructura',
  publishedAt: new Date().toISOString(),
  headerImageUrl: 'https://example.com/imagen.jpg',
  contentHtml: '<h2>Título</h2><p>Contenido...</p>',
  isPublished: true,
}, token);
```

#### 5. Actualizar Post (Admin)

```javascript
async function actualizarPost(id, postData, token) {
  const response = await fetch(`https://blog.arsystech.net/api/posts/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(postData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Error al actualizar post');
  }

  return await response.json();
}

// Uso
const token = localStorage.getItem('blogToken');
const postActualizado = await actualizarPost(1, {
  title: 'Título Actualizado',
  excerpt: 'Nuevo resumen',
}, token);
```

#### 6. Eliminar Post (Admin)

```javascript
async function eliminarPost(id, token) {
  const response = await fetch(`https://blog.arsystech.net/api/posts/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Error al eliminar post');
  }

  return await response.json();
}

// Uso
const token = localStorage.getItem('blogToken');
await eliminarPost(1, token);
```

### Clase de Servicio Completa

```javascript
class BlogAPIService {
  constructor(baseUrl = 'https://blog.arsystech.net/api', token = null) {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  setToken(token) {
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token && !endpoint.includes('/posts') || options.requiresAuth) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Error desconocido' }));
      throw new Error(error.message || `Error ${response.status}`);
    }

    return await response.json();
  }

  // Endpoints públicos
  async getPosts(page = 1, limit = 6, tag = null) {
    let endpoint = `/posts?page=${page}&limit=${limit}`;
    if (tag) endpoint += `&tag=${encodeURIComponent(tag)}`;
    return this.request(endpoint);
  }

  async getPostBySlug(slug) {
    return this.request(`/posts/${slug}`);
  }

  async getHealth() {
    return this.request('/health');
  }

  // Endpoints admin (requieren autenticación)
  async createPost(postData) {
    return this.request('/posts', {
      method: 'POST',
      body: JSON.stringify(postData),
      requiresAuth: true,
    });
  }

  async updatePost(id, postData) {
    return this.request(`/posts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(postData),
      requiresAuth: true,
    });
  }

  async deletePost(id) {
    return this.request(`/posts/${id}`, {
      method: 'DELETE',
      requiresAuth: true,
    });
  }
}

// Uso
const blogAPI = new BlogAPIService();
blogAPI.setToken(localStorage.getItem('blogToken'));

// Obtener posts
const { data: posts } = await blogAPI.getPosts(1, 6, 'Infraestructura');

// Obtener post completo
const post = await blogAPI.getPostBySlug('como-combinar-infraestructura-privada-ia-negocio');

// Crear post (requiere token admin)
const nuevoPost = await blogAPI.createPost({
  title: 'Nuevo Post',
  excerpt: 'Resumen',
  author: 'Autor',
  publishedAt: new Date().toISOString(),
  headerImageUrl: 'https://example.com/imagen.jpg',
  contentHtml: '<p>Contenido...</p>',
});
```

### Python (Flask/Requests)

```python
import requests
from datetime import datetime

class BlogAPI:
    def __init__(self, base_url='https://blog.arsystech.net/api', token=None):
        self.base_url = base_url
        self.token = token
        self.headers = {'Content-Type': 'application/json'}
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
    
    def get_posts(self, page=1, limit=6, tag=None):
        url = f'{self.base_url}/posts'
        params = {'page': page, 'limit': limit}
        if tag:
            params['tag'] = tag
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_post_by_slug(self, slug):
        url = f'{self.base_url}/posts/{slug}'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def create_post(self, post_data):
        url = f'{self.base_url}/posts'
        response = requests.post(url, json=post_data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def update_post(self, post_id, post_data):
        url = f'{self.base_url}/posts/{post_id}'
        response = requests.put(url, json=post_data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def delete_post(self, post_id):
        url = f'{self.base_url}/posts/{post_id}'
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

# Uso
# 1. Obtener token desde Portal de Clientes
portal_response = requests.post(
    'https://clientes.arsystech.net/api/auth/login',
    json={'email': 'admin@arsysintela.com', 'password': 'password123'}
)
token = portal_response.json()['token']

# 2. Usar Blog API
blog_api = BlogAPI(token=token)

# Obtener posts
posts_data = blog_api.get_posts(page=1, limit=6, tag='Infraestructura')
print(f"Total posts: {posts_data['pagination']['total']}")

# Obtener post completo
post = blog_api.get_post_by_slug('como-combinar-infraestructura-privada-ia-negocio')
print(f"Título: {post['title']}")

# Crear post
nuevo_post = blog_api.create_post({
    'title': 'Nuevo Post',
    'excerpt': 'Resumen',
    'author': 'Autor',
    'tag': 'Infraestructura',
    'publishedAt': datetime.now().isoformat(),
    'headerImageUrl': 'https://example.com/imagen.jpg',
    'contentHtml': '<h2>Título</h2><p>Contenido...</p>',
    'isPublished': True
})
```

---

## Consideraciones Importantes

### 1. Autenticación Compartida

- El Blog API **NO tiene su propio endpoint de login**
- Debes obtener el token desde el **Portal de Clientes API**: `POST /api/auth/login`
- El mismo token funciona en ambas APIs
- Solo usuarios con rol `admin` pueden gestionar posts

### 2. Endpoints Públicos vs Protegidos

- **Públicos** (sin autenticación):
  - `GET /api/posts` - Listar posts
  - `GET /api/posts/:slug` - Obtener post completo
  - `GET /api/health` - Healthcheck

- **Protegidos** (requieren JWT + rol admin):
  - `POST /api/posts` - Crear post
  - `PUT /api/posts/:id` - Actualizar post
  - `DELETE /api/posts/:id` - Eliminar post

### 3. Generación de Slugs

- Los slugs se generan automáticamente desde el título
- Son únicos: si un slug ya existe, se añade un sufijo numérico
- No es necesario (ni recomendado) enviar el slug manualmente

### 4. Filtrado y Paginación

- Usa `?page=1&limit=6` para paginación
- Usa `?tag=Infraestructura` para filtrar por tag
- Puedes combinar ambos: `?page=1&limit=6&tag=IA`

### 5. Manejo de Errores

- Siempre verifica el código de estado HTTP
- Los errores 401 indican token inválido/expirado → obtener nuevo token
- Los errores 403 indican falta de permisos → verificar rol admin
- Los errores 404 indican recurso no encontrado

### 6. CORS

- El Blog API está configurado para aceptar requests desde:
  - `https://www.arsysintela.com`
  - `https://arsysintela.com`
  - `http://localhost:5000` (Flask en desarrollo)

---

## Troubleshooting

### Error 401: Token inválido o expirado

**Solución**: Obtén un nuevo token desde el Portal de Clientes:
```javascript
const response = await fetch('https://clientes.arsystech.net/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password }),
});
const { token } = await response.json();
```

### Error 403: No autorizado

**Causa**: El usuario no tiene rol `admin`.  
**Solución**: Verifica que el usuario tenga rol `admin` en el Portal de Clientes.

### Posts no aparecen en listado

**Causas posibles**:
- El post tiene `isPublished: false`
- La fecha `publishedAt` es futura (si aplica lógica adicional)
- El filtro por `tag` no coincide

**Solución**: Verifica estos campos en la base de datos o al crear/actualizar el post.

### Error de CORS

**Causa**: El origen no está permitido en la configuración CORS.  
**Solución**: Contacta al administrador para agregar tu dominio a la lista de orígenes permitidos.

---

## Recursos Adicionales

- **Documentación Swagger**: `https://blog.arsystech.net/api/docs`
- **Portal de Clientes API**: `https://clientes.arsystech.net/api/docs`
- **Healthcheck**: `https://blog.arsystech.net/api/health`

---

**Última actualización**: Enero 2025  
**Versión API**: 1.0.0

