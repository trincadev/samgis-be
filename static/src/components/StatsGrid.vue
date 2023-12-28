<template>
  <dl class="grid md:pt-1 md:pb-1" v-for="item in props.statsArray" v-bind:key="item.statName">
    <div class="flex flex-col bg-blue-100 text-center p-1 md:p-2">
      <dt class="order-last font-medium">{{ item.statName }}</dt>
      <dd class="text-lg font-extrabold text-blue-600">{{ item.statValue }}</dd>
    </div>
  </dl>
</template>

<script setup lang="ts">
const props = defineProps<{
  statsArray: Array<{
    statName: string,
    statValue: string
  }>
}>()
</script>