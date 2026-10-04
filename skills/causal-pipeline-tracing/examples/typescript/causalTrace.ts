/**
 * CausalPipelineTrace: High-density diagnostic logger for asynchronous pipelines
 * optimized for LLM coding agents and deterministic fault localization.
 */

export type TraceContext = Record<string, string | number | boolean | null | undefined>;

export class CausalPipelineTrace {
  private readonly steps: string[] = [];

  constructor(private readonly tag: string) {}

  /**
   * Appends a forward progression or branch step in the causal pipeline.
   * e.g., trace.step(1).step(2).step('3b')
   */
  step(stepId: string | number): this {
    this.steps.push(String(stepId));
    return this;
  }

  /**
   * Logs a successful pipeline completion.
   */
  success(context: TraceContext = {}): void {
    const formattedCtx = this.formatContext(context);
    const line = `[${this.tag}-TRACE] ${this.renderSteps()} [OK]${formattedCtx}`;
    console.log(line);
  }

  /**
   * Logs a failed pipeline run with an explicit machine-readable reason tag.
   */
  fail(reason: string, context: TraceContext = {}): void {
    const formattedCtx = this.formatContext(context);
    const line = `[${this.tag}-TRACE] ${this.renderSteps()} [FAIL] reason=${reason}${formattedCtx}`;
    console.error(line);
  }

  /**
   * Logs an aborted pipeline run (e.g., cancelled due to debounce or superseded rev).
   */
  abort(reason: string, context: TraceContext = {}): void {
    const formattedCtx = this.formatContext(context);
    const line = `[${this.tag}-TRACE] ${this.renderSteps()} [ABORT] reason=${reason}${formattedCtx}`;
    console.warn(line);
  }

  private renderSteps(): string {
    return this.steps.join(' -> ');
  }

  private formatContext(context: TraceContext): string {
    const entries = Object.entries(context).filter(([_, v]) => v !== undefined && v !== null);
    if (entries.length === 0) return '';
    return ' | ' + entries.map(([k, v]) => `${k}=${v}`).join(' | ');
  }
}
