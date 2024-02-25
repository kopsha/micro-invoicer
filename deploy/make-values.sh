#!/usr/bin/env bash
set -euo pipefail

context=${1:-local}
domain=${2:-fibonet.ro}

DB_ADMIN_PASS=$(pwgen -s1 42)
DB_APP_PASS=$(pwgen -s1 42)

DJANGO_SECRET_KEY=$(pwgen -s1 63)
DJANGO_ADMIN_PASS=$(pwgen -s1 42)

cat <<END
useDomain: "${domain}"
useEnvironment: "${context}"

secrets:
  dbUser: "django"
  dbPassword: "${DB_APP_PASS}"
  dbName: "microinvoicer_${context}"

  djangoSecretKey: "${DJANGO_SECRET_KEY}"
END
