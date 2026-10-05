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
import math
from app.engine.biomechanical_graph import default_graph, ExerciseNode
from app.engine.rule_engine import BiomechanicalRuleEngine
from app.engine.hypertrophy_math import HypertrophyMathEngine
from app.ai.adapters import LLMAdapterFactory
from app.schemas.routine_agent import (
    DecisionRationaleDetails,
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


def calculate_evidence_based_rest(
    movement_pattern: str,
    axial_stress: int,
    equipment: str,
    sleep_hours: float,
    available_minutes: int,
    status_tag: str
) -> Tuple[int, str]:
    """
    Calculates evidence-based rest interval (seconds) and scientific rationale grounded in
    Schoenfeld (2016) and Grgic (2017) meta-analyses on rest intervals and hypertrophy.
    """
    if status_tag == "MYO_REPS":
        return (
            15,
            "15s entre mini-series (Protocolo Myo-Reps de Borge Fagerli): Pausa breve para resíntesis parcial de fosfocreatina manteniendo el reclutamiento de unidades motoras de alto umbral en estado de fatiga."
        )
    if status_tag == "APS_PAIRED":
        rest = 60 if available_minutes <= 30 else 75
        return (
            rest,
            f"{rest}s entre pares antagónicos: El grupo muscular opuesto descansa pasivamente durante el trabajo de su antagonista, permitiendo ~2.5 minutos de recuperación local por músculo con una reducción de tiempo del ~45% (Robbins et al., 2010)."
        )

    is_heavy_compound = (
        axial_stress >= 5 or
        movement_pattern in ["squat", "hinge"] or
        any(k in equipment.lower() for k in ["barbell", "squat_rack", "hack_squat"])
    )
    is_moderate_compound = (
        axial_stress >= 2 or
        movement_pattern in ["horizontal_press", "horizontal_pull", "vertical_press", "vertical_pull", "hip_extension"]
    )

    if available_minutes <= 30:
        if is_heavy_compound:
            return (
                120,
                "120s de descanso (2 min): Umbral mínimo de seguridad y tensión mecánica en movimientos compuestos pesados bajo restricción severa de tiempo, evitando el fallo prematuro por hipoxia muscular."
            )
        elif is_moderate_compound:
            return (
                90,
                "90s de descanso: Balance de densidad y aclaramiento de metabolitos para ejercicios multiarticulares moderados en sesión compacta."
            )
        else:
            return (
                60,
                "60s de descanso: Suficiente para ejercicios monoarticulares (aislamiento) donde la fatiga sistémica y espinal es casi nula."
            )
    elif available_minutes <= 45:
        if is_heavy_compound:
            return (
                150,
                "150s de descanso (2.5 min): Permite ~90-95% de resíntesis de ATP y fosfocreatina (ATP/CP), maximizando la tensión mecánica en cada serie efectiva (Schoenfeld, 2016)."
            )
        elif is_moderate_compound:
            return (
                105,
                "105s de descanso: Tiempo óptimo para mantener repeticiones efectivas en rangos de hipertrofia sin alargar la sesión."
            )
        else:
            return (
                75,
                "75s de descanso: Intervalo ideal para aislamiento muscular, equilibrando tensión mecánica y estrés metabólico."
            )
    else:
        if is_heavy_compound:
            rest = 180 if sleep_hours < 6.0 else 150
            reason = (
                f"{rest}s de descanso (3 min): Con déficit de sueño ({sleep_hours}h), la excitabilidad corticoespinal y la recuperación del SNC son más lentas. 3 minutos garantizan resíntesis completa de ATP/CP y previenen la pérdida prematura de fuerza entre series (Grgic et al., 2017)."
                if sleep_hours < 6.0 else
                f"{rest}s de descanso (2.5 min): Duración recomendada por la literatura para máxima sobrecarga progresiva en movimientos con alta demanda axial y multiarticular."
            )
            return (rest, reason)
        elif is_moderate_compound:
            return (
                120,
                "120s de descanso (2 min): Estándar de oro para ejercicios multiarticulares en polea o máquinas guiadas según el metaanálisis de Schoenfeld (2016)."
            )
        else:
            return (
                90,
                "90s de descanso: Recuperación completa para grupos musculares pequeños (brazos, hombro lateral) sin interferencia sistémica."
            )


def build_decision_details(
    original: ParsedExercise,
    adapted_name: str,
    adapted_sets: int,
    adapted_reps: str,
    adapted_load_str: Optional[str],
    load_delta_percent: Optional[int],
    rest_sec: int,
    rest_rationale: str,
    status_tag: str,
    sub_reason: str,
    sleep_hours: float,
    available_minutes: int,
    paired_with: Optional[str] = None
) -> DecisionRationaleDetails:
    """Builds transparent, evidence-based reasoning for every aspect of this exercise."""
    # 1. Exercise Selection
    if status_tag == "SUBSTITUTED":
        sel_reason = (
            f"Sustitución de '{original.name}' por '{adapted_name}'. Motivo: {sub_reason}. "
            f"Se sustituyó este ejercicio para eliminar el vector de cizallamiento espinal o sobrecarga articular, "
            f"redirigiendo el 100% de la tensión mecánica al vientre muscular ({', '.join(original.primary_muscles)}) "
            f"con una trayectoria biomecánicamente guiada y mayor estabilidad."
        )
    elif status_tag == "APS_PAIRED":
        sel_reason = (
            f"Se emparejó '{adapted_name}' en Superserie Antagónica (APS) con '{paired_with}'. "
            f"Aprovecha la inhibición recíproca neuromuscular: mientras el grupo agonista trabaja, el antagonista se relaja, "
            f"duplicando la densidad de entrenamiento sin reducir el volumen efectivo ni la fuerza (Robbins et al., 2010)."
        )
    elif status_tag == "MYO_REPS":
        sel_reason = (
            f"Protocolo Myo-Reps para '{adapted_name}'. En lugar de series tradicionales, se realiza 1 serie de activación "
            f"seguida de 3 mini-series de repeticiones efectivas cerca del fallo. Ahorra hasta 8 minutos manteniendo la síntesis proteica muscular."
        )
    else:
        sel_reason = (
            f"Preservado '{adapted_name}' del plan original. Es un ejercicio biomecánicamente excelente para el patrón "
            f"'{original.movement_pattern}' y el grupo ({', '.join(original.primary_muscles)}), con un ratio estímulo-fatiga (SFR) sobresaliente."
        )

    # 2. Volume & Sets
    if status_tag == "MYO_REPS":
        vol_reason = (
            "Adaptado a 1 serie cluster (10-12 reps + 3x3 mini-series): Con restricción de tiempo, "
            "este formato comprime todo el estímulo hipertrófico efectivo en solo 4 minutos."
        )
    elif adapted_sets < original.sets:
        vol_reason = (
            f"Reducido de {original.sets} a {adapted_sets} series (-{original.sets - adapted_sets} serie): "
            f"Con {sleep_hours}h de sueño y tiempo ajustado ({available_minutes} min), el volumen adicional "
            f"se convertiría en 'volumen basura'. Mantener {adapted_sets} series a RIR 1-2 preserva el estímulo sin fatiga residual."
        )
    else:
        vol_reason = (
            f"Mantenido en {adapted_sets} series ({adapted_reps} reps): Se sitúa en tu rango de volumen adaptativo "
            f"óptimo (MAV), maximizando la señal anabólica sin saturar la capacidad de recuperación del SNC."
        )

    # 3. Rest
    rest_reason = rest_rationale

    # 4. Load & Intensity
    if load_delta_percent and load_delta_percent < 0:
        load_reason = (
            f"Carga ajustada con {load_delta_percent}% ({adapted_load_str} vs {original.load_str or 'base'} original): "
            f"La restricción de sueño ({sleep_hours}h) reduce la fuerza máxima un 8-12% por menor reclutamiento neural. "
            f"Ajustar la carga preserva la tensión mecánica en el rango de reps sin riesgo de fallo técnico ni lesión."
        )
    else:
        load_reason = (
            f"Carga de trabajo mantenida ({adapted_load_str or original.load_str or 'Según plan'}): "
            f"Sin déficit que comprometa la coordinación, se sostiene la sobrecarga progresiva prevista en tu rutina."
        )

    return DecisionRationaleDetails(
        exercise_selection=sel_reason,
        volume_and_sets=vol_reason,
        rest_period=rest_reason,
        load_and_intensity=load_reason
    )


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
            adapted_sets = original.sets
            adapted_reps = original.reps
            paired_with_name = None

            if needs_substitute:
                status_tag = "SUBSTITUTED"

            # Autoregulate volume sets under time crunch to avoid junk volume
            if is_severe_time_crunch and original.sets >= 4:
                adapted_sets = 3
            elif is_time_crunch and original.sets > 3 and i >= 2:
                adapted_sets = 3

            # Antagonist Paired Sets (APS) logic for time crunch
            if is_time_crunch and i not in paired_indices:
                for j in range(i + 1, len(target_day.exercises)):
                    if j not in paired_indices:
                        other = target_day.exercises[j]
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
                            paired_with_name = other.name
                            intensifier = f"Antagonist Paired Set con {other.name}"
                            break

            # Myo-Reps for secondary isolation on severe time crunch
            if is_severe_time_crunch and original.axial_stress_rating <= 1 and not intensifier and i >= 2:
                status_tag = "MYO_REPS"
                intensifier = "Myo-Reps: 1 serie activación (10-12 reps) + 3 mini-series de 3 reps (15s descanso)"
                adapted_sets = 1
                adapted_reps = "10-12 + 3x3"

            # If load was scaled down due to sleep
            if load_scale < 1.0 and status_tag == "PRESERVED":
                status_tag = "LOAD_AUTOREGULATED"

            # Calculate Evidence-Based Rest grounded in Schoenfeld (2016) and Grgic (2017)
            rest_sec, rest_rationale = calculate_evidence_based_rest(
                movement_pattern=original.movement_pattern,
                axial_stress=original.axial_stress_rating,
                equipment=original.required_equipment,
                sleep_hours=sleep_hours,
                available_minutes=available_minutes,
                status_tag=status_tag
            )

            # Estimate net lifting/resting duration for this adapted exercise
            duration = HypertrophyMathEngine.estimate_exercise_duration(
                sets=adapted_sets,
                rest_seconds=rest_sec,
                is_aps_paired=(status_tag == "APS_PAIRED"),
                is_myo_reps=(status_tag == "MYO_REPS")
            )
            total_adapted_duration += duration
            total_effective_sets += (3 if status_tag == "MYO_REPS" else adapted_sets)

            # Concise summary note
            rationale_notes = []
            if sub_reason:
                rationale_notes.append(sub_reason)
            if load_scale < 1.0:
                pct_reduced = int(round((1.0 - load_scale) * 100))
                rationale_notes.append(f"Cargas ajustadas -{pct_reduced}% por déficit de sueño ({sleep_hours}h)")
            if intensifier:
                rationale_notes.append(f"Densidad: {intensifier}")
            if not rationale_notes:
                rationale_notes.append("Ejercicio y series mantenidas en rango óptimo de tensión mecánica")

            # Structured deep rationale for dropdown exploration
            decision_details = build_decision_details(
                original=original,
                adapted_name=sub_name,
                adapted_sets=adapted_sets,
                adapted_reps=adapted_reps,
                adapted_load_str=adapted_load_str,
                load_delta_percent=load_delta_percent,
                rest_sec=rest_sec,
                rest_rationale=rest_rationale,
                status_tag=status_tag,
                sub_reason=sub_reason,
                sleep_hours=sleep_hours,
                available_minutes=available_minutes,
                paired_with=paired_with_name
            )

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
                decision_details=decision_details,
                intensifier=intensifier
            ))

        # 4. Realistic Transition & Setup Cushion ("Colchón para cambio de máquinas y etc.")
        num_adapted = len(comparisons)
        if available_minutes <= 30:
            per_switch_sec = 60
            warmup_sec = 90
        else:
            per_switch_sec = 90
            warmup_sec = 180

        transition_seconds = (max(0, num_adapted - 1) * per_switch_sec) + (warmup_sec if num_adapted > 0 else 0)
        transition_buffer_min = math.ceil(transition_seconds / 60)
        raw_exercise_time_min = total_adapted_duration
        estimated_duration_min = raw_exercise_time_min + transition_buffer_min

        orig_transitions = (max(0, len(target_day.exercises) - 1) * per_switch_sec) + (warmup_sec if target_day.exercises else 0)
        orig_total = total_original_duration + math.ceil(orig_transitions / 60)
        time_saved = max(0, orig_total - estimated_duration_min)

        # 5. Generate AI Coaching Prose via Minimax
        prompt_drawbacks = {
            "sleep_hours": sleep_hours,
            "available_minutes": available_minutes,
            "occupied_equipment": request.occupied_equipment,
            "localized_pain_symptoms": request.localized_pain_symptoms,
            "subjective_readiness": readiness,
            "transition_buffer_min": transition_buffer_min
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
            estimated_duration_min=estimated_duration_min,
            raw_exercise_time_min=raw_exercise_time_min,
            transition_buffer_min=transition_buffer_min,
            time_saved_min=time_saved,
            effective_volume_percentage=100.0,
            sfr_rating="VERY_HIGH" if is_sleep_deprived or pain_symptoms else "HIGH",
            comparisons=comparisons,
            coaching_rationale=coaching_text,
            created_at=datetime.now(timezone.utc)
        )


agent_service = PersonalHypertrophyAgent()
