import L, { icon, Evented as LEvented, type LatLng, Map as LMap } from 'leaflet'
import {
  responseMessageRef,
  waitingString,
  durationRef,
  numberOfPolygonsRef,
  numberOfPredictedMasksRef
} from './constants'
import {
  ExcludeIncludeLabelPrompt as excludeIncludeLabelPrompt,
  type ArrayNumber,
  type BboxLatLng,
  type ExcludeIncludeLabelPrompt,
  type IBodyLatLngPoints,
  type IPointPrompt,
  type IRectanglePrompt, type IRectangleTable, type IPointTable
} from './types.d'
import type { Ref } from 'vue'


export const applyFnToObjectWithinArray = (array: Array<IPointPrompt | IRectanglePrompt>): Array<IPointTable | IRectangleTable> => {
  let newArray = []
  for (const el of array) {
    newArray.push(el.type === 'rectangle' ? getUpdatedRectangle(el) : getUpdatedPoint(el))
  }
  return newArray
}

const getUpdatedPoint = (obj: IPointPrompt): IPointTable => {
  return {
    id: obj.id,
    data: obj.data,
    label: obj.label
  }
}

const getUpdatedRectangle = (obj: IRectanglePrompt): IRectangleTable => {
  return {
    id: obj.id,
    data_ne: obj.data.ne,
    data_sw: obj.data.sw,
  }
}

/** get a custom icon given a PNG path with its anchor/size values  */
const getCustomIconMarker = (
  iconUrlNoExt: string,
  shadowUrl = '/marker-shadow.png',
  iconSize: ArrayNumber = [25, 41],
  iconAnchor: ArrayNumber = [12, 41],
  popupAnchor: ArrayNumber = [1, -34],
  tooltipAnchor: ArrayNumber = [5, -25],
  shadowSize: ArrayNumber = [41, 41]
): icon => {
  return icon({
    iconUrl: `${iconUrlNoExt}.png`,
    iconRetinaUrl: `${iconUrlNoExt}-2x.png`,
    shadowUrl,
    iconSize,
    iconAnchor,
    popupAnchor,
    shadowSize,
    tooltipAnchor
  })
}

/** get an  the leaflet editor geoman.io toolbar with the custom actions to draw/edit/move point and rectangle layers */
const getCustomGeomanActionsObject = (
  actionName: string, descriptionAction: string, arrayActions: Array<object>, customClassName: string
) => {
  return {
    name: actionName,
    block: 'custom',
    className: customClassName,
    title: descriptionAction,
    actions: arrayActions
  }
}

/** prepare the leaflet editor geoman.io toolbar with the custom actions to draw/edit/move point and rectangle layers */
export function setGeomanControls(localMap: LMap) {
  // leaflet geoman toolbar
  localMap.pm.addControls({
    position: 'topleft',
    drawControls: false,
    rotateMode: false,
    cutPolygon: false,
    customControls: true
  })

  const actionArray = [{
      onClick(actionEvent: LEvented) {
        console.log('actionEvent:', typeof actionEvent, '|', actionEvent, '')
      },
      name: 'actionName'
  }]
  const includeMarkerControl = localMap.pm.Toolbar.copyDrawControl('Marker',
    getCustomGeomanActionsObject(
      'IncludeMarkerPrompt',
      'Marker point that add recognition regions from SAM prompt requests',
      actionArray,
      'control-icon leaflet-pm-icon-marker-include'
    )
  )
  // custom marker icon on map
  includeMarkerControl.drawInstance.setOptions({
    markerStyle: { icon: getCustomIconMarker('/marker-icon-include') }
  })
  const excludeMarkerControl = localMap.pm.Toolbar.copyDrawControl('Marker',
    getCustomGeomanActionsObject(
      'ExcludeMarkerPrompt',
      'Marker point that remove recognition regions from SAM prompt requests',
      actionArray,
      'control-icon leaflet-pm-icon-marker-exclude'
    )
  )
  excludeMarkerControl.drawInstance.setOptions({
    markerStyle: { icon: getCustomIconMarker('/marker-icon-exclude') }
  })
  localMap.pm.Toolbar.copyDrawControl('Rectangle', {
    actions: actionArray,
    block: 'custom',
    name: 'RectanglePrompt',
    title: 'Rectangular recognition regions for SAM prompt requests'
  })
  localMap.pm.setPathOptions({
    color: "green",
    fillColor: "green",
    fillOpacity: 0.15,
  })
}

/** get the selected rectangle layer bounding box coordinate */
export const getSelectedRectangleCoordinatesBBox = (leafletEvent: LEvented): BboxLatLng => {
  const { _northEast, _southWest } = leafletEvent.layer._bounds
  return {
    ne: new L.LatLng(_northEast.lat, _northEast.lng),
    sw: new L.LatLng(_southWest.lat, _southWest.lng)
  }
}

/** get the current selected point coordinate */
export const getSelectedPointCoordinate = (leafletEvent: LEvented): LatLng => {
  return leafletEvent.layer._latlng
}

/** get the current map bounding box coordinates */
export const getExtentCurrentViewMapBBox = (leafletMap: LMap): BboxLatLng => {
  const boundaries = leafletMap.getBounds()
  return { ne: boundaries.getNorthEast(), sw: boundaries.getSouthWest() }
}

/** send the ML request to the backend API through the cloudflare proxy function */
export const getGeoJSONRequest = async (
  requestBody: IBodyLatLngPoints,
  urlApi: string
) => {
  responseMessageRef.value = waitingString
  const data = await fetch(urlApi, {
    method: 'POST',
    body: JSON.stringify(requestBody),
    headers: {
      'Content-type': 'application/json'
    }
  })
  try {
    if (data.status === 200) {
      const output: Object = await data.json()
      try {
        const parsed = JSON.parse(output.body)
        const { geojson, n_predictions, n_shapes_geojson } = parsed.output

        const parsedGeojson = JSON.parse(geojson)
      durationRef.value = parsed.duration_run
        numberOfPolygonsRef.value = n_shapes_geojson
        numberOfPredictedMasksRef.value = n_predictions
      responseMessageRef.value = ''
        return parsedGeojson
      } catch (errParseOutput1) {
        console.error("errParseOutput1::", errParseOutput1)
        return String(errParseOutput1)
      }
    } else {
      const outputText = await data.text()
      console.error('getGeoJSONRequest => status not 200, outputText', outputText, '#')
      responseMessageRef.value = `error message response: ${outputText}...`
    }
  } catch (errorOtherData) {
    const statusText = data.statusText || 'no response or uncaught exception!'
    console.error(
      'getGeoJSONRequest => data',
      data,
      'statusText',
      statusText,
      'errorOtherData',
      errorOtherData,
      '#'
    )
    responseMessageRef.value = `error status response: ${statusText}...`
  }
}

/** populate a single point ML request prompt, by type (exclude or include), see type ExcludeIncludeLabelPrompt */
export const getPointPromptElement = (e: LEvented, elementType: ExcludeIncludeLabelPrompt): IPointPrompt|IRectanglePrompt => {
  const currentPointLayer: LatLng = getSelectedPointCoordinate(e)
  return {
    id: e.layer._leaflet_id,
    type: 'point',
    data: currentPointLayer,
    label: elementType
  }
}

/** populate a single rectangle ML request prompt */
export const getRectanglePromptElement = (e: LEvented) => {
  return {
    id: e.layer._leaflet_id,
    type: 'rectangle',
    data: getSelectedRectangleCoordinatesBBox(e)
  }
}

/** handle different event/layer types (rectangle, point: IncludeMarkerPrompt, ExcludeMarkerPrompt) */
const updateLayerOnCreateOrEditEvent = (
  event: LEvented,
  getPopupContentPointFn: (arg0: LEvented, arg1: number) => HTMLDivElement,
  promptsArrayRef: Ref) => {
  responseMessageRef.value = '-'
  if (event.shape === 'IncludeMarkerPrompt' || event.shape === 'ExcludeMarkerPrompt') {
    const labelPoint = Number(excludeIncludeLabelPrompt[event.shape])
    const div = getPopupContentPointFn(event, labelPoint)
    event.layer.bindPopup(div).openPopup()
    promptsArrayRef.value.push(getPointPromptElement(event, labelPoint))
  }
  if (event.shape === 'RectanglePrompt') {
    event.layer.bindPopup(`id:${event.layer._leaflet_id}.`).openPopup()
    promptsArrayRef.value.push(getRectanglePromptElement(event))
  }
}

/** listen on the leaflet editor geoman.io events and update its layer properties within the promptsArrayRef vue ref */
export const updateMapData = (
  localMap: LMap,
  getPopupContentPointFn: (arg0: LEvented, arg1: number) => HTMLDivElement,
  promptsArrayRef: Ref
) => {
  localMap.on('pm:create', (e: LEvented) => {
    updateLayerOnCreateOrEditEvent(e, getPopupContentPointFn, promptsArrayRef)

    // listen to changes on the new layer and update its object within promptsArrayRef
    e.layer.on('pm:edit', function(newEvent: LEvented) {
      promptsArrayRef.value = removeEventFromArrayByIndex(promptsArrayRef.value, newEvent)
      updateLayerOnCreateOrEditEvent(e, getPopupContentPointFn, promptsArrayRef)
    });
  })
  localMap.on('pm:remove', (e: LEvented) => {
    responseMessageRef.value = '-'
    promptsArrayRef.value = removeEventFromArrayByIndex(promptsArrayRef.value, e)
  })
}

/** remove the selected layer from the ML request array prompt */
const removeEventFromArrayByIndex = (arr: Array<LEvented>, e: LEvented) => {
  return arr.filter((el: LEvented) => {
    return el.id != e.layer._leaflet_id
  })
}
