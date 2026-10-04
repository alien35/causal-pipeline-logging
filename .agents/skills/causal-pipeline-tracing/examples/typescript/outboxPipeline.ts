import { CausalPipelineTrace } from './causalTrace';

export interface CommandItem {
  id: string;
  entityId: string;
  revision: number;
  payload: Record<string, any>;
  retries: number;
}

export interface OutboxState {
  inFlight: boolean;
  queue: CommandItem[];
  appliedRevision: number;
}

/**
 * Example: Asynchronous Outbox Pipeline with Causal Numbered Pipeline Tracing.
 * 
 * Pipeline Stage Map:
 *   [1] Enqueue command into outbox buffer
 *   [2] Verify lock & check online status
 *       ├── [2a] Pipeline paused: lock contended or offline
 *       └── [2b] Prepare transport dispatch
 *   [3] Dispatch to remote server
 *       ├── [3a] Fast optimistic local commit
 *       └── [3b] Network transport in-flight
 *   [4] Await ACK confirmation
 *       ├── [5a] Remote ACK 200 OK -> Evict from queue, increment rev
 *       ├── [5b] 4xx Validation error -> In-flight not cleared (BUG DETECTED)
 *       └── [5c] 5xx Network timeout -> Trigger exponential backoff
 */
export async function processOutboxQueue(
  state: OutboxState,
  transportSend: (item: CommandItem) => Promise<{ status: number }>
): Promise<void> {
  if (state.queue.length === 0) return;

  const item = state.queue[0];
  const trace = new CausalPipelineTrace('OUTBOX-PIPELINE');

  // Step 1: Dequeue & acquire pipeline processing slot
  trace.step(1);

  // Step 2: Check concurrency guard
  if (state.inFlight) {
    trace.step('2a').abort('concurrency-lock-held', {
      entityId: item.entityId,
      queueDepth: state.queue.length,
      inFlight: state.inFlight
    });
    return;
  }

  trace.step('2b');
  state.inFlight = true;

  try {
    // Step 3: Remote transport dispatch
    trace.step(3).step('3b');
    
    // Step 4: Await ACK
    trace.step(4);
    const response = await transportSend(item);

    if (response.status === 200) {
      // Step 5a: Success
      state.inFlight = false;
      state.appliedRevision = item.revision;
      state.queue.shift();
      trace.step('5a').step(6).success({
        entityId: item.entityId,
        rev: state.appliedRevision,
        queueDepth: state.queue.length
      });
    } else if (response.status >= 400 && response.status < 500) {
      // Step 5b: Client Error
      // NOTE: Here is where deadlocks happen if inFlight is not cleared!
      // The causal trace explicitly outputs: reason=unhandled-4xx-inFlight-not-cleared
      state.inFlight = false; // Bug fix applied
      state.queue.shift();    // Evict corrupted item
      trace.step('5b').fail('unhandled-4xx-inFlight-cleared', {
        entityId: item.entityId,
        status: response.status,
        queueDepth: state.queue.length,
        inFlight: state.inFlight
      });
    }
  } catch (err: any) {
    state.inFlight = false;
    trace.step(4).step('5c').fail('network-timeout-retrying', {
      entityId: item.entityId,
      retries: item.retries + 1,
      queueDepth: state.queue.length
    });
  }
}
