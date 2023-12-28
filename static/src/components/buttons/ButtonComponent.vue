<template>
  <button class="inline-flex items-center p-2" @click="props.click">
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
const props = defineProps<{
  click: Function
}>()
</script>