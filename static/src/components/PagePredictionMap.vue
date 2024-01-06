<template>
  <div class="h-auto">

    <div class="grid grid-cols-1 2xl:grid-cols-5 lg:gap-1 lg:border-r ml-2 mt-2 md:ml-4 md:mr-4">

      <div class="lg:border-r lg:col-span-3">
        <div id="id-map-cont" class="">
          <p
            class="block lg:hidden"
            v-if="currentPathnameRef.startsWith(pathnameCheckRef)"
          >Trouble on page scrolling? Use the <a :href="embeddedSpaceRef">embedded space</a>.</p>
          <p class="hidden lg:block">{{ description }}</p>
          <div class="w-full md:pt-1 md:pb-1 lg:hidden portrait:xl:hidden">
            <ButtonMapSendRequest
              class="h-8 text-sm font-extralight min-w-[180px] max-w-[180px]"
              :current-base-map-name="currentBaseMapNameRef"
              :map="map"
              :prompts-array="promptsArrayRef"
              :response-message="responseMessageRef"
              :send-m-l-request="sendMLRequest"
              :waiting-string="waitingString"
            />
          </div>
          <div id="map" class="map-predictions" />
          <ButtonMapSendRequest
            class="h-8 min-w-[240px] max-w-[240px] mt-2 mb-2 hidden sd:h-14 lg:block portrait:xl:block"
            :current-base-map-name="currentBaseMapNameRef"
            :map="map"
            :prompts-array="promptsArrayRef"
            :response-message="responseMessageRef"
            :send-m-l-request="sendMLRequest"
            :waiting-string="waitingString"
          />

        </div>
      </div>

      <div class="lg:col-span-2">
        <div class="lg:pl-2 lg:pr-2 lg:border-l lg:border-3">

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

        <h1>ML request prompt</h1>
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
import { onMounted, ref, type Ref } from 'vue'

import {
  durationRef,
  numberOfPolygonsRef,
  numberOfPredictedMasksRef,
  OpenStreetMap,
  prefix,
  responseMessageRef,
  Satellite,
  waitingString
} from '@/components/constants'
import {
  applyFnToObjectWithinArray,
  getExtentCurrentViewMapBBox,
  getGeoJSONRequest,
  getSelectedPointCoordinate,
  setGeomanControls,
  updateMapData
} from '@/components/helpers'
import type { IBodyLatLngPoints, IPointPrompt, IRectanglePrompt, SourceTileType } from '@/components/types';
import StatsGrid from '@/components/StatsGrid.vue';
import TableGenericComponent from '@/components/TableGenericComponent.vue';
import ButtonMapSendRequest from '@/components/buttons/ButtonMapSendRequest.vue';

const currentBaseMapNameRef = ref("")
const currentMapBBoxRef = ref()
const currentZoomRef = ref()
const promptsArrayRef: Ref<Array<IPointPrompt | IRectanglePrompt>> = ref([])
const pathnameCheckRef = ref(import.meta.env.VITE__PATHNAME_CHECK || "")
const currentPathnameRef = ref("current-pathname-placeholder")
const embeddedSpaceRef = ref(import.meta.env.VITE__SAMGIS_SPACE || "")
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
  currentPathnameRef.value = window.location.pathname || ""
  const osmTile = tileLayer.provider(OpenStreetMap)
  let localVarSatellite: SourceTileType = import.meta.env.VITE_SATELLITE_NAME ? String(import.meta.env.VITE_SATELLITE_NAME) : Satellite
  const satelliteTile = tileLayer.provider(localVarSatellite)

  let baseMaps: ServiceTiles = { OpenStreetMap: osmTile }
  baseMaps[localVarSatellite] = satelliteTile
  currentBaseMapNameRef.value = OpenStreetMap

  map = LeafletMap('map', {
    layers: [osmTile]
  })
  map.fitBounds(props.mapBounds)
  map.attributionControl.setPrefix(prefix)
  LeafletControl.scale({ position: 'bottomleft', imperial: false, metric: true }).addTo(map)

  LeafletControl.layers(baseMaps).addTo(map)
  setGeomanControls(map)
  updateZoomBboxMap(map)

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
})
</script>

