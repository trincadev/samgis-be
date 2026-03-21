<template>
  <button
    :class="`${props.class} bg-gray-200 bg-opacity-50`"
    :disabled="promptsArray.length === 0 || responseMessage === waitingString"
    v-if="promptsArray.length === 0 || responseMessage === waitingString"
    data-testid="submit-button-disabled"
    aria-disabled="true"
  >{{ responseMessage === waitingString ? responseMessage : '🚫 Empty prompt (disabled)' }}
  </button>
  <button
    :class="`${props.class} bg-blue-300 whitespace-no-wrap overflow-hidden truncate`"
    @click="sendMLRequest(map, promptsArray, currentBaseMapName)"
    v-else
    data-testid="submit-button"
    aria-label="Send ML request"
  >
    <span v-if="responseMessage && responseMessage !== '-'">{{ responseMessage }}</span>
    <span v-else>🔍 send ML request</span>
  </button>
</template>

<script setup lang="ts">
import {Map as LMap} from 'leaflet';
import type { IPointPrompt, IRectanglePrompt, SourceTileType } from '@/components/types'

const props = defineProps<{
  class: string,
  currentBaseMapName: string,
  promptsArray: Array<IPointPrompt | IRectanglePrompt>,
  responseMessage: string,
  map: LMap,
  sendMLRequest: (map: LMap, prompts: Array<IPointPrompt | IRectanglePrompt>, sourceType: SourceTileType) => Promise<void>,
  waitingString: string
}>()
</script>