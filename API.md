# API Documentation

> Documentación completa de los endpoints REST del backend de rutinas de gimnasio.
> Base URL: `http://localhost:8000`
> Versión: `1.0.0`
> Swagger UI: `/api/docs/` · Redoc: `/api/redoc/` · Schema: `/api/schema/`

---

## Convenciones generales

- **Content-Type**: `application/json` en todas las requests y responses.
- **Autenticación**: JWT Bearer en header `Authorization: Bearer <access_token>`.
- **Paginación**: todas las listas siguen `PageNumberPagination` (página 20 por defecto).
  ```json
  { "count": 42, "next": "...?page=2", "previous": null, "results": [ ... ] }
  ```
- **Fechas**: ISO 8601 (`YYYY-MM-DD` para fechas, `YYYY-MM-DDTHH:MM:SSZ` para datetime).
- **Errores**:
  ```json
  { "detail": "Mensaje descriptivo." }
  ```
  o, en validación:
  ```json
  { "field": ["Error message."] }
  ```
- **Códigos**:
  - `200 OK` éxito
  - `201 Created` creado
  - `204 No Content` borrado
  - `205 Reset Content` logout OK
  - `400 Bad Request` validación
  - `401 Unauthorized` sin token / token inválido
  - `403 Forbidden` sin permiso
  - `404 Not Found` recurso no existe

---

## Índice de endpoints

### Autenticación
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`

### Usuarios
- `GET    /api/users/`
- `GET    /api/users/{id}/`
- `GET    /api/users/me/`
- `PATCH  /api/users/me/`
- `POST   /api/users/me/change-password/`

### Roles
- `GET    /api/roles/`
- `POST   /api/roles/`
- `GET    /api/roles/{id}/`
- `PATCH  /api/roles/{id}/`
- `DELETE /api/roles/{id}/`

### Músculos
- `GET    /api/muscles/`
- `POST   /api/muscles/`
- `GET    /api/muscles/{id}/`
- `PATCH  /api/muscles/{id}/`
- `DELETE /api/muscles/{id}/`

### Ejercicios
- `GET    /api/exercises/`
- `POST   /api/exercises/`
- `GET    /api/exercises/{id}/`
- `PATCH  /api/exercises/{id}/`
- `DELETE /api/exercises/{id}/`
- `GET    /api/exercises/{id}/muscles/`

### Técnicas de intensidad
- `GET    /api/intensity-techniques/`
- `POST   /api/intensity-techniques/`
- `GET    /api/intensity-techniques/{id}/`
- `PATCH  /api/intensity-techniques/{id}/`
- `DELETE /api/intensity-techniques/{id}/`

### Splits (plantillas globales)
- `GET    /api/splits/`
- `POST   /api/splits/`
- `GET    /api/splits/{id}/`
- `PATCH  /api/splits/{id}/`
- `DELETE /api/splits/{id}/`
- `GET    /api/splits/{id}/days/`
- `POST   /api/splits/{id}/days/`
- `PATCH  /api/splits/{id}/days/{dayId}/`
- `DELETE /api/splits/{id}/days/{dayId}/`

### Mis splits (adopción)
- `GET    /api/my-splits/`
- `POST   /api/my-splits/`
- `GET    /api/my-splits/{id}/`
- `PATCH  /api/my-splits/{id}/`
- `DELETE /api/my-splits/{id}/`
- `GET    /api/my-splits/active/`

### Mis rutinas
- `GET    /api/my-routines/`
- `POST   /api/my-routines/`
- `GET    /api/my-routines/{id}/`
- `PATCH  /api/my-routines/{id}/`
- `DELETE /api/my-routines/{id}/`
- `GET    /api/my-routines/by-day/?dayId=...`

### Workouts
- `GET    /api/workouts/`
- `POST   /api/workouts/`
- `GET    /api/workouts/{id}/`
- `PATCH  /api/workouts/{id}/`
- `DELETE /api/workouts/{id}/`
- `GET    /api/workouts/stats/`

### Mis ejercicios (favoritos)
- `GET    /api/my-exercises/`
- `POST   /api/my-exercises/`
- `DELETE /api/my-exercises/{id}/`

---

## Autenticación

### `POST /api/auth/register`

Crea un usuario nuevo con rol `user` por defecto.

**Permiso**: público.

**Request body**
```json
{
  "firstName": "Juan",
  "lastName": "Perez",
  "userName": "juanperez",
  "email": "juan@example.com",
  "password": "StrongPass123!",
  "passwordConfirm": "StrongPass123!"
}
```

**Respuesta `201 Created`**
```json
{
  "id": 1,
  "firstName": "Juan",
  "lastName": "Perez",
  "fullName": "Juan Perez",
  "userName": "juanperez",
  "email": "juan@example.com",
  "status": true,
  "lastLogin": null,
  "role": { "id": 3, "name": "user", "description": "Regular gym user" },
  "roleId": null,
  "created": "2026-08-17T10:00:00Z",
  "updated": "2026-08-17T10:00:00Z"
}
```

**Errores**
- `400` — `passwordConfirm` no coincide.
- `400` — `email`/`userName` ya existe.

---

### `POST /api/auth/login`

Devuelve tokens JWT (`access` + `refresh`) y datos del usuario.

**Permiso**: público. Throttling: `5/min`.

**Request body**
```json
{ "email": "juan@example.com", "password": "StrongPass123!" }
```

**Respuesta `200 OK`**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { "id": 1, "email": "juan@example.com", "...": "..." }
}
```

**Errores**
- `401` — credenciales inválidas.

---

### `POST /api/auth/refresh`

Renueva el `access` token a partir de un `refresh` válido.

**Permiso**: público.

**Request body**
```json
{ "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

**Respuesta `200 OK`**
```json
{ "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

Si `ROTATE_REFRESH_TOKENS=True`, también devuelve un nuevo `refresh`.

---

### `POST /api/auth/logout`

Invalida el `refresh` token (lo añade a la blacklist).

**Permiso**: autenticado.

**Request body**
```json
{ "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

**Respuesta `205 Reset Content`**
```json
{ "detail": "Logged out." }
```

---

## Usuarios

### `GET /api/users/`

Lista todos los usuarios.

**Permiso**: solo `admin`.

**Query params**
- `role=admin|trainer|user` — filtra por nombre de rol.

**Respuesta `200 OK`**: ver forma de usuario.

---

### `GET /api/users/{id}/`

Detalle de un usuario.

**Permiso**: solo `admin`.

---

### `GET /api/users/me/`

Datos del usuario autenticado.

**Permiso**: autenticado.

**Respuesta `200 OK`**
```json
{
  "id": 1, "firstName": "Juan", "lastName": "Perez",
  "userName": "juanperez", "email": "juan@example.com",
  "status": true, "lastLogin": "2026-08-17T10:05:00Z",
  "role": { "id": 3, "name": "user", "description": "Regular gym user" },
  "fullName": "Juan Perez",
  "created": "...", "updated": "..."
}
```

---

### `PATCH /api/users/me/`

Actualización parcial del perfil del usuario autenticado.

**Permiso**: autenticado.

**Request body** (todos opcionales)
```json
{ "firstName": "Juan Carlos", "userName": "juanp" }
```

**Respuesta `200 OK`**: usuario actualizado.

---

### `POST /api/users/me/change-password/`

Cambia la contraseña del usuario autenticado.

**Permiso**: autenticado.

**Request body**
```json
{ "currentPassword": "StrongPass123!", "newPassword": "EvenStronger456!" }
```

**Respuesta `200 OK`**
```json
{ "detail": "Password updated." }
```

**Errores**
- `400` — `currentPassword` incorrecta.
- `400` — `newPassword` no cumple validadores.

---

## Roles

### `GET /api/roles/`
Lista roles. **Permiso**: solo `admin`.

### `POST /api/roles/`
Crea un rol. **Permiso**: solo `admin`.

**Request body**
```json
{ "name": "coach", "description": "Assistant trainer" }
```

**Respuesta `201 Created`**
```json
{
  "id": 4,
  "name": "coach",
  "description": "Assistant trainer",
  "status": true,
  "created": "...",
  "updated": "..."
}
```

### `GET / PATCH / DELETE /api/roles/{id}/`
Acciones estándar sobre un rol. Permiso: solo `admin`.

---

## Músculos

### `GET /api/muscles/`
Lista músculos (paginado). **Permiso**: autenticado (cualquier rol).

**Query params**
- `search=biceps` — busca por nombre (icontains).
- `ordering=name|-name|created|-created`.

### `POST /api/muscles/`
Crea un músculo. **Permiso**: `admin` o `trainer`.

**Request body**
```json
{ "name": "Bíceps braquial", "imgUrl": "/img/biceps.png", "description": "Músculo flexor del codo" }
```

**Respuesta `201 Created`**
```json
{
  "id": 1, "name": "Bíceps braquial",
  "imgUrl": "/img/biceps.png", "description": "Músculo flexor del codo",
  "status": true, "created": "...", "updated": "..."
}
```

### `GET / PATCH / DELETE /api/muscles/{id}/`
- GET: autenticado.
- PATCH/DELETE: `admin` o `trainer`.

---

## Ejercicios

### `GET /api/exercises/`
Lista ejercicios (paginado). **Permiso**: autenticado.

**Query params**
- `search=press` — busca por nombre o descripción.
- `ordering=name|-name|created|-created`.

### `POST /api/exercises/`
Crea un ejercicio. **Permiso**: `admin` o `trainer`.

**Request body**
```json
{
  "name": "Press banca",
  "description": "Ejercicio compuesto de empuje horizontal",
  "videoUrl": "https://example.com/press.mp4",
  "muscleIds": [1, 2]
}
```

**Respuesta `201 Created`**
```json
{
  "id": 1,
  "name": "Press banca",
  "description": "Ejercicio compuesto de empuje horizontal",
  "videoUrl": "https://example.com/press.mp4",
  "status": true,
  "created": "...",
  "updated": "...",
  "muscles": [
    { "id": 1, "idMuscle": 1, "muscleName": "Pectoral mayor", "role": "primary" }
  ],
  "muscleIds": [1, 2]
}
```

### `GET /api/exercises/{id}/`
Detalle de un ejercicio. **Permiso**: autenticado.

### `PATCH /api/exercises/{id}/`
Actualiza un ejercicio. `muscleIds` reemplaza la lista de músculos asociados. **Permiso**: `admin` o `trainer`.

### `DELETE /api/exercises/{id}/`
Borra un ejercicio (soft delete, marca `status=false`). **Permiso**: `admin` o `trainer`.

### `GET /api/exercises/{id}/muscles/`
Lista los músculos asociados al ejercicio con su rol. **Permiso**: autenticado.

**Respuesta `200 OK`**
```json
[
  { "id": 1, "idMuscle": 1, "muscleName": "Pectoral mayor", "role": "primary" },
  { "id": 2, "idMuscle": 5, "muscleName": "Deltoides anterior", "role": "secondary" }
]
```

---

## Técnicas de intensidad

Endpoints estándar CRUD sobre `/api/intensity-techniques/`.

- `GET` autenticado.
- `POST/PATCH/DELETE` requiere `admin` o `trainer`.

**Forma del recurso**
```json
{
  "id": 1,
  "name": "Drop set",
  "description": "Reduce weight progressively within a set",
  "status": true,
  "created": "...",
  "updated": "..."
}
```

---

## Splits (plantillas)

### `GET /api/splits/`
Lista splits. **Permiso**: autenticado.

**Respuesta `200 OK`**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1, "name": "Push/Pull/Legs", "description": "...",
      "status": true, "created": "...", "updated": "...",
      "days": [
        { "id": 1, "idSplit": 1, "dayNumber": 1, "name": "Push", "status": true, "created": "...", "updated": "..." },
        { "id": 2, "idSplit": 1, "dayNumber": 2, "name": "Pull", "status": true, "created": "...", "updated": "..." },
        { "id": 3, "idSplit": 1, "dayNumber": 3, "name": "Legs", "status": true, "created": "...", "updated": "..." }
      ]
    }
  ]
}
```

### `POST /api/splits/`
Crea un split. **Permiso**: solo `admin`.

**Request body**
```json
{ "name": "Upper/Lower", "description": "4-day split" }
```

### `GET / PATCH / DELETE /api/splits/{id}/`
- GET: autenticado.
- PATCH/DELETE: solo `admin`.

### `GET /api/splits/{id}/days/`
Lista los días de un split. **Permiso**: autenticado.

**Respuesta `200 OK`**
```json
[
  { "id": 1, "idSplit": 1, "dayNumber": 1, "name": "Push", "status": true, "created": "...", "updated": "..." }
]
```

### `POST /api/splits/{id}/days/`
Añade un día al split. **Permiso**: `admin` o `trainer`.

**Request body**
```json
{ "dayNumber": 4, "name": "Cardio" }
```

**Respuesta `201 Created`**: día creado.

**Errores**
- `400` — `dayNumber` fuera de `1..7` o ya existe para ese split.

### `PATCH /api/splits/{id}/days/{dayId}/`
Actualiza un día. **Permiso**: `admin` o `trainer`.

### `DELETE /api/splits/{id}/days/{dayId}/`
Borra un día. **Permiso**: `admin` o `trainer`.

---

## Mis splits (adopción)

### `GET /api/my-splits/`
Lista los splits que el usuario actual ha adoptado (admin ve todos). **Permiso**: autenticado.

### `POST /api/my-splits/`
El usuario adopta un split.

**Permiso**: autenticado.

**Request body**
```json
{
  "idSplit": 1,
  "startDate": "2026-08-01",
  "endDate": null,
  "isActive": true
}
```

**Respuesta `201 Created`**
```json
{
  "id": 10,
  "idUser": 1,
  "idSplit": 1,
  "splitName": "Push/Pull/Legs",
  "startDate": "2026-08-01",
  "endDate": null,
  "isActive": true,
  "status": true,
  "created": "...",
  "updated": "..."
}
```

**Comportamiento**: al crear con `isActive=true`, todos los splits activos previos del mismo usuario pasan a `isActive=false`.

### `GET /api/my-splits/{id}/`
Detalle de la adopción.

### `PATCH /api/my-splits/{id}/`
Modifica la adopción (ej. marcar `endDate` para finalizar).

**Request body**
```json
{ "endDate": "2026-08-15", "isActive": false }
```

### `DELETE /api/my-splits/{id}/`
Borra la adopción. Soft delete (`status=false`).

### `GET /api/my-splits/active/`
Devuelve el split actualmente activo del usuario.

**Respuesta `200 OK`**: ver forma anterior.
**Respuesta `404 Not Found`** si no hay split activo.

---

## Mis rutinas

### `GET /api/my-routines/`
Lista las entradas de la rutina del usuario actual. **Permiso**: autenticado.

**Query params**
- `ordering=order|-order|created|-created`.
- `dayId=<int>` (vía action `/by-day/`, ver más abajo).

**Respuesta `200 OK`**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "idUserSplit": 10,
      "idSplitDay": 1,
      "dayNumber": 1,
      "dayName": "Push",
      "idExercise": 1,
      "exerciseName": "Press banca",
      "exercise": { "id": 1, "name": "Press banca", "...": "..." },
      "order": 1,
      "targetSets": 4,
      "targetReps": "8-12",
      "status": true,
      "created": "...",
      "updated": "..."
    }
  ]
}
```

### `POST /api/my-routines/`
Crea una entrada de rutina. **Permiso**: autenticado (sobre sus propios splits).

**Request body**
```json
{
  "idUserSplit": 10,
  "idSplitDay": 1,
  "idExercise": 1,
  "order": 1,
  "targetSets": 4,
  "targetReps": "8-12"
}
```

**Errores**
- `400` — `idSplitDay` no pertenece al `idUserSplit`.
- `400` — `targetSets` debe ser > 0.

### `GET /api/my-routines/{id}/`
Detalle.

### `PATCH /api/my-routines/{id}/`
Actualización parcial.

### `DELETE /api/my-routines/{id}/`
Borra la entrada.

### `GET /api/my-routines/by-day/?dayId={id}`
Devuelve las entradas de rutina del usuario filtradas por `idSplitDay`.

**Respuesta `200 OK`**: lista de entradas.

---

## Workouts

### `GET /api/workouts/`
Lista workouts del usuario (admin ve todos). **Permiso**: autenticado.

**Query params**
- `routineId=<int>` — filtra por rutina.
- `ordering=workoutDate|-workoutDate|setNumber|-setNumber`.

### `POST /api/workouts/`
Registra un set realizado. **Permiso**: autenticado.

**Request body**
```json
{
  "idRoutine": 1,
  "idIntensityTechnique": 1,
  "setNumber": 1,
  "repetitions": 10,
  "kg": "60.00",
  "rpe": "8.0",
  "notes": "Buen set"
}
```

**Respuesta `201 Created`**
```json
{
  "id": 1,
  "idRoutine": 1,
  "idIntensityTechnique": 1,
  "intensityTechnique": { "id": 1, "name": "Drop set", "...": "..." },
  "exerciseName": "Press banca",
  "dayNumber": 1,
  "workoutDate": "2026-08-17T10:00:00Z",
  "setNumber": 1,
  "repetitions": 10,
  "kg": "60.00",
  "rpe": "8.0",
  "notes": "Buen set",
  "status": true,
  "created": "...",
  "updated": "..."
}
```

**Errores**
- `400` — `kg < 0`, `repetitions < 0`, `setNumber <= 0`, `rpe` fuera de `1..10`.

### `GET /api/workouts/{id}/`
Detalle.

### `PATCH /api/workouts/{id}/`
Actualiza el set (ej. corregir repeticiones).

### `DELETE /api/workouts/{id}/`
Borra el set.

### `GET /api/workouts/stats/`
Estadísticas agregadas de los workouts del usuario.

**Query params**
- `routineId=<int>` (opcional) — filtra por una rutina concreta.

**Respuesta `200 OK`**
```json
{
  "byExercise": [
    {
      "idRoutine__idExercise__id": 1,
      "idRoutine__idExercise__name": "Press banca",
      "totalSets": 8,
      "totalReps": 72,
      "totalVolume": "4830.00"
    },
    {
      "idRoutine__idExercise__id": 2,
      "idRoutine__idExercise__name": "Remo con barra",
      "totalSets": 4,
      "totalReps": 40,
      "totalVolume": "2400.00"
    }
  ]
}
```

> `totalVolume = Σ (kg × repetitions)` ordenado de mayor a menor volumen.

---

## Mis ejercicios (favoritos)

### `GET /api/my-exercises/`
Lista los ejercicios guardados por el usuario. **Permiso**: autenticado.

**Respuesta `200 OK`**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "idUser": 1,
      "exerciseId": 1,
      "exerciseName": "Press banca",
      "exercise": { "id": 1, "name": "Press banca", "...": "..." },
      "created": "..."
    }
  ]
}
```

### `POST /api/my-exercises/`
Guarda un ejercicio en favoritos.

**Request body**
```json
{ "idExercise": 1 }
```

**Respuesta `201 Created`**: ver forma anterior.
**Idempotente**: si ya existe, no crea duplicado.

### `DELETE /api/my-exercises/{id}/`
Quita el ejercicio de favoritos. **Respuesta `204 No Content`**.

---

## Modelos de datos (referencia rápida)

### `users`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | BIGINT PK | auto |
| `idRole` | BIGINT FK → `roles.id` | PROTECT |
| `firstName` | NVARCHAR(100) | NOT NULL |
| `lastName` | NVARCHAR(100) | NOT NULL |
| `userName` | VARCHAR(60) | UNIQUE |
| `email` | VARCHAR(255) | UNIQUE |
| `password` | VARCHAR(255) | hash PBKDF2 |
| `status` | BIT | default 1 |
| `lastLogin` | DATETIME | NULL |
| `created` | DATETIME | auto |
| `updated` | DATETIME | auto |

### `roles`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | BIGINT PK | auto |
| `name` | VARCHAR(50) | UNIQUE |
| `description` | NVARCHAR(255) | |
| `status` | BIT | default 1 |
| `created`, `updated` | DATETIME | auto |

### `muscles`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | BIGINT PK | auto |
| `name` | VARCHAR(100) | UNIQUE |
| `imgUrl` | VARCHAR(500) | |
| `description` | TEXT | |
| `status`, `created`, `updated` | | |

### `exercises`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | BIGINT PK | auto |
| `name` | VARCHAR(150) | |
| `description` | TEXT | |
| `videoUrl` | VARCHAR(500) | |
| `status`, `created`, `updated` | | |

### `exercise_muscles`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | BIGINT PK | auto |
| `idExercise` | FK → `exercises` | CASCADE |
| `idMuscle` | FK → `muscles` | PROTECT |
| `role` | VARCHAR(20) | `primary`/`secondary`/`stabilizer` |

### `intensity_techniques`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | BIGINT PK | auto |
| `name` | VARCHAR(100) | UNIQUE |
| `description` | TEXT | |
| `status`, `created`, `updated` | | |

### `splits`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | BIGINT PK | auto |
| `name` | VARCHAR(100) | UNIQUE |
| `description` | TEXT | |
| `status`, `created`, `updated` | | |

### `split_days`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | BIGINT PK | auto |
| `idSplit` | FK → `splits` | CASCADE |
| `dayNumber` | SMALLINT | 1..7, UNIQUE con split |
| `name` | VARCHAR(80) | |

### `user_splits`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | BIGINT PK | auto |
| `idUser` | FK → `users` | CASCADE |
| `idSplit` | FK → `splits` | PROTECT |
| `startDate` | DATE | |
| `endDate` | DATE | NULL = activo |
| `isActive` | BIT | uno activo por usuario |

### `user_exercises`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | BIGINT PK | auto |
| `idUser` | FK → `users` | CASCADE |
| `idExercise` | FK → `exercises` | PROTECT |

UNIQUE(`idUser`, `idExercise`).

### `routines`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | BIGINT PK | auto |
| `idUserSplit` | FK → `user_splits` | CASCADE |
| `idSplitDay` | FK → `split_days` | PROTECT |
| `idExercise` | FK → `exercises` | PROTECT |
| `order` | SMALLINT | |
| `targetSets` | SMALLINT | > 0 |
| `targetReps` | VARCHAR(15) | ej. `8-12` |

### `workouts`
| Campo | Tipo | Notas |
|---|---|---|
| `id` | BIGINT PK | auto |
| `idRoutine` | FK → `routines` | CASCADE |
| `idIntensityTechnique` | FK → `intensity_techniques` | PROTECT, NULL |
| `workoutDate` | DATETIME | auto al crear |
| `setNumber` | SMALLINT | > 0 |
| `repetitions` | SMALLINT | ≥ 0 |
| `kg` | DECIMAL(6,2) | ≥ 0 |
| `rpe` | DECIMAL(3,1) | 1..10, NULL |
| `notes` | NVARCHAR(500) | |

---

## Flujo típico de uso

1. **Registro/Login** → obtener `access` y `refresh`.
2. **Adoptar un split** → `POST /api/my-splits/` con `isActive=true`.
3. **Crear rutina** → `POST /api/my-routines/` indicando `idUserSplit`, `idSplitDay`, `idExercise`, `targetSets`, `targetReps`.
4. **Entrenar** → `POST /api/workouts/` por cada set realizado.
5. **Ver progreso** → `GET /api/workouts/stats/`.
