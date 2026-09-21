# Database Design — Yojana Sahayak

## Overview
Yojana Sahayak utilizes PostgreSQL for transactional data persistence and Supabase for managed authentication and database hosting.

## Core Relational Tables

### 1. `profiles`
Stores citizen profile attributes used by the deterministic matching engine.
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to `auth.users`)
- `name`: VARCHAR(255)
- `state`: VARCHAR(100)
- `district`: VARCHAR(100)
- `age`: INTEGER
- `gender`: VARCHAR(50)
- `annual_income`: NUMERIC(12, 2)
- `occupation`: VARCHAR(100)
- `category`: VARCHAR(50) (e.g., General, OBC, SC, ST, EWS)
- `area`: VARCHAR(50) (Rural / Urban)
- `disability`: BOOLEAN
- `created_at`: TIMESTAMP WITH TIME ZONE
- `updated_at`: TIMESTAMP WITH TIME ZONE

### 2. `schemes`
Stores verified government welfare scheme information.
- `id`: UUID (Primary Key)
- `slug`: VARCHAR(255) UNIQUE
- `name`: VARCHAR(255)
- `name_hi`: VARCHAR(255)
- `description`: TEXT
- `description_hi`: TEXT
- `category`: VARCHAR(100) (Agriculture, Education, Health, etc.)
- `ministry`: VARCHAR(255)
- `level`: VARCHAR(50) (Central / State)
- `states`: JSONB (List of applicable states or `["ALL"]`)
- `eligibility_rules`: JSONB (Structured deterministic rule definitions)
- `benefits`: JSONB (List of benefits in EN/HI)
- `documents`: JSONB (Required documents list)
- `application_steps`: JSONB (Step-by-step procedure)
- `official_url`: TEXT (Official government portal link)
- `source_url`: TEXT (Origin government data source link)
- `source_name`: VARCHAR(100) (e.g., "Data.gov.in", "Ministry Portal")
- `last_verified_at`: TIMESTAMP WITH TIME ZONE
- `verification_status`: VARCHAR(50) (Verified, Pending, Archived)
- `active`: BOOLEAN DEFAULT TRUE
- `created_at`: TIMESTAMP WITH TIME ZONE
- `updated_at`: TIMESTAMP WITH TIME ZONE

### 3. `saved_schemes`
Bookmarked schemes for quick access.
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key)
- `scheme_id`: UUID (Foreign Key to `schemes.id`)
- `created_at`: TIMESTAMP WITH TIME ZONE

### 4. `scheme_tracking`
Application lifecycle tracking for citizens.
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key)
- `scheme_id`: UUID (Foreign Key to `schemes.id`)
- `status`: VARCHAR(50) (`Saved`, `Planning to Apply`, `Application Started`, `Applied`, `Completed`)
- `notes`: TEXT
- `created_at`: TIMESTAMP WITH TIME ZONE
- `updated_at`: TIMESTAMP WITH TIME ZONE
