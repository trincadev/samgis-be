<template>
  <div class="h-auto" id="id-prediction-map-container">

    <div class="grid grid-cols-1 2xl:grid-cols-5 lg:gap-1 lg:border-r ml-2 mt-2 md:ml-4 md:mr-4">

      <div class="lg:border-r lg:col-span-3">
        <div id="id-map-cont" class="">
          <p class="hidden lg:block">{{ description }}</p>
          <div class="w-full md:pt-1 md:pb-1 lg:hidden portrait:xl:hidden">
            <ButtonMapSendRequest
              id="id-button-submit"
              class="h-8 text-sm font-extralight min-w-[180px] max-w-[180px]"
              :current-base-map-name="currentBaseMapNameRef"
              :map="map"
              :prompts-array="promptsArrayRef"
              :response-message="responseMessageRef"
              :send-m-l-request="sendMLRequest"
              :waiting-string="waitingString"
            />
            <span class="ml-2 lg:hidden">
              <input type="checkbox" id="checkboxMapNavigationLocked" v-model="mapNavigationLocked" />
              <span class="ml-2">
                  <label class="text-red-600" for="checkboxMapNavigationLocked" v-if="mapNavigationLocked">locked map navigation!</label>
                  <label class="text-blue-600" for="checkboxMapNavigationLocked" v-else>map navigation unlocked</label>
              </span>
            </span>
          </div>
          <div id="map" class="map-predictions" />
          <ButtonMapSendRequest
            class="h-8 min-w-[240px] max-w-[240px] mt-2 mb-2 hidden sd:h-14 lg:block portrait:xl:block"
            :current-base-map-name="currentBaseMapNameRef"
            id="id-button-submit"
            :map="map"
            :prompts-array="promptsArrayRef"
            :response-message="responseMessageRef"
            :send-m-l-request="sendMLRequest"
            :waiting-string="waitingString"
          />
          <span class="hidden lg:block lg:ml-2">
              <input type="checkbox" id="checkboxMapNavigationLocked" v-model="mapNavigationLocked" />
              <span class="ml-2">
                  <label class="text-red-600" for="checkboxMapNavigationLocked" v-if="mapNavigationLocked">locked map navigation!</label>
                  <label class="text-blue-600" for="checkboxMapNavigationLocked" v-else>map navigation unlocked</label>
              </span>
            </span>
        </div>
      </div>

      <div class="lg:col-span-2">
        <div class="lg:pl-2 lg:pr-2 lg:border-l lg:border-3" id="id-map-info">

          <h1>Map Info</h1>
          <div class="grid grid-cols-1 md:grid-cols-3">
            <StatsGrid :stats-array="[
              {statName: 'current Zoom', statValue: currentZoomRef},
              {statName: 'current map name/type', statValue: currentBaseMapNameRef},
              {statName: 'prompt: points/rectangles number', statValue: promptsArrayRef.length},
            ]" />
          </div>
          <div v-if="responseMessageRef === waitingString" />
          <h2 v-else-if="responseMessageRef || responseMessageRef == '-'" class="text-lg text-red-600">{{ responseMessageRef }}</h2>
          <div v-else>
            <div class="grid grid-cols-1 md:grid-cols-3">
              <StatsGrid :stats-array="[
                  {statName: 'request duration', statValue: `${durationRef.toFixed(2)}s`},
                  {statName: 'polygons number', statValue: numberOfPolygonsRef},
                  {statName: 'predicted masks number', statValue: numberOfPredictedMasksRef},
                ]" />
            </div>
          </div>
        </div>

        <h1 id="id-ml-request-prompt">ML request prompt</h1>
        <p>Exclude points: label 0, include points: label 1.</p>
        <div v-if="promptsArrayRef.filter(el => {return el.type === 'point'}).length > 0">
          <TableGenericComponent
            :header="['id', 'data', 'label']"
            :rows="applyFnToObjectWithinArray(promptsArrayRef.filter(el => {return el.type === 'point'}))"
            title="Points"
            row-key="id"
          />
        </div>
        <br />
        <div v-if="promptsArrayRef.filter(el => {return el.type === 'rectangle'}).length > 0">
          <TableGenericComponent
            :header="['id', 'data_ne', 'data_sw']"
            :rows="applyFnToObjectWithinArray(promptsArrayRef.filter(el => {return el.type === 'rectangle'}))"
            title="Rectangles"
            row-key="id"
            class="2md:min-h-[100px]"
          />
        </div>
      </div>

    </div>
  </div>
</template>

<script lang="ts" setup>
import {
  control as LeafletControl,
  Evented as LEvented,
  geoJSON as LeafletGeoJSON,
  type LatLng,
  Map as LMap,
  map as LeafletMap,
  tileLayer,
  TileLayer as LTileLayer
} from 'leaflet'
import 'leaflet-providers'
import '@geoman-io/leaflet-geoman-free'
import { onMounted, onUpdated, ref, type Ref } from 'vue'
import { driver } from "../../node_modules/driver.js/src/driver"

import {
  durationRef,
  maxZoom,
  minZoom,
  numberOfPolygonsRef,
  numberOfPredictedMasksRef,
  OpenStreetMap,
  prefix,
  responseMessageRef,
  Satellite,
  waitingString
} from './constants'
import {
  applyFnToObjectWithinArray,
  getExtentCurrentViewMapBBox,
  getGeoJSONRequest,
  getQueryParams,
  getSelectedPointCoordinate,
  setGeomanControls,
  updateMapData
} from '@/components/helpers'
import type { IBodyLatLngPoints, IPointPrompt, IRectanglePrompt, SourceTileType } from '@/components/types';
import StatsGrid from '@/components/StatsGrid.vue';
import TableGenericComponent from '@/components/TableGenericComponent.vue';
import ButtonMapSendRequest from '@/components/buttons/ButtonMapSendRequest.vue';

const driverObj = driver({
  showProgress: true,
  steps: [
    { element: 'id-prediction-map-container', popover: { title: 'SamGIS', description: 'A quick tour about SamGIS functionality' } },
    { element: '#map', popover: { title: 'Webmap for ML prompt', description: 'Add here your machine learning prompt' } },
    { element: '.leaflet-pm-icon-marker-include', popover: { title: '"Include" point prompt', description: 'add "include" points prompt (label 1) for machine learning request' } },
    { element: '.leaflet-pm-icon-marker-exclude', popover: { title: '"Exclude" point prompt', description: 'add "exclude" points prompt (label 0) for machine learning request' } },
    { element: '.leaflet-pm-icon-rectangle', popover: { title: '"Include" rectangle prompt', description: 'add "include" rectangles prompt for machine learning request' } },
    { element: "#id-button-submit", popover: { title: 'ML submit button', description: 'Machine learning submit button' } },
    { element: '.leaflet-control-layers-toggle', popover: { title: 'Map provider selector', description: 'select a different map provider' } },
    { element: '#id-map-info', popover: { title: 'map info', description: 'Section about various map info' } },
    { element: '#id-ml-request-prompt', popover: { title: 'ML prompt quest', description: 'Empty at beginning, this table will contain the machine learning prompt (points and rectangles) section' } }
  ]
});

const currentBaseMapNameRef = ref("")
const currentMapBBoxRef = ref()
const currentZoomRef = ref()
const promptsArrayRef: Ref<Array<IPointPrompt | IRectanglePrompt>> = ref([])
const mapNavigationLocked = ref(false)
const mapOptionsDefaultRef = ref()
let map: LMap
type ServiceTiles = {
  [key: SourceTileType]: LTileLayer;
};

const props = defineProps<{
  mapBounds: Array<LatLng>,
  mapName: string,
  description: string
}>()

const getPopupContentPoint = (leafletEvent: LEvented, label: number): HTMLDivElement => {
  let popupContent: HTMLDivElement = document.createElement('div')
  let currentPointLayer: LatLng = getSelectedPointCoordinate(leafletEvent)

  popupContent.innerHTML = `<span>lat:${JSON.stringify(currentPointLayer.lat)}<br/>`
  popupContent.innerHTML += `lng:${JSON.stringify(currentPointLayer.lng)}<br/>`
  popupContent.innerHTML += `label:${label}, id:${leafletEvent.layer._leaflet_id}</span>`

  const popupDiv: HTMLDivElement = document.createElement('div')
  popupDiv.className = 'leaflet-popup-content-inner'
  popupDiv.appendChild(popupContent)

  return popupDiv
}

const sendMLRequest = async (leafletMap: LMap, promptRequest: Array<IPointPrompt | IRectanglePrompt>, sourceType: SourceTileType = OpenStreetMap) => {
  if (map.pm.globalDragModeEnabled()) {
    map.pm.disableGlobalDragMode()
  }
  if (map.pm.globalEditModeEnabled()) {
    map.pm.disableGlobalEditMode()
  }
  mapNavigationLocked.value = true
  const bodyRequest: IBodyLatLngPoints = {
    bbox: getExtentCurrentViewMapBBox(leafletMap),
    prompt: promptRequest,
    zoom: leafletMap.getZoom(),
    source_type: sourceType
  }
  try {
    const geojsonOutputOnMounted = await getGeoJSONRequest(bodyRequest, '/infer_samgis')
    const featureNew = LeafletGeoJSON(geojsonOutputOnMounted)
    leafletMap.addLayer(featureNew)
  } catch (errGeojsonOutputOnMounted) {
    console.error('sendMLRequest:: sourceType: ', sourceType)
    console.error('sendMLRequest:: promptRequest: ', promptRequest.length, '::', promptRequest)
    console.error('sendMLRequest:: bodyRequest => ', bodyRequest, "#")
    console.error("errGeojsonOutputOnMounted => ", errGeojsonOutputOnMounted)
  }
}

const updateZoomBboxMap = (localMap: LMap) => {
  currentZoomRef.value = localMap.getZoom()
  currentMapBBoxRef.value = getExtentCurrentViewMapBBox(localMap)
}

const getCurrentBasemap = (url: string, providersArray: ServiceTiles) => {
  for (const [key, value] of Object.entries(providersArray)) {
    if (value._url == url) {
      return key
    }
  }
}

onMounted(async () => {
  const osmTile = tileLayer.provider(OpenStreetMap)
  const params = getQueryParams()
  let localVarSatellite: SourceTileType = params.source ? params.source : Satellite
  let localVarSatelliteOptions = params.options ? params.options : {}
  const satelliteTile = tileLayer.provider(localVarSatellite, localVarSatelliteOptions)
  let localVarTerrain: SourceTileType = "nextzen.terrarium"
  const terrainTile = new LTileLayer(
      "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png", {
        id: localVarTerrain,
        attribution: "<a href='https://nextzen.org'>nextzen</a>," +
            "<a href='https://registry.opendata.aws/terrain-tiles/'>Mapzen Terrain Tiles - AWS opendata registry</a>," +
            "<a href='https://github.com/tilezen/joerd/blob/master/docs/attribution.md'>Mapzen Source Attributions</a>."
      }
  )
  let baseMaps: ServiceTiles = { OpenStreetMap: osmTile }
  baseMaps[localVarSatellite] = satelliteTile
  baseMaps[localVarTerrain] = terrainTile
  currentBaseMapNameRef.value = OpenStreetMap

  map = LeafletMap('map', {
    layers: [osmTile],
    minZoom: minZoom,
    maxZoom: maxZoom
  })
  map.fitBounds(props.mapBounds)
  map.attributionControl.setPrefix(prefix)
  LeafletControl.scale({ position: 'bottomleft', imperial: false, metric: true }).addTo(map)

  LeafletControl.layers(baseMaps).addTo(map)
  setGeomanControls(map)
  updateZoomBboxMap(map)
  mapOptionsDefaultRef.value = {...map.options}

  map.on('zoomend', (e: LEvented) => {
    updateZoomBboxMap(map)
  })

  map.on('mouseup', (e: LEvented) => {
    currentMapBBoxRef.value = getExtentCurrentViewMapBBox(map)
  })

  updateMapData(map, getPopupContentPoint, promptsArrayRef)
  map.on('baselayerchange', (e: LEvented) => {
    currentBaseMapNameRef.value = getCurrentBasemap(e.layer._url, baseMaps)
  })

  driverObj.drive();
})

onUpdated(() => {
  if (mapNavigationLocked.value) {
    map.setMaxZoom(currentZoomRef.value)
    map.setMinZoom(currentZoomRef.value)
    map.options.maxBoundsViscosity = 1.0
    map.setMaxBounds(map.getBounds())
  }
  if (!mapNavigationLocked.value) {
    map.setMaxZoom(maxZoom)
    map.setMinZoom(minZoom)
    map.options.maxBoundsViscosity = 0.0
    map.setMaxBounds([
      [90, 180],
      [-90, -180]
    ])
  }
})
</script>

