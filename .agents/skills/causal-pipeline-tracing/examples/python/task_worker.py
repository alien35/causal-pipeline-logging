"""
task_worker.py - Example async background pipeline showing causal trace usage.
"""
import asyncio
from typing import Dict, Any
from causal_trace import CausalPipelineTrace

async def handle_job_pipeline(job_id: str, payload: Dict[str, Any], state: Dict[str, Any]):
    trace = CausalPipelineTrace("TASK-WORKER")
    
    # 1. Acquire job lease
    trace.step(1)
    
    # 2. Check deduplication cache
    if job_id in state.get("seen_ids", set()):
        trace.step("2a").abort("duplicate-job-discarded", jobId=job_id)
        return
    trace.step("2b")
    
    # 3. Fetch latest entity snapshot
    trace.step(3)
    current_rev = state.get("revisions", {}).get(payload.get("entity_id"), 0)
    incoming_rev = payload.get("revision", 0)
    
    # Check for Revision Inversion (Regime 1 defect)
    if incoming_rev < current_rev:
        trace.step("3b").step(4).fail(
            "revision-inversion-detected",
            jobId=job_id,
            entityId=payload.get("entity_id"),
            incomingRev=incoming_rev,
            currentRev=current_rev
        )
        return
        
    # 4. Commit delta update
    trace.step(4).step(5).success(
        jobId=job_id,
        entityId=payload.get("entity_id"),
        newRev=incoming_rev
    )

if __name__ == "__main__":
    state = {
        "seen_ids": {"job-100"},
        "revisions": {"entity-42": 5}
    }
    
    # Run test simulations
    asyncio.run(handle_job_pipeline("job-100", {"entity_id": "entity-42", "revision": 6}, state))
    asyncio.run(handle_job_pipeline("job-101", {"entity_id": "entity-42", "revision": 4}, state))
    asyncio.run(handle_job_pipeline("job-102", {"entity_id": "entity-42", "revision": 7}, state))
