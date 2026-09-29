# Subsystem: Biomechanical Graph Engine

## 1. Relational Property Graph Model
IronGraph-Engine represents the exercise and anatomical universe as a directed property graph $G = (V, E)$ where:
- $V$: Entities partitioned by type (`exercise`, `muscle_group`, `joint`, `equipment`, `contraindication`).
- $E$: Directed relationships (`targets_primary`, `targets_secondary`, `loads_joint`, `contraindicated_for`, `substitute_for`, `antagonist_pair_with`).
- Attributes include: `axial_stress_rating` (0–10), `resistance_curve_focus` (`lengthened`, `mid_range`, `shortened`), and `sfr_rating` (`moderate`, `high`, `very_high`).

## 2. In-Memory Graph & Recursive CTE Traversal
- **Active Memory Model**: An in-process `NetworkX` graph is maintained in the worker for sub-millisecond constraint pruning.
- **Relational Backing**: PostgreSQL tables `exercises` and `biomechanical_edges` store the authoritative taxonomy.

### SQL Recursive CTE for Biomechanical Substitution
```sql
WITH target_pattern AS (
    SELECT movement_pattern, primary_muscles
    FROM exercises
    WHERE id = $1
)
SELECT e.id, e.name, e.axial_stress_rating, e.sfr_rating, e.required_equipment
FROM exercises e, target_pattern tp
WHERE e.movement_pattern = tp.movement_pattern
  AND e.primary_muscles @> tp.primary_muscles
  AND e.axial_stress_rating <= $2
  AND e.required_equipment = ANY($3::varchar[])
  AND e.id != $1
ORDER BY e.axial_stress_rating ASC, e.sfr_rating DESC
LIMIT $4;
```
