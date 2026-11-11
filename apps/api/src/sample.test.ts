import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadSample, parseSample, SampleError } from './sample';
import { sampleObject } from './testing/sample';

const repoRoot = fileURLToPath(new URL('../../../', import.meta.url));
const FACCT_SAMPLE = join(repoRoot, 'review/samples/facct-2026-11-03-k10.json');
const FIXTURE_SAMPLE = join(repoRoot, 'fixtures/review_sample.json');

const parse = (obj: unknown) => parseSample(JSON.stringify(obj), 'test.json');
const without = (key: string) => {
  const obj = sampleObject();
  delete obj[key];
  return obj;
};

describe('loadSample', () => {
  let dir: string;
  beforeAll(() => {
    dir = mkdtempSync(join(tmpdir(), 'api-sample-'));
  });
  afterAll(() => rmSync(dir, { recursive: true, force: true }));

  it('loads the committed FAccT sample, keeping its exact bytes', () => {
    const sample = loadSample(FACCT_SAMPLE);
    expect(sample.sampleId).toBe('facct-2026-11-03-k10');
    expect(sample.json).toBe(readFileSync(FACCT_SAMPLE, 'utf8'));
  });

  it('loads the hand-built fixture sample (the Phase 2 contract file)', () => {
    expect(loadSample(FIXTURE_SAMPLE).sampleId).toBe('review_sample');
  });

  it('fails on a missing file, naming the path', () => {
    const missing = join(dir, 'nope.json');
    expect(() => loadSample(missing)).toThrow(SampleError);
    expect(() => loadSample(missing)).toThrow(missing);
  });

  it('fails on a file that is not JSON', () => {
    const path = join(dir, 'bad.json');
    writeFileSync(path, '{"format": 1,');
    expect(() => loadSample(path)).toThrow(/not valid JSON/);
  });
});

describe('parseSample', () => {
  it('accepts a minimal valid sample', () => {
    expect(parse(sampleObject('s-1')).sampleId).toBe('s-1');
  });

  it('rejects a non-object', () => {
    expect(() => parse([sampleObject()])).toThrow(/a sample is a JSON object/);
    expect(() => parse(null)).toThrow(/a sample is a JSON object/);
  });

  it('rejects any format but 1', () => {
    for (const format of [2, '1', 0, null]) {
      expect(() => parse({ ...sampleObject(), format })).toThrow(/unsupported sample format/);
    }
    expect(() => parse(without('format'))).toThrow(/unsupported sample format/);
  });

  it('rejects a missing top-level key, naming it', () => {
    for (const key of ['cells', 'per_stratum', 'sample_id', 'seed', 'source_run', 'strata', 'texts']) {
      expect(() => parse(without(key))).toThrow(new RegExp(`missing keys ${key}`));
    }
  });

  it('rejects an empty or non-string sample_id', () => {
    expect(() => parse({ ...sampleObject(), sample_id: '' })).toThrow(/sample_id/);
    expect(() => parse({ ...sampleObject(), sample_id: 7 })).toThrow(/sample_id/);
  });

  it('rejects a sample with no cells', () => {
    expect(() => parse({ ...sampleObject(), cells: [] })).toThrow(/cells is empty/);
  });

  it('rejects cells, strata or texts that are not lists of objects', () => {
    for (const key of ['cells', 'strata', 'texts']) {
      expect(() => parse({ ...sampleObject(), [key]: {} })).toThrow(new RegExp(`${key} must be a list`));
      expect(() => parse({ ...sampleObject(), [key]: ['x'] })).toThrow(new RegExp(`${key} must be a list`));
    }
  });
});
