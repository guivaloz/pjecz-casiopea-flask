# pjecz-casiopea-flask

Plataforma de administración del sistema de citas

## Variables de entorno

Crear un archivo `.env` en la raíz del proyecto con las siguientes variables de entorno:

```env
# Flask, para SECRET_KEY use openssl rand -hex 24
FLASK_APP=pjecz_casiopea_flask.main
FLASK_DEBUG=1
SECRET_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Base de datos
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=pjecz_casiopea
DB_USER=adminpjeczcasiopea
DB_PASS=XXXXXXXXXXXX
SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://adminpjeczcasiopea:XXXXXXXXXXXX@127.0.0.1:5432/pjecz_casiopea"

# CLI migrar copiar: base de datos NUEVA pjecz_casiopea
NEW_DB_HOST=
NEW_DB_PORT=
NEW_DB_NAME=
NEW_DB_USER=
NEW_DB_PASS=
NEW_SQLALCHEMY_DATABASE_URI=

# CLI migrar copiar: base de datos ANTERIOR pjecz_citas_v2
OLD_DB_HOST=
OLD_DB_PORT=
OLD_DB_NAME=
OLD_DB_USER=
OLD_DB_PASS=
OLD_SQLALCHEMY_DATABASE_URI=

# Cryptography
FERNET_KEY=XXXXXXXXXXXX
SALT=XXXXXXXXXXXX

# Host
HOST=http://127.0.0.1:5000

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
TASK_QUEUE_NAME=pjecz_casiopea

# Huso Horario
TZ=America/Mexico_City

# Sendgrid
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=

# URLs de confirmación y de recuperación de cuenta
NEW_ACCOUNT_CONFIRM_URL=
RECOVER_ACCOUNT_CONFIRM_URL=

# Definir si es para desarrollo (development) o producción (production)
ENVIRONMENT=development

# Si es para producción, definir el prefijo de la aplicación comenzando con /
PREFIX=
```
