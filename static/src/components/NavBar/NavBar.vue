<template>
  <nav class="fixed top-2 right-5 mr-2 items-center" data-testid="navbar" aria-label="Main navigation">
    <TabComponent description="About SamGIS" href="https://trinca.tornidor.com/projects/samgis-segment-anything-applied-to-GIS" />
    <TabComponent description="My blog" href="https://trinca.tornidor.com/" />
    <TabComponent description="SamGIS docs" href="https://docs.ml-trinca.tornidor.com/" />
  </nav>
</template>

<script setup lang="ts">

import TabComponent from '@/components/NavBar/TabComponent.vue'
</script>
