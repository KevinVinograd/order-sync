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

