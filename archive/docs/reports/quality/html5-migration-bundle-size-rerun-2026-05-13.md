# HTML5 Migration Bundle Size Rerun

Date: 2026-05-13

Change: `implement-html5-migration-experience-optimization`

Scope: Current repo-local bundle-size rerun for task `1.4.5`; this is not a bundle-target closure.

## Command

```bash
cd web/frontend
npm run build:no-types
```

## Result

- Exit status: `0`
- Build duration measured by wrapper: `56.6s`
- Vite output: `built in 55.28s`

## Size Summary

| Scope | Size | Bytes | Target status |
| --- | ---: | ---: | --- |
| `dist` | `6.14 MB` | not used for target | observation only |
| `dist/assets` | `4.45 MB` | `4,665,122` | above `2.5MiB` |
| `dist/assets/js` | `2.47 MB` | `2,584,904` | below `2.5MiB` by MiB arithmetic |
| `dist/assets/css` | `1.98 MB` | `2,080,218` | observation only |

Target reference used by the wrapper: `2.5MiB = 2,621,440 bytes`.

Top JavaScript chunks:

| Chunk | Size | Bytes |
| --- | ---: | ---: |
| `assets/js/echarts-yX0NoSA7.js` | `819.76 KB` | `839,436` |
| `assets/js/element-plus-uYjrXP-Q.js` | `522.77 KB` | `535,317` |
| `assets/js/vendor-BUg80WbF.js` | `351.06 KB` | `359,485` |
| `assets/js/vue-core-CmqAJJas.js` | `104.89 KB` | `107,407` |

## Disposition

`1.4.5` remains open.

The latest build proves the current JS directory is under `2.5MiB`, but total `dist/assets` is still above the `2.5MiB` target. Because the OpenSpec task does not unambiguously define whether the target means total assets, JS-only, gzip-only, or first-screen critical payload, this rerun cannot be used to close the task.

Future closure requires either:

- an approved bundle-size target definition, followed by a passing measurement under that definition; or
- further bundle/CSS/assets optimization until the agreed target is met.

