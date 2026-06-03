# Database Migrations

This folder contains SQL migrations for the database schema.

## Migration File Naming

Migrations use the following naming convention:
```
<timestamp>_description_up.sql    # Upgrade/Apply migration
<timestamp>_description_down.sql  # Downgrade/Rollback migration
```

## Example

- `1717334640_initial_up.sql` - Creates the employees table with UUID primary key
- `1717334640_initial_down.sql` - Drops the employees table

## How to Run Migrations

### Apply all migrations (upgrade)

```bash
psql -h localhost -p 5432 -U employee -d mydatabase -f migrations/1717334640_initial_up.sql
```

### Rollback migrations (downgrade)

```bash
psql -h localhost -p 5432 -U employee -d mydatabase -f migrations/1717334640_initial_down.sql
```

## Creating New Migrations

1. Create two new files with a timestamp suffix (or Unix timestamp):
   - `timestamp_description_up.sql`
   - `timestamp_description_down.sql`

2. Write your SQL in the `up.sql` file for the changes
3. Write the reverse SQL in the `down.sql` file for rollback

## Current Migrations

- `1717334640_initial_up.sql` - Initial schema with employees table using UUID keys
