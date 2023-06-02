<script setup lang="ts">
import Chat from "@/components/Chat.vue";
import {computed} from "vue";

const host = computed(()=>window.location.hostname)
</script>

<template>
<chat :websocket_url="`ws://localhost:8765`"/>
<!--<chat :websocket_url="`ws://${host}:8765`"/>-->
</template>

<style scoped>

</style>
