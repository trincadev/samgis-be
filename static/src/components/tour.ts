export const driverSteps = [
  { element: 'id-prediction-map-container', popover: { title: 'SamGIS', description: 'A quick tour about SamGIS functionality'} },
  { element: '#map', popover: { title: 'Webmap for ML prompt', description: 'Add here your machine learning prompt. Pay attention about markers and polygons outside the map bounds: you could get unexpected results' } },
  { element: '.leaflet-pm-icon-marker-include', popover: { title: '"Include" point prompt', description: 'add "include" points prompt (label 1) for machine learning request' } },
  { element: '.leaflet-pm-icon-marker-exclude', popover: { title: '"Exclude" point prompt', description: 'add "exclude" points prompt (label 0) for machine learning request' } },
  { element: '.leaflet-pm-icon-rectangle', popover: { title: '"Include" rectangle prompt', description: 'add "include" rectangles prompt for machine learning request' } },
  { element: "#id-button-submit", popover: { title: 'ML submit button', description: 'Machine learning submit button' } },
  { element: '.leaflet-control-layers-toggle', popover: { title: 'Map provider selector', description: 'select a different map provider' } },
  { element: '#id-map-info', popover: { title: 'map info', description: 'Section about various map info' } },
  { element: '#id-ml-request-prompt', popover: { title: 'ML prompt quest', description: 'Empty at beginning, this table will contain the machine learning prompt (points and rectangles) section' } }
]
