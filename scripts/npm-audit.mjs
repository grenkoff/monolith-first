import { spawnSync } from 'node:child_process'
import { readFileSync } from 'node:fs'

const allowlist = new URL('../npm-audit-allowlist.json', import.meta.url)
const allowed = new Set(
  JSON.parse(readFileSync(allowlist, 'utf8')).map((entry) => entry.advisory),
)

const audit = spawnSync('npm', ['audit', '--json'], { encoding: 'utf8' })
const report = JSON.parse(audit.stdout)

const advisories = Object.values(report.vulnerabilities ?? {})
  .flatMap((vulnerability) => vulnerability.via)
  .filter((via) => typeof via === 'object')
  .map((via) => ({
    id: new URL(via.url).pathname.split('/').pop(),
    name: via.name,
    severity: via.severity,
    title: via.title,
  }))

const blocking = advisories.filter((advisory) => !allowed.has(advisory.id))
const stale = [...allowed].filter(
  (id) => !advisories.some((advisory) => advisory.id === id),
)

for (const advisory of blocking) {
  console.error(
    `${advisory.severity} ${advisory.name}: ${advisory.title} (${advisory.id})`,
  )
}
for (const id of stale) {
  console.error(`${id} is no longer reported: remove it from npm-audit-allowlist.json`)
}
for (const id of allowed) {
  console.log(`allowed: ${id}`)
}

process.exit(blocking.length + stale.length > 0 ? 1 : 0)
