import { ref, type Ref } from "vue"
import L, {Control as LeafletControl} from 'leaflet'
import type { IPointPrompt, IRectanglePrompt } from "./types"

export const prefix = " &copy; <a target=\"_blank\" href=\"https://leafletjs.com\">leaflet</a>"
export const OpenStreetMap = "OpenStreetMap"
export const Satellite = "OpenStreetMap.HOT"
export const maxZoom = 20
export const minZoom = 2
export const waitingString = "waiting..."
export const durationRef = ref(0)
export const numberOfPolygonsRef = ref(0)
export const numberOfPredictedMasksRef = ref(0)
export const responseMessageRef = ref("-")
export const geojsonRef = ref("geojsonOutput-placeholder")
export const currentBaseMapNameRef = ref("")
export const currentMapBBoxRef = ref()
export const currentZoomRef = ref()
export const promptsArrayRef: Ref<Array<IPointPrompt | IRectanglePrompt>> = ref([])
export const mapOptionsDefaultRef = ref()
export const layerControlGroupLayersRef = ref(new LeafletControl.Layers());
export const mapNavigationLocked = ref(false)
// htmlStatusMessages removed — was dead code (no runtime consumers).
// Last version: commit 4386da5. Source: https://github.com/for-GET/know-your-http-well
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