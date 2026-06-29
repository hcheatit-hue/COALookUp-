# HC Heat Exchangers — Design Direction Guide

## Purpose
This document defines three possible user interface styles for HC Heat Exchangers internal systems, dashboards, portals, and workflow applications.

The goal is to create interfaces that feel professional, usable, and aligned with a manufacturing / engineering environment while still giving room for modern UI patterns.

---

# Brand Context

## Company Feel
HC Heat Exchangers should feel:

- Industrial but modern
- Reliable and structured
- Operationally focused
- Clear and easy to use
- Professional enough for management users
- Practical enough for factory, dispatch, quality, stores, and admin users

## Suggested Core Brand Keywords

- Precision
- Heat transfer
- Manufacturing
- Engineering
- Reliability
- Workflow
- Control
- Visibility
- Efficiency

---

# Global Design Principles

## 1. Clarity First
Every screen must make it obvious what the user needs to do next.

Good examples:

- Clear action buttons
- Status badges
- Search-first layouts
- Simple tables
- Short labels
- Visible filters
- Minimal unnecessary text

## 2. Operational Speed
Many HC systems are used in live working environments. Users should not waste time figuring out the interface.

Design for:

- Fast scanning
- Bulk actions
- Search and filter
- Large click areas
- Tablet-friendly layouts
- Clear error messages
- Strong confirmation states

## 3. Consistent Status Language
Use the same colours and wording across apps.

Example:

| Status | Meaning | Suggested Colour |
|---|---|---|
| Pending | Waiting for action | Amber / Yellow |
| In Progress | Currently active | Blue |
| Completed | Finished successfully | Green |
| Failed / Rejected | Requires correction | Red |
| Archived | Stored / closed | Grey |

## 4. Business System Friendly
The UI should work well with ERP, SharePoint, SQL, document workflows, QR scanning, and internal dashboards.

Design should support:

- Data tables
- Document previews
- Forms
- Approvals
- Audit trails
- User roles
- Reports
- Search screens
- Admin panels

---

# Style Option 1: Bento Grid Style

## Design Summary
A modern, warm, modular interface using card-based layouts, rounded corners, soft shadows, and floating hover effects.

This style is best for:

- Internal dashboard home pages
- App launchers
- KPI overview screens
- Intranet landing pages
- Department dashboards
- Management summaries

## Visual Direction

The layout uses a bento grid structure where content is grouped into flexible cards of different sizes. Each card should feel like a separate module but still belong to one clean system.

## Personality

- Modern
- Friendly
- Warm
- Slightly premium
- Easy to scan
- Less corporate, more polished

## Colour Palette

### Primary Warm Palette

| Token | Colour | Usage |
|---|---|---|
| `--color-primary` | `#C96F32` | Primary buttons, highlights |
| `--color-primary-dark` | `#9E4F24` | Hover states |
| `--color-accent` | `#F4A261` | Secondary highlights |
| `--color-background` | `#FAF7F2` | Main page background |
| `--color-surface` | `#FFFFFF` | Cards and panels |
| `--color-muted` | `#EFE7DC` | Soft card backgrounds |
| `--color-text` | `#2B2520` | Main text |
| `--color-subtext` | `#6F6258` | Supporting text |
| `--color-border` | `#E4D7CA` | Card borders |

## Typography

Use medium-sized fonts. Avoid tiny text.

| Element | Size | Weight |
|---|---:|---:|
| Page title | 28px – 34px | 700 |
| Section title | 20px – 24px | 600 |
| Card title | 16px – 18px | 600 |
| Body text | 14px – 16px | 400 |
| Table text | 14px | 400 |
| Labels | 12px – 13px | 600 |

Recommended fonts:

- Inter
- Segoe UI
- Aptos
- Roboto

## Layout Rules

Use a 12-column grid on desktop.

Example bento layout:

```text
┌────────────────────┬──────────────┬──────────────┐
│ Welcome / Overview │ Quick Action │ Quick Action │
│                    ├──────────────┴──────────────┤
│                    │ KPI Summary                  │
├────────────┬───────┴──────────────┬──────────────┤
│ App Card   │ Recent Activity       │ Notifications│
├────────────┴──────────────────────┴──────────────┤
│ Data Table / Main Work Area                       │
└───────────────────────────────────────────────────┘
```

## Card Design

Cards should use:

- Border radius: `20px` to `28px`
- Soft shadow
- Light border
- Good internal spacing
- Hover lift effect

Example CSS:

```css
.bento-card {
  background: #ffffff;
  border: 1px solid #e4d7ca;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(43, 37, 32, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.bento-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 45px rgba(43, 37, 32, 0.14);
  border-color: #f4a261;
}
```

## Button Style

```css
.btn-primary {
  background: #c96f32;
  color: #ffffff;
  border: none;
  border-radius: 14px;
  padding: 11px 18px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease;
}

.btn-primary:hover {
  background: #9e4f24;
  transform: translateY(-2px);
}
```

## Component Ideas

### Dashboard Cards

- Open Work Orders
- Pending QC Slips
- Documents Awaiting Review
- Delivery Notes Uploaded
- Stock Exceptions
- Recent COA Searches
- Active Users
- System Health

### Quick Actions

- Upload document
- Search order
- Scan QR code
- Create incident
- View reports
- Open SharePoint folder

## Best Use Case

Use this style for a modern HC internal portal or app dashboard where users need a welcoming landing page with important actions grouped visually.

---

# Style Option 2: HC Corporate

## Design Summary
A structured, Microsoft Outlook-inspired corporate design with rigid grids, clear navigation, strong alignment, and business-focused layouts.

This style is best for:

- ERP-style tools
- Admin panels
- Document management systems
- User management
- Workflow approvals
- Formal reporting apps
- Systems used by finance, HR, stores, quality, and dispatch

## Visual Direction

This interface should feel close to Microsoft 365 / Outlook: clean, structured, dependable, and familiar to office users.

## Personality

- Corporate
- Practical
- Formal
- Familiar
- Low-risk
- Productivity-focused

## Colour Palette

| Token | Colour | Usage |
|---|---|---|
| `--color-primary` | `#0F6CBD` | Main action colour |
| `--color-primary-dark` | `#0B4F8A` | Hover state |
| `--color-background` | `#F5F6F8` | App background |
| `--color-surface` | `#FFFFFF` | Panels, tables, forms |
| `--color-sidebar` | `#F0F2F5` | Navigation area |
| `--color-border` | `#DADDE3` | Grid and panel borders |
| `--color-text` | `#1F2933` | Main text |
| `--color-subtext` | `#5F6B7A` | Secondary text |
| `--color-header` | `#FFFFFF` | Top bar |

## Typography

Recommended font:

- Segoe UI
- Aptos
- Arial

| Element | Size | Weight |
|---|---:|---:|
| Page title | 24px – 28px | 600 |
| Section title | 18px – 20px | 600 |
| Table header | 13px – 14px | 600 |
| Body text | 14px | 400 |
| Form label | 13px | 600 |
| Small helper text | 12px | 400 |

## Layout Rules

The HC Corporate layout should follow a rigid app shell.

```text
┌─────────────────────────────────────────────┐
│ Top Header / App Bar                         │
├───────────────┬─────────────────────────────┤
│ Sidebar Nav   │ Page Header                  │
│               ├─────────────────────────────┤
│               │ Toolbar / Filters            │
│               ├─────────────────────────────┤
│               │ Main Table / Form / Workflow │
└───────────────┴─────────────────────────────┘
```

## Navigation

Use a left sidebar with clear sections.

Example:

```text
Dashboard
Documents
Work Orders
Quality Control
Delivery Notes
Reports
Users
Settings
```

## Top Bar

The top bar should include:

- App name
- Search input
- Notifications
- User profile
- Role indicator

## Panel Style

```css
.corporate-panel {
  background: #ffffff;
  border: 1px solid #dadde3;
  border-radius: 8px;
  padding: 18px;
}
```

## Table Style

Tables are central to this style.

```css
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: #ffffff;
  font-size: 14px;
}

.data-table th {
  background: #f0f2f5;
  color: #1f2933;
  font-weight: 600;
  text-align: left;
  padding: 12px;
  border-bottom: 1px solid #dadde3;
}

.data-table td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.data-table tr:hover {
  background: #f7faff;
}
```

## Button Style

```css
.btn-corporate {
  background: #0f6cbd;
  color: #ffffff;
  border: 1px solid #0f6cbd;
  border-radius: 6px;
  padding: 9px 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-corporate:hover {
  background: #0b4f8a;
}
```

## Form Design

Forms should be compact, aligned, and easy to complete.

Rules:

- Labels above inputs
- Required fields clearly marked
- Use helper text for unclear fields
- Use inline validation
- Keep submit buttons in a fixed footer for long forms

Example fields:

- Customer Name
- Customer ID
- Work Order Number
- Delivery Note Number
- Department
- Status
- Assigned To
- Date Created

## Best Use Case

Use HC Corporate for serious business applications where structure, accuracy, auditability, and data-heavy workflows are more important than visual personality.

---

# Style Option 3: Casual Dashboard

## Design Summary
A flexible, UI-focused dashboard style that supports both dark and light themes. It is more relaxed than HC Corporate but more operational than the Bento style.

This style is best for:

- Operational monitoring dashboards
- IT dashboards
- App launcher dashboards
- Factory status screens
- Internal tools used often by technical users
- Mixed desktop and tablet usage

## Visual Direction

This design should feel like a modern SaaS dashboard. It should be clean, functional, and comfortable for daily use.

## Personality

- Modern
- Flexible
- Practical
- Dashboard-first
- Slightly technical
- Easy to theme

---

## Light Theme Palette

| Token | Colour | Usage |
|---|---|---|
| `--color-primary` | `#2563EB` | Primary actions |
| `--color-secondary` | `#14B8A6` | Secondary actions / success highlights |
| `--color-background` | `#F8FAFC` | Main background |
| `--color-surface` | `#FFFFFF` | Cards and panels |
| `--color-muted` | `#EEF2F7` | Muted areas |
| `--color-border` | `#E2E8F0` | Borders |
| `--color-text` | `#0F172A` | Main text |
| `--color-subtext` | `#64748B` | Supporting text |

## Dark Theme Palette

| Token | Colour | Usage |
|---|---|---|
| `--color-primary` | `#60A5FA` | Primary actions |
| `--color-secondary` | `#2DD4BF` | Secondary actions / success highlights |
| `--color-background` | `#0F172A` | Main background |
| `--color-surface` | `#111827` | Cards and panels |
| `--color-muted` | `#1E293B` | Muted areas |
| `--color-border` | `#334155` | Borders |
| `--color-text` | `#F8FAFC` | Main text |
| `--color-subtext` | `#94A3B8` | Supporting text |

## Theme Token Example

```css
:root {
  --color-primary: #2563eb;
  --color-secondary: #14b8a6;
  --color-background: #f8fafc;
  --color-surface: #ffffff;
  --color-muted: #eef2f7;
  --color-border: #e2e8f0;
  --color-text: #0f172a;
  --color-subtext: #64748b;
}

[data-theme="dark"] {
  --color-primary: #60a5fa;
  --color-secondary: #2dd4bf;
  --color-background: #0f172a;
  --color-surface: #111827;
  --color-muted: #1e293b;
  --color-border: #334155;
  --color-text: #f8fafc;
  --color-subtext: #94a3b8;
}
```

## Layout Rules

The dashboard should be modular but less decorative than Bento.

```text
┌──────────────────────────────────────────────┐
│ Header: Search, Theme Toggle, User            │
├──────────────────────────────────────────────┤
│ KPI Cards                                     │
├───────────────┬──────────────────────────────┤
│ Sidebar/Menu  │ Charts / Tables / Work Queue  │
├───────────────┴──────────────────────────────┤
│ Activity Feed / Logs / Recent Actions         │
└──────────────────────────────────────────────┘
```

## Card Style

```css
.dashboard-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
}
```

## Theme Toggle

Include a simple light/dark mode toggle.

```css
.theme-toggle {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  border-radius: 999px;
  padding: 8px 12px;
  cursor: pointer;
}
```

## Dashboard Components

Recommended components:

- KPI cards
- Activity feed
- Recent uploads
- Work queue
- Status widgets
- User profile dropdown
- Search bar
- Notification centre
- Theme toggle
- App shortcuts
- Charts
- Small admin widgets

## Example KPI Cards

| KPI | Example |
|---|---|
| Open Work Orders | 128 |
| Pending Delivery Notes | 42 |
| QC Slips Awaiting Review | 17 |
| Stock Exceptions | 9 |
| Incidents This Month | 4 |
| Documents Uploaded Today | 36 |

## Button Style

```css
.btn-dashboard {
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 10px;
  padding: 10px 16px;
  font-weight: 600;
  cursor: pointer;
}

.btn-dashboard:hover {
  opacity: 0.9;
}
```

## Best Use Case

Use Casual Dashboard for systems where users need live visibility, quick actions, and regular daily interaction.

---

# Shared Components Across All Styles

## Status Badge

```css
.badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 700;
}

.badge-success {
  background: #dcfce7;
  color: #166534;
}

.badge-warning {
  background: #fef3c7;
  color: #92400e;
}

.badge-danger {
  background: #fee2e2;
  color: #991b1b;
}

.badge-info {
  background: #dbeafe;
  color: #1e40af;
}
```

## Search Bar

```css
.search-input {
  width: 100%;
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 12px;
  padding: 11px 14px;
  font-size: 14px;
  background: var(--color-surface, #ffffff);
  color: var(--color-text, #0f172a);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}
```

## Empty State

Use clear empty states instead of blank screens.

Example copy:

```text
No records found
Try changing your search filters or check the order number again.
```

## Loading State

Use skeleton loaders for dashboard cards and tables.

```css
.skeleton {
  background: linear-gradient(90deg, #e5e7eb 25%, #f3f4f6 37%, #e5e7eb 63%);
  background-size: 400% 100%;
  animation: skeleton-loading 1.4s ease infinite;
  border-radius: 10px;
}

@keyframes skeleton-loading {
  0% { background-position: 100% 50%; }
  100% { background-position: 0 50%; }
}
```

---

# Recommended Usage by HC App Type

| App / System | Recommended Style |
|---|---|
| Main internal app launcher | Bento Grid Style |
| Intranet homepage | Bento Grid Style or Casual Dashboard |
| Delivery Note App | HC Corporate |
| QC Slip Management | HC Corporate |
| COA / Box QR system | Casual Dashboard |
| Incident reporting | HC Corporate |
| IT dashboard | Casual Dashboard |
| Management KPI dashboard | Bento Grid Style |
| User management | HC Corporate |
| SharePoint document portal | HC Corporate |
| Factory tablet interface | Casual Dashboard |

---

# Accessibility Rules

## Minimum Requirements

- Text must have strong contrast
- Buttons must be large enough to click on tablets
- Form labels must always be visible
- Do not rely only on colour to show status
- Add icons or text with colour indicators
- Use clear error messages
- Ensure keyboard navigation works

## Recommended Button Sizes

| Device | Minimum Button Height |
|---|---:|
| Desktop | 38px |
| Tablet | 44px |
| Factory touchscreen | 48px – 56px |

---

# Icon Direction

Use simple line icons.

Recommended icon categories:

- Dashboard
- Search
- Upload
- Document
- QR code
- Factory
- User
- Settings
- Bell
- Check circle
- Warning triangle
- Archive
- Calendar
- Report

Recommended icon libraries:

- Lucide Icons
- Heroicons
- Bootstrap Icons
- Microsoft Fluent Icons

---

# Animation Rules

Use subtle animation only.

Allowed:

- Button hover lift
- Card hover lift
- Fade-in on page load
- Slide-in panels
- Smooth theme transition

Avoid:

- Excessive bouncing
- Slow animations
- Distracting loaders
- Overly decorative motion

Suggested timing:

```css
transition: all 0.2s ease;
```

---

# Final Recommendation

## Best Overall Direction
Use a combined approach:

1. **Bento Grid Style** for the main landing page and management overview.
2. **HC Corporate** for forms, tables, admin screens, document workflows, and approval processes.
3. **Casual Dashboard** for monitoring screens, IT dashboards, QR workflows, and tablet-friendly factory interfaces.

This gives HC Heat Exchangers a flexible internal design system that can support polished dashboards and serious business applications without making every screen look the same.

---

# Suggested File Naming

```text
design.md
hc-design-system.md
hc-ui-style-guide.md
hc-internal-app-design-guide.md
```

---

# Developer Notes

When building React, Flask, Bootstrap, or plain HTML apps, keep the design tokens separate from the layout CSS.

Recommended structure:

```text
src/
  styles/
    tokens.css
    layout.css
    components.css
    themes.css
```

For plain HTML / Bootstrap projects:

```text
static/
  css/
    design-tokens.css
    app.css
```

For React projects:

```text
src/
  styles/
    tokens.css
    themes.css
  components/
    Card.jsx
    Button.jsx
    Badge.jsx
    DataTable.jsx
    AppShell.jsx
```

---

# Implementation Priority

Start with:

1. Colour tokens
2. Typography rules
3. Cards
4. Buttons
5. Tables
6. Forms
7. Badges
8. App shell
9. Theme support
10. Motion effects

