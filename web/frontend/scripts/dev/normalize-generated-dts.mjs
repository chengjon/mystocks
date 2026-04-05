import { existsSync } from 'node:fs'
import { readFile, writeFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const GENERATED_TS_NOCHECK_PATTERN = /(^|\n)\/\/ @ts-nocheck\r?\n/

export function stripTsNoCheckFromGeneratedDts(source) {
  return source.replace(GENERATED_TS_NOCHECK_PATTERN, '$1')
}

export async function normalizeGeneratedDtsFile(filePath, cwd = process.cwd()) {
  const absolutePath = resolve(cwd, filePath)

  if (!existsSync(absolutePath)) {
    return false
  }

  const source = await readFile(absolutePath, 'utf8')
  const normalizedSource = stripTsNoCheckFromGeneratedDts(source)

  if (normalizedSource === source) {
    return false
  }

  await writeFile(absolutePath, normalizedSource, 'utf8')
  return true
}
