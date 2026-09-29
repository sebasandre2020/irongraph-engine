"""Intelligent Gym Routine Text Parser for English and Spanish formats."""

import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class ParsedExercise(BaseModel):
    """Structured exercise extracted from unstructured text."""
    name: str
    movement_pattern: str
    primary_muscles: List[str]
    axial_stress_rating: int = 1
    sets: int = 3
    reps: str = "8-10"
    load_str: Optional[str] = None
    load_kg: Optional[float] = None
    required_equipment: str = "general"
    notes: Optional[str] = None
    raw_line: str = ""


class ParsedDay(BaseModel):
    """A day section extracted from a multi-day routine."""
    day_id: str
    title: str
    exercises: List[ParsedExercise] = Field(default_factory=list)


# Biomechanical keyword mapping across Spanish and English
KEYWORD_TAXONOMY = [
    # Squats & Quads
    {
        "keywords": ["hack squat", "hack"],
        "name": "Machine Hack Squat",
        "pattern": "squat",
        "muscles": ["quads"],
        "axial": 3,
        "equipment": "hack_squat_machine"
    },
    {
        "keywords": ["leg press", "prensa"],
        "name": "45-Degree Leg Press",
        "pattern": "squat",
        "muscles": ["quads"],
        "axial": 2,
        "equipment": "leg_press_machine"
    },
    {
        "keywords": ["extensión cuádriceps", "leg extension", "extension cuadriceps", "extension de cuadriceps"],
        "name": "Leg Extension",
        "pattern": "knee_extension",
        "muscles": ["quads"],
        "axial": 0,
        "equipment": "leg_extension_machine"
    },
    {
        "keywords": ["zancadas búlgaras", "zancadas bulgaras", "bulgarian split squat", "zancadas"],
        "name": "Bulgarian Split Squats",
        "pattern": "squat",
        "muscles": ["quads", "glutes"],
        "axial": 3,
        "equipment": "dumbbells"
    },
    {
        "keywords": ["barbell squat", "back squat", "sentadilla con barra", "sentadilla libre", "squat"],
        "name": "Barbell Back Squat",
        "pattern": "squat",
        "muscles": ["quads", "glutes"],
        "axial": 9,
        "equipment": "squat_rack"
    },
    # Posterior Chain & Hamstrings
    {
        "keywords": ["leg curl", "curl femoral", "curl isquios", "isquios"],
        "name": "Seated Hamstring Leg Curl",
        "pattern": "knee_flexion",
        "muscles": ["hamstrings"],
        "axial": 0,
        "equipment": "leg_curl_machine"
    },
    {
        "keywords": ["peso muerto rumano", "rumanian deadlift", "rdl", "deadlift", "peso muerto"],
        "name": "Romanian Deadlift",
        "pattern": "hinge",
        "muscles": ["hamstrings", "glutes"],
        "axial": 8,
        "equipment": "barbell"
    },
    {
        "keywords": ["hip thrust"],
        "name": "Barbell Hip Thrust",
        "pattern": "hip_extension",
        "muscles": ["glutes"],
        "axial": 2,
        "equipment": "barbell"
    },
    # Horizontal Pull & Back
    {
        "keywords": ["mid row", "remo en máquina", "remo maquina"],
        "name": "Machine Mid Row",
        "pattern": "horizontal_pull",
        "muscles": ["lats", "upper_back"],
        "axial": 1,
        "equipment": "row_machine"
    },
    {
        "keywords": ["tbar row", "t-bar row", "chest supported", "pecho en banco", "tbar"],
        "name": "Chest-Supported T-Bar Row",
        "pattern": "horizontal_pull",
        "muscles": ["lats", "rhomboids"],
        "axial": 1,
        "equipment": "tbar_machine"
    },
    {
        "keywords": ["barbell row", "remo con barra", "remo inclinado"],
        "name": "Barbell Bent-Over Row",
        "pattern": "horizontal_pull",
        "muscles": ["lats", "upper_back"],
        "axial": 7,
        "equipment": "barbell"
    },
    {
        "keywords": ["remo sentado", "cable row", "seated cable row"],
        "name": "Seated Cable Row",
        "pattern": "horizontal_pull",
        "muscles": ["lats", "rhomboids"],
        "axial": 2,
        "equipment": "cable_machine"
    },
    # Vertical Pull & Lats
    {
        "keywords": ["jalón al pecho", "jalon al pecho", "lat pulldown", "pulldown", "polea al pecho"],
        "name": "Lat Pulldown (Cable)",
        "pattern": "vertical_pull",
        "muscles": ["lats"],
        "axial": 1,
        "equipment": "cable_pulldown"
    },
    {
        "keywords": ["pullover", "pull-over", "pull over"],
        "name": "Cable Pullover",
        "pattern": "shoulder_extension",
        "muscles": ["lats"],
        "axial": 0,
        "equipment": "cable_machine"
    },
    # Horizontal Press & Chest
    {
        "keywords": ["press inclinado", "incline dumbbell press", "incline bench press", "incline press"],
        "name": "Incline Dumbbell Bench Press",
        "pattern": "horizontal_press",
        "muscles": ["upper_chest", "triceps"],
        "axial": 1,
        "equipment": "dumbbells"
    },
    {
        "keywords": ["press plano", "flat dumbbell press", "bench press", "press de banca"],
        "name": "Flat Dumbbell Press",
        "pattern": "horizontal_press",
        "muscles": ["chest", "triceps"],
        "axial": 1,
        "equipment": "dumbbells"
    },
    {
        "keywords": ["fondos", "dips", "chest dips"],
        "name": "Chest Dips",
        "pattern": "horizontal_press",
        "muscles": ["chest", "triceps"],
        "axial": 1,
        "equipment": "dip_bars"
    },
    {
        "keywords": ["aperturas", "cable fly", "cable flye", "peck deck", "pec deck"],
        "name": "Cable Chest Flyes",
        "pattern": "horizontal_adduction",
        "muscles": ["chest"],
        "axial": 0,
        "equipment": "cable_machine"
    },
    # Shoulders
    {
        "keywords": ["lateral rises", "lateral raises", "elevaciones laterales"],
        "name": "Cable Lateral Raises",
        "pattern": "shoulder_abduction",
        "muscles": ["lateral_deltoid"],
        "axial": 0,
        "equipment": "cable_machine"
    },
    {
        "keywords": ["shoulder press", "press militar", "overhead press"],
        "name": "Machine Shoulder Press",
        "pattern": "vertical_press",
        "muscles": ["anterior_deltoid", "triceps"],
        "axial": 4,
        "equipment": "shoulder_press_machine"
    },
    {
        "keywords": ["reverse cable crossover", "pajaros", "rear delt fly"],
        "name": "Reverse Cable Flyes",
        "pattern": "horizontal_abduction",
        "muscles": ["rear_deltoids"],
        "axial": 0,
        "equipment": "cable_machine"
    },
    # Arms
    {
        "keywords": ["curl predicador", "preacher curl"],
        "name": "Preacher Curl (EZ Bar)",
        "pattern": "elbow_flexion",
        "muscles": ["biceps"],
        "axial": 0,
        "equipment": "preacher_bench"
    },
    {
        "keywords": ["curl bayesian", "bayesian curl", "curl inclinado", "incline curl"],
        "name": "Bayesian / Incline Dumbbell Curl",
        "pattern": "elbow_flexion",
        "muscles": ["biceps"],
        "axial": 0,
        "equipment": "dumbbells"
    },
    {
        "keywords": ["curl martillo", "hammer curl"],
        "name": "Seated Hammer Curl",
        "pattern": "elbow_flexion",
        "muscles": ["brachialis", "forearms"],
        "axial": 0,
        "equipment": "dumbbells"
    },
    {
        "keywords": ["skullcrusher", "skull crusher", "press frances"],
        "name": "Barbell Skullcrushers",
        "pattern": "elbow_extension",
        "muscles": ["triceps"],
        "axial": 0,
        "equipment": "barbell"
    },
    {
        "keywords": ["extensión de triceps", "extension triceps", "triceps pushdown", "tricep pushdown"],
        "name": "Triceps Cable Pushdown",
        "pattern": "elbow_extension",
        "muscles": ["triceps"],
        "axial": 0,
        "equipment": "cable_machine"
    },
    # Calves & Abs
    {
        "keywords": ["pantorrillas", "calf raise", "elevacion de talones"],
        "name": "Calf Raises",
        "pattern": "plantar_flexion",
        "muscles": ["calves"],
        "axial": 1,
        "equipment": "calf_machine"
    },
    {
        "keywords": ["crunch", "abdominales", "elevación de piernas", "elevacion de piernas", "leg raise"],
        "name": "Cable / Hanging Abdominal Crunch",
        "pattern": "spinal_flexion",
        "muscles": ["abdominals"],
        "axial": 0,
        "equipment": "cable_machine"
    }
]


def extract_day_sections(raw_text: str) -> List[ParsedDay]:
    """Splits a multi-day routine into discrete Day blocks with deduplicated primary exercises."""
    cleaned_text = raw_text.replace('\u200b', '').replace('\ufeff', '')
    lines = cleaned_text.splitlines()
    days: List[ParsedDay] = []
    current_day: Optional[ParsedDay] = None
    day_regex = re.compile(r'^\s*(?:[•\-*]\s*)?(?:[dD][íÍiI]a\s*\d+|day\s*\d+)\s*[:\-]\s*(.+)', re.IGNORECASE)

    for line in lines:
        match = day_regex.match(line)
        if match:
            day_title = line.strip().lstrip("•-* \t")
            day_id = f"day_{len(days) + 1}"
            current_day = ParsedDay(day_id=day_id, title=day_title, exercises=[])
            days.append(current_day)
            continue

        if current_day:
            parsed_ex = parse_exercise_line(line)
            if parsed_ex:
                # Avoid consecutive duplicate cards (e.g. detailed logged sets for same exercise)
                if not current_day.exercises or current_day.exercises[-1].name != parsed_ex.name:
                    current_day.exercises.append(parsed_ex)
                else:
                    # Update load info if previously missing
                    if not current_day.exercises[-1].load_str and parsed_ex.load_str:
                        current_day.exercises[-1].load_str = parsed_ex.load_str
                        current_day.exercises[-1].load_kg = parsed_ex.load_kg

    # If no day headers found, treat entire text as one day
    if not days:
        single_day = ParsedDay(day_id="day_1", title="Current Workout Routine", exercises=[])
        for line in lines:
            parsed_ex = parse_exercise_line(line)
            if parsed_ex:
                if not single_day.exercises or single_day.exercises[-1].name != parsed_ex.name:
                    single_day.exercises.append(parsed_ex)
        if single_day.exercises:
            days.append(single_day)

    return days


def parse_exercise_line(line: str) -> Optional[ParsedExercise]:
    """Parses a single line to see if it represents an exercise entry."""
    cleaned = line.strip().lstrip("•-* \t")
    if not cleaned or len(cleaned) < 3:
        return None

    lower = cleaned.lower()
    # Filter pure category headers or log prefixes
    if lower in ["espalda", "pecho", "bíceps", "biceps", "tríceps", "triceps", "pierna", "hombros", "estirar", "antebrazo"]:
        return None
    if re.match(r'^\d+\s*serie\b', lower) or re.match(r'^\d+\s*reps\b', lower):
        return None

    # Match against keyword taxonomy
    matched_entry = None
    for entry in KEYWORD_TAXONOMY:
        for kw in entry["keywords"]:
            if kw in lower:
                matched_entry = entry
                break
        if matched_entry:
            break

    if not matched_entry:
        return None

    # Extract sets and reps
    sets = 3
    reps = "8-12"
    
    set_match = re.search(r'(\d+)\s*(?:series|serie|sets?)\s*(?:x\s*(\d+(?:-\d+)?|\d+\+\d+)?\s*(?:reps?)?)?', lower)
    if set_match:
        try:
            sets = int(set_match.group(1))
        except Exception:
            sets = 3
        if set_match.group(2):
            reps = set_match.group(2)
    else:
        # Check "2 x 12-15" pattern
        alt_match = re.search(r'(\d+)\s*x\s*(\d+(?:-\d+)?)', lower)
        if alt_match:
            try:
                sets = int(alt_match.group(1))
                reps = alt_match.group(2)
            except Exception:
                pass

    # Extract load / weight
    load_kg = None
    load_str = None
    load_match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|lbs|lb)', lower)
    if load_match:
        load_str = f"{load_match.group(1)} {load_match.group(2)}"
        try:
            val = float(load_match.group(1))
            load_kg = val if "kg" in load_match.group(2) else val * 0.453592
        except Exception:
            pass

    return ParsedExercise(
        name=matched_entry["name"],
        movement_pattern=matched_entry["pattern"],
        primary_muscles=matched_entry["muscles"],
        axial_stress_rating=matched_entry["axial"],
        sets=sets,
        reps=reps,
        load_str=load_str,
        load_kg=round(load_kg, 1) if load_kg else None,
        required_equipment=matched_entry["equipment"],
        notes=cleaned,
        raw_line=cleaned
    )
