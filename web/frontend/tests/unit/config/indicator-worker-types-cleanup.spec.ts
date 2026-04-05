import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('indicator worker type cleanup', () => {
  it('keeps the indicator worker free of ts-nocheck', () => {
    const source = readFileSync(
      resolve(process.cwd(), 'src/workers/indicatorDataWorker.worker.ts'),
      'utf8'
    )
    const tsNoCheckDirective = '@ts-' + 'nocheck'

    expect(source).not.toContain(tsNoCheckDirective)
  })
})
