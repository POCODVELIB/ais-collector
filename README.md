**`README.md`** :
```markdown
# AIS Collector

Collecte en temps réel les messages AIS sur les côtes françaises et les ingère dans Snowflake.

## Stack
- **Source** : [AISStream.io](https://aisstream.io) (WebSocket)
- **Stockage** : Snowflake (table `AIS_RAW`, colonne `RAW_JSON VARIANT`)
- **Scheduler** : GitHub Actions (toutes les x heures à définir )

## Structure
```
├── ais_stream.py        # Collecte et ingestion Snowflake
├── ais_dataprep.py      # Preprocessing et encoding four-hot
├── snowflake_config.py  # Connexion Snowflake via variables d'env
├── requirements.txt     # Dépendances
└── .github/
    └── workflows/
        └── ais_collect.yml  # GitHub Actions
```

## Variables d'environnement
À configurer dans `Settings → Secrets → Actions` sur GitHub :

| Variable | Description |
|---|---|
| `AISSTREAM_API_KEY` | Clé API AISStream.io |
| `SF_USER` | Utilisateur Snowflake |
| `SF_PASSWORD` | Mot de passe Snowflake |
| `SF_ACCOUNT` | Account Snowflake (ex: `abc123.eu-west-1`) |
| `SF_WAREHOUSE` | Warehouse Snowflake |
| `SF_DATABASE` | Database Snowflake |
| `SF_SCHEMA` | Schema Snowflake |

## Snowflake DDL
```sql
CREATE TABLE IF NOT EXISTS AIS_RAW (
    RAW_JSON VARIANT
);
```
