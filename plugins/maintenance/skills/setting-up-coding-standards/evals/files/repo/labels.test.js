import assert from 'node:assert/strict';
import test from 'node:test';
import { previewLabel } from './labels.js';

test('preview trims whitespace', () => {
  assert.equal(previewLabel(' ab '), 'AB');
});
