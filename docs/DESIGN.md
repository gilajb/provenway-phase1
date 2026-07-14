---
name: Architectural Precision
colors:
  surface: '#fcf9f5'
  surface-dim: '#dcdad6'
  surface-bright: '#fcf9f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f0'
  surface-container: '#f0edea'
  surface-container-high: '#eae8e4'
  surface-container-highest: '#e5e2df'
  on-surface: '#1b1c1a'
  on-surface-variant: '#424750'
  inverse-surface: '#30302e'
  inverse-on-surface: '#f3f0ed'
  outline: '#737781'
  outline-variant: '#c2c6d1'
  surface-tint: '#325f99'
  primary: '#002e59'
  on-primary: '#ffffff'
  primary-container: '#0c447c'
  on-primary-container: '#88b2f1'
  inverse-primary: '#a5c8ff'
  secondary: '#1960a6'
  on-secondary: '#ffffff'
  secondary-container: '#7ab3ff'
  on-secondary-container: '#00447e'
  tertiary: '#581500'
  on-tertiary: '#ffffff'
  tertiary-container: '#7f2200'
  on-tertiary-container: '#ff9472'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d4e3ff'
  primary-fixed-dim: '#a5c8ff'
  on-primary-fixed: '#001c3a'
  on-primary-fixed-variant: '#124780'
  secondary-fixed: '#d4e3ff'
  secondary-fixed-dim: '#a4c9ff'
  on-secondary-fixed: '#001c39'
  on-secondary-fixed-variant: '#004883'
  tertiary-fixed: '#ffdbd0'
  tertiary-fixed-dim: '#ffb59e'
  on-tertiary-fixed: '#3a0b00'
  on-tertiary-fixed-variant: '#852400'
  background: '#fcf9f5'
  on-background: '#1b1c1a'
  surface-variant: '#e5e2df'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 40px
  xl: 64px
  gutter: 24px
  margin: 32px
---

## Brand & Style
The design system is engineered for construction professionals who demand the same structural integrity in their software as they do in their buildings. The brand personality is authoritative yet approachable, blending high-stakes reliability with modern digital efficiency.

The visual style is a hybrid of **Minimalism** and **Glassmorphism**, taking cues from high-end SaaS leaders like Linear and Stripe. It avoids "industrial" grit in favor of "architectural" polish. Key characteristics include expansive whitespace, a restrained but purposeful color palette, and a focus on structural clarity. Subtle blueprint-inspired patterns—such as fine light-blue grid lines or coordinate markings—are used sparingly in headers and empty states to provide industry-specific texture without cluttering the interface.

## Colors
The palette is rooted in deep, trustworthy blues that evoke stability and professional heritage. 

- **Primary & Secondary Blues:** Used for navigation, primary actions, and brand reinforcement. These colors represent the core strength of the platform.
- **Coral Accent:** Reserved strictly for key calls-to-action (CTAs), notification badges, and progress indicators that require immediate attention. It provides a warm, high-visibility contrast to the cool blue tones.
- **Teal Success:** Used for verification badges, "on-schedule" statuses, and completed milestones.
- **Surface Tones:** The background is kept a crisp white to ensure maximum legibility, with a soft blue-tinted secondary background (`#E6F1FB`) used for sidebars, grouping elements, or distinct UI sections.
- **Neutral Grays:** Text and borders use warm-toned grays to soften the overall feel and avoid the harshness of pure black or cold steel grays.

## Typography
This design system utilizes **Inter** for its systematic, utilitarian, and highly legible qualities. 

The type hierarchy is designed for clarity in data-dense environments. Headlines use a slightly tighter letter-spacing and heavier weight to appear grounded and confident. Body text is optimized for long-form reading of project specs and contracts. Labels utilize a medium or semibold weight to differentiate them from body text, ensuring they stand out in complex forms and dashboards. For mobile views, large display type scales down significantly to maintain a professional, balanced density.

## Layout & Spacing
The layout follows a **Fluid Grid** philosophy with fixed maximum widths for content containers on desktop to prevent eye strain. 

- **Desktop:** A 12-column grid with 24px gutters. Content is typically housed in cards that span 4, 6, 8, or 12 columns.
- **Tablet:** An 8-column grid with 16px gutters and 24px margins.
- **Mobile:** A 4-column grid with 16px gutters and 16px margins.

Spacing follows a 4px/8px baseline rhythm to ensure mathematical harmony. Horizontal padding in sections should be generous (`lg` or `xl`) to create the "premium" feel of high-end SaaS applications. Data-dense tables and lists are the exception, utilizing `sm` or `xs` vertical padding to maximize information density.

## Elevation & Depth
Depth is created through a combination of **Tonal Layering** and **Ambient Shadows**.

- **Level 0 (Base):** Primary background (`#FFFFFF`) or Secondary background (`#E6F1FB`).
- **Level 1 (Cards/Surface):** White cards with a 1px border in `#B4B2A9` at 40% opacity. A very soft, diffused shadow (0px 4px 20px rgba(12, 68, 124, 0.05)) gives the card a slight "lift."
- **Level 2 (Modals/Popovers):** Surface with a more pronounced shadow (0px 12px 32px rgba(12, 68, 124, 0.12)).
- **Glassmorphism:** Navigation bars and floating headers use a `backdrop-filter: blur(12px)` with a semi-transparent white background (`rgba(255, 255, 255, 0.8)`). This keeps the UI feeling light and modern.

## Shapes
The shape language is intentional and structural. A uniform **Rounded** setting is applied to ensure the UI feels approachable without losing its professional edge.

- **Standard Elements (Buttons, Inputs, Small Cards):** 0.5rem (8px) corner radius.
- **Large Layout Containers (Project Cards, Image Holders):** 1rem (16px) corner radius.
- **Badges/Chips:** Fully pill-shaped to contrast with the more geometric layout containers.

Corners should never be sharp, as the software aims to be a helpful partner, not a rigid or cold tool.

## Components
- **Buttons:** Primary buttons use a solid `#0C447C` fill with white text. Secondary buttons use a subtle `#E6F1FB` fill with blue text. The accent button (reserved for "Create" or "Urgent") uses `#D85A30`.
- **Large Cards:** These are the primary layout building blocks. They feature 16px rounded corners, subtle shadows, and often house project imagery with a `background-size: cover` treatment.
- **Professional Verification Badges:** Small, pill-shaped components with a Teal (`#1D9E75`) background and a white "check" icon, used to indicate verified pros or completed inspections.
- **Timeline Elements:** Vertical lines (2px, `#B4B2A9`) with solid primary blue circles for completed steps and hollow circles for upcoming ones. This provides a clear "construction schedule" feel.
- **Input Fields:** Clean, white backgrounds with a subtle border. On focus, the border transitions to `#185FA5` with a 2px outer glow of the same color at 20% opacity.
- **Project Imagery Holders:** High-fidelity placeholders that use a subtle blueprint grid pattern when no image is present, maintaining the architectural aesthetic.