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