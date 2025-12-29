# Asociación Usuario-Cliente - Guía para Frontend

## 📋 Descripción General

La API del Portal de Clientes implementa una **asociación uno a uno** entre **Usuarios (User)** y **Clientes (Client)** basada en el **email**.

### Concepto Clave

- **User**: Representa la cuenta de acceso al sistema (login/logout, autenticación)
- **Client**: Representa los datos de negocio del cliente (información comercial, productos asociados)

**Relación**: Un usuario tiene un cliente asociado. La asociación se realiza automáticamente por email.

---

## 🔑 Flujo de Trabajo

### 1. Usuario se autentica

El usuario inicia sesión y obtiene un token JWT:

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "cliente@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "cliente@example.com",
    "name": "Juan Pérez",
    "role": "user"
  }
}
```

### 2. Obtener datos del cliente asociado

Una vez autenticado, el usuario puede obtener su cliente asociado usando el endpoint especial:

```http
GET /api/clients/me
Authorization: Bearer <token>
```

**Response (200 OK)**:
```json
{
  "id": 5,
  "name": "Juan Pérez",
  "email": "cliente@example.com",
  "phone": "+34 600 123 456",
  "company": "Empresa S.L.",
  "notes": "Cliente preferencial",
  "userId": 1,
  "createdAt": "2025-01-15T10:30:00.000Z",
  "updatedAt": "2025-01-15T10:30:00.000Z",
  "user": {
    "id": 1,
    "email": "cliente@example.com",
    "name": "Juan Pérez",
    "role": "user"
  },
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

**Response (404 Not Found)** - Si el usuario no tiene cliente asociado:
```json
{
  "message": "No se encontró un cliente asociado a tu cuenta",
  "details": "Contacta al administrador para asociar un cliente a tu usuario"
}
```

---

## 📡 Endpoints Disponibles

### Para Usuarios Autenticados (No Admin)

#### `GET /api/clients/me`

Obtiene el cliente asociado al usuario autenticado.

**Autenticación**: Requerida (JWT Bearer Token)

**Descripción**: 
- Este es el endpoint principal que deben usar los usuarios normales para obtener sus propios datos de cliente
- Incluye automáticamente los productos asociados al cliente
- Incluye información del usuario asociado

**Ejemplo de uso en JavaScript/Fetch**:
```javascript
async function obtenerMiCliente(token) {
  const response = await fetch('https://clientes.arsystech.net/api/clients/me', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });

  if (response.status === 404) {
    // Usuario no tiene cliente asociado
    const error = await response.json();
    console.error(error.message);
    return null;
  }

  if (!response.ok) {
    throw new Error('Error al obtener cliente');
  }

  const cliente = await response.json();
  return cliente;
}

// Uso
const token = localStorage.getItem('authToken');
const miCliente = await obtenerMiCliente(token);
console.log('Mis productos:', miCliente.products);
```

---

### Para Administradores

Los administradores pueden usar todos los endpoints de clientes:

- `GET /api/clients` - Listar todos los clientes
- `GET /api/clients/:id` - Obtener cliente específico
- `POST /api/clients` - Crear cliente
- `PUT /api/clients/:id` - Actualizar cliente
- `DELETE /api/clients/:id` - Eliminar cliente

**Nota**: Estos endpoints ahora incluyen información del usuario asociado en la respuesta.

---

## 🔄 Comportamiento Automático

### Al crear un usuario

Cuando un administrador crea un usuario mediante `POST /api/users`, automáticamente se crea un cliente asociado:

```http
POST /api/users
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "email": "nuevo@example.com",
  "password": "password123",
  "name": "Nuevo Usuario",
  "role": "user"
}
```

**Response**:
```json
{
  "id": 2,
  "email": "nuevo@example.com",
  "name": "Nuevo Usuario",
  "role": "user",
  "clientId": 6,
  "createdAt": "2025-01-29T00:00:00.000Z",
  "updatedAt": "2025-01-29T00:00:00.000Z"
}
```

El campo `clientId` indica que se creó un cliente automáticamente.

### Al crear/actualizar un cliente

Si se crea o actualiza un cliente con un email que coincide con un usuario existente, se asocia automáticamente:

```http
POST /api/clients
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Cliente Nuevo",
  "email": "usuario@example.com",
  "phone": "+34 600 789 012"
}
```

Si existe un usuario con email `usuario@example.com`, el cliente se asociará automáticamente a ese usuario.

---

## 📊 Estructura de Datos

### Respuesta de `GET /api/clients/me`

```typescript
interface ClienteCompleto {
  id: number;
  name: string;
  email: string | null;
  phone: string | null;
  company: string | null;
  notes: string | null;
  userId: number | null;  // ID del usuario asociado
  createdAt: string;
  updatedAt: string;
  user: {
    id: number;
    email: string;
    name: string | null;
    role: 'admin' | 'user';
  } | null;
  products: Array<{
    id: number;
    code: string;
    name: string;
    description: string | null;
    active: boolean;
    createdAt: string;
    updatedAt: string;
    ClientProduct: {
      id: number;
      status: 'activo' | 'suspendido' | 'finalizado';
      startDate: string | null;
      endDate: string | null;
      notes: string | null;
    };
  }>;
}
```

---

## 🎯 Casos de Uso para Frontend

### Caso 1: Dashboard del Cliente

Después del login, obtener los datos del cliente y sus productos:

```javascript
// 1. Login
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const { token, user } = await loginResponse.json();

// Guardar token
localStorage.setItem('authToken', token);

// 2. Obtener datos del cliente
const clienteResponse = await fetch('/api/clients/me', {
  headers: { 'Authorization': `Bearer ${token}` }
});

if (clienteResponse.status === 404) {
  // Usuario no tiene cliente asociado
  mostrarMensaje('Tu cuenta no tiene un cliente asociado. Contacta al administrador.');
  return;
}

const cliente = await clienteResponse.json();

// 3. Mostrar información
console.log('Nombre:', cliente.name);
console.log('Email:', cliente.email);
console.log('Productos activos:', cliente.products.filter(p => p.ClientProduct.status === 'activo'));
```

### Caso 2: Verificar si el usuario tiene cliente

```javascript
async function tieneClienteAsociado(token) {
  try {
    const response = await fetch('/api/clients/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.status === 200;
  } catch (error) {
    return false;
  }
}

// Uso
const token = localStorage.getItem('authToken');
if (await tieneClienteAsociado(token)) {
  // Mostrar dashboard de cliente
} else {
  // Mostrar mensaje de que no tiene cliente asociado
}
```

### Caso 3: Obtener productos del cliente

```javascript
async function obtenerProductosDelCliente(token) {
  const response = await fetch('/api/clients/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });

  if (!response.ok) {
    throw new Error('Error al obtener cliente');
  }

  const cliente = await response.json();
  return cliente.products;
}

// Uso
const productos = await obtenerProductosDelCliente(token);
const productosActivos = productos.filter(p => p.ClientProduct.status === 'activo');
```

---

## ⚠️ Consideraciones Importantes

### 1. Separación de Conceptos

- **User**: Solo para autenticación (login/logout)
- **Client**: Datos de negocio (información comercial, productos)

### 2. Asociación por Email

- La asociación se realiza automáticamente cuando el email del cliente coincide con el email del usuario
- Es case-insensitive (no distingue mayúsculas/minúsculas)
- Si un usuario no tiene cliente asociado, el endpoint `/api/clients/me` retorna 404

### 3. Permisos

- **Usuarios normales**: Solo pueden acceder a su propio cliente mediante `/api/clients/me`
- **Administradores**: Pueden acceder a todos los clientes mediante los endpoints estándar

### 4. Manejo de Errores

```javascript
async function obtenerMiCliente(token) {
  try {
    const response = await fetch('/api/clients/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.status === 401) {
      // Token inválido o expirado
      localStorage.removeItem('authToken');
      redirigirALogin();
      return null;
    }

    if (response.status === 404) {
      // Usuario no tiene cliente asociado
      const error = await response.json();
      return { error: error.message };
    }

    if (!response.ok) {
      throw new Error(`Error ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error al obtener cliente:', error);
    return { error: 'Error de conexión' };
  }
}
```

---

## 🔍 Endpoints Relacionados

### Obtener información del usuario autenticado

El token JWT contiene la información básica del usuario. Si necesitas más información:

```javascript
// Decodificar el token (sin verificar, solo para leer)
function obtenerInfoDelToken(token) {
  const payload = JSON.parse(atob(token.split('.')[1]));
  return {
    id: payload.id,
    email: payload.email,
    role: payload.role
  };
}
```

### Obtener productos del cliente

Los productos ya vienen incluidos en la respuesta de `GET /api/clients/me`. Si necesitas solo los productos:

```javascript
const cliente = await obtenerMiCliente(token);
const productos = cliente.products;
```

O usar el endpoint específico:

```http
GET /api/clients/{id}/products
Authorization: Bearer <token>
```

---

## 📝 Ejemplo Completo de Integración

```javascript
class ClienteService {
  constructor(apiBaseUrl, token) {
    this.apiBaseUrl = apiBaseUrl;
    this.token = token;
  }

  async obtenerMiCliente() {
    const response = await fetch(`${this.apiBaseUrl}/api/clients/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.status === 404) {
      return { error: 'No tiene cliente asociado' };
    }

    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  async obtenerProductosActivos() {
    const cliente = await this.obtenerMiCliente();
    if (cliente.error) {
      return [];
    }
    return cliente.products.filter(
      p => p.ClientProduct.status === 'activo'
    );
  }
}

// Uso
const service = new ClienteService(
  'https://clientes.arsystech.net',
  localStorage.getItem('authToken')
);

const miCliente = await service.obtenerMiCliente();
if (!miCliente.error) {
  console.log('Cliente:', miCliente.name);
  console.log('Productos:', miCliente.products.length);
}
```

---

## 🚀 Migración de Datos Existentes

Si ya tienes usuarios y clientes en la base de datos, ejecuta el script de migración:

```bash
npm run migrate:user-client
```

Este script:
- Asocia automáticamente clientes con usuarios por email
- Crea clientes para usuarios que no tienen cliente asociado
- Es seguro ejecutarlo múltiples veces (idempotente)

---

## 📞 Soporte

Para más información sobre la API completa, consulta:
- Documentación Swagger: `https://clientes.arsystech.net/api/docs`
- Documentación completa: `API_PORTAL_CLIENTES.md`

---

**Última actualización**: Enero 2025  
**Versión API**: 1.0.1

