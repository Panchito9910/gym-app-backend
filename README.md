# Gym App Backend

REST API para gestión de rutinas de gimnasio. Stack **Django 6.1 + DRF + SimpleJWT + SQL Server**.

## Estructura

```
gym-app-backend/
├── manage.py
├── requirements.txt
├── .env.example
├── gym_app/                  Configuración del proyecto
│   ├── settings/             base / development / production / test
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── apps/
│   ├── core/                 Utilidades comunes (BaseModel, permissions, factories)
│   ├── authentication/       JWT endpoints (register/login/refresh/logout)
│   ├── users/                Custom User + Role + favoritos
│   ├── catalog/              Muscle, Exercise, IntensityTechnique, ExerciseMuscle
│   ├── splits/               Split, SplitDay, UserSplit
│   ├── routines/             Routine
│   └── workouts/             Workout
└── PLAN.md                   Plan de arquitectura detallado
└── API.md                    Documentación de endpoints
```

## Setup local

```powershell
# 1. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 2. Instalar dependencias (si no están)
pip install -r requirements.txt

# 3. Configurar variables
cp .env.example .env
# Editar .env con tu servidor SQL Server (DB_HOST, DB_USER, DB_PASSWORD...)

# 4. Crear la base de datos en SQL Server
#    CREATE DATABASE gym_app;

# 5. Migrar
python manage.py migrate

# 6. Cargar datos iniciales (roles + técnicas de intensidad)
python manage.py loaddata roles
python manage.py loaddata intensity_techniques

# 7. Crear superusuario
python manage.py createsuperuser

# 8. Arrancar
python manage.py runserver
```

Documentación Swagger: <http://localhost:8000/api/docs/>
Schema OpenAPI: <http://localhost:8000/api/schema/>

## Tests

```powershell
python manage.py test --settings=gym_app.settings.test
```

Usa SQLite en memoria (configurado en `settings/test.py`) para velocidad.

## Settings por entorno

| Variable | Default | Uso |
|---|---|---|
| `DJANGO_SETTINGS_ENV` | `development` | Alterna entre `development`, `production`, `test` |
| `DJANGO_DEBUG` | `True` | Modo debug |
| `DJANGO_SECRET_KEY` | - | Clave secreta JWT |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hosts permitidos |
| `DB_ENGINE` | `mssql` | Engine Django |
| `DB_NAME` | `gym_app` | Nombre BD |
| `DB_USER` / `DB_PASSWORD` | - | Credenciales |
| `DB_HOST` / `DB_PORT` | `localhost` / `1433` | Servidor SQL Server |
| `DB_DRIVER` | `ODBC Driver 18 for SQL Server` | Driver ODBC |
| `JWT_ACCESS_MINUTES` | `15` | Vida access token |
| `JWT_REFRESH_DAYS` | `7` | Vida refresh token |
| `CORS_ALLOWED_ORIGINS` | - | Orígenes permitidos (CSV) |

## Endpoints principales

Ver [`API.md`](./API.md) para detalle completo.

| Recurso | Prefijo |
|---|---|
| Auth | `/api/auth/{register,login,logout,refresh}` |
| Usuarios | `/api/users/`, `/api/users/me/`, `/api/users/me/change-password/` |
| Roles | `/api/roles/` |
| Músculos | `/api/muscles/` |
| Ejercicios | `/api/exercises/` |
| Técnicas | `/api/intensity-techniques/` |
| Splits | `/api/splits/`, `/api/splits/{id}/days/` |
| Mis splits | `/api/my-splits/`, `/api/my-splits/active/` |
| Mi rutina | `/api/my-routines/`, `/api/my-routines/by-day/` |
| Workouts | `/api/workouts/`, `/api/workouts/stats/` |
| Mis ejercicios | `/api/my-exercises/` |

## Roles

- `admin`: acceso total.
- `trainer`: puede editar catálogo.
- `user`: solo gestiona sus propios recursos.

## Seguridad

- JWT con `HS256`, access 15 min, refresh 7 días con blacklist.
- Passwords con PBKDF2 y validadores nativos Django.
- Throttling: `30/min` anónimo, `120/min` autenticado, `5/min` en login.
- CORS configurable por `CORS_ALLOWED_ORIGINS`.
- HSTS, SSL redirect, cookies seguras en producción.
