# Subsystem: Autoregulation Mathematics & Hypertrophy Protocols

## 1. Stimulus-to-Fatigue Ratio (SFR) Optimization
Hypertrophy is driven by localized mechanical tension on muscle fibers. Systemic fatigue (axial spinal compression, nervous system exhaustion, tendon wear) limits how much volume a lifter can tolerate.

$$\text{SFR} = \frac{\text{Local Muscle Tension}}{\text{Axial Stress} + \text{Joint Inflammation} + \text{CNS Fatigue}}$$

When sleep is under 5 hours or subjective readiness is low, the engine automatically selects exercises with an $\text{SFR} \ge \text{HIGH}$, substituting heavy free-weight axial movements with machine or chest-supported equivalents.

---

## 2. Dynamic RIR Load Autoregulation
Standard percentage-based programming (e.g. "Do 4x8 at 80% 1RM") fails on sleep-deprived days because 80% 1RM might correspond to 0 RIR (failure) instead of the intended 2 RIR.

The engine uses dynamic Reps in Reserve (RIR) autoregulation:
$$\text{Target Weight} = \text{Baseline 1RM} \times \text{RepPercentile}(\text{Reps}) \times \alpha(\text{SleepHours}, \text{Readiness})$$
Where the scaling factor $\alpha$ is defined as:
$$\alpha = 1.0 - \max\left(0, \frac{7.0 - \text{SleepHours}}{20}\right)$$
For 4.5 hours of sleep, load is scaled down by approximately 6–8%, ensuring the lifter hits the target 1–2 RIR without technical breakdown or dangerous compensatory form.

---

## 3. Time-Density Compression Protocols

### Protocol A: Antagonist Paired Sets (APS)
- **Concept**: Pairing non-competing muscle groups (e.g. Horizontal Push + Horizontal Pull; Quad Extension + Hamstring Curl).
- **Execution**: 
  - Set 1: Incline Dumbbell Press $\to$ Rest 60s
  - Set 2: Chest-Supported T-Bar Row $\to$ Rest 60s
  - Repeat for 3 cycles.
- **Outcome**: Each muscle receives a full 2.5 minutes of rest before its next set, yet total workout duration drops by ~45%.

### Protocol B: Myo-Reps (Rest-Pause Density)
- **Concept**: Only the final 3–5 reps of a set near failure provide high mechanical tension ("effective reps"). Instead of doing 3 separate straight sets with 2-minute rests, Myo-reps execute:
  1. **Activation Set**: 10–12 reps taken to 1 RIR.
  2. **Rest**: 15 seconds (deep breaths).
  3. **Mini-Sets**: 3 mini-sets of 3 reps with 15s rest between each.
- **Outcome**: Yields 12–15 effective high-tension reps in 3.5 minutes compared to 12 minutes for 3 straight sets.
