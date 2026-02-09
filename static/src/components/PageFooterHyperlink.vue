<template>
  <a
    :href="props.path"
    class="underline"
    target="_blank"
    rel="noopener noreferrer"
    :data-testid="`footer-link-${props.path.replace(/https?:\/\//, '').replace(/[^a-z0-9]+/gi, '-').replace(/-$/, '').toLowerCase()}`"
  >
    <slot />
  </a>
</template>

<script setup lang="ts">
const props = defineProps<{
  path: string
}>()
</script>
