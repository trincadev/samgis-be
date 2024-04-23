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
// modified from https://github.com/for-GET/know-your-http-well/blob/master/json/status-codes.json
export const htmlStatusMessages = [
  {
    code: 100,
    phrase: 'Continue'
  },
  {
    code: 101,
    phrase: 'Switching Protocols'
  },
  {
    code: 200,
    phrase: 'OK'
  },
  {
    code: 201,
    phrase: 'Created'
  },
  {
    code: 202,
    phrase: 'Accepted'
  },
  {
    code: 203,
    phrase: 'Non-Authoritative Information'
  },
  {
    code: 204,
    phrase: 'No Content'
  },
  {
    code: 205,
    phrase: 'Reset Content'
  },
  {
    code: 206,
    phrase: 'Partial Content'
  },
  {
    code: 300,
    phrase: 'Multiple Choices'
  },
  {
    code: 302,
    phrase: 'Found'
  },
  {
    code: 303,
    phrase: 'See Other'
  },
  {
    code: 304,
    phrase: 'Not Modified'
  },
  {
    code: 305,
    phrase: 'Use Proxy'
  },
  {
    code: 307,
    phrase: 'Temporary Redirect'
  },
  {
    code: 400,
    phrase: 'Bad Request'
  },
  {
    code: 401,
    phrase: 'Unauthorized'
  },
  {
    code: 402,
    phrase: 'Payment Required'
  },
  {
    code: 403,
    phrase: 'Forbidden'
  },
  {
    code: 404,
    phrase: 'Not Found'
  },
  {
    code: 405,
    phrase: 'Method Not Allowed'
  },
  {
    code: 406,
    phrase: 'Not Acceptable'
  },
  {
    code: 407,
    phrase: 'Proxy Authentication Required'
  },
  {
    code: 408,
    phrase: 'Request Timeout'
  },
  {
    code: 409,
    phrase: 'Conflict'
  },
  {
    code: 410,
    phrase: 'Gone'
  },
  {
    code: 411,
    phrase: 'Length Required'
  },
  {
    code: 412,
    phrase: 'Precondition Failed'
  },
  {
    code: 413,
    phrase: 'Payload Too Large'
  },
  {
    code: 414,
    phrase: 'URI Too Long'
  },
  {
    code: 415,
    phrase: 'Unsupported Media Type'
  },
  {
    code: 416,
    phrase: 'Range Not Satisfiable'
  },
  {
    code: 417,
    phrase: 'Expectation Failed'
  },
  {
    code: 418,
    phrase: "I'm a teapot"
  },
  {
    code: 426,
    phrase: 'Upgrade Required'
  },
  {
    code: 500,
    phrase: 'Internal Server Error'
  },
  {
    code: 501,
    phrase: 'Not Implemented'
  },
  {
    code: 502,
    phrase: 'Bad Gateway'
  },
  {
    code: 503,
    phrase: 'Service Unavailable'
  },
  {
    code: 504,
    phrase: 'Gateway Time-out'
  },
  {
    code: 505,
    phrase: 'HTTP Version Not Supported'
  },
  {
    code: 102,
    phrase: 'Processing'
  },
  {
    code: 207,
    phrase: 'Multi-Status'
  },
  {
    code: 226,
    phrase: 'IM Used'
  },
  {
    code: 308,
    phrase: 'Permanent Redirect'
  },
  {
    code: 422,
    phrase: 'Unprocessable Entity'
  },
  {
    code: 423,
    phrase: 'Locked'
  },
  {
    code: 424,
    phrase: 'Failed Dependency'
  },
  {
    code: 428,
    phrase: 'Precondition Required'
  },
  {
    code: 429,
    phrase: 'Too Many Requests'
  },
  {
    code: 431,
    phrase: 'Request Header Fields Too Large'
  },
  {
    code: 451,
    phrase: 'Unavailable For Legal Reasons'
  },
  {
    code: 506,
    phrase: 'Variant Also Negotiates'
  },
  {
    code: 507,
    phrase: 'Insufficient Storage'
  },
  {
    code: 511,
    phrase: 'Network Authentication Required'
  }
]
export const driverSteps = [
  { element: 'id-prediction-map-container', popover: { title: 'SamGIS', description: 'A quick tour about SamGIS functionality' } },
  { element: '#map', popover: { title: 'Webmap for ML prompt', description: 'Add here your machine learning prompt. Pay attention about markers and polygons outside the map bounds: you could get unexpected results' } },
  { element: '.leaflet-pm-icon-marker-include', popover: { title: '"Include" point prompt', description: 'add "include" points prompt (label 1) for machine learning request' } },
  { element: '.leaflet-pm-icon-marker-exclude', popover: { title: '"Exclude" point prompt', description: 'add "exclude" points prompt (label 0) for machine learning request' } },
  { element: '.leaflet-pm-icon-rectangle', popover: { title: '"Include" rectangle prompt', description: 'add "include" rectangles prompt for machine learning request' } },
  { element: "#id-button-submit", popover: { title: 'ML submit button', description: 'Machine learning submit button' } },
  { element: '.leaflet-control-layers-toggle', popover: { title: 'Map provider selector', description: 'select a different map provider' } },
  { element: '#id-map-info', popover: { title: 'map info', description: 'Section about various map info' } },
  { element: '#id-ml-request-prompt', popover: { title: 'ML prompt quest', description: 'Empty at beginning, this table will contain the machine learning prompt (points and rectangles) section' } }
]