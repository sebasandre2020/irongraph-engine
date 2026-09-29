# Subsystem: Sports Science Retrieval & Qdrant Integration

## 1. Overview
The **Qdrant** vector store indexes peer-reviewed exercise science, sports medicine, and hypertrophy physiology literature. When atypical session constraints are detected, the system retrieves relevant scientific evidence chunks to ground the Hypertrophy Agent's reasoning.

## 2. Qdrant Collection Configuration
- **Collection Name**: `hypertrophy_science`
- **Vector Dimension**: 1536 (OpenAI `text-embedding-3-small`) or 384 (`bge-small-en-v1.5`)
- **Distance Metric**: Cosine Similarity
- **Payload Schema**:
  ```json
  {
    "study_id": "robbins_2010_antagonist_paired_sets",
    "topic": "antagonist_paired_sets",
    "authors": "Robbins et al.",
    "year": 2010,
    "key_finding": "APS protocols maintain volume load and throw power while cutting training time by nearly 50% compared to traditional sets.",
    "doi": "10.1519/JSC.0b013e3181ddb7cd"
  }
  ```

## 3. Context Injection into Agent Prompt
Retrieved evidence is injected directly into the LLM system prompt context, ensuring that recommendations (e.g. rest intervals between paired sets) match published scientific consensus.
