# Order Sync (Python)

Sincroniza órdenes por cliente a Excel y sube opcionalmente a Google Drive.

## Configuración (.env)

```
MONGO_URI=mongodb+srv://user:pass@cluster/db?retryWrites=true&w=majority
ACCOUNT_IDS=68c322a783f1aee03860e01b
GOOGLE_CLIENT_EMAIL=service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nABC...\n-----END PRIVATE KEY-----\nGOOGLE_DRIVE_FOLDER_ID=xxxxxxxxxxxxxxxxxxxx
OUTPUT_DIR=./order_sync_output
TZ=America/Argentina/Buenos_Aires
```

Bases/colecciones (hardcoded):
- Órdenes: `MGP-ORDER/Order`
- Logs: `MGP-ORDER/OrderLog`
- Cuentas: `MGP-ACCOUNT/Accounts`

## Uso

- Modo único (full la primera vez, incremental luego):
```bash
python -m order_sync --env-file ./.env mongo-auto
```
- Verbose (muestra un resumen de logs de OrderLog desde last_sync):
```bash
python -m order_sync --env-file ./.env mongo-auto --verbose
```

Salida:
- XLSX por cuenta (nombre = `accountName`) con hoja `report` formateada y columnas técnicas ocultas (`orderId`, `__createdAt`, `__lastUpdateAt`).
- Hoja `meta` con `last_sync` (ISO).
- Si Drive está configurado, sube/actualiza el XLSX.

---

## Deploy en AWS EC2 (Ubuntu)

- Código en servidor: `/opt/order-sync`
- Script de ejecución: `/usr/local/bin/order-sync-run`
- Logs:
  - Servicio: `/var/log/order_sync/order_sync.log`
  - Cron (stdout/err): `/var/log/order_sync/runner.log`

### 1) Paquetes
```bash
sudo apt update -y
sudo apt install -y git python3 python3-venv unzip curl
```

### 2) Clonar repo e instalar
```bash
sudo mkdir -p /opt/order-sync /var/log/order_sync
sudo chown -R "$USER":"$USER" /opt/order-sync /var/log/order_sync
cd /opt/order-sync
git clone https://github.com/KevinVinograd/order-sync.git .
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -e .
```

### 3) Secrets en SSM Parameter Store (no .env en disco)
Crear parámetros (ajusta valores y región):
```bash
aws ssm put-parameter --name /order-sync/MONGO_URI --type SecureString --value 'mongodb+srv://USER:PASS@cluster.mongodb.net/?retryWrites=true&w=majority' --overwrite
aws ssm put-parameter --name /order-sync/ACCOUNT_IDS --type String --value '68c322a783f1aee03860e01b' --overwrite
# Por cuenta sin filtro de prefijo y prefijos globales (opcional)
aws ssm put-parameter --name /order-sync/ACCOUNT_IDS_NO_PREFIX --type String --value '' --overwrite
aws ssm put-parameter --name /order-sync/ACCOUNT_REF_PREFIXES --type String --value 'VARE,VARI' --overwrite
aws ssm put-parameter --name /order-sync/GOOGLE_CLIENT_EMAIL --type String --value 'service-account@project.iam.gserviceaccount.com' --overwrite
aws ssm put-parameter --name /order-sync/GOOGLE_PRIVATE_KEY --type SecureString --value '-----BEGIN PRIVATE KEY-----\nABC...\n-----END PRIVATE KEY-----\n' --overwrite
aws ssm put-parameter --name /order-sync/GOOGLE_DRIVE_FOLDER_ID --type String --value 'xxxxxxxxxxxxxxxxxxxx' --overwrite
aws ssm put-parameter --name /order-sync/OUTPUT_DIR --type String --value '/var/log/order_sync' --overwrite
aws ssm put-parameter --name /order-sync/TZ --type String --value 'America/Argentina/Buenos_Aires' --overwrite
```

### 4) Wrapper seguro (lee SSM y ejecuta)
```bash
sudo tee /usr/local/bin/order-sync-run >/dev/null <<'SH'
#!/usr/bin/env bash
set -euo pipefail

exec 9>/tmp/order-sync.lock
flock -n 9 || exit 0

: "${AWS_DEFAULT_REGION:=us-east-1}"; export AWS_DEFAULT_REGION

getp() { aws ssm get-parameter --with-decryption --name "$1" --query 'Parameter.Value' --output text; }

export MONGO_URI="$(getp /order-sync/MONGO_URI)"
export ACCOUNT_IDS="$(getp /order-sync/ACCOUNT_IDS)"
export ACCOUNT_IDS_NO_PREFIX="$(getp /order-sync/ACCOUNT_IDS_NO_PREFIX || true)"
export ACCOUNT_REF_PREFIXES="$(getp /order-sync/ACCOUNT_REF_PREFIXES || true)"
export GOOGLE_CLIENT_EMAIL="$(getp /order-sync/GOOGLE_CLIENT_EMAIL)"
export GOOGLE_PRIVATE_KEY="$(getp /order-sync/GOOGLE_PRIVATE_KEY)"
export GOOGLE_DRIVE_FOLDER_ID="$(getp /order-sync/GOOGLE_DRIVE_FOLDER_ID)"
export OUTPUT_DIR="$(getp /order-sync/OUTPUT_DIR)"
export TZ="$(getp /order-sync/TZ)"

cd /opt/order-sync
. .venv/bin/activate
exec python -m order_sync mongo-auto
SH
sudo chmod 700 /usr/local/bin/order-sync-run
```

### 5) Probar manual
```bash
/usr/local/bin/order-sync-run
tail -n 100 /var/log/order_sync/order_sync.log
```

### 6) Cron (ejemplos)
- Cada 1 minuto (test):
```bash
crontab -e
```
Contenido:
```bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
TZ=America/Argentina/Buenos_Aires
* * * * * /usr/local/bin/order-sync-run >> /var/log/order_sync/runner.log 2>&1
```
- Lunes a viernes 09/12/15/18 (cada 3 horas):
```bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
TZ=America/Argentina/Buenos_Aires
0 9-18/3 * * 1-5 /usr/local/bin/order-sync-run >> /var/log/order_sync/runner.log 2>&1
```
- Todos los días 09–18hs cada 1 hora:
```bash
0 9-18 * * * /usr/local/bin/order-sync-run >> /var/log/order_sync/runner.log 2>&1
```

### 7) Actualizar código en EC2 (cuando haya cambios)
```bash
cd /opt/order-sync
git pull --ff-only
. .venv/bin/activate
python -m pip install -r requirements.txt -e .
/usr/local/bin/order-sync-run
```

### 8) Troubleshooting
- Ver servicio cron:
```bash
systemctl status cron
```
- Ver crontab actual:
```bash
crontab -l
```
- Logs:
```bash
tail -n 200 /var/log/order_sync/runner.log
tail -n 200 /var/log/order_sync/order_sync.log
```

