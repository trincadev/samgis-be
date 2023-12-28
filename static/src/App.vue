<template>
  <PageLayout page-title="Prediction map page">
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
            description="This page displays predictions made with a remote machine learning model living within an AWS Lambda..."
        />
      </div>
    </div>
  </PageLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import PredictionMap from '@/components/PagePredictionMap.vue'
import PageLayout from '@/components/PageLayout.vue'

const mapName = ref('prediction-map')
</script>
