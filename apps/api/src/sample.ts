import { readFileSync } from 'node:fs';

/** The sample file format this service understands (`review_sample.FORMAT` in the pipelines). */
export const SAMPLE_FORMAT = 1;

/** The top-level keys every sample carries (`review_sample.TOP_KEYS` in the pipelines). */
const TOP_KEYS = ['cells', 'format', 'per_stratum', 'sample_id', 'seed', 'source_run', 'strata', 'texts'];
const LIST_KEYS = ['cells', 'strata', 'texts'];

/** A sample file that is missing, unreadable, or not the shape this service serves. */
export class SampleError extends Error {
  override name = 'SampleError';
}

/**
 * The one active review sample: its id (which keys every draft and submission) and the file's exact
 * bytes, served as-is by `GET /api/sample`. The viewer owns the strict per-cell parse; the service
 * only checks the envelope, so a bad file stops startup instead of reaching a reviewer.
 */
export interface ActiveSample {
  sampleId: string;
  json: string;
}

const isPlainObject = (v: unknown): v is Record<string, unknown> =>
  typeof v === 'object' && v !== null && !Array.isArray(v);

/** Validate a sample's text. `origin` names the source in error messages. */
export function parseSample(text: string, origin: string): ActiveSample {
  let sample: unknown;
  try {
    sample = JSON.parse(text);
  } catch (err) {
    throw new SampleError(`${origin}: not valid JSON (${(err as Error).message})`);
  }
  if (!isPlainObject(sample)) throw new SampleError(`${origin}: a sample is a JSON object`);
  if (sample.format !== SAMPLE_FORMAT) {
    throw new SampleError(`${origin}: unsupported sample format ${JSON.stringify(sample.format)}`);
  }
  const missing = TOP_KEYS.filter((k) => !(k in sample));
  if (missing.length > 0) throw new SampleError(`${origin}: missing keys ${missing.join(', ')}`);
  if (typeof sample.sample_id !== 'string' || sample.sample_id === '') {
    throw new SampleError(`${origin}: sample_id must be a non-empty string`);
  }
  for (const key of LIST_KEYS) {
    const value = sample[key];
    if (!Array.isArray(value) || !value.every(isPlainObject)) {
      throw new SampleError(`${origin}: ${key} must be a list of objects`);
    }
  }
  return { sampleId: sample.sample_id, json: text };
}

/** Read and validate the sample file at `path`. Any problem throws a `SampleError`. */
export function loadSample(path: string): ActiveSample {
  let text: string;
  try {
    text = readFileSync(path, 'utf8');
  } catch (err) {
    throw new SampleError(`${path}: cannot read sample (${(err as Error).message})`);
  }
  return parseSample(text, path);
}
