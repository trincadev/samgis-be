<template>
  <PageLayout pageTitle="SamGIS - Inference map page">
    <div>
      <div id="map-container-md">
        <PredictionMap
            :mapName="mapName"
            :mapBounds='[{
                    "lat": 46.235421781941776,
                    "lng": 9.49699401855469
                }, {
                    "lat": 46.1351347810282,
                    "lng": 9.32121276855469
              }]'
            :description=description
        />
      </div>
    </div>
  </PageLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import PredictionMap from '@/components/PagePredictionMap.vue'
import PageLayout from '@/components/PageLayout.vue'

const mapName = ref('prediction-map')
const description = ref("This page displays predictions made with a machine learning model")

onMounted(() => {
  console.log("descr:", description.value, import.meta.env.VITE__MAP_DESCRIPTION)
  description.value = import.meta.env.VITE__MAP_DESCRIPTION ? import.meta.env.VITE__MAP_DESCRIPTION : description.value
})
</script>
