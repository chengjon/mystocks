const test = require('node:test')
const assert = require('node:assert/strict')
const net = require('node:net')
const fs = require('node:fs')
const path = require('node:path')
const { spawnSync } = require('node:child_process')

const frontendRoot = path.resolve(__dirname, '..', '..')
const startScriptPath = path.join(frontendRoot, 'scripts', 'test-runner', 'start-sandbox-safe-dev.sh')
const smokeScriptPath = path.join(frontendRoot, 'scripts', 'test-runner', 'run-api-availability-smoke.sh')
const portSelectionPath = path.join(frontendRoot, 'scripts', 'test-runner', 'port-selection.sh')
const readmePath = path.join(frontendRoot, 'tests', 'README-E2E.md')

function read(filePath) {
  return fs.readFileSync(filePath, 'utf8')
}

function runShellExpression(expression) {
  const result = spawnSync('bash', ['-lc', `source "${portSelectionPath}"; ${expression}`], {
    cwd: frontendRoot,
    encoding: 'utf8',
  })

  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout || 'shell expression failed')
  }

  return result.stdout.trim()
}

async function withListeningPort(run) {
  const server = net.createServer()
  await new Promise((resolve, reject) => {
    server.once('error', reject)
    server.listen(0, '127.0.0.1', resolve)
  })

  try {
    const address = server.address()
    await run(address.port)
  } finally {
    await new Promise((resolve) => server.close(resolve))
  }
}

test('sandbox-safe dev runner uses standard fallback ports and real-backend default', () => {
  const source = read(startScriptPath)

  assert.match(source, /FRONTEND_PORT="\$\{FRONTEND_PORT:-3020\}"/)
  assert.match(source, /FRONTEND_BACKUP_PORT="\$\{FRONTEND_BACKUP_PORT:-3021\}"/)
  assert.match(source, /BACKEND_PORT="\$\{BACKEND_PORT:-8020\}"/)
  assert.match(source, /BACKEND_BACKUP_PORT="\$\{BACKEND_BACKUP_PORT:-8021\}"/)
  assert.match(source, /VITE_USE_MOCK_DATA="\$\{VITE_USE_MOCK_DATA:-false\}"/)
})

test('api availability smoke runner uses the same fallback ports as helper/docs', () => {
  const source = read(smokeScriptPath)

  assert.match(source, /FRONTEND_PORT="\$\{FRONTEND_PORT:-3020\}"/)
  assert.match(source, /FRONTEND_BACKUP_PORT="\$\{FRONTEND_BACKUP_PORT:-3021\}"/)
  assert.match(source, /BACKEND_PORT="\$\{BACKEND_PORT:-8020\}"/)
  assert.match(source, /BACKEND_BACKUP_PORT="\$\{BACKEND_BACKUP_PORT:-8021\}"/)
})

test('readme explicitly distinguishes real-backend dev runner from mock fallback usage', () => {
  const source = read(readmePath)

  assert.match(source, /npm run dev:sandbox-safe/)
  assert.match(source, /VITE_USE_MOCK_DATA=true/)
})

test('backend target keeps the preferred port when it is already listening', async () => {
  await withListeningPort(async (primaryPort) => {
    const backupPort = primaryPort + 1
    const selectedPort = runShellExpression(`resolve_backend_target_port ${primaryPort} ${backupPort} ""`)
    assert.equal(selectedPort, String(primaryPort))
  })
})

test('backend spawn port moves to backup only when primary is occupied and we need a new backend', async () => {
  await withListeningPort(async (primaryPort) => {
    const backupPort = primaryPort + 1
    const selectedPort = runShellExpression(`resolve_backend_spawn_port ${primaryPort} ${backupPort} ""`)
    assert.equal(selectedPort, String(backupPort))
  })
})
