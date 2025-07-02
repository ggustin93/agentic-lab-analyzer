# Supabase Migrations

This directory contains all database schema migrations for the Agentic Lab Analyzer project.

## 📁 Structure

```
supabase/
├── migrations/           # Database schema changes
├── seeds/               # Initial data and test data
└── types/               # TypeScript type definitions
```

## 🔄 Migration Naming Convention

```
YYYYMMDD_NNN_description.sql
```

- **YYYYMMDD**: Date (e.g., 20250102)
- **NNN**: Sequential number (001, 002, etc.)
- **description**: Brief description in snake_case

## 📝 Current Migrations

1. **20250102_001_add_progress_tracking_columns.sql**
   - Adds `progress` and `processing_stage` columns to `documents` table
   - Enables real-time progress tracking during document analysis
   - Adds index for efficient querying of processing documents

## 🚀 How to Apply Migrations

### Using Supabase MCP (Recommended)
```typescript
// In the AI agent context
mcp_supabase_apply_migration({
  project_id: "eeogiqkrjaubijuhirfn",
  name: "migration_name",
  query: "SQL content here"
})
```

### Using Supabase CLI
```bash
supabase db push
```

### Manual Application
Copy and paste the SQL from migration files into the Supabase SQL Editor.

## 🔄 Rollback Migrations

Each migration should have a corresponding rollback file with the suffix `_rollback.sql`.

## 🧪 Testing Migrations

1. Test on a development branch/database first
2. Verify data integrity after applying
3. Test rollback procedures
4. Document any breaking changes

## 📊 Best Practices

- ✅ Always backup before applying migrations in production
- ✅ Include comments explaining the purpose
- ✅ Add appropriate indexes for performance
- ✅ Use `IF EXISTS` / `IF NOT EXISTS` for safety
- ✅ Test rollback procedures
- ❌ Never modify existing migration files once applied 