import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

const publicDir = join(process.cwd(), 'public')
const manifestPath = join(publicDir, 'manifest.json')

interface ManifestImageResource {
  src: string
  form_factor?: string
}

interface WebManifest {
  icons?: ManifestImageResource[]
  screenshots?: ManifestImageResource[]
  shortcuts?: Array<{
    icons?: ManifestImageResource[]
  }>
}

function readManifest(): WebManifest {
  return JSON.parse(readFileSync(manifestPath, 'utf8')) as WebManifest
}

function toPublicPath(src: string): string {
  return join(publicDir, src.replace(/^\//u, ''))
}

describe('PWA manifest asset truth', () => {
  it('only references static assets that exist under public/', () => {
    const manifest = readManifest()
    const referencedAssets = [
      ...(manifest.icons ?? []),
      ...(manifest.screenshots ?? []),
      ...(manifest.shortcuts ?? []).flatMap((shortcut) => shortcut.icons ?? []),
    ]

    expect(referencedAssets.map((asset) => asset.src)).not.toEqual([])

    const missingAssets = referencedAssets
      .map((asset) => asset.src)
      .filter((src) => !existsSync(toPublicPath(src)))

    expect(missingAssets).toEqual([])
  })

  it('does not declare mobile-only screenshot form factors in Desktop-only scope', () => {
    const manifest = readManifest()

    expect((manifest.screenshots ?? []).map((screenshot) => screenshot.form_factor)).not.toContain('narrow')
  })
})
