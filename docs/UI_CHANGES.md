# InsightTracker UI Design Reference

Approved Design: Dark, minimalist layout with blue gradient accents (primary #3b82f6 → accent #6366f1), soft elevation, rounded surfaces, restrained animation.

## 1. Color Tokens (theme.css)
Primary: `#3b82f6`
Accent: `#6366f1`
Secondary (text/elements): `#64748b`
Success: `#22c55e`
Warning: `#eab308`
Danger: `#ef4444`
Background: `#0b0f14`
Surface (panels/nav/cards): `#0f1620`
Card Background: `#101a26`
Border: `#1f2937`
Gradient Accent: `linear-gradient(135deg, var(--primary-color), var(--accent-color))`

## 2. Spacing Scale
`--space-1:4px` `--space-2:8px` `--space-3:12px` `--space-4:16px` `--space-5:20px` `--space-6:24px` `--space-8:32px` `--space-10:40px`
Use multiples consistently for padding & gaps. Example: card inner padding = `var(--space-4)`.

## 3. Radius Scale
`--radius-xs:4px` `--radius-sm:8px` `--radius-md:12px` `--radius-lg:16px` `--radius-xl:22px`
Cards: `--radius-lg`
Buttons: `--radius-md`
Avatars: 50% (circular)

## 4. Elevation & Shadows
Soft: `--shadow-soft`
Default Card Hover: `--shadow`
Glow (primary emphasis): `--shadow-glow`

## 5. Typography
Font: Inter (weights 400–800). Large hero heading uses gradient + heavy weight (800). Section headers weight 700. Uppercase micro-labels weight 600.

## 6. Components
- Navbar: Dark surface, horizontal layout, active link uses subtle translucent primary fill.
- Card: Gradient-tinted radial overlay (pseudo-element), smooth lift on hover.
- Button Primary: Gradient background + glow hover.
- Button Outline: Dark surface, neutral border, subtle lift on hover.
- Badge: Uppercase compact pill with contextual color & translucent background.
- Table: Compact, uppercase header row, subtle row hover darken.

## 7. Interaction & Focus
Focus ring: `--focus-ring` applied for keyboard accessibility. Buttons & links show outline/glow without layout shift.
Animations kept minimal (fade-up / scale-in) for performance.

## 8. Removed Systems
Per-page accent system (`page-styles.css` + body page-* classes) removed for unified visual identity. All pages now rely on shared tokens in `theme.css` only.

## 9. Adding a New Page
1. Extend `base.html`.
2. Avoid inline variable redefinition—use existing tokens.
3. Use `.section` wrappers for logical vertical spacing.
4. Prefer `.grid`, `.grid-3`, `.grid-4` utilities for responsive content blocks.
5. For a hero/header, reuse card structure or create a container with `border:1px solid var(--border-color)` + `border-radius: var(--radius-xl)`.
6. Use gradient heading via `.h1-gradient` when emphasizing page title.

## 10. Creating a New Component
1. Base shape chooses a radius token.
2. Apply background (`var(--surface)` or `var(--card-bg)`).
3. Border: `1px solid var(--border-color)` for structural definition.
4. Elevation: Start with `--shadow-soft`; add hover state with transform + `--shadow`.
5. Motion: Use `.fade-up` or `.scale-in` classes and add intersection observer if progressive reveal needed.

## 11. Accessibility Notes
- Ensure text contrast (avoid light-on-light overlays).
- Maintain focus visible styles (`:focus-visible`).
- Provide `aria-label` for icon-only buttons.

## 12. Screenshot References (Add later)
Add images to `docs/screenshots/` then link:
- Hero/Home: `docs/screenshots/home_hero.png`
- Analytics Map: `docs/screenshots/analytics_map.png`
- News Feed: `docs/screenshots/news_feed.png`
- Login Form: `docs/screenshots/login.png`

## 13. Extension Guidelines
Keep palette stable—do not introduce new accent colors unless adding a semantic category. If additional semantic state needed (info, neutral), derive lighter/darker variants of existing blue.

## 14. Performance Guidance
- Prefer CSS transitions over JS animations.
- Limit box-shadows in large lists.
- Lazy load heavy charts/maps where possible.

## 15. Future Enhancements (Optional)
- Light mode variant via separate variable override block.
- Compact density mode for power users.
- Theme switcher (user preference) if requested.

## 16. Light Mode Implementation
Light theme added via CSS variable overrides under `:root[data-theme='light']`.

Variables adjusted: background, surface, card-bg, text colors, border color, shadows, header background.

Toggle: Button with id `themeToggle` in `base.html` switches between `dark` (default) and `light`, persists preference to `localStorage` under key `theme-preference`.

Usage:
1. Default loads system preference (prefers-color-scheme light) if no saved value.
2. User click swaps theme and updates icon (sun for dark, moon for light context).
3. To force light mode server-side, you can set `<html data-theme="light">` but JS may overwrite based on stored preference.

Accessibility: Focus ring consistent; ensure contrast of text on light backgrounds remains WCAG AA (primary text #1e293b on #ffffff).

Extending: Avoid hardcoded colors in components—use variables so both themes stay aligned.

---
Document maintained: 2025-11-23. Update when tokens or global components change.
