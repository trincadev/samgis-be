<template>
  <table class="min-w-full divide-y-2 divide-gray-200 border border-gray-200 bg-white text-left p-4">
    <caption class="text-2xl bg-blue-100">{{ props.title }}</caption>
    <thead class="text-left">
    <tr class="text-left">
      <th
        class="whitespace-nowrap px-1 py-1 text-gray-900 text-left 2md:font-medium 2md:py-2 2md:px-4"
        v-for="item in props.header"
        :key="item"
      >{{ item }}</th>
    </tr>
    </thead>

    <tbody class="divide-y divide-gray-200" v-for="row in props.rows" :key="props.rows[props.rowKey]">
    <tr class="odd:bg-gray-50">
      <td v-for="item in row" class="whitespace-nowrap px-1 py-1 text-gray-900 2md:font-medium 2md:py-2 2md:px-4">{{ item }}</td>
    </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
const props = defineProps<{
  header: Array<string>,
  rows: Array<Map<string, string>>,
  title: string,
  rowKey: string
}>()
</script>

