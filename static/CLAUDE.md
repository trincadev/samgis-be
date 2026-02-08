# CLAUDE.md - SamGIS Frontend

This file provides guidance to Claude Code (claude.ai/code) when working with the Vue.js frontend in this directory.

## Project Overview

The SamGIS frontend is a Single Page Application (SPA) built with Vue 3, TypeScript, and Vite. It provides an interactive map interface using Leaflet for geospatial ML segmentation with the Segment Anything Model (SAM).

**Key Features:**
- Interactive Leaflet map with drawing tools (Geoman)
- Point and rectangle prompts for ML inference
- Multiple basemap layers (OpenStreetMap, satellite)
- Real-time feedback and tour guide (driver.js)
- Responsive design with Tailwind CSS

## Technology Stack

- **Framework**: Vue 3 (Composition API with `<script setup>`)
- **Language**: TypeScript
- **Build Tool**: Vite 7
- **Styling**: Tailwind CSS 4
- **Mapping**: Leaflet with leaflet-providers and @geoman-io/leaflet-geoman-free
- **Testing**: Vitest with jsdom environment, @vue/test-utils for component tests
- **UI Tour**: driver.js (custom fork)
- **Package Manager**: pnpm

## Development Setup

### Prerequisites

- Node.js 20 or higher
- pnpm package manager

### Installation

```bash
# Install pnpm globally if needed
npm install -g pnpm

# Install dependencies
pnpm install
```

### Development Commands

```bash
# Start development server (with HMR)
pnpm dev
# Accessible at http://localhost:5173 by default

# Build for production
pnpm build
# Output: dist/ directory

# Build Tailwind CSS separately (required after build)
pnpm build:tailwindcss
# or: pnpm tailwindcss -i src/input.css -o dist/output.css

# Preview production build
pnpm preview --port 5173

# Run tests once
pnpm test

# Run tests in watch mode (re-runs on file changes)
pnpm test:watch

# Lint and fix
pnpm lint:fix
```

### Full Build Process

The complete build process includes both Vite build and Tailwind CSS compilation:

```bash
pnpm build
# This runs: rm -rf dist && vite build && pnpm tailwindcss -i src/input.css -o dist/output.css
```

## Project Structure

```
static/
├── src/
│   ├── App.vue                    # Root component
│   ├── main.ts                    # Application entry point
│   ├── input.css                  # Tailwind CSS input
│   ├── leaflet-custom.css         # Custom Leaflet styles
│   └── components/
│       ├── PagePredictionMap.vue  # Main map component (core logic)
│       ├── PageLayout.vue         # Layout wrapper
│       ├── PageFooter.vue         # Footer component
│       ├── PageFooterHyperlink.vue
│       ├── StatsGrid.vue          # Statistics display
│       ├── TableGenericComponent.vue
│       ├── constants.ts           # Shared constants and refs
│       ├── helpers.ts             # Utility functions
│       ├── types.d.ts             # TypeScript type definitions
│       ├── NavBar/                # Navigation components
│       │   ├── NavBar.vue
│       │   ├── MobileNavBar.vue
│       │   └── TabComponent.vue
│       └── buttons/               # Button components
│           ├── ButtonComponent.vue
│           └── ButtonMapSendRequest.vue
├── tests/                         # Vitest test suite
│   └── *.test.ts                  # Test files (*.test.ts or *.spec.ts)
├── public/                        # Static assets (favicon, manifest, etc.)
├── dist/                          # Production build output
├── index.html                     # HTML entry point
├── vite.config.ts                 # Vite configuration
├── tailwind.config.js             # Tailwind configuration
├── tsconfig.json                  # TypeScript project references
├── tsconfig.app.json              # App TypeScript config
├── tsconfig.node.json             # Node/build TypeScript config
├── tsconfig.vitest.json           # Test TypeScript config
├── package.json                   # Dependencies and scripts
└── .env                           # Environment variables template
```

## Core Architecture

### Component Hierarchy

```
App.vue
└── PageLayout.vue
    └── PagePredictionMap.vue (main component)
        ├── ButtonMapSendRequest.vue
        ├── StatsGrid.vue
        └── TableGenericComponent.vue
```

### State Management

The app uses Vue 3's Composition API with reactive refs for state management. Global state is managed in `constants.ts`:

**Key reactive state:**
- `currentBaseMapNameRef`: Current basemap layer name
- `currentMapBBoxRef`: Current map bounding box
- `currentZoomRef`: Current zoom level
- `promptsArrayRef`: Array of point/rectangle prompts for ML inference
- `responseMessageRef`: API response status message
- `mapNavigationLocked`: Lock/unlock map pan/zoom
- `durationRef`: Last request duration
- `numberOfPolygonsRef`: Number of polygons in response
- `numberOfPredictedMasksRef`: Number of predicted masks

### Main Component: PagePredictionMap.vue

The core map component handles:
- Leaflet map initialization and configuration
- Drawing tool integration (Geoman)
- Prompt creation (points and rectangles)
- ML inference API calls to backend `/infer_samgis`
- GeoJSON result visualization
- User onboarding tour (driver.js)

**Key functionality:**
1. Initialize Leaflet map with configurable bounds
2. Add basemap layers (OpenStreetMap, satellite, etc.)
3. Enable drawing tools (point markers, rectangles)
4. Track drawn features as prompts
5. Send prompts to backend API on request
6. Display returned GeoJSON polygons on map

### API Integration

**Inference endpoint:** `POST /infer_samgis`

**Request payload structure:**
```typescript
{
  bbox: {
    ne: { lat: number, lng: number },
    sw: { lat: number, lng: number }
  },
  prompt: Array<IPointPrompt | IRectanglePrompt>,
  zoom: number,
  source_name: string  // e.g., "OpenStreetMap.HOT"
}
```

**Response structure:**
```typescript
{
  body: {
    duration_run: number,
    output: {
      type: "FeatureCollection",
      features: Array<GeoJSON.Feature>
    }
  }
}
```

The API call is handled in `ButtonMapSendRequest.vue` component which sends map state to backend.

## TypeScript Configuration

The project uses TypeScript with strict type checking:
- `tsconfig.json`: Project references for multi-config setup
- `tsconfig.app.json`: Application code configuration
- `tsconfig.node.json`: Build tool (Vite) configuration
- `tsconfig.vitest.json`: Test configuration (extends app config, includes `tests/` dir, adds jsdom types)

**Type definitions** are in `src/components/types.d.ts`:
- `IPointPrompt`: Point marker with label (0=exclude, 1=include)
- `IRectanglePrompt`: Rectangle bounds
- `ITableGenericHeader`, `ITableGenericRow`: Table component types

## Tailwind CSS Configuration

Custom responsive breakpoints for various device sizes:
- `xxs`: 300px (very small phones)
- `xs`: 512px (phones)
- `tall`: Custom media query for tall phones
- `verySmallTablet`: Max 800x600
- `smallTablet`: Max 1030x770
- `2md`: 1024px
- `lg`: 1200px
- `xl`: 1380px
- `2xl`: 2000px
- `3xl`: 2360px

**Custom font:** Inter var (sans-serif)

Content scanning paths:
- `./dist/index.html`
- `./src/**/*.{vue,js,ts}`

## Environment Variables

Environment variables are prefixed with `VITE_` or `VITE__` and accessed via `import.meta.env`:

**Key variables:**
- `VITE__MAP_DESCRIPTION`: Map description text
- `VITE_INDEX_URL`: Base URL path for the app (used in Vite base config)
- `VITE__SAMGIS_SPACE`: HuggingFace space URL
- `VITE__STATIC_INDEX_URL`: Static files base URL
- `VITE_SATELLITE_NAME`: Satellite basemap layer name
- `VITE_DOCS_SAMGIS_DOMAIN`: Documentation domain

**Usage example:**
```typescript
const description = import.meta.env.VITE__MAP_DESCRIPTION || "Default description"
```

Note: Environment variables are loaded from `.env` file during build.

## Vite Configuration

Key settings in `vite.config.ts`:
- **Base path**: Configurable via `VITE_INDEX_URL` env variable
- **Alias**: `@` maps to `./src` for clean imports
- **Entry point**: `index.html` (Vite's default)
- **Build output**: `dist/`
- **Test config**: `test.include` targets `tests/**/*.{test,spec}.ts` with jsdom environment

**Import alias usage:**
```typescript
import Component from '@/components/Component.vue'
```

## Leaflet Integration

### Map Initialization

The map is initialized in `PagePredictionMap.vue` with:
- Configurable initial bounds
- Zoom controls
- Scale control
- Layer controls for basemap switching

### Drawing Tools (Geoman)

Geoman provides drawing capabilities:
- **Marker tool**: Create point prompts (with label 0 or 1)
- **Rectangle tool**: Create bounding box prompts
- **Edit mode**: Modify existing shapes
- **Remove mode**: Delete shapes

Drawing events are captured to update `promptsArrayRef`.

### Custom Leaflet Styles

Custom styles in `src/leaflet-custom.css` override default Leaflet CSS for:
- Control positioning
- Marker appearance
- Popup styling
- Drawing tool UI

## Testing

Tests use [Vitest](https://vitest.dev/) with jsdom environment. Test files live in `tests/` directory, separate from source code.

```bash
# Run all tests once
pnpm test

# Run tests in watch mode
pnpm test:watch
```

**Conventions:**
- Test files: `tests/*.test.ts` or `tests/*.spec.ts`
- Use `@/` alias to import source modules (same as app code)
- The `@` alias resolves to `./src`
- Use `@vue/test-utils` (`mount`, `shallowMount`) for Vue component tests

## Common Development Tasks

### Adding a New Component

1. Create component file in `src/components/`
2. Use `<script setup lang="ts">` for Composition API
3. Import and use in parent component
4. Add TypeScript types if needed

### Modifying Map Behavior

Main map logic is in `PagePredictionMap.vue`:
- Map initialization: `onMounted()` hook
- Drawing handlers: Geoman event listeners
- API calls: `sendMLRequest()` function

### Updating Styles

1. Modify Tailwind classes directly in components
2. For custom Tailwind utilities, update `tailwind.config.js`
3. For Leaflet-specific styles, edit `src/leaflet-custom.css`
4. Rebuild: `pnpm build:tailwindcss`

### Working with State

1. Import refs from `constants.ts`:
   ```typescript
   import { promptsArrayRef, currentZoomRef } from '@/components/constants'
   ```
2. Read: `promptsArrayRef.value`
3. Update: `promptsArrayRef.value = newValue`

## Dependencies

### Core Dependencies
- `vue`: ^3.5.27 - Vue.js framework
- `leaflet`: ^1.9.4 - Interactive maps
- `leaflet-providers`: ^3.0.0 - Basemap layer providers
- `@geoman-io/leaflet-geoman-free`: ^2.19.2 - Drawing tools
- `driver.js`: ^1.4.0 - User onboarding tours (custom fork)

### Dev Dependencies
- `vite`: ^7.3.1 - Build tool
- `@vitejs/plugin-vue`: ^6.0.4 - Vue SFC support
- `tailwindcss`: ^4.1.18 - CSS framework
- `@tailwindcss/cli`: ^4.1.18 - Tailwind CLI
- `typescript`: Via tsconfig dependencies
- `eslint`: ^10.0.0 - Linting
- `eslint-plugin-vue`: ^10.7.0 - Vue-specific linting
- `vitest`: ^4.0.18 - Unit testing framework
- `@vue/test-utils`: ^2.4.6 - Vue component testing utilities
- `jsdom`: ^28.0.0 - DOM environment for tests
- `prettier`: ^3.8.1 - Code formatting

## Troubleshooting

### Build fails with "Cannot find module @/..."

- Ensure TypeScript paths are configured in `tsconfig.app.json`
- Check Vite alias in `vite.config.ts`

### Styles not applying

- Ensure Tailwind CSS is built: `pnpm build:tailwindcss`
- Check content paths in `tailwind.config.js`
- Verify CSS is imported in `index.html`

### Map not displaying

- Check if Leaflet CSS is loaded
- Verify map container has height CSS
- Check browser console for tile loading errors
- Ensure `import 'leaflet-providers'` is present

### Type errors

- Run `pnpm install` to ensure types are available
- Check `tsconfig.app.json` includes paths
- Verify type definitions in `types.d.ts`

## Integration with Backend

The frontend expects the backend to be running on the same origin or configured via CORS. In development:
- Frontend: `http://localhost:5173` (Vite dev server)
- Backend: `http://localhost:7860` (FastAPI)

For production, the built frontend (`dist/`) is served by FastAPI as static files.

**API endpoint used:**
- `POST /infer_samgis` - ML inference with prompts
- `GET /health` - Backend health check (not directly used by frontend)

The backend serves the built frontend at the root path `/`.
