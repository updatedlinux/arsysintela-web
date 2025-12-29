# Arsys Intela – Portal de Clientes API

## Descripción General

API REST backend para el Portal de Clientes de Arsys Intela. Esta API proporciona endpoints para autenticación mediante JWT, gestión de usuarios del sistema, gestión de clientes, gestión de productos y la relación entre clientes y productos.

**Propósito**: Servir como backend para login, gestión de usuarios, gestión de clientes y relación con productos.

**Nota importante**: Los **Usuarios (User)** y los **Clientes (Client)** son entidades distintas:
- **User**: Usuarios del sistema que pueden iniciar sesión (autenticación). Son las personas que utilizan la API.
- **Client**: Clientes de negocio, es decir, las empresas o personas que son clientes de Arsys Intela.

---

## Autenticación

### Tipo de Autenticación

La API utiliza **JWT (JSON Web Token)** con esquema **Bearer Token**.

### Endpoint de Login

**POST** `/api/auth/login`

Inicia sesión y obtiene un token JWT válido para realizar peticiones autenticadas.

#### Request

```json
{
  "email": "admin@arsysintela.com",
  "password": "admin123"
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

#### Códigos de Estado

- **200**: Login exitoso
- **400**: Email y contraseña son requeridos
- **401**: Credenciales inválidas

### Uso del Token

Para realizar peticiones autenticadas, incluye el token en el header `Authorization`:

```
Authorization: Bearer <tu_token_jwt>
```

**Ejemplo**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Expiración del Token

El token JWT tiene un tiempo de expiración configurable mediante la variable de entorno `JWT_EXPIRES_IN`. Por defecto es `1d` (1 día).

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
  "timestamp": "2025-01-28T23:30:00.000Z"
}
```

**Campos**:
- `status`: Estado del servicio (siempre "ok" si responde)
- `uptime`: Tiempo de actividad del proceso en segundos
- `timestamp`: Fecha y hora actual en formato ISO 8601

---

## Endpoints Principales

### Autenticación

#### POST `/api/auth/login`

Ver sección [Autenticación](#autenticación) arriba.

---

### Clientes

Todos los endpoints de clientes requieren autenticación JWT.

#### GET `/api/clients`

Obtiene una lista paginada de clientes.

**Autenticación**: Requerida (JWT Bearer Token)

**Query Parameters**:
- `page` (opcional, integer, default: 1): Número de página
- `limit` (opcional, integer, default: 10): Elementos por página

**Ejemplo de Request**:
```
GET /api/clients?page=1&limit=10
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": 1,
      "name": "Juan Pérez",
      "email": "juan.perez@example.com",
      "phone": "+34 600 123 456",
      "company": "Empresa S.L.",
      "notes": "Cliente preferencial",
      "createdAt": "2025-01-15T10:30:00.000Z",
      "updatedAt": "2025-01-15T10:30:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "totalPages": 3
  }
}
```

**Códigos de Estado**:
- **200**: Lista obtenida exitosamente
- **401**: No autorizado (token inválido o faltante)

---

#### GET `/api/clients/{id}`

Obtiene los detalles de un cliente específico, incluyendo sus productos asociados.

**Autenticación**: Requerida (JWT Bearer Token)

**Path Parameters**:
- `id` (required, integer): ID del cliente

**Ejemplo de Request**:
```
GET /api/clients/1
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "name": "Juan Pérez",
  "email": "juan.perez@example.com",
  "phone": "+34 600 123 456",
  "company": "Empresa S.L.",
  "notes": "Cliente preferencial",
  "createdAt": "2025-01-15T10:30:00.000Z",
  "updatedAt": "2025-01-15T10:30:00.000Z",
  "products": [
    {
      "id": 1,
      "code": "ASSISTANT360",
      "name": "Assistant 360",
      "description": "Solución de asistencia virtual 360°",
      "active": true,
      "createdAt": "2025-01-10T08:00:00.000Z",
      "updatedAt": "2025-01-10T08:00:00.000Z",
      "ClientProduct": {
        "id": 1,
        "status": "activo",
        "startDate": "2025-01-15",
        "endDate": null,
        "notes": "Contrato activo"
      }
    }
  ]
}
```

**Códigos de Estado**:
- **200**: Cliente encontrado
- **401**: No autorizado
- **404**: Cliente no encontrado

---

#### POST `/api/clients`

Crea un nuevo cliente.

**Autenticación**: Requerida (JWT Bearer Token)

**Request Body**:
```json
{
  "name": "María García",
  "email": "maria.garcia@example.com",
  "phone": "+34 600 789 012",
  "company": "García & Asociados",
  "notes": "Nuevo cliente"
}
```

**Campos**:
- `name` (required, string): Nombre del cliente
- `email` (optional, string, formato email): Email del cliente
- `phone` (optional, string): Teléfono del cliente
- `company` (optional, string): Empresa del cliente
- `notes` (optional, string): Notas adicionales

**Ejemplo de Request**:
```
POST /api/clients
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "María García",
  "email": "maria.garcia@example.com",
  "phone": "+34 600 789 012",
  "company": "García & Asociados"
}
```

**Response (201 Created)**:
```json
{
  "id": 2,
  "name": "María García",
  "email": "maria.garcia@example.com",
  "phone": "+34 600 789 012",
  "company": "García & Asociados",
  "notes": null,
  "createdAt": "2025-01-28T23:35:00.000Z",
  "updatedAt": "2025-01-28T23:35:00.000Z"
}
```

**Códigos de Estado**:
- **201**: Cliente creado exitosamente
- **400**: Error de validación (nombre requerido, email inválido, etc.)
- **401**: No autorizado
- **409**: Conflicto (email duplicado si tiene restricción única)

---

#### PUT `/api/clients/{id}`

Actualiza los datos de un cliente existente.

**Autenticación**: Requerida (JWT Bearer Token)

**Path Parameters**:
- `id` (required, integer): ID del cliente

**Request Body**:
```json
{
  "name": "María García López",
  "email": "maria.garcia.lopez@example.com",
  "phone": "+34 600 789 013",
  "company": "García & Asociados S.L.",
  "notes": "Cliente actualizado"
}
```

Todos los campos son opcionales. Solo se actualizarán los campos enviados.

**Ejemplo de Request**:
```
PUT /api/clients/2
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "María García López",
  "phone": "+34 600 789 013"
}
```

**Response (200 OK)**:
```json
{
  "id": 2,
  "name": "María García López",
  "email": "maria.garcia@example.com",
  "phone": "+34 600 789 013",
  "company": "García & Asociados",
  "notes": null,
  "createdAt": "2025-01-28T23:35:00.000Z",
  "updatedAt": "2025-01-28T23:40:00.000Z"
}
```

**Códigos de Estado**:
- **200**: Cliente actualizado exitosamente
- **400**: Error de validación
- **401**: No autorizado
- **404**: Cliente no encontrado

---

#### DELETE `/api/clients/{id}`

Elimina un cliente (borrado físico).

**Autenticación**: Requerida (JWT Bearer Token)

**Path Parameters**:
- `id` (required, integer): ID del cliente

**Ejemplo de Request**:
```
DELETE /api/clients/2
Authorization: Bearer <token>
```

**Response (204 No Content)**: Sin cuerpo de respuesta

**Códigos de Estado**:
- **204**: Cliente eliminado exitosamente
- **401**: No autorizado
- **404**: Cliente no encontrado
- **400**: Error de referencia (si el cliente tiene productos asociados y hay restricción de clave foránea)

---

### Productos

Todos los endpoints de productos requieren autenticación JWT.

#### GET `/api/products`

Obtiene una lista paginada de productos, con opción de filtrar por estado activo.

**Autenticación**: Requerida (JWT Bearer Token)

**Query Parameters**:
- `page` (opcional, integer, default: 1): Número de página
- `limit` (opcional, integer, default: 10): Elementos por página
- `active` (opcional, boolean): Filtrar por productos activos (`true` o `false`)

**Ejemplo de Request**:
```
GET /api/products?page=1&limit=10&active=true
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
  "data": [
    {
      "id": 1,
      "code": "ASSISTANT360",
      "name": "Assistant 360",
      "description": "Solución de asistencia virtual 360°",
      "active": true,
      "createdAt": "2025-01-10T08:00:00.000Z",
      "updatedAt": "2025-01-10T08:00:00.000Z"
    },
    {
      "id": 2,
      "code": "CONDOMINIO360",
      "name": "Condominio 360",
      "description": "Gestión integral de condominios",
      "active": true,
      "createdAt": "2025-01-10T08:05:00.000Z",
      "updatedAt": "2025-01-10T08:05:00.000Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 4,
    "totalPages": 1
  }
}
```

**Códigos de Estado**:
- **200**: Lista obtenida exitosamente
- **401**: No autorizado

---

#### GET `/api/products/{id}`

Obtiene los detalles de un producto específico.

**Autenticación**: Requerida (JWT Bearer Token)

**Path Parameters**:
- `id` (required, integer): ID del producto

**Ejemplo de Request**:
```
GET /api/products/1
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "code": "ASSISTANT360",
  "name": "Assistant 360",
  "description": "Solución de asistencia virtual 360°",
  "active": true,
  "createdAt": "2025-01-10T08:00:00.000Z",
  "updatedAt": "2025-01-10T08:00:00.000Z"
}
```

**Códigos de Estado**:
- **200**: Producto encontrado
- **401**: No autorizado
- **404**: Producto no encontrado

---

#### POST `/api/products`

Crea un nuevo producto.

**Autenticación**: Requerida (JWT Bearer Token)

**Request Body**:
```json
{
  "code": "INTELA_NEW",
  "name": "Intela New Product",
  "description": "Nuevo producto de gestión",
  "active": true
}
```

**Campos**:
- `code` (required, string, único): Código único del producto (ej: "ASSISTANT360", "CONDOMINIO360")
- `name` (required, string): Nombre del producto
- `description` (optional, string): Descripción del producto
- `active` (optional, boolean, default: true): Estado activo del producto

**Ejemplo de Request**:
```
POST /api/products
Authorization: Bearer <token>
Content-Type: application/json

{
  "code": "INTELA_NEW",
  "name": "Intela New Product",
  "description": "Nuevo producto de gestión",
  "active": true
}
```

**Response (201 Created)**:
```json
{
  "id": 5,
  "code": "INTELA_NEW",
  "name": "Intela New Product",
  "description": "Nuevo producto de gestión",
  "active": true,
  "createdAt": "2025-01-28T23:45:00.000Z",
  "updatedAt": "2025-01-28T23:45:00.000Z"
}
```

**Códigos de Estado**:
- **201**: Producto creado exitosamente
- **400**: Error de validación (código y nombre requeridos)
- **401**: No autorizado
- **409**: Conflicto (código duplicado)

---

#### PUT `/api/products/{id}`

Actualiza los datos de un producto existente.

**Autenticación**: Requerida (JWT Bearer Token)

**Path Parameters**:
- `id` (required, integer): ID del producto

**Request Body**:
```json
{
  "code": "INTELA_NEW_UPDATED",
  "name": "Intela New Product Updated",
  "description": "Descripción actualizada",
  "active": false
}
```

Todos los campos son opcionales. Solo se actualizarán los campos enviados.

**Ejemplo de Request**:
```
PUT /api/products/5
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Intela New Product Updated",
  "active": false
}
```

**Response (200 OK)**:
```json
{
  "id": 5,
  "code": "INTELA_NEW",
  "name": "Intela New Product Updated",
  "description": "Nuevo producto de gestión",
  "active": false,
  "createdAt": "2025-01-28T23:45:00.000Z",
  "updatedAt": "2025-01-28T23:50:00.000Z"
}
```

**Códigos de Estado**:
- **200**: Producto actualizado exitosamente
- **400**: Error de validación
- **401**: No autorizado
- **404**: Producto no encontrado
- **409**: Conflicto (código duplicado)

---

### Relaciones Cliente-Producto

Todos los endpoints de relaciones cliente-producto requieren autenticación JWT.

#### GET `/api/clients/{id}/products`

Obtiene todos los productos asociados a un cliente específico.

**Autenticación**: Requerida (JWT Bearer Token)

**Path Parameters**:
- `id` (required, integer): ID del cliente

**Ejemplo de Request**:
```
GET /api/clients/1/products
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "clientId": 1,
    "productId": 1,
    "status": "activo",
    "startDate": "2025-01-15",
    "endDate": null,
    "notes": "Contrato activo",
    "createdAt": "2025-01-15T10:30:00.000Z",
    "updatedAt": "2025-01-15T10:30:00.000Z",
    "product": {
      "id": 1,
      "code": "ASSISTANT360",
      "name": "Assistant 360",
      "description": "Solución de asistencia virtual 360°",
      "active": true,
      "createdAt": "2025-01-10T08:00:00.000Z",
      "updatedAt": "2025-01-10T08:00:00.000Z"
    }
  },
  {
    "id": 2,
    "clientId": 1,
    "productId": 2,
    "status": "suspendido",
    "startDate": "2025-01-10",
    "endDate": "2025-02-10",
    "notes": "Suspensión temporal",
    "createdAt": "2025-01-10T09:00:00.000Z",
    "updatedAt": "2025-01-20T14:00:00.000Z",
    "product": {
      "id": 2,
      "code": "CONDOMINIO360",
      "name": "Condominio 360",
      "description": "Gestión integral de condominios",
      "active": true,
      "createdAt": "2025-01-10T08:05:00.000Z",
      "updatedAt": "2025-01-10T08:05:00.000Z"
    }
  }
]
```

**Códigos de Estado**:
- **200**: Lista obtenida exitosamente
- **401**: No autorizado
- **404**: Cliente no encontrado

---

#### POST `/api/clients/{id}/products`

Asocia un producto a un cliente, creando una relación cliente-producto.

**Autenticación**: Requerida (JWT Bearer Token)

**Path Parameters**:
- `id` (required, integer): ID del cliente

**Request Body**:
```json
{
  "product_id": 1,
  "status": "activo",
  "start_date": "2025-01-28",
  "end_date": null,
  "notes": "Nueva asociación"
}
```

**Campos**:
- `product_id` (required, integer): ID del producto a asociar
- `status` (optional, enum: "activo" | "suspendido" | "finalizado", default: "activo"): Estado de la relación
- `start_date` (optional, string, formato: "YYYY-MM-DD"): Fecha de inicio
- `end_date` (optional, string, formato: "YYYY-MM-DD"): Fecha de fin
- `notes` (optional, string): Notas adicionales

**Ejemplo de Request**:
```
POST /api/clients/1/products
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": 3,
  "status": "activo",
  "start_date": "2025-01-28",
  "notes": "Nueva asociación de producto"
}
```

**Response (201 Created)**:
```json
{
  "id": 3,
  "clientId": 1,
  "productId": 3,
  "status": "activo",
  "startDate": "2025-01-28",
  "endDate": null,
  "notes": "Nueva asociación de producto",
  "createdAt": "2025-01-28T23:55:00.000Z",
  "updatedAt": "2025-01-28T23:55:00.000Z",
  "product": {
    "id": 3,
    "code": "INTELA_GRID",
    "name": "Intela Grid",
    "description": "Plataforma de gestión inteligente",
    "active": true,
    "createdAt": "2025-01-10T08:10:00.000Z",
    "updatedAt": "2025-01-10T08:10:00.000Z"
  }
}
```

**Códigos de Estado**:
- **201**: Producto asociado al cliente exitosamente
- **400**: Error de validación (product_id requerido)
- **401**: No autorizado
- **404**: Cliente o producto no encontrado
- **409**: El producto ya está asociado a este cliente

---

#### PUT `/api/client-products/{id}`

Actualiza una relación cliente-producto existente.

**Autenticación**: Requerida (JWT Bearer Token)

**Path Parameters**:
- `id` (required, integer): ID de la relación cliente-producto

**Request Body**:
```json
{
  "status": "suspendido",
  "start_date": "2025-01-15",
  "end_date": "2025-02-15",
  "notes": "Suspensión temporal por mantenimiento"
}
```

Todos los campos son opcionales. Solo se actualizarán los campos enviados.

**Campos**:
- `status` (optional, enum: "activo" | "suspendido" | "finalizado"): Estado de la relación
- `start_date` (optional, string, formato: "YYYY-MM-DD"): Fecha de inicio
- `end_date` (optional, string, formato: "YYYY-MM-DD"): Fecha de fin
- `notes` (optional, string): Notas adicionales

**Ejemplo de Request**:
```
PUT /api/client-products/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "suspendido",
  "end_date": "2025-02-15",
  "notes": "Suspensión temporal"
}
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "clientId": 1,
  "productId": 1,
  "status": "suspendido",
  "startDate": "2025-01-15",
  "endDate": "2025-02-15",
  "notes": "Suspensión temporal",
  "createdAt": "2025-01-15T10:30:00.000Z",
  "updatedAt": "2025-01-28T23:58:00.000Z",
  "product": {
    "id": 1,
    "code": "ASSISTANT360",
    "name": "Assistant 360",
    "description": "Solución de asistencia virtual 360°",
    "active": true,
    "createdAt": "2025-01-10T08:00:00.000Z",
    "updatedAt": "2025-01-10T08:00:00.000Z"
  },
  "client": {
    "id": 1,
    "name": "Juan Pérez",
    "email": "juan.perez@example.com",
    "phone": "+34 600 123 456",
    "company": "Empresa S.L.",
    "notes": "Cliente preferencial",
    "createdAt": "2025-01-15T10:30:00.000Z",
    "updatedAt": "2025-01-15T10:30:00.000Z"
  }
}
```

**Códigos de Estado**:
- **200**: Relación actualizada exitosamente
- **400**: Error de validación
- **401**: No autorizado
- **404**: Relación cliente-producto no encontrada

---

#### DELETE `/api/client-products/{id}`

Elimina una relación cliente-producto (borrado físico).

**Autenticación**: Requerida (JWT Bearer Token)

**Path Parameters**:
- `id` (required, integer): ID de la relación cliente-producto

**Ejemplo de Request**:
```
DELETE /api/client-products/1
Authorization: Bearer <token>
```

**Response (204 No Content)**: Sin cuerpo de respuesta

**Códigos de Estado**:
- **204**: Relación eliminada exitosamente
- **401**: No autorizado
- **404**: Relación cliente-producto no encontrada

---

### Usuarios

**Importante**: Los **Usuarios (User)** y los **Clientes (Client)** son entidades distintas:
- **User**: Representa a los usuarios del sistema que pueden iniciar sesión (autenticación). Son las personas que utilizan la API.
- **Client**: Representa a los clientes de negocio, es decir, las empresas o personas que son clientes de Arsys Intela.

Todos los endpoints de usuarios requieren autenticación JWT. Algunos endpoints adicionalmente requieren rol de administrador.

#### GET `/api/users`

Obtiene una lista de todos los usuarios del sistema.

**Autenticación**: Requerida (JWT Bearer Token) + **Rol admin requerido**

**Ejemplo de Request**:
```
GET /api/users
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "email": "admin@arsysintela.com",
    "name": "Administrador",
    "role": "admin",
    "createdAt": "2025-01-10T08:00:00.000Z",
    "updatedAt": "2025-01-10T08:00:00.000Z"
  },
  {
    "id": 2,
    "email": "usuario@arsysintela.com",
    "name": "Usuario Normal",
    "role": "user",
    "createdAt": "2025-01-15T10:30:00.000Z",
    "updatedAt": "2025-01-15T10:30:00.000Z"
  }
]
```

**Nota**: El campo `passwordHash` nunca se incluye en las respuestas por seguridad.

**Códigos de Estado**:
- **200**: Lista obtenida exitosamente
- **401**: No autorizado (token inválido o faltante)
- **403**: Acceso denegado (se requieren permisos de administrador)

---

#### POST `/api/users`

Crea un nuevo usuario en el sistema. La contraseña se hashea automáticamente antes de guardarse.

**Autenticación**: Requerida (JWT Bearer Token) + **Rol admin requerido**

**Request Body**:
```json
{
  "email": "nuevo@arsysintela.com",
  "password": "password123",
  "name": "Nombre Usuario",
  "role": "user"
}
```

**Campos**:
- `email` (required, string, formato email, único): Email del usuario
- `password` (required, string, mínimo 8 caracteres): Contraseña en texto plano (se hashea automáticamente)
- `name` (optional, string): Nombre del usuario
- `role` (optional, enum: "admin" | "user", default: "user"): Rol del usuario

**Ejemplo de Request**:
```
POST /api/users
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "nuevo@arsysintela.com",
  "password": "password123",
  "name": "Nombre Usuario",
  "role": "user"
}
```

**Response (201 Created)**:
```json
{
  "id": 3,
  "email": "nuevo@arsysintela.com",
  "name": "Nombre Usuario",
  "role": "user",
  "createdAt": "2025-01-28T23:55:00.000Z",
  "updatedAt": "2025-01-28T23:55:00.000Z"
}
```

**Nota**: La contraseña nunca se retorna en la respuesta.

**Códigos de Estado**:
- **201**: Usuario creado exitosamente
- **400**: Error de validación (email inválido, contraseña muy corta, etc.)
- **401**: No autorizado
- **403**: Acceso denegado (se requieren permisos de administrador)
- **409**: Conflicto (el email ya está registrado)

---

#### PUT `/api/users/{id}/password`

Permite cambiar la contraseña de un usuario.

**Autenticación**: Requerida (JWT Bearer Token)

**Reglas de acceso**:
- Si el usuario es **admin**: Puede cambiar la contraseña de cualquier usuario sin necesidad de proporcionar la contraseña actual.
- Si el usuario es el **mismo** (cambia su propia contraseña): Debe proporcionar y validar la contraseña actual.

**Path Parameters**:
- `id` (required, integer): ID del usuario cuya contraseña se desea cambiar

**Request Body**:
```json
{
  "currentPassword": "password_actual",
  "newPassword": "nuevaPassword123"
}
```

**Campos**:
- `currentPassword` (conditional, string): 
  - **Requerido** si el usuario está cambiando su propia contraseña (no admin)
  - **No requerido** si el usuario es admin
- `newPassword` (required, string, mínimo 8 caracteres): Nueva contraseña en texto plano (se hashea automáticamente)

**Ejemplo de Request (usuario cambiando su propia contraseña)**:
```
PUT /api/users/2/password
Authorization: Bearer <token>
Content-Type: application/json

{
  "currentPassword": "password_actual",
  "newPassword": "nuevaPassword123"
}
```

**Ejemplo de Request (admin cambiando contraseña de otro usuario)**:
```
PUT /api/users/2/password
Authorization: Bearer <token>
Content-Type: application/json

{
  "newPassword": "nuevaPassword123"
}
```

**Response (200 OK)**:
```json
{
  "message": "Contraseña actualizada correctamente"
}
```

**Códigos de Estado**:
- **200**: Contraseña actualizada exitosamente
- **400**: Error de validación (contraseña muy corta, falta currentPassword cuando es requerida, etc.)
- **401**: No autorizado o contraseña actual incorrecta
- **404**: Usuario no encontrado

---

## Modelos de Datos

### User

Modelo de usuario para autenticación.

| Campo | Tipo | Requerido | Notas |
|-------|------|-----------|-------|
| `id` | INTEGER | Sí (PK) | Clave primaria, autoincremental |
| `email` | STRING | Sí | Email único, validado como formato email |
| `passwordHash` | STRING | Sí | Hash de la contraseña (bcrypt) |
| `name` | STRING | No | Nombre del usuario |
| `role` | ENUM | Sí | Valores: `'admin'`, `'user'` (default: `'user'`) |
| `createdAt` | DATE | Sí | Fecha de creación (automático) |
| `updatedAt` | DATE | Sí | Fecha de actualización (automático) |

**Tabla en BD**: `users`

---

### Client

Modelo de cliente.

| Campo | Tipo | Requerido | Notas |
|-------|------|-----------|-------|
| `id` | INTEGER | Sí (PK) | Clave primaria, autoincremental |
| `name` | STRING | Sí | Nombre del cliente |
| `email` | STRING | No | Email del cliente, validado como formato email |
| `phone` | STRING | No | Teléfono del cliente |
| `company` | STRING | No | Empresa del cliente |
| `notes` | TEXT | No | Notas adicionales |
| `createdAt` | DATE | Sí | Fecha de creación (automático) |
| `updatedAt` | DATE | Sí | Fecha de actualización (automático) |

**Tabla en BD**: `clients`

**Relaciones**:
- Muchos a muchos con `Product` a través de `ClientProduct`

---

### Product

Modelo de producto.

| Campo | Tipo | Requerido | Notas |
|-------|------|-----------|-------|
| `id` | INTEGER | Sí (PK) | Clave primaria, autoincremental |
| `code` | STRING | Sí | Código único del producto (ej: "ASSISTANT360", "CONDOMINIO360") |
| `name` | STRING | Sí | Nombre del producto |
| `description` | TEXT | No | Descripción del producto |
| `active` | BOOLEAN | Sí | Estado activo del producto (default: `true`) |
| `createdAt` | DATE | Sí | Fecha de creación (automático) |
| `updatedAt` | DATE | Sí | Fecha de actualización (automático) |

**Tabla en BD**: `products`

**Relaciones**:
- Muchos a muchos con `Client` a través de `ClientProduct`

---

### ClientProduct

Modelo de relación muchos-a-muchos entre Cliente y Producto.

| Campo | Tipo | Requerido | Notas |
|-------|------|-----------|-------|
| `id` | INTEGER | Sí (PK) | Clave primaria, autoincremental |
| `clientId` | INTEGER | Sí (FK) | Referencia a `clients.id` |
| `productId` | INTEGER | Sí (FK) | Referencia a `products.id` |
| `status` | ENUM | Sí | Valores: `'activo'`, `'suspendido'`, `'finalizado'` (default: `'activo'`) |
| `startDate` | DATEONLY | No | Fecha de inicio (formato: "YYYY-MM-DD") |
| `endDate` | DATEONLY | No | Fecha de fin (formato: "YYYY-MM-DD") |
| `notes` | TEXT | No | Notas adicionales |
| `createdAt` | DATE | Sí | Fecha de creación (automático) |
| `updatedAt` | DATE | Sí | Fecha de actualización (automático) |

**Tabla en BD**: `client_products`

**Relaciones**:
- Pertenece a `Client` (foreign key: `clientId`)
- Pertenece a `Product` (foreign key: `productId`)

---

## Errores y Formato de Respuesta de Error

### Estructura de Error

Todos los errores retornan un objeto JSON con la siguiente estructura:

```json
{
  "message": "Descripción del error",
  "details": "Información adicional del error (opcional)"
}
```

En modo desarrollo (`NODE_ENV=development`), el campo `details` puede incluir el stack trace completo.

### Tipos de Errores

#### Error de Validación (400)

```json
{
  "message": "Error de validación",
  "details": [
    {
      "field": "email",
      "message": "email must be a valid email"
    },
    {
      "field": "name",
      "message": "name cannot be null"
    }
  ]
}
```

#### Error de Credenciales Inválidas (401)

```json
{
  "message": "Credenciales inválidas"
}
```

#### Error de Token Inválido (401)

```json
{
  "message": "Token inválido o expirado",
  "details": "jwt expired"
}
```

#### Error de Recurso No Encontrado (404)

```json
{
  "message": "Cliente no encontrado"
}
```

#### Error de Conflicto (409)

```json
{
  "message": "Conflicto: el recurso ya existe",
  "details": [
    {
      "field": "code",
      "message": "code must be unique"
    }
  ]
}
```

O para relaciones duplicadas:

```json
{
  "message": "El producto ya está asociado a este cliente"
}
```

#### Error de Referencia (400)

```json
{
  "message": "Error de referencia: recurso relacionado no encontrado",
  "details": "Cannot add or update a child row: a foreign key constraint fails"
}
```

#### Error Interno del Servidor (500)

```json
{
  "message": "Error interno del servidor",
  "details": "Stack trace (solo en desarrollo)"
}
```

### Códigos de Estado HTTP

- **200**: OK - Operación exitosa
- **201**: Created - Recurso creado exitosamente
- **204**: No Content - Operación exitosa sin contenido de respuesta
- **400**: Bad Request - Error de validación o solicitud inválida
- **401**: Unauthorized - No autenticado o token inválido
- **404**: Not Found - Recurso no encontrado
- **409**: Conflict - Conflicto (recurso duplicado)
- **500**: Internal Server Error - Error interno del servidor

---

## Configuración y Entorno

### Variables de Entorno

El API utiliza las siguientes variables de entorno (definidas en archivo `.env`):

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `NODE_ENV` | Entorno de ejecución | `development` |
| `PORT` | Puerto del servidor | `3000` |
| `DB_HOST` | Host de la base de datos | `localhost` |
| `DB_PORT` | Puerto de la base de datos | `3306` |
| `DB_USER` | Usuario de la base de datos | `arsys_portal` |
| `DB_PASSWORD` | Contraseña de la base de datos | `changeme` |
| `DB_NAME` | Nombre de la base de datos | `arsys_portal_db` |
| `JWT_SECRET` | Secreto para firmar tokens JWT | `supersecretkeychangeme` |
| `JWT_EXPIRES_IN` | Tiempo de expiración del token | `1d` |
| `LOG_LEVEL` | Nivel de logging | `info` |

### URLs Base

- **Desarrollo**: `http://localhost:3000/api`
- **Producción**: `https://clientes.arsystech.net/api`

### Ejemplo de archivo `.env`

```env
NODE_ENV=production
PORT=3000

DB_HOST=localhost
DB_PORT=3306
DB_USER=arsys_portal
DB_PASSWORD=tu_contraseña_segura
DB_NAME=arsys_portal_db

JWT_SECRET=tu_secreto_jwt_muy_seguro_y_largo
JWT_EXPIRES_IN=1d

LOG_LEVEL=info
```

---

## Swagger

### Documentación Interactiva

La API incluye documentación Swagger/OpenAPI generada automáticamente desde el código mediante anotaciones JSDoc.

**URL de acceso**:
- **Desarrollo**: `http://localhost:3000/api/docs`
- **Producción**: `https://clientes.arsystech.net/api/docs`

### Características

- Documentación interactiva con interfaz Swagger UI
- Pruebas de endpoints directamente desde el navegador
- Autenticación JWT integrada (botón "Authorize")
- Ejemplos de request y response
- Esquemas de datos completos

### Uso

1. Accede a la URL de documentación Swagger
2. Haz clic en "Authorize" e introduce tu token JWT (obtenido del endpoint `/api/auth/login`)
3. Explora los endpoints y realiza pruebas directamente desde la interfaz

La documentación Swagger se actualiza automáticamente cuando se modifican las anotaciones en el código fuente.

---

## Notas Adicionales

### Paginación

Los endpoints de listado (`GET /api/clients`, `GET /api/products`) soportan paginación mediante parámetros de query:
- `page`: Número de página (default: 1)
- `limit`: Elementos por página (default: 10)

La respuesta incluye un objeto `pagination` con:
- `page`: Página actual
- `limit`: Límite de elementos por página
- `total`: Total de elementos
- `totalPages`: Total de páginas

### Ordenamiento

Los listados están ordenados por fecha de creación descendente (`createdAt DESC`) por defecto.

### Fechas

- Las fechas en la base de datos se almacenan en formato UTC
- Las respuestas JSON incluyen fechas en formato ISO 8601
- Los campos `startDate` y `endDate` en `ClientProduct` usan formato `DATEONLY` (YYYY-MM-DD)

### Autenticación

- Todos los endpoints excepto `/api/health` y `/api/auth/login` requieren autenticación JWT
- El token debe enviarse en el header `Authorization` con el formato: `Bearer <token>`
- Si el token es inválido o ha expirado, se retorna un error 401

---

**Versión del API**: 1.0.0  
**Última actualización**: Enero 2025


