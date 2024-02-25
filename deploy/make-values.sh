#!/usr/bin/env bash
set -euo pipefail

context=${1:-local}
domain=${2:-fibonet.ro}

DB_APP_USER=django
DB_APP_PASS=$(pwgen -s1 42)
DB_APP_NAME="microinvoicer_${context}"

DJANGO_SECRET_KEY=$(pwgen -s1 63)
DJANGO_ADMIN_PASS=$(pwgen -s1 42)

cat <<END
useDomain: "${domain}"
useEnvironment: "${context}"

secrets:
  dbUser: "django"
  dbPassword: "${DB_APP_PASS}"
  dbName: "${DB_APP_NAME}"

  djangoSecretKey: "${DJANGO_SECRET_KEY}"
END

cat >init-db.sh <<END
# init-db.sh
#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username postgres <<-EOSQL
    CREATE USER ${DB_APP_USER} WITH PASSWORD '${DB_APP_PASS}';
    CREATE DATABASE ${DB_APP_NAME};
    GRANT ALL PRIVILEGES ON DATABASE ${DB_APP_NAME} TO ${DB_APP_USER};
EOSQL
END
echo "Wrote new init-db.sh"
