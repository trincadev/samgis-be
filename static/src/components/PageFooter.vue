<template>
  <!-- style 'z-index: 1001' here is needed to avoid override from leafletjs css -->
  <footer class="fixed bottom-0 w-full pl-4 font-light text-xs" style="z-index: 9999;" v-if="showFooterRef" data-testid="page-footer">
    <div class="relative flex items-center bg-gray-200 h-6">
      <div class="pl-1 w-full">
        <p class="">
          <span>Trouble on scrolling this page? Open the
          <PageFooterHyperlink path="https://aletrn-samgis.hf.space">direct URL space</PageFooterHyperlink>
          as a new tab. </span>
          <span><PageFooterHyperlink path="/">SamGIS</PageFooterHyperlink>: An inference machine learning POC applied to GIS thanks to
            <PageFooterHyperlink path="https://github.com/vietanhdev/samexporter/">SAM Exporter</PageFooterHyperlink>
            and inspired by
            <PageFooterHyperlink path="https://samgeo.gishub.org/">Segment Geospatial</PageFooterHyperlink>
          </span>
        </p>
      </div>
      <div class="pr-2">
        <button
          aria-label="Close"
          data-testid="footer-close-button"
          class="shrink-0 rounded-lg bg-black/10 p-1 transition hover:bg-black/20"
          @click="showFooterRef = !showFooterRef"
        >Close</button>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import {ref} from 'vue'
import PageFooterHyperlink from "@/components/PageFooterHyperlink.vue";

const showFooterRef = ref(true)
</script>