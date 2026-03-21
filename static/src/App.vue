<template>
  <PageLayout pageTitle="SamGIS - Inference map page">
    <div>
      <div id="map-container-md">
        <PredictionMap
            :mapName="mapName"
            :mapBounds='[{
                    "lat": 46.235421781941776,
                    "lng": 9.47699401855469
                }, {
                    "lat": 46.1351347810282,
                    "lng": 9.30121276855469
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
const modelVariant = import.meta.env.VITE__MODEL_VARIANT || ""
const modelDescription = modelVariant
  ? `ML predictions powered by ${modelVariant}`
  : "This page displays predictions made with a machine learning model"
const description = ref(modelDescription)

onMounted(() => {
  const mapDescription = import.meta.env.VITE__MAP_DESCRIPTION || ""
  if (mapDescription) {
    description.value = `${mapDescription} ${description.value}`
  }
})
</script>
