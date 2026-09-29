-- IronGraph-Engine Biomechanical Knowledge Graph & Workout Adaptation Schema
-- PostgreSQL 16+

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Lifter Profiles & Volume Landmarks
CREATE TABLE IF NOT EXISTS lifter_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    experience_tier VARCHAR(50) NOT NULL DEFAULT 'intermediate', -- 'beginner', 'intermediate', 'advanced'
    volume_landmarks JSONB NOT NULL DEFAULT '{
        "chest": {"mev": 8, "mav": 14, "mrv": 20},
        "back": {"mev": 10, "mav": 16, "mrv": 22},
        "quads": {"mev": 8, "mav": 12, "mrv": 18},
        "hamstrings": {"mev": 6, "mav": 10, "mrv": 14}
    }'::jsonb,
    baseline_1rms JSONB NOT NULL DEFAULT '{}'::jsonb,
    active_contraindications JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Exercise Taxonomy & Biomechanical Profiles
CREATE TABLE IF NOT EXISTS exercises (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    movement_pattern VARCHAR(100) NOT NULL, -- 'squat', 'hinge', 'horizontal_press', 'horizontal_pull', 'vertical_press', 'vertical_pull'
    primary_muscles JSONB NOT NULL,
    secondary_muscles JSONB NOT NULL DEFAULT '[]'::jsonb,
    axial_stress_rating INT NOT NULL CHECK (axial_stress_rating BETWEEN 0 AND 10),
    required_equipment VARCHAR(100) NOT NULL,
    sfr_rating VARCHAR(50) NOT NULL DEFAULT 'high', -- 'moderate', 'high', 'very_high'
    is_unilateral BOOLEAN NOT NULL DEFAULT FALSE,
    resistance_curve_focus VARCHAR(50) NOT NULL DEFAULT 'mid_range', -- 'lengthened', 'mid_range', 'shortened'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Biomechanical Graph Edges (Muscles, Contraindications, Substitutes, APS)
CREATE TABLE IF NOT EXISTS biomechanical_edges (
    source_id VARCHAR(100) NOT NULL,
    target_id VARCHAR(100) NOT NULL,
    relation VARCHAR(100) NOT NULL, -- 'contraindicated_for', 'substitute_for', 'antagonist_pair_with', 'targets_muscle'
    properties JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (source_id, target_id, relation)
);

-- 4. Planned Workouts (Standard Regimens)
CREATE TABLE IF NOT EXISTS planned_workouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lifter_id UUID NOT NULL REFERENCES lifter_profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    target_muscle_groups JSONB NOT NULL,
    exercise_template JSONB NOT NULL,
    target_duration_min INT NOT NULL DEFAULT 60,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Session Adaptations (Atypical Friction Ingestion & Output)
CREATE TABLE IF NOT EXISTS session_adaptations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lifter_id UUID NOT NULL REFERENCES lifter_profiles(id) ON DELETE CASCADE,
    planned_workout_id UUID REFERENCES planned_workouts(id) ON DELETE SET NULL,
    drawbacks JSONB NOT NULL,
    adapted_workout JSONB NOT NULL,
    effective_volume_delta INT NOT NULL DEFAULT 0,
    coaching_prose TEXT NOT NULL,
    committed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indices for Traversal & Retrieval
CREATE INDEX IF NOT EXISTS idx_lifters_id ON lifter_profiles(id);
CREATE INDEX IF NOT EXISTS idx_exercises_pattern ON exercises(movement_pattern);
CREATE INDEX IF NOT EXISTS idx_edges_source ON biomechanical_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON biomechanical_edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edges_relation ON biomechanical_edges(relation);
CREATE INDEX IF NOT EXISTS idx_adaptations_lifter ON session_adaptations(lifter_id, committed_at DESC);

-- Seed Data: Sample Lifter Profile
INSERT INTO lifter_profiles (id, name, experience_tier, baseline_1rms, active_contraindications)
VALUES (
    'f1e2d3c4-b5a6-7890-1234-567890abcdef',
    'Alex Turner',
    'advanced',
    '{"barbell_back_squat": 160, "incline_dumbbell_press": 42, "barbell_bent_over_row": 110}'::jsonb,
    '["acute_lumbar_strain"]'::jsonb
) ON CONFLICT DO NOTHING;

-- Seed Exercises
INSERT INTO exercises (id, name, movement_pattern, primary_muscles, secondary_muscles, axial_stress_rating, required_equipment, sfr_rating, resistance_curve_focus) VALUES
('barbell_back_squat', 'Barbell Back Squat', 'squat', '["quads", "glutes"]'::jsonb, '["adductors", "spinal_erectors"]'::jsonb, 9, 'squat_rack', 'moderate', 'mid_range'),
('hack_squat', 'Machine Hack Squat', 'squat', '["quads"]'::jsonb, '["glutes"]'::jsonb, 3, 'hack_squat_machine', 'very_high', 'lengthened'),
('leg_press', '45-Degree Leg Press', 'squat', '["quads"]'::jsonb, '["glutes"]'::jsonb, 2, 'leg_press_machine', 'high', 'mid_range'),
('incline_dumbbell_press', 'Incline Dumbbell Bench Press', 'horizontal_press', '["upper_chest"]'::jsonb, '["anterior_deltoid", "triceps"]'::jsonb, 1, 'dumbbells', 'very_high', 'lengthened'),
('chest_supported_tbar_row', 'Chest-Supported T-Bar Row', 'horizontal_pull', '["lats", "rhomboids"]'::jsonb, '["biceps", "rear_delts"]'::jsonb, 1, 'tbar_machine', 'very_high', 'lengthened'),
('barbell_bent_over_row', 'Barbell Bent-Over Row', 'horizontal_pull', '["lats", "upper_back"]'::jsonb, '["spinal_erectors", "biceps"]'::jsonb, 7, 'barbell', 'moderate', 'mid_range'),
('seated_leg_curl', 'Seated Hamstring Leg Curl', 'knee_flexion', '["hamstrings"]'::jsonb, '["gastrocnemius"]'::jsonb, 0, 'leg_curl_machine', 'very_high', 'lengthened'),
('romanian_deadlift', 'Barbell Romanian Deadlift', 'hinge', '["hamstrings", "glutes"]'::jsonb, '["spinal_erectors"]'::jsonb, 8, 'barbell', 'high', 'lengthened')
ON CONFLICT DO NOTHING;

-- Seed Biomechanical Edges (Substitutes & Antagonist Pairings)
INSERT INTO biomechanical_edges (source_id, target_id, relation, properties) VALUES
('barbell_back_squat', 'hack_squat', 'substitute_for', '{"reason": "lowers_axial_stress_preserves_quad_tension"}'::jsonb),
('barbell_back_squat', 'leg_press', 'substitute_for', '{"reason": "eliminates_spinal_loading"}'::jsonb),
('barbell_bent_over_row', 'chest_supported_tbar_row', 'substitute_for', '{"reason": "eliminates_lower_back_fatigue"}'::jsonb),
('incline_dumbbell_press', 'chest_supported_tbar_row', 'antagonist_pair_with', '{"antagonist_plane": "horizontal_push_pull", "time_savings_pct": 45}'::jsonb)
ON CONFLICT DO NOTHING;
