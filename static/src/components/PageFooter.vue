<template>
  <!-- style 'z-index: 1001' here is needed to avoid override from leafletjs css -->
  <footer class="fixed bottom-0 w-full bg-gray-200 pl-4 font-light text-xs" style="z-index: 9999;" v-if="showFooterRef">
    <div class="relative flex">
      <div class="w-full">
        <p class="">Trouble on scrolling this page? Open the
          <PageFooterHyperlink path="https://aletrn-samgis.hf.space">direct URL space</PageFooterHyperlink>
          as a new tab.
        </p>
        <p class="">
          <span><PageFooterHyperlink path="/">SamGIS</PageFooterHyperlink>: An inference machine learning POC applied to GIS thanks to
            <PageFooterHyperlink path="https://github.com/vietanhdev/samexporter/">SAM Exporter</PageFooterHyperlink>
            and inspired by
            <PageFooterHyperlink path="https://samgeo.gishub.org/">Segment Geospatial</PageFooterHyperlink>
          </span>
        </p>
      </div>
      <div>
        <button
          aria-label="Close"
          class="shrink-0 rounded-lg bg-black/10 p-2 transition hover:bg-black/20"
          @click="showFooterRef = !showFooterRef"
        >x</button>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import PageFooterHyperlink from "@/components/PageFooterHyperlink.vue";

const showFooterRef = ref(true)
</script>