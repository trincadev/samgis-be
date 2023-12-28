<template>
  <!-- style 'z-index: 1001' here is needed to avoid override from leafletjs css -->
  <footer class="fixed bottom-0 w-full bg-gray-200 pl-2 font-light text-xs" style="z-index: 9999;">
    <p>
      <span><PageFooterHyperlink path="/">SamGIS</PageFooterHyperlink>: An inference machine learning POC applied to GIS thanks to
        <PageFooterHyperlink path="https://github.com/vietanhdev/samexporter/">SAM Exporter</PageFooterHyperlink>
        and inspired by
        <PageFooterHyperlink path="https://samgeo.gishub.org/">Segment Geospatial</PageFooterHyperlink>
      </span>
    </p>
  </footer>
</template>

<script setup lang="ts">
import PageFooterHyperlink from "@/components/PageFooterHyperlink.vue";
</script>