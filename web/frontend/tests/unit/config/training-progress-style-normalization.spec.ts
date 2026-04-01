import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('TrainingProgress style normalization', () => {
  it('moves training icon colors into semantic classes', () => {
    const source = readSource('src/components/sse/TrainingProgress.vue')

    expect(source).toContain('training-progress-icon--info')
    expect(source).toContain('training-progress-icon--loss')
    expect(source).toContain('training-progress-icon--accuracy')

    expect(source).not.toContain('emptyIconColor')
    expect(source).not.toContain('lossIconColor')
    expect(source).not.toContain('accuracyIconColor')
    expect(source).not.toContain(':color="emptyIconColor"')
  })
})
