# ArtDecoMechanicalSwitch SCSS Style Split Report

Date: 2026-06-04

## Scope

- Target: `web/frontend/src/components/artdeco/business/styles/ArtDecoMechanicalSwitch.scss`
- Change type: style-only SCSS structure split
- Behavior scope: no Vue template, script, route, API, or runtime logic changes

## Split Result

- `ArtDecoMechanicalSwitch.scss`: retained as the 9-line style entrypoint.
- `ArtDecoMechanicalSwitch.base.scss`: root switch, disabled state, label, and control container styles.
- `ArtDecoMechanicalSwitch.frame.scss`: frame and Art Deco corner decorator styles.
- `ArtDecoMechanicalSwitch.toggle.scss`: toggle body, active state, and disabled toggle styles.
- `ArtDecoMechanicalSwitch.thumb.scss`: thumb container, thumb, screw, and slot styles.
- `ArtDecoMechanicalSwitch.track.scss`: track-line styles.
- `ArtDecoMechanicalSwitch.effects-status.scss`: keyframes, status text, and design note.

## Verification

- Mechanical equivalence check: concatenated split bodies match the original SCSS body after removing the entry token import line.
- Line count after split:
  - entrypoint: 9 lines
  - base: 48 lines
  - frame: 89 lines
  - toggle: 62 lines
  - thumb: 134 lines
  - track: 48 lines
  - effects-status: 71 lines

## Notes

- The split preserves existing selector order and declaration text.
- Existing token spellings were intentionally left unchanged because this batch is structure-only.
