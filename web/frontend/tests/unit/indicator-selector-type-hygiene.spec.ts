import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('market IndicatorSelector type hygiene', () => {
  it('does not suppress type checking and keeps checkbox value handling explicit', () => {
    const source = readSource('src/components/market/IndicatorSelector.vue')

    expect(source).not.toContain('@ts-nocheck')
    expect(source).not.toContain('@ts-expect-error')
    expect(source).toContain("import type { CheckboxValueType } from 'element-plus'")
    expect(source).toContain('const isIndicatorSelected = (indicator: string): boolean => {')
    expect(source).toContain('const onCheckboxChange = (indicator: string, value: CheckboxValueType): void => {')
  })
})
