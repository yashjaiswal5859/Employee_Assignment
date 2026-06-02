# Database Migrations

This folder contains SQL migrations for the database schema.

## Migration File Naming

Migrations use the following naming convention:
```
YYYYMMDDHHMMSS_description_up.sql    # Upgrade/Apply migration
YYYYMMDDHHMMSS_description_down.sql  # Downgrade/Rollback migration
```

## Example

- `20260602094400_initial_up.sql` - Creates the employees table
- `20260602094400_initial_down.sql` - Drops the employees table

## How to Run Migrations

### Apply all migrations (upgrade)
```bash
# Inside the container
docker compose exec postgres psql -U employee -d mydatabase -f /docker-entrypoint-initdb.d/migrations/20260602094400_initial_up.sql

# Or from host using psql
psql -h localhost -U employee -d mydatabase -f migrations/20260602094400_initial_up.sql
```

### Rollback migrations (downgrade)
```bash
psql -h localhost -U employee -d mydatabase -f migrations/20260602094400_initial_down.sql
```

## Creating New Migrations

1. Create two new files with timestamp:
   - `YYYYMMDDHHMMSS_description_up.sql`
   - `YYYYMMDDHHMMSS_description_down.sql`

2. Write your SQL in the `up.sql` file for the changes
3. Write the reverse SQL in the `down.sql` file for rollback

## Current Migrations

- `20260602094400_initial_up.sql` - Initial schema with employees table
