<template>
<div :class="message.sender === 'assistant'?'bubble-left':'bubble-right'"><span v-html="getHTML(message.text)"/></div>
</template>

<script lang="ts" setup>
import type {Message} from "@/components/Chat.vue";
import {marked} from "marked";

const props = defineProps<{message: Message}>()

function getHTML(markdown: string): string {
  return marked.parse(markdown, {mangle: false, headerIds: false}).split('<a').join('<a target="_blank"');
}
</script>

<style scoped>

</style>
