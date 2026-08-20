# PLAN - Backend de Rutinas de Gimnasio

> Documento de planificación. Define arquitectura, modelo de datos, endpoints y fases de implementación.
> Stack confirmado: **Django 6.1 + DRF + SimpleJWT + SQL Server**.

---

## 1. Resumen ejecutivo

Backend para una aplicación de rutinas de gimnasio que permita:

- Registrar usuarios con autenticación JWT (access + refresh).
- Gestionar un catálogo de **ejercicios**, **músculos** y **técnicas de intensidad**.
- Gestionar **splits** (plantillas globales tipo *Push/Pull/Legs*) y que un usuario adopte uno activo.
- Definir la **rutina** planificada por día/ejercicio dentro del split adoptado.
- Registrar los **workouts** reales (sets, reps, kg, técnica usada, fecha).
- Controlar roles (`admin`, `user`, `trainer`) y permisos por rol.

---

## 2. Stack tecnológico

| Componente | Tecnología | Justificación |
|---|---|---|
| Framework | Django 6.1 | Ya inicializado en `gym_app/` |
| API | Django REST Framework | Estándar con Django |
| Auth | `djangorestframework-simplejwt` | JWT con refresh tokens out-of-the-box |
| DB driver | `mssql-django` + `pyodbc` | Driver oficial Microsoft para SQL Server |
| Env vars | `python-decouple` | Lectura robusta de `.env` |
| CORS | `django-cors-headers` | Si hay frontend separado |
| Docs API | `drf-spectacular` | OpenAPI/Swagger automático |
| Validaciones | `django-password-validators` | Políticas de contraseña nativas |

---

## 3. Análisis del esquema SQL recibido

### 3.1 Problemas encontrados

| # | Problema | Tipo |
|---|---|---|
| 1 | Typos: `stymulus`, `stymulus-ratio`, `rols`, `idStymulus`, `idUserExcercise` | Nomenclatura |
| 2 | Guiones en nombres de tabla: `user-exercises`, `users-splits`, `stymulus-ratio` | Nomenclatura (SQL Server los requiere entre corchetes `[user-exercises]`) |
| 3 | Inconsistencia singular/plural: `split` (singular) vs el resto | Nomenclatura |
| 4 | `users.email` y `users.userName` sin `UNIQUE` | Integridad |
| 5 | `users.password` como `VARCHAR(255)` plano (debe ser hash) | Seguridad |
| 6 | Sin `ON DELETE` / `ON UPDATE` definidos en las FKs | Integridad |
| 7 | Sin `DEFAULT` en `status`, `created`, `updated` | Mantenimiento |
| 8 | `stymulus` colgado de `user-exercises` (debería ser del `exercise`) | Diseño |
| 9 | `workout.kg` como `BIGINT` (debería permitir decimales) | Datos |
| 10 | `workout` sin fecha/hora del workout real | Diseño |
| 11 | `routine` sin día/orden dentro del split | Diseño |
| 12 | `users-splits` sin fecha de inicio/fin ni flag activo | Diseño |
| 13 | Falta tabla de **refresh tokens** persistidos para revocación | Seguridad |
| 14 | Falta tabla de **días del split** (`split_day`) | Diseño |
| 15 | Descripciones en `VARCHAR(255)` (probablemente cortas) | Datos |
| 16 | Falta índice en algunas FK (`routine.idExercise`, `users.idRole`) | Performance |

### 3.2 Cambios de nomenclatura propuestos

| Original | Propuesto |
|---|---|
| `rols` | `roles` |
| `stymulus` | `stimulus` |
| `stymulus-ratio` | `stimulus_ratio` |
| `idStymulus` | `idStimulus` |
| `idUserExcercise` | `idUserExercise` |
| `user-exercises` | `user_exercises` |
| `users-splits` | `user_splits` |
| `split` | `splits` |

---

## 4. Modelo de datos propuesto

### 4.1 Diagrama lógico

```
roles 1---* users
users 1---* user_exercises
users 1---* user_splits *---1 splits
splits 1---* split_days 1---* routines *---1 exercises
exercises 1---* exercise_muscles *---1 muscles
exercises 1---* exercise_stimulus_ratio *---1 muscles
routines 1---* workouts *---1 intensity_techniques
users 1---* workouts  (vía routine → user_split)
users 1---* refresh_tokens
```

### 4.2 Tablas

#### `roles`
- `id` BIGINT PK
- `name` VARCHAR(50) UNIQUE NOT NULL  → `admin`, `user`, `trainer`
- `description` NVARCHAR(255)
- `status` BIT DEFAULT 1
- `created` DATETIME DEFAULT GETDATE()
- `updated` DATETIME (trigger de auto-actualización)

#### `users`
- `id` BIGINT PK
- `idRole` BIGINT FK → `roles(id)` ON DELETE RESTRICT
- `firstName` NVARCHAR(100) NOT NULL
- `lastName` NVARCHAR(100) NOT NULL
- `userName` VARCHAR(60) UNIQUE NOT NULL
- `email` VARCHAR(255) UNIQUE NOT NULL
- `password` VARCHAR(255) NOT NULL  → hash BCrypt (gestionado por Django)
- `status` BIT DEFAULT 1
- `lastLogin` DATETIME NULL
- `created` DATETIME DEFAULT GETDATE()
- `updated` DATETIME

> Django gestionará el hash con `AbstractUser`/`AbstractBaseUser` y `set_password()`.

#### `muscles`
- `id` BIGINT PK
- `imgUrl` VARCHAR(500) NULL
- `name` VARCHAR(100) UNIQUE NOT NULL  → ej. *Pectoral mayor*, *Bíceps braquial*
- `description` NVARCHAR(MAX) NULL
- `status` BIT DEFAULT 1
- `created`, `updated`

#### `exercises`
- `id` BIGINT PK
- `name` VARCHAR(150) NOT NULL
- `description` NVARCHAR(MAX) NULL
- `videoUrl` VARCHAR(500) NULL
- `status` BIT DEFAULT 1
- `created`, `updated`

#### `exercise_muscles`  *(N:M ejercicio ↔ músculo con rol)*
- `id` BIGINT PK
- `idExercise` BIGINT FK → `exercises` ON DELETE CASCADE
- `idMuscle` BIGINT FK → `muscles` ON DELETE RESTRICT
- `role` VARCHAR(20) NOT NULL CHECK (`role` IN (`'primary'`, `'secondary'`, `'stabilizer'`))
- UNIQUE (`idExercise`, `idMuscle`, `role`)

> Esta tabla sustituye a `stymulus`/`stymulus-ratio`. Indica qué músculos trabaja el ejercicio y en qué rol.

#### `intensity_techniques`
- `id` BIGINT PK
- `name` VARCHAR(100) UNIQUE NOT NULL  → *Drop set*, *Piramidal*, *Rest-pause*…
- `description` NVARCHAR(MAX) NULL
- `status` BIT DEFAULT 1
- `created`, `updated`

#### `splits`
- `id` BIGINT PK
- `name` VARCHAR(100) UNIQUE NOT NULL  → *Push/Pull/Legs*, *Upper/Lower*…
- `description` NVARCHAR(MAX) NULL
- `status` BIT DEFAULT 1
- `created`, `updated`

#### `split_days`  *(NUEVO: días que componen un split)*
- `id` BIGINT PK
- `idSplit` BIGINT FK → `splits` ON DELETE CASCADE
- `dayNumber` TINYINT NOT NULL CHECK (`dayNumber` BETWEEN 1 AND 7)
- `name` VARCHAR(80) NOT NULL  → *Push day*, *Pierna*, *Cardio*
- UNIQUE (`idSplit`, `dayNumber`)
- `status` BIT DEFAULT 1
- `created`, `updated`

#### `user_splits`  *(adopción de un split por un usuario)*
- `id` BIGINT PK
- `idUser` BIGINT FK → `users` ON DELETE CASCADE
- `idSplit` BIGINT FK → `splits` ON DELETE RESTRICT
- `startDate` DATE NOT NULL
- `endDate` DATE NULL  → NULL = activo
- `isActive` BIT NOT NULL DEFAULT 1
- `status` BIT DEFAULT 1
- `created`, `updated`

> Solo debe existir **un** `user_split` con `isActive=1` por usuario (CHECK con vista indexada o validación de aplicación).

#### `user_exercises`  *(ejercicios favoritos/guardados por el usuario)*
- `id` BIGINT PK
- `idUser` BIGINT FK → `users` ON DELETE CASCADE
- `idExercise` BIGINT FK → `exercises` ON DELETE RESTRICT
- UNIQUE (`idUser`, `idExercise`)
- `status` BIT DEFAULT 1
- `created`, `updated`

#### `routines`  *(plan: ejercicio asignado a un día del split adoptado)*
- `id` BIGINT PK
- `idUserSplit` BIGINT FK → `user_splits` ON DELETE CASCADE
- `idSplitDay` BIGINT FK → `split_days` ON DELETE RESTRICT
- `idExercise` BIGINT FK → `exercises` ON DELETE RESTRICT
- `order` SMALLINT NOT NULL  → orden dentro del día
- `targetSets` SMALLINT NOT NULL CHECK (`targetSets` > 0)
- `targetReps` VARCHAR(15) NOT NULL  → ej. `8-12`, `5`, `AMRAP`
- `status` BIT DEFAULT 1
- `created`, `updated`

> Cambios vs. original: se añade día (`idSplitDay`), orden y series/reps objetivo.

#### `workouts`  *(log real de entrenamiento)*
- `id` BIGINT PK
- `idRoutine` BIGINT FK → `routines` ON DELETE CASCADE
- `idIntensityTechnique` BIGINT FK → `intensity_techniques` ON DELETE RESTRICT NULL
- `workoutDate` DATETIME NOT NULL DEFAULT GETDATE()  → NUEVO
- `setNumber` SMALLINT NOT NULL  → NUEVO (número de set)
- `repetitions` SMALLINT NOT NULL CHECK (`repetitions` >= 0)
- `kg` DECIMAL(6,2) NOT NULL CHECK (`kg` >= 0)  → CAMBIO: BIGINT → DECIMAL
- `rpe` DECIMAL(3,1) NULL CHECK (`rpe` BETWEEN 1 AND 10)  → opcional
- `notes` NVARCHAR(500) NULL
- `created`, `updated`

#### `refresh_tokens`  *(NUEVO: para blacklist/revocación)*
- `id` BIGINT PK
- `idUser` BIGINT FK → `users` ON DELETE CASCADE
- `token` VARCHAR(500) UNIQUE NOT NULL
- `expiresAt` DATETIME NOT NULL
- `revoked` BIT NOT NULL DEFAULT 0
- `createdAt` DATETIME DEFAULT GETDATE()

> Se activa con `SIMPLEJWT` + tabla de blacklist, o se gestiona manualmente.

---

## 5. Estructura del proyecto Django

```
gym-app-backend/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore                      (ya existe)
├── gym_app/                        (configuración, ya existe)
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                 (refactor de settings.py)
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    ├── __init__.py
    ├── core/                       (utilidades comunes)
    │   ├── models.py               (BaseModel con created/updated/status)
    │   ├── permissions.py
    │   └── pagination.py
    ├── users/
    │   ├── models.py               (Role, User)
    │   ├── serializers.py
    │   ├── views.py                (RegisterView, MeView)
    │   ├── urls.py
    │   ├── managers.py             (UserManager)
    │   ├── services.py             (UserService)
    │   └── tests/
    ├── catalog/                    (músculos, ejercicios, técnicas)
    │   ├── models.py               (Muscle, Exercise, IntensityTechnique)
    │   ├── serializers.py
    │   ├── views.py                (ViewSets)
    │   ├── urls.py
    │   ├── filters.py
    │   └── tests/
    ├── splits/                     (plantillas de split y adopción)
    │   ├── models.py               (Split, SplitDay, UserSplit)
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── tests/
    ├── routines/                   (planificación)
    │   ├── models.py               (Routine)
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── tests/
    ├── workouts/                   (log real)
    │   ├── models.py               (Workout, RefreshToken)
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── tests/
    └── authentication/             (JWT custom views si se requieren)
        ├── views.py                (Login, Logout, Refresh)
        ├── urls.py
        └── services.py
```

---

## 6. Configuración de SQL Server

### 6.1 Dependencias

```
Django==6.1
djangorestframework
djangorestframework-simplejwt
mssql-django
pyodbc
python-decouple
django-cors-headers
drf-spectacular
```

Driver ODBC: **ODBC Driver 18 for SQL Server** (instalado en el sistema).

### 6.2 Settings (`gym_app/settings/base.py`)

```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='1433'),
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes',
            # para Azure SQL: 'encrypt': 'yes',
        },
    }
}
```

> En SQL Server, Django usará `BigAutoField` por defecto y se respetará la convención de nombres.

### 6.3 Migraciones

- Definir modelos en Django que reflejen las tablas corregidas.
- `python manage.py makemigrations` + `python manage.py migrate`.
- Para campos `BIT` usar `BooleanField`; para `DATETIME` usar `DateTimeField` con `auto_now_add`/`auto_now`.

---

## 7. Autenticación JWT

### 7.1 Flujo

```
Cliente                         Backend
   │ ── POST /api/auth/login ──▶  { username, password }
   │                              valida credenciales
   │ ◀── 200 ────────────────────  { access, refresh }
   │
   │ ── GET /api/... (Authorization: Bearer <access>) ──▶
   │ ◀── 200 / 401
   │
   │ ── POST /api/auth/refresh ──▶ { refresh }
   │ ◀── 200 ──────────────────── { access (nuevo) }
   │
   │ ── POST /api/auth/logout ──▶ { refresh }   (blacklist)
   │ ◀── 204
```

### 7.2 Configuración SimpleJWT (`base.py`)

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

### 7.3 Endpoints de auth

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| POST | `/api/auth/register` | AllowAny | Alta de usuario con `role=user` por defecto |
| POST | `/api/auth/login` | AllowAny | Devuelve `access` + `refresh` |
| POST | `/api/auth/refresh` | AllowAny | Renueva `access` |
| POST | `/api/auth/logout` | IsAuthenticated | Blacklist del `refresh` |
| GET | `/api/auth/me` | IsAuthenticated | Datos del usuario actual |
| PATCH | `/api/auth/me` | IsAuthenticated | Actualización parcial |

---

## 8. API REST - Endpoints

> Todos los endpoints requieren `Authorization: Bearer <access>` salvo donde se indique `AllowAny`.

### 8.1 Catálogo (lectura: autenticado; escritura: admin/trainer)

| Método | Ruta | Descripción |
|---|---|---|
| GET/POST | `/api/muscles/` | Listar / crear |
| GET/PATCH/DELETE | `/api/muscles/{id}/` | Detalle |
| GET/POST | `/api/exercises/` | Listar / crear |
| GET/PATCH/DELETE | `/api/exercises/{id}/` | Detalle |
| GET/POST | `/api/intensity-techniques/` | Listar / crear |
| GET/PATCH/DELETE | `/api/intensity-techniques/{id}/` | Detalle |

### 8.2 Splits

| Método | Ruta | Descripción |
|---|---|---|
| GET/POST | `/api/splits/` | Listar/crear (admin) |
| GET/PATCH/DELETE | `/api/splits/{id}/` | Detalle |
| GET/POST | `/api/splits/{id}/days/` | Listar/crear días del split |
| GET | `/api/splits/{id}/days/{dayId}/` | Detalle día |

### 8.3 Adopción de split por usuario

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/my-splits/` | Splits del usuario actual |
| POST | `/api/my-splits/` | Adoptar un split (marca el anterior como inactivo) |
| PATCH | `/api/my-splits/{id}/` | Finalizar (`endDate`, `isActive=0`) |
| GET | `/api/my-splits/active` | Split activo del usuario |

### 8.4 Rutinas

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/my-routines/` | Rutinas del usuario actual (filtrables por split activo/día) |
| POST | `/api/my-routines/` | Crear ejercicio en un día del split activo |
| PATCH/DELETE | `/api/my-routines/{id}/` | Editar/eliminar |
| POST | `/api/my-routines/copy-from-template/{splitId}/` | Inicializa la rutina desde una plantilla |

### 8.5 Workouts (log)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/workouts/` | Listar (filtros: `routineId`, `from`, `to`) |
| POST | `/api/workouts/` | Registrar set realizado |
| PATCH/DELETE | `/api/workouts/{id}/` | Editar/borrar |
| GET | `/api/workouts/stats/` | Resumen por ejercicio / músculo (KPIs) |

### 8.6 Ejercicios del usuario (favoritos)

| Método | Ruta | Descripción |
|---|---|---|
| GET/POST | `/api/my-exercises/` | Listar / guardar |
| DELETE | `/api/my-exercises/{id}/` | Quitar de favoritos |

---

## 9. Seguridad

Aplicar lo indicado por la skill `django-security` (resumen):

- `SECRET_KEY`, credenciales DB y claves JWT en **variables de entorno** (nunca en repo).
- `DEBUG=False` en producción, `ALLOWED_HOSTS` explícito.
- `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`, `SECURE_HSTS_*`.
- Contraseñas hasheadas con **PBKDF2** (default Django) o BCrypt; **nunca** texto plano.
- Validadores de contraseña activos (longitud, similitud, comunes, numéricos).
- Permisos por rol:
  - `admin`: CRUD total.
  - `trainer`: CRUD en catálogos y lectura de rutinas de usuarios asignados.
  - `user`: CRUD solo sobre sus propios recursos (`user_splits`, `routines`, `workouts`).
- Rate limiting en `/api/auth/login` (DRF throttling: `5/min`).
- Tokens de refresh con **blacklist** tras rotación.
- ORM Django (sin SQL crudo) para evitar SQL injection.
- Sanitización de entradas en serializers (XSS).
- CORS restrictivo: solo orígenes conocidos.
- Logging de auditoría (`LOGIN`, `LOGOUT`, cambios en `workouts`).
- HTTPS obligatorio en producción; cookies `SameSite=Lax`.

---

## 10. Variables de entorno (`.env.example`)

```
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=gym_app
DB_USER=sa
DB_PASSWORD=change-me
DB_HOST=localhost
DB_PORT=1433
DB_DRIVER=ODBC Driver 18 for SQL Server

JWT_ACCESS_MINUTES=15
JWT_REFRESH_DAYS=7

CORS_ALLOWED_ORIGINS=http://localhost:3000
```

---

## 11. Plan de implementación por fases

### Fase 1 - Cimientos (1-2 días)
1. Refactorizar `settings.py` → `settings/{base,development,production,test}.py`.
2. Instalar dependencias: `djangorestframework`, `simplejwt`, `mssql-django`, `pyodbc`, `python-decouple`, `django-cors-headers`, `drf-spectacular`.
3. Configurar `.env` y conexión a SQL Server.
4. Crear `apps/core` con `BaseModel` abstracto (`created`, `updated`, `status`).
5. Verificar `python manage.py check` y `migrate --run-syncdb` sobre DB vacía.

### Fase 2 - Auth (2-3 días)
1. Crear `apps/users` con modelo `User` (custom) y `Role`.
2. Manager custom (`create_user`, `create_superuser`).
3. Serializers y views: register, login, refresh, logout, me.
4. Migración + seed inicial de roles (`admin`, `user`, `trainer`).
5. Tests: registro, login válido/inválido, refresh, logout (blacklist).

### Fase 3 - Catálogo (1-2 días)
1. `apps/catalog`: `Muscle`, `Exercise`, `IntensityTechnique`, `ExerciseMuscle`.
2. ViewSets + permisos (`IsAdminOrTrainer` para escritura).
3. Filtros por `status` y búsqueda por nombre.
4. Seed inicial de músculos y técnicas.

### Fase 4 - Splits y rutinas (3-4 días)
1. `apps/splits`: `Split`, `SplitDay`, `UserSplit`.
2. `apps/routines`: `Routine`.
3. Endpoints de adopción (`/my-splits/active`).
4. Validación: solo un `UserSplit` activo por usuario.
5. Tests de consistencia.

### Fase 5 - Workouts (2-3 días)
1. `apps/workouts`: `Workout`, `RefreshToken` (si se gestiona manualmente).
2. Endpoints + filtros por fecha y ejercicio.
3. Endpoint `/workouts/stats/` con agregaciones.

### Fase 6 - Hardening y docs (1-2 días)
1. Activar `drf-spectacular` y exponer Swagger en `/api/docs/`.
2. Rate limiting en login.
3. Logging de auditoría.
4. Configuración `production.py` con `SECURE_*`.
5. README con instrucciones de setup, migraciones, seeds y cómo correr tests.

---

## 12. Decisiones abiertas (a confirmar)

- [ ] ¿El usuario puede tener varios `UserSplit` activos históricos o solo uno vigente a la vez? → Propuesto: uno vigente.
- [ ] ¿El catálogo (`exercises`, `muscles`) es editable por `trainer` o solo por `admin`? → Propuesto: ambos, con `IsAdminOrTrainer`.
- [ ] ¿Se requiere endpoint de **stats** (volumen por grupo muscular, progresión de kg)? → Propuesto: sí, en `/workouts/stats/`.
- [ ] ¿Se envían emails de verificación o recuperación de contraseña? → Propuesto: sí (opcional, fase 6+).
- [ ] ¿Roles personalizados dinámicos o fijos (`admin`, `user`, `trainer`)? → Propuesto: tabla `roles` permite agregar más.

---

## 13. Cómo arrancar localmente (referencia rápida)

```bash
# 1. Entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Dependencias
pip install -r requirements.txt

# 3. Variables de entorno
cp .env.example .env
# editar .env con credenciales de SQL Server

# 4. Migraciones + seed
python manage.py migrate
python manage.py loaddata apps/users/fixtures/roles.json

# 5. Superusuario
python manage.py createsuperuser

# 6. Run
python manage.py runserver

# 7. Swagger
# http://localhost:8000/api/docs/
```
