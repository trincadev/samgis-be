<template>
  <a
    :href="props.path"
    class="underline"
    target="_blank"
    rel="noopener noreferrer"
  >
    <slot />
  </a>
</template>

<script setup lang="ts">
const props = defineProps<{
  path: string
}>()
</script>
