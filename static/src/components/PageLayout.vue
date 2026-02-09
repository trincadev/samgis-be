<template>
  <div class="relative min-h-screen lg:flex" data-testid="page-layout">
    <!-- Menubar -->
    <NavBar class="hidden portrait:sd:hidden portrait:md:flex landscape:flex" style="z-index: 9999;"/>
    <MobileNavBar class="flex portrait:sd:flex portrait:md:hidden landscape:hidden" style="z-index: 9999;"/>

    <main id="content" class="flex-1 z-1 lg:ml-0 mr-4 overflow-y-auto md:pl-1 lg:h-screen">
      <header class="hidden items-center justify-between h-10 ml-2 landscape:md:flex portrait:sd:flex portrait:md:h-12 bg-gray-200 border-b" aria-label="Page header">
        <h2 class="hidden sd:text-sm ml-2 md:block md:text-2xl">{{  props.pageTitle }}</h2>
      </header>

      <div class="">
        <slot></slot>
      </div>

      <div class="bottom-0 w-full text-black">
        <Footer></Footer>
      </div>
    </main>
  </div>

</template>

<script setup lang="ts">
import Footer from "@/components/PageFooter.vue"
import NavBar from '@/components/NavBar/NavBar.vue'
import MobileNavBar from '@/components/NavBar/MobileNavBar.vue'

const props = defineProps<{
  pageTitle: string
}>()
</script>
