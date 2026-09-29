# Subsystem: API Admission & Control Plane

## 1. Overview
The Control Plane is an asynchronous FastAPI service handling lifter authentication, Pydantic v2 schema admission, lifter concurrency leasing in Redis, and Server-Sent Events (SSE) streaming.

## 2. Concurrency Leasing via Redis Distributed Locks
To ensure that a lifter's active session is not modified by two concurrent adaptations, the control plane acquires a distributed Redis lock:

```python
lock_key = f"lock:lifter:{lifter_id}"
# Acquire lock with a 30-second TTL
acquired = await redis.set(lock_key, worker_id, nx=True, ex=30)
if not acquired:
    raise HTTPException(status_code=409, detail="Lifter is actively processing an adaptation.")
```

If the client terminates the SSE connection prematurely, a cancellation hook releases the Redis lock and terminates the upstream generation task.
