"""Personal Hypertrophy Agent Service.
Adapts free-form gym routines based on day-to-day drawbacks:
sleep deficits, time crunches, occupied machines, and localized pain.
"""

from typing import List, Optional, Tuple
from uuid import uuid4
from datetime import datetime, timezone

from app.engine.routine_parser import (
    ParsedDay,
    ParsedExercise,
    extract_day_sections,
)
from app.engine.biomechanical_graph import default_graph, ExerciseNode
from app.engine.rule_engine import BiomechanicalRuleEngine
from app.engine.hypertrophy_math import HypertrophyMathEngine
from app.ai.adapters import LLMAdapterFactory
from app.schemas.routine_agent import (
    ExerciseComparison,
    TextAdaptationRequest,
    TextAdaptationResponse,
)


def round_gym_weight(weight: float, unit: str = "kg", equipment: str = "general") -> float:
    """Rounds weight to realistic commercial gym increments (dumbbells, plates, pin stacks)."""
    if weight <= 0:
        return 0.0
    if unit == "lbs":
        step = 5.0 if weight >= 40 else 2.5
        rounded = round(weight / step) * step
        return round(rounded, 1) if rounded % 1 != 0 else int(rounded)
    else:
        eq_lower = equipment.lower()
        if "dumbbell" in eq_lower or "mancuerna" in eq_lower:
            step = 2.0 if weight < 24 else 2.5
        elif "cable" in eq_lower or "polea" in eq_lower:
            step = 2.5 if weight < 40 else 5.0
        else:  # Barbell or heavy plate machine
            step = 2.5 if weight < 80 else 5.0
        rounded = round(weight / step) * step
        return round(rounded, 1) if rounded % 1 != 0 else int(rounded)


def classify_equipment(equipment: str, exercise_name: str) -> str:
    """Categorizes equipment to optimize gym-floor logistics."""
    eq = (equipment + " " + exercise_name).lower()
    if any(k in eq for k in ["dumbbell", "mancuerna"]):
        return "dumbbell"
    elif any(k in eq for k in ["cable", "polea", "jalón", "jalon"]):
        return "cable"
    elif any(k in eq for k in ["barbell", "barra", "rack", "banca", "bench"]):
        return "barbell"
    elif any(k in eq for k in ["machine", "máquina", "maquina", "hack", "press", "curl"]):
        return "machine"
    return "bodyweight"


class PersonalHypertrophyAgent:
    """Consumable agent service that adapts personal training plans to daily life friction."""

    def __init__(self):
        self.graph = default_graph
        self.rule_engine = BiomechanicalRuleEngine(self.graph)
        self.llm_adapter = LLMAdapterFactory.get_adapter()

    async def adapt_routine(self, request: TextAdaptationRequest) -> TextAdaptationResponse:
        """Adapts free-form routine text according to daily drawbacks."""
        # 1. Parse routine into days
        days = extract_day_sections(request.routine_text)
        if not days:
            raise ValueError("No exercises could be recognized in the provided routine text.")

        # Select target day
        target_day = days[0]
        if request.selected_day:
            for d in days:
                if d.day_id == request.selected_day or request.selected_day.lower() in d.title.lower():
                    target_day = d
                    break

        # 2. Extract drawbacks
        sleep_hours = request.sleep_hours
        available_minutes = request.available_minutes
        blocked_equipment = [eq.lower().strip() for eq in request.occupied_equipment]
        pain_symptoms = [p.lower().strip() for p in request.localized_pain_symptoms]
        readiness = request.subjective_readiness_1_to_10

        # Load scaling factor for sleep & readiness
        load_scale = HypertrophyMathEngine.calculate_load_scaling_factor(sleep_hours, readiness)
        is_sleep_deprived = sleep_hours < 6.0
        is_time_crunch = available_minutes <= 45
        is_severe_time_crunch = available_minutes <= 30

        # 3. Process each planned exercise
        comparisons: List[ExerciseComparison] = []
        total_adapted_duration = 0
        total_original_duration = 0
        total_effective_sets = 0

        # Track paired exercises to avoid repeating APS pairs
        paired_indices = set()

        for i, original in enumerate(target_day.exercises):
            orig_duration = HypertrophyMathEngine.estimate_exercise_duration(
                sets=original.sets, rest_seconds=90, is_aps_paired=False
            )
            total_original_duration += orig_duration

            # Check if contraindicated or blocked
            name_lower = original.name.lower()
            needs_substitute = False
            sub_reason = ""
            sub_name = original.name

            # Check equipment blocker
            for blocked in blocked_equipment:
                if blocked and (blocked in original.required_equipment.lower() or blocked in name_lower):
                    needs_substitute = True
                    sub_reason = f"Equipo bloqueado: {blocked} ocupado o no disponible"
                    break

            # Check lumbar / lower back pain
            has_lumbar_pain = any("lumbar" in p or "lower_back" in p or "espalda baja" in p for p in pain_symptoms)
            if has_lumbar_pain and original.axial_stress_rating >= 6:
                needs_substitute = True
                sub_reason = f"Protección espinal por molestia lumbar (estrés axial {original.axial_stress_rating}/10 eliminado)"

            # Check sleep-induced axial limit
            if is_sleep_deprived and original.axial_stress_rating >= 7 and not needs_substitute:
                needs_substitute = True
                sub_reason = f"Sustitución por déficit de sueño ({sleep_hours}h): eliminada carga axial sobre el SNC"

            # Execute substitution if needed
            if needs_substitute:
                if "squat" in original.movement_pattern or "back squat" in name_lower:
                    sub_name = "45-Degree Leg Press" if "leg_press" not in blocked_equipment else "Bulgarian Split Squats"
                elif "hinge" in original.movement_pattern or "deadlift" in name_lower:
                    sub_name = "Seated Hamstring Leg Curl"
                elif "row" in original.movement_pattern or "barbell bent-over" in name_lower:
                    sub_name = "Chest-Supported T-Bar Row"
                elif "jalón" in name_lower or "lat pulldown" in name_lower:
                    sub_name = "Chest-Supported Dumbbell Row" if "polea" in blocked_equipment or "cable" in blocked_equipment else "Lat Pulldown (Cable)"
                else:
                    sub_name = f"{original.name} (Variante con Mancuernas)"

            eq_cat = classify_equipment(original.required_equipment, original.name)

            # Calculate adapted load with realistic gym increments
            adapted_load_str = None
            load_delta_percent = None
            if load_scale < 1.0:
                load_delta_percent = -int(round((1.0 - load_scale) * 100))

            if original.load_kg:
                scaled_kg = original.load_kg * load_scale
                rounded_kg = round_gym_weight(scaled_kg, unit="kg", equipment=original.required_equipment)
                adapted_load_str = f"{rounded_kg} kg"
            elif original.load_str:
                import re
                if "lbs" in original.load_str.lower():
                    m = re.search(r'(\d+(?:\.\d+)?)', original.load_str)
                    if m:
                        val = float(m.group(1)) * load_scale
                        rounded_lbs = round_gym_weight(val, unit="lbs")
                        adapted_load_str = f"{rounded_lbs} lbs"
                    else:
                        adapted_load_str = f"{original.load_str} (autoregulado)"
                elif "kg" in original.load_str.lower():
                    m = re.search(r'(\d+(?:\.\d+)?)', original.load_str)
                    if m:
                        val = float(m.group(1)) * load_scale
                        rounded_kg = round_gym_weight(val, unit="kg", equipment=original.required_equipment)
                        adapted_load_str = f"{rounded_kg} kg"
                    else:
                        adapted_load_str = f"{original.load_str} (autoregulado)"
                else:
                    adapted_load_str = f"{original.load_str} (autoregulado)"

            # Intensifiers & Time-Density Compression
            status_tag = "PRESERVED"
            intensifier = None
            rest_sec = 90
            adapted_sets = original.sets
            adapted_reps = original.reps

            if needs_substitute:
                status_tag = "SUBSTITUTED"

            # Antagonist Paired Sets (APS) logic for time crunch
            if is_time_crunch and i not in paired_indices:
                # Find complementary exercise later in list (e.g. Press + Row, Quads + Hamstrings, Biceps + Triceps)
                for j in range(i + 1, len(target_day.exercises)):
                    if j not in paired_indices:
                        other = target_day.exercises[j]
                        # Pair Push + Pull or Leg Extensions + Curls
                        motion_ok = (
                            ("press" in original.movement_pattern and "pull" in other.movement_pattern) or
                            ("pull" in original.movement_pattern and "press" in other.movement_pattern) or
                            ("flexion" in original.movement_pattern and "extension" in other.movement_pattern) or
                            ("extension" in original.movement_pattern and "flexion" in other.movement_pattern)
                        )
                        station_ok = True
                        if request.same_station_only:
                            other_cat = classify_equipment(other.required_equipment, other.name)
                            station_ok = (eq_cat == other_cat and eq_cat in ["dumbbell", "cable"])

                        is_pairable = motion_ok and station_ok
                        if is_pairable:
                            paired_indices.add(i)
                            paired_indices.add(j)
                            status_tag = "APS_PAIRED"
                            intensifier = f"Antagonist Paired Set con {other.name} (60s descanso)"
                            rest_sec = 60
                            break

            # Myo-Reps for secondary isolation on severe time crunch
            if is_severe_time_crunch and original.axial_stress_rating <= 1 and not intensifier and i >= 2:
                status_tag = "MYO_REPS"
                intensifier = "Myo-Reps: 1 serie activación (10-12 reps) + 3 mini-series de 3 reps (15s descanso)"
                adapted_sets = 1
                adapted_reps = "10-12 + 3x3"
                rest_sec = 15

            # If load was scaled down due to sleep
            if load_scale < 1.0 and status_tag == "PRESERVED":
                status_tag = "LOAD_AUTOREGULATED"

            # Estimate duration for this adapted exercise
            duration = HypertrophyMathEngine.estimate_exercise_duration(
                sets=adapted_sets,
                rest_seconds=rest_sec,
                is_aps_paired=(status_tag == "APS_PAIRED"),
                is_myo_reps=(status_tag == "MYO_REPS")
            )
            total_adapted_duration += duration
            total_effective_sets += (3 if status_tag == "MYO_REPS" else adapted_sets)

            # Rationale text
            rationale_notes = []
            if sub_reason:
                rationale_notes.append(sub_reason)
            if load_scale < 1.0:
                pct_reduced = int(round((1.0 - load_scale) * 100))
                rationale_notes.append(f"Cargas ajustadas -{pct_reduced}% para compensar déficit de sueño ({sleep_hours}h) y evitar fatiga del SNC")
            if intensifier:
                rationale_notes.append(f"Estrategia de densidad: {intensifier}")
            if not rationale_notes:
                rationale_notes.append("Ejercicio y series mantenidas en rango óptimo de tensión mecánica")

            comparisons.append(ExerciseComparison(
                original_name=original.name,
                original_sets=original.sets,
                original_reps=original.reps,
                original_load=original.load_str,
                adapted_name=sub_name,
                adapted_sets=adapted_sets,
                adapted_reps=adapted_reps,
                adapted_load=adapted_load_str or original.load_str,
                load_delta_percent=load_delta_percent,
                equipment_category=eq_cat,
                rest_seconds=rest_sec,
                status_tag=status_tag,
                change_rationale=" | ".join(rationale_notes),
                intensifier=intensifier
            ))

        time_saved = max(0, total_original_duration - total_adapted_duration)

        # 4. Generate AI Coaching Prose via Minimax
        prompt_drawbacks = {
            "sleep_hours": sleep_hours,
            "available_minutes": available_minutes,
            "occupied_equipment": request.occupied_equipment,
            "localized_pain_symptoms": request.localized_pain_symptoms,
            "subjective_readiness": readiness
        }
        prompt_exercises = [c.model_dump() for c in comparisons]

        coaching_text = await self.llm_adapter.generate_coaching_rationale(
            lifter_name="Atleta",
            drawbacks=prompt_drawbacks,
            adapted_exercises=prompt_exercises,
            volume_delta=0
        )

        return TextAdaptationResponse(
            adaptation_id=uuid4(),
            detected_day_title=target_day.title,
            original_exercises_count=len(target_day.exercises),
            adapted_exercises_count=len(comparisons),
            estimated_duration_min=total_adapted_duration,
            time_saved_min=time_saved,
            effective_volume_percentage=100.0,
            sfr_rating="VERY_HIGH" if is_sleep_deprived or pain_symptoms else "HIGH",
            comparisons=comparisons,
            coaching_rationale=coaching_text,
            created_at=datetime.now(timezone.utc)
        )


agent_service = PersonalHypertrophyAgent()
