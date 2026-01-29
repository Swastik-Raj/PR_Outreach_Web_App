/*
  # Add Missing Columns to Existing Tables

  This migration adds critical columns that are referenced in the application code
  but were missing from the database schema. These columns are essential for:
  - Email verification and enrichment tracking
  - Unsubscribe functionality
  - Blocked email tracking
  - Campaign analytics accuracy

  ## Changes Made

  1. **journalists table** - Add 4 columns:
     - `email_confidence` (integer) - Stores confidence score from Hunter API (0-100)
     - `email_source` (text) - Tracks where email came from (hunter, manual, etc.)
     - `unsubscribed` (boolean) - Marks if journalist opted out
     - `unsubscribed_at` (timestamptz) - Timestamp when journalist unsubscribed

  2. **campaigns table** - Add 2 columns:
     - `blocked_count` (integer) - Counts emails blocked by ISPs
     - `unsubscribed_count` (integer) - Counts unsubscribe requests

  3. **emails table** - Add 1 column:
     - `blocked_at` (timestamptz) - Timestamp when email was blocked

  ## Security
  - All tables already have RLS enabled
  - No policy changes needed (service_role has full access)

  ## Notes
  - All numeric columns default to 0 for accurate analytics
  - All boolean columns default to false for safe operation
  - Timestamp columns are nullable (only set when event occurs)
  - Uses IF NOT EXISTS to prevent errors if columns already present
*/

-- Add missing columns to journalists table
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'journalists' AND column_name = 'email_confidence'
  ) THEN
    ALTER TABLE journalists ADD COLUMN email_confidence integer DEFAULT 0;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'journalists' AND column_name = 'email_source'
  ) THEN
    ALTER TABLE journalists ADD COLUMN email_source text DEFAULT 'hunter';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'journalists' AND column_name = 'unsubscribed'
  ) THEN
    ALTER TABLE journalists ADD COLUMN unsubscribed boolean DEFAULT false;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'journalists' AND column_name = 'unsubscribed_at'
  ) THEN
    ALTER TABLE journalists ADD COLUMN unsubscribed_at timestamptz;
  END IF;
END $$;

-- Add missing columns to campaigns table
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'campaigns' AND column_name = 'blocked_count'
  ) THEN
    ALTER TABLE campaigns ADD COLUMN blocked_count integer DEFAULT 0;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'campaigns' AND column_name = 'unsubscribed_count'
  ) THEN
    ALTER TABLE campaigns ADD COLUMN unsubscribed_count integer DEFAULT 0;
  END IF;
END $$;

-- Add missing column to emails table
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'emails' AND column_name = 'blocked_at'
  ) THEN
    ALTER TABLE emails ADD COLUMN blocked_at timestamptz;
  END IF;
END $$;

-- Update the increment_campaign_counter function to handle new counters
CREATE OR REPLACE FUNCTION increment_campaign_counter(campaign_id uuid, field_name text)
RETURNS void AS $$
BEGIN
  CASE field_name
    WHEN 'sent_count' THEN
      UPDATE campaigns SET sent_count = sent_count + 1 WHERE id = campaign_id;
    WHEN 'opened_count' THEN
      UPDATE campaigns SET opened_count = opened_count + 1 WHERE id = campaign_id;
    WHEN 'clicked_count' THEN
      UPDATE campaigns SET clicked_count = clicked_count + 1 WHERE id = campaign_id;
    WHEN 'bounced_count' THEN
      UPDATE campaigns SET bounced_count = bounced_count + 1 WHERE id = campaign_id;
    WHEN 'blocked_count' THEN
      UPDATE campaigns SET blocked_count = blocked_count + 1 WHERE id = campaign_id;
    WHEN 'unsubscribed_count' THEN
      UPDATE campaigns SET unsubscribed_count = unsubscribed_count + 1 WHERE id = campaign_id;
  END CASE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;