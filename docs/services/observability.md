# Subsystem: Observability & Telemetry

## 1. Observability Architecture
IronGraph-Engine incorporates end-to-end AI observability across three tiers:
1. **Langfuse Tracing**: Tracking LLM prompt versions, input tokens, output tokens, cost, and per-node latency.
2. **Prometheus Metrics**: High-resolution operational metrics for adaptation latency, volume preservation percentages, and biomechanical pruning counts.
3. **Structured Correlation Logging**: Unified JSON logging stamped with `lifter_id` and `adaptation_id`.

## 2. Key Prometheus Metrics Exposed (`/metrics`)

| Metric Name | Type | Labels | Description |
| :--- | :--- | :--- | :--- |
| `irongraph_adaptations_total` | Counter | `status` | Total adaptations generated |
| `irongraph_adaptation_duration_seconds` | Histogram | `quantile` | End-to-end adaptation latency |
| `irongraph_ttft_seconds` | Histogram | `provider`, `model` | Time to first streaming token |
| `irongraph_effective_volume_preservation_ratio` | Gauge | `lifter_tier` | Ratio of adapted vs planned effective sets |
| `irongraph_biomechanical_pruning_total` | Counter | `reason` | Exercises filtered due to axial load or gear |
| `irongraph_reflection_loops_total` | Counter | `reason` | Self-correction cycles triggered |
