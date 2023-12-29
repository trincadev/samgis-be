<template>
  <h2>
    <a :href="props.href"
      class="bg-white border-2 no-underline pl-2 pr-2 p-1
      landscape:border-gray-300 landscape:font-semibold landscape:text-lg"
    >{{ props.description }}</a>
  </h2>
</template>

<script setup lang="ts">
const props = defineProps<{
  href: string,
  description: string,
}>()
</script>