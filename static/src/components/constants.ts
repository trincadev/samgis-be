import { ref } from "vue"

export const prefix = " &copy; <a target=\"_blank\" href=\"https://leafletjs.com\">leaflet</a>"
export const OpenStreetMap = "OpenStreetMap"
export const Satellite = "OpenStreetMap.HOT"
export const maxZoom = 20
export const minZoom = 3
export const waitingString = "waiting..."
export const durationRef = ref(0)
export const numberOfPolygonsRef = ref(0)
export const numberOfPredictedMasksRef = ref(0)
export const responseMessageRef = ref("-")
export const geojsonRef = ref("geojsonOutput-placeholder")
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
