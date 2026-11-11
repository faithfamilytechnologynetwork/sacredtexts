import { parseSample } from '../sample';
import type { ActiveSample } from '../sample';

/** The sample id the route tests treat as active. */
export const TEST_SAMPLE_ID = 'facct-2026-11-03-k10';

/** A minimal valid sample object (envelope only; one cell, one stratum, one text). */
export function sampleObject(sampleId = TEST_SAMPLE_ID): Record<string, unknown> {
  return {
    cells: [{ cell_id: 'facct-2026-11-03:astra:e84250807e983aef', text: 'islam/native' }],
    format: 1,
    per_stratum: 10,
    sample_id: sampleId,
    seed: 'test',
    source_run: 'runs/facct-2026-11-03',
    strata: [{ outcome: 'correct', task: 'cite_passage', text: 'islam/native', population: 1, drawn: 1 }],
    texts: [{ id: 'islam/native', label: "Qur'an", drawn: 1 }],
  };
}

/** The active sample the route tests hand to `createApp`. */
export function testSample(sampleId = TEST_SAMPLE_ID): ActiveSample {
  return parseSample(JSON.stringify(sampleObject(sampleId)), 'test sample');
}
