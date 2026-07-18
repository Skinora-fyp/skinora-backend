-- ============================================================
-- Skinora Database Schema — MySQL 8.0
-- Run this entire file in MySQL Workbench:
--   File → Open SQL Script → skinora_db.sql → Execute (lightning bolt)
-- ============================================================

CREATE DATABASE IF NOT EXISTS skinora_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE skinora_db;

-- ──────────────────────────────────────────────
-- 1. users
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id                  INT           NOT NULL AUTO_INCREMENT,
  name                VARCHAR(100)  NOT NULL,
  email               VARCHAR(255)  NOT NULL,
  password_hash       VARCHAR(255)  NULL,          -- NULL for Google-only accounts
  google_id           VARCHAR(255)  NULL,
  avatar_url          TEXT          NULL,
  is_verified         TINYINT(1)    NOT NULL DEFAULT 0,
  verification_token  VARCHAR(255)  NULL,
  created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email    (email),
  UNIQUE KEY uq_users_google   (google_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────────
-- 2. detections
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS detections (
  id                    INT          NOT NULL AUTO_INCREMENT,
  user_id               INT          NOT NULL,
  image_url             TEXT         NULL,
  skin_type             ENUM('Dry','Oily','Normal')              NOT NULL,
  skin_type_confidence  FLOAT        NOT NULL,                   -- 0.0 – 1.0
  acne_status           ENUM('Acne','NoAcne')                   NOT NULL,
  acne_confidence       FLOAT        NOT NULL,                   -- 0.0 – 1.0
  final_condition       VARCHAR(50)  NOT NULL,                   -- e.g. Oily_Acne
  routing               ENUM('direct','questionnaire','consultant') NOT NULL DEFAULT 'direct',
  detected_at           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_detections_user (user_id),
  CONSTRAINT fk_detections_user FOREIGN KEY (user_id)
    REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────────
-- 3. questions
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS questions (
  id              INT          NOT NULL AUTO_INCREMENT,
  question_text   TEXT         NOT NULL,
  category        VARCHAR(100) NOT NULL,
  relevance       JSON         NULL,   -- list of final_condition strings this applies to
  answer_type     ENUM('yes_no','scale_1_5','multiple_choice') NOT NULL,
  answer_options  JSON         NULL,
  sort_order      INT          NOT NULL DEFAULT 0,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────────
-- 4. questionnaire_responses
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS questionnaire_responses (
  id            INT      NOT NULL AUTO_INCREMENT,
  detection_id  INT      NOT NULL,
  question_id   INT      NOT NULL,
  answer_value  TEXT     NOT NULL,
  answered_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_qr_detection (detection_id),
  CONSTRAINT fk_qr_detection FOREIGN KEY (detection_id)
    REFERENCES detections(id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_qr_question FOREIGN KEY (question_id)
    REFERENCES questions(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────────
-- 5. remedies  (each remedy stored once)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS remedies (
  id                INT          NOT NULL AUTO_INCREMENT,
  name              VARCHAR(255) NOT NULL,
  ingredients       JSON         NULL,
  instructions      JSON         NOT NULL,
  confidence_level  ENUM('High','Medium') NOT NULL DEFAULT 'High',
  source_url        TEXT         NULL,
  lifestyle_tags    JSON         NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────────
-- 6. condition_remedies  (junction: condition ↔ remedy)
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS condition_remedies (
  id               INT         NOT NULL AUTO_INCREMENT,
  final_condition  VARCHAR(50) NOT NULL,
  remedy_id        INT         NOT NULL,
  sort_order       INT         NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uq_condition_remedy (final_condition, remedy_id),
  CONSTRAINT fk_cr_remedy FOREIGN KEY (remedy_id)
    REFERENCES remedies(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────────
-- 7. tracking
-- ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tracking (
  id             INT      NOT NULL AUTO_INCREMENT,
  user_id        INT      NOT NULL,
  detection_id   INT      NULL,
  remedy_id      INT      NOT NULL,
  frequency      ENUM('weekly','monthly') NOT NULL DEFAULT 'weekly',
  next_reminder  DATETIME NULL,
  last_status    ENUM('better','no_progress','worse') NULL,
  is_active      TINYINT(1) NOT NULL DEFAULT 1,
  started_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_tracking_user    (user_id),
  KEY idx_tracking_next    (next_reminder),
  CONSTRAINT fk_tracking_user      FOREIGN KEY (user_id)       REFERENCES users(id)      ON DELETE CASCADE,
  CONSTRAINT fk_tracking_detection FOREIGN KEY (detection_id)  REFERENCES detections(id) ON DELETE SET NULL,
  CONSTRAINT fk_tracking_remedy    FOREIGN KEY (remedy_id)     REFERENCES remedies(id)   ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ============================================================
-- SEED DATA — Remedies
-- ============================================================

INSERT INTO remedies (name, ingredients, instructions, confidence_level, source_url, lifestyle_tags) VALUES
(
  'Aloe Vera Gel',
  '["Pure aloe vera gel"]',
  '["Wash the face gently with a mild cleanser.", "Apply a thin, even layer of pure aloe vera gel to the entire face.", "Leave it on overnight.", "Wash off with cool water the next morning."]',
  'High',
  'https://www.nccih.nih.gov/health/aloe-vera',
  '["high_stress", "low_water"]'
),
(
  'Raw Honey Face Mask',
  '["Raw honey (unpasteurised)"]',
  '["Cleanse the face with warm water.", "Apply a thin layer of raw honey to the face.", "Leave it on for 15 minutes.", "Rinse thoroughly with lukewarm water and pat dry."]',
  'High',
  'https://www.reddit.com/search/?q=raw+honey+face+mask&cId=b4b0bd6d-296a-43d7-b6f7-68523ce1c9ba&iId=7f315009-c15b-4f90-bc26-7ad14e8ea8c9',
  '["poor_sleep"]'
),
(
  'Oatmeal Face Mask',
  '["Plain oatmeal (finely ground)", "Warm water"]',
  '["Mix finely ground oatmeal with enough warm water to form a smooth paste.", "Apply the paste gently to the face, avoiding the eye area.", "Leave it on for 15 minutes.", "Rinse gently with cool water and pat dry."]',
  'High',
  'https://www.byrdie.com/oatmeal-facial-masks-2442870',
  '["high_stress", "poor_sleep"]'
),
(
  'Green Tea Toner',
  '["Green tea bag or 1 tsp loose green tea", "Hot water", "Cotton pads"]',
  '["Brew a strong cup of green tea with hot water.", "Allow the tea to cool completely to room temperature.", "Pour into a clean bottle or bowl.", "Apply to the face using a cotton pad.", "Use once daily, preferably in the morning or evening routine."]',
  'High',
  'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5384166/',
  '["high_stress", "dairy"]'
),
(
  'Avocado Face Mask',
  '["Half a ripe avocado"]',
  '["Mash half a ripe avocado in a bowl until smooth.", "Apply the mashed avocado evenly to a cleansed face.", "Leave it on for 15 minutes.", "Rinse gently with lukewarm water and pat dry."]',
  'High',
  'https://www.siobeauty.com/blogs/resource-center/6-avocado-face-mask-recipes-you-can-make-at-home',
  '["low_water", "poor_sleep"]'
),
(
  'Rose Water Toner',
  '["Pure rose water", "Cotton pads"]',
  '["Pour pure rose water onto a clean cotton pad.", "Gently wipe the cotton pad across the face.", "Use morning and evening after cleansing.", "No rinsing required — allow it to absorb into the skin."]',
  'High',
  'https://plumgoodness.com/blogs/skincare/bulgarian-valley-rose-water-toner-isn-t-your-ordinary-toner',
  '["high_stress"]'
),
(
  'Cucumber Face Mask',
  '["Half a fresh cucumber"]',
  '["Blend half a fresh cucumber until smooth.", "Apply the cucumber paste evenly to a cleansed face.", "Leave it on for 15 minutes.", "Rinse with cool water and pat dry."]',
  'High',
  'https://www.healthline.com/health/beauty-skin-care/cucumber-face-mask',
  '["high_stress", "low_water"]'
);

-- ============================================================
-- SEED DATA — Condition ↔ Remedy mappings
-- ============================================================

INSERT INTO condition_remedies (final_condition, remedy_id, sort_order) VALUES
-- Dry_Acne: Aloe Vera, Raw Honey, Oatmeal
('Dry_Acne',     1, 1), ('Dry_Acne',     2, 2), ('Dry_Acne',     3, 3),
-- Oily_Acne: Aloe Vera, Green Tea, Raw Honey
('Oily_Acne',    1, 1), ('Oily_Acne',    4, 2), ('Oily_Acne',    2, 3),
-- Normal_Acne: Aloe Vera, Raw Honey, Green Tea
('Normal_Acne',  1, 1), ('Normal_Acne',  2, 2), ('Normal_Acne',  4, 3),
-- Dry_NoAcne: Oatmeal, Avocado, Aloe Vera
('Dry_NoAcne',   3, 1), ('Dry_NoAcne',   5, 2), ('Dry_NoAcne',   1, 3),
-- Oily_NoAcne: Green Tea, Rose Water, Aloe Vera
('Oily_NoAcne',  4, 1), ('Oily_NoAcne',  6, 2), ('Oily_NoAcne',  1, 3),
-- Normal_NoAcne: Cucumber, Aloe Vera, Raw Honey
('Normal_NoAcne',7, 1), ('Normal_NoAcne',1, 2), ('Normal_NoAcne',2, 3);

-- ============================================================
-- SEED DATA — Questions
-- ============================================================

INSERT INTO questions (question_text, category, relevance, answer_type, answer_options, sort_order) VALUES
('How many glasses of water do you drink daily?', 'water', NULL, 'multiple_choice', '["Less than 4 glasses", "4–8 glasses", "More than 8 glasses"]', 1),
('How would you rate your stress level?', 'stress', NULL, 'multiple_choice', '["Low", "Medium", "High"]', 2),
('How many hours of sleep do you get per night?', 'sleep', NULL, 'multiple_choice', '["Less than 6 hours", "6–8 hours", "More than 8 hours"]', 3),
('Do you currently use any skincare products?', 'products', NULL, 'yes_no', '["yes", "no"]', 4),
('Do you consume dairy products regularly?', 'dairy', '["Dry_Acne","Oily_Acne","Normal_Acne"]', 'yes_no', '["yes", "no"]', 5),
('How oily does your skin feel by midday?', 'oil_production', '["Oily_Acne","Oily_NoAcne"]', 'scale_1_5', NULL, 6),
('How often does your skin feel tight or flaky?', 'skin_dryness', '["Dry_Acne","Dry_NoAcne"]', 'scale_1_5', NULL, 7),
('Do you spend many hours in air-conditioned spaces?', 'ac_exposure', '["Dry_Acne","Dry_NoAcne","Normal_NoAcne"]', 'yes_no', '["yes", "no"]', 8);

-- ============================================================
-- Useful join queries for reference
-- ============================================================

-- Get all remedies for a specific condition
-- SELECT r.* FROM remedies r
-- JOIN condition_remedies cr ON r.id = cr.remedy_id
-- WHERE cr.final_condition = 'Oily_Acne'
-- ORDER BY cr.sort_order;

-- Get full detection history for a user
-- SELECT d.*, u.name, u.email
-- FROM detections d
-- JOIN users u ON d.user_id = u.id
-- WHERE d.user_id = 1
-- ORDER BY d.detected_at DESC;

-- Get active tracking with remedy and detection info
-- SELECT t.*, r.name AS remedy_name, d.final_condition
-- FROM tracking t
-- JOIN remedies r ON t.remedy_id = r.id
-- LEFT JOIN detections d ON t.detection_id = d.id
-- WHERE t.user_id = 1 AND t.is_active = 1;

-- Get questionnaire answers for a detection session
-- SELECT q.question_text, q.category, qr.answer_value, qr.answered_at
-- FROM questionnaire_responses qr
-- JOIN questions q ON qr.question_id = q.id
-- WHERE qr.detection_id = 42
-- ORDER BY q.sort_order;

-- Get due reminders (run by APScheduler daily)
-- SELECT t.*, u.email, r.name AS remedy_name
-- FROM tracking t
-- JOIN users u ON t.user_id = u.id
-- JOIN remedies r ON t.remedy_id = r.id
-- WHERE t.is_active = 1 AND t.next_reminder <= NOW();
