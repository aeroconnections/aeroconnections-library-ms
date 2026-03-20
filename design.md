# Library Management System — Design Documentation

## Brand Identity

**Company:** AeroConnections
**Product:** Library Management System
**Version:** 1.0

### Mission Statement
A clean, professional library management interface for AeroConnections staff to track book inventory, loans, and overdue returns.

### Core Design Principles
1. **Clarity** — Information hierarchy is clear, actions are obvious
2. **Efficiency** — Common tasks require minimal clicks
3. **Professionalism** — Clean, modern aesthetic suitable for corporate environments
4. **Accessibility** — WCAG 2.1 AA compliant

---

## Brand Colors (AeroConnections)

### Primary Palette
| Name | Pantone | Hex | Usage |
|------|---------|-----|-------|
| Primary Red | Pantone 485 C | `#DA291C` | Primary buttons, links, accents, active states |
| Light Grey | Pantone Cool Grey 5 C | `#C8C9C7` | Page background, card backgrounds |
| Dark Grey | Pantone Cool Grey 11 C | `#5B6770` | Body text, sidebar, secondary text |
| White | - | `#FFFFFF` | Card surfaces, inputs, contrast areas |

### Semantic Colors
| Name | Hex | Usage |
|------|-----|-------|
| Success | `#059669` | Returned status, available, positive actions |
| Warning | `#D97706` | Due soon (25+ days), pending states |
| Danger | `#DA291C` | Overdue (30+ days), errors, destructive actions |

### Status Color Mapping
| Status | Background | Text |
|--------|------------|------|
| Available | White | Success |
| On Loan | Light Grey | Dark Grey |
| Overdue | `#FEE2E2` | Danger |
| Returned | `#D1FAE5` | Success |

---

## Typography

### Font Stack
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Type Scale
| Name | Size | Weight | Usage |
|------|------|--------|-------|
| Display | 2.5rem (40px) | 700 | Page titles |
| H1 | 2rem (32px) | 700 | Section headings |
| H2 | 1.5rem (24px) | 600 | Card titles |
| H3 | 1.25rem (20px) | 600 | Subsections |
| Body | 1rem (16px) | 400 | Primary content |
| Small | 0.875rem (14px) | 400 | Secondary text |
| Caption | 0.75rem (12px) | 500 | Labels, badges |

### Line Heights
- Headings: 1.2
- Body: 1.5

---

## Spacing System

### Base Unit
`4px` (0.25rem)

### Spacing Scale
| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Tight gaps |
| `space-2` | 8px | Icon gaps |
| `space-3` | 12px | Form padding |
| `space-4` | 16px | Standard padding |
| `space-5` | 20px | Card padding |
| `space-6` | 24px | Section gaps |
| `space-8` | 32px | Page margins |

### Border Radius
| Token | Value | Usage |
|-------|-------|-------|
| `radius-sm` | 4px | Badges, small buttons |
| `radius-md` | 8px | Inputs, cards |
| `radius-lg` | 12px | Modals, large cards |

---

## Components

### Buttons

#### Primary Button (AeroConnections Red)
- Background: `#DA291C` (Primary Red)
- Text: White, weight 500
- Padding: 12px 16px
- Border Radius: 8px
- Hover: Darken to `#B8231A`
- Active: Scale 0.98
- Disabled: Opacity 50%

#### Secondary Button
- Background: White
- Border: 1px `#C8C9C7` (Light Grey)
- Text: `#5B6770` (Dark Grey)
- Hover: Background `#C8C9C7`

#### Ghost Button
- Background: Transparent
- Text: `#DA291C`
- Hover: Background `#FEE2E2`

#### Button Sizes
| Size | Height | Padding |
|------|--------|---------|
| Small | 32px | 8px 12px |
| Medium | 40px | 12px 16px |
| Large | 48px | 16px 24px |

### Form Inputs

#### Text Input
- Height: 40px
- Border: 1px `#C8C9C7`
- Border Radius: 8px
- Padding: 12px horizontal
- Background: White
- Focus: Border `#DA291C`, ring `#FEE2E2`
- Placeholder: `#5B6770`

#### File Upload
- Border: 2px dashed `#C8C9C7`
- Border Radius: 8px
- Hover: Border `#DA291C`
- Accept: image/* files only

### Status Badges

| Status | Background | Text |
|--------|------------|------|
| Available | `#D1FAE5` | `#059669` |
| On Loan | `#C8C9C7` | `#5B6770` |
| Due Soon (25+ days) | `#FEF3C7` | `#D97706` |
| Overdue (30+ days) | `#FEE2E2` | `#DA291C` |
| Returned | `#D1FAE5` | `#059669` |

### Cards

#### Book Card
- Background: White
- Border: 1px `#C8C9C7`
- Border Radius: 12px
- Padding: 16px
- Shadow: `0 1px 3px rgba(0,0,0,0.05)`
- Hover: Shadow `0 4px 6px rgba(0,0,0,0.1)`

#### Stat Card
- Background: White
- Border: 1px `#C8C9C7`
- Border Radius: 12px
- Padding: 20px
- Icon: 40px circle with brand color background

### Navigation

#### Sidebar (Desktop)
- Width: 256px
- Background: `#5B6770` (Dark Grey)
- Text: White
- Items: 48px height
- Active: Background `#DA291C` (Red)
- Hover: Background `rgba(255,255,255,0.1)`

#### Top Bar
- Height: 64px
- Background: White
- Border-bottom: 1px `#C8C9C7`
- Logo: Left-aligned
- User menu: Right-aligned

---

## Page Layouts

### Dashboard
```
┌────────────────────────────────────────────────────────────┐
│  AeroConnections Logo                                       │
├──────────┬─────────────────────────────────────────────────┤
│          │                                                 │
│ Dashboard│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐│
│ ─────────│  │ Books   │ │Active   │ │Due Soon │ │Overdue ││
│ Books    │  │   123   │ │  45     │ │   12    │ │   5    ││
│ Loans    │  └─────────┘ └─────────┘ └─────────┘ └────────┘│
│ Return   │                                                 │
│ Notes    │  Recent Activity          Overdue Alerts        │
│          │  ┌────────────────┐      ┌────────────────┐      │
│ Settings │  │ • Book #12 out│      │ #7 - 35 days  │      │
│          │  │ • Book #5 ret │      │ #15 - 32 days │      │
│          │  └────────────────┘      └────────────────┘      │
└──────────┴─────────────────────────────────────────────────┘
```

### Loan List
```
┌────────────────────────────────────────────────────────────┐
│  Loans                               [+ New Loan] [Filter ▼] │
├──────────┬─────────────────────────────────────────────────┤
│          │                                                  │
│ Dashboard│  ┌─────────────────────────────────────────────┐ │
│ Books    │  │ ID │ Book │ Borrower │ Date │ Days │ Status│ │
│ Loans    │  │ 01 │ Book │ John     │ Mar 1│  20  │Active │ │
│ Return   │  │ 07 │ Book │ Jane     │ Feb15│  35  │OVERDUE│ │
│ Notes    │  └─────────────────────────────────────────────┘ │
│          │                                                  │
└──────────┴─────────────────────────────────────────────────┘
```

### Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Single column, bottom nav |
| Tablet | 640px - 1024px | Collapsible sidebar |
| Desktop | > 1024px | Full sidebar |

---

## Loan System Logic

### Days Calculation
- `days_out` = Current date - Checkout date
- `days_until_due` = Due date - Current date

### Status Thresholds
| Days Out | Status | Action |
|----------|--------|--------|
| 0-29 | On Loan | Normal |
| 25-29 | Due Soon | Warning (amber) |
| 30+ | Overdue | Alert (red) + Google Chat notification |

### Default Loan Duration
- 30 days
- Renewal requires return + re-checkout

---

## Data Models

### Book
| Field | Type | Notes |
|-------|------|-------|
| book_id | CharField | Auto-generated (01, 02...), editable |
| title | CharField | Book title |
| author | CharField | Author name |
| isbn | CharField | ISBN |
| status | ChoiceField | Available, On Loan |
| created_at | DateTime | Auto |

### Loan
| Field | Type | Notes |
|-------|------|-------|
| book | ForeignKey | Link to book |
| book_id_snapshot | CharField | Snapshot of book_id |
| borrower_name | CharField | Borrower's name |
| checkout_date | DateField | Checkout date |
| due_date | DateField | Checkout + 30 days |
| return_date | DateField | Actual return date |
| status | ChoiceField | Active, Returned, Overdue |
| notes | TextField | Optional return notes |
| damage_image | ImageField | Optional damage photo |
| created_by | ForeignKey | Staff user |
| created_at | DateTime | Auto |

### ReturnNote
| Field | Type | Notes |
|-------|------|-------|
| loan | ForeignKey | Link to loan |
| book | ForeignKey | Link to book |
| borrower_name | CharField | Snapshot of borrower |
| note | TextField | Return notes (optional) |
| image | ImageField | Damage photo (optional) |
| created_by | ForeignKey | Staff user |
| created_at | DateTime | Auto |

---

## Icons

Using **Heroicons** (MIT licensed):
- Outline style for navigation
- Solid style for emphasis
- 20px default size

---

## Accessibility

- Focus: 2px outline `#DA291C`
- Touch targets: 44x44px minimum
- Contrast: 4.5:1 minimum
- Keyboard navigation: Full support
