<template>
<div :class="message.sender === 'assistant'?'bubble-left':'bubble-right'"><span v-html="message.text"/></div>
</template>

<script lang="ts" setup>
import type {Message} from "@/components/Chat.vue";

const props = defineProps<{message: Message}>()
</script>

<style scoped>

</style>
