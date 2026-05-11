import { describe, expect, it } from 'vitest'
import { existsSync } from 'node:fs'
import { resolve } from 'node:path'

describe('monitoring style sources', () => {
  it('does not keep archived alert-rules styles in active monitoring style guards', () => {
    expect(existsSync(resolve(process.cwd(), 'src/views/monitoring/styles/AlertRulesManagement.scss'))).toBe(false)
  })
})
