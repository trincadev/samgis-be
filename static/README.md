# SamGIS frontend

This is the [SPA](https://wikipedia.org/wiki/Single-page_application) frontend for [SamGIS](https://github.com/trincadev/samgis-be).

## Requirements

1. a recent nodejs version (I'm using nodejs 20 now)
2. `pnpm`

Then execute from this folder (`static/`):

```nodejs
npm install -g pnpm
pnpm install
pnpm build
pnpm tailwindcss -i $PWD/src/input.css -o $PWD/dist/output.css
```

## Dependencies

- [driver.js](https://github.com/trincadev/driver.js/)
- [leaflet](https://leafletjs.com/)
- [tailwind](https://tailwindcss.com/)
- [typescript](https://www.typescriptlang.org/)
- [vuejs](https://vuejs.org/)
- [vite](https://vitejs.dev/)
