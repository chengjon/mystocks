# Product

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Register

product

## Users

Individual quantitative investors and small trading teams focused on A-share (Chinese) markets. They sit at a desk with a large monitor, often running multiple panels simultaneously. Their context is time-sensitive: market hours demand split-second reads on price action, risk exposure, and strategy signals. They are technically literate, comfortable with data-dense interfaces, and do not need hand-holding. Many have experience with professional terminals like Bloomberg or TongDaXin and expect similar information density.

## Product Purpose

MyStocks is a local-deployment quantitative trading analysis terminal. It provides market data ingestion, technical analysis, strategy backtesting, portfolio attribution, risk monitoring, and trade decision support for A-share markets. Success means the user can move from market signal to informed decision faster and with higher confidence than with scattered tools. The product is not a broker and does not execute trades; it serves analysis and decision-making.

## Brand Personality

Precise, authoritative, restrained.

The interface communicates expert competence without shouting. Gold accents and ArtDeco geometry signal premium intent, but the system never lets decoration compete with data. When the user glances at a risk panel during volatile trading, every pixel must justify itself. The tone is that of a trusted analyst: calm under pressure, rigorous in detail, confident without bravado.

## Anti-references

- **Generic SaaS dashboards**: Tailwind-blue hero sections, identical card grids with icon-heading-text repetition, cookie-cutter metric layouts, gradient-on-white everything.
- **Consumer finance apps**: Playful illustrations, rounded pastel UI, gamified onboarding, emoji-driven feedback, soft shadows on everything.
- **Over-decorated fintech**: Gold used indiscriminately across every surface, gratuitous animation loops, decorative elements that compete with live data for attention, form over function.

## Design Principles

1. **Data speaks first**: In trading and monitoring surfaces, decoration yields to information density. ArtDeco motifs are available for brand-forward moments, never for data-critical panels.
2. **Expert confidence**: The interface trusts the user. No excessive tooltips, no onboarding tours on every visit, no confirmation dialogs for reversible actions. Speak the language of the domain, not the language of generic software.
3. **Precision over spectacle**: Every visual element must earn its place against the data it frames. A gold glow that obscures a price tick is a bug, not a feature. Animation duration is measured against the user's reaction time, not against aesthetic preference.
4. **Theatrical restraint**: ArtDeco drama is a deliberate choice, not a default. Use it where it reinforces brand identity (overview dashboards, empty states, feature introductions) and withdraw it where it would slow down a trading decision.
5. **A-share native**: The system thinks in Chinese market conventions: red for profit, green for loss, percentage-based price limits, sector concepts like longhubang and dragon-tiger lists. Never translate these into Western metaphors; present them natively.

## Accessibility & Inclusion

- WCAG AA contrast minimum across all text and interactive elements
- All animations degrade to opacity-only or no animation under `prefers-reduced-motion: reduce`
- Price flash feedback is never the sole carrier of meaning; numeric delta, icon, or label must always remain visible
- Desktop-only platform (minimum 1280x720); no mobile or tablet adaptation required
- Keyboard-accessible primary actions in trading panels with visible focus rings
- Tabular numeric data uses `font-variant-numeric: tabular-nums` for column alignment
