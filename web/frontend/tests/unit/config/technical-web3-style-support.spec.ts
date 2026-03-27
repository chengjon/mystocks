import { describe, expect, it } from 'vitest'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('technical web3 style support', () => {
  it('uses the technical page style file through @use', () => {
    const source = readSource('src/views/technical/TechnicalAnalysis.vue')

    expect(source).toContain('@use "./styles/TechnicalAnalysis.scss" as *;')
    expect(source).not.toContain('@import "./styles/TechnicalAnalysis"')
  })

  it('uses shared web3 style support files through @use', () => {
    const source = readSource('src/views/technical/styles/TechnicalAnalysis.scss')

    expect(source).toContain("@use '../../../styles/web3-tokens.scss' as *;")
    expect(source).toContain("@use '../../../styles/web3-global.scss' as *;")
  })

  it('ships the required shared web3 style support files', () => {
    expect(existsSync(resolve(process.cwd(), 'src/styles/web3-tokens.scss'))).toBe(true)
    expect(existsSync(resolve(process.cwd(), 'src/styles/web3-global.scss'))).toBe(true)
  })
})
