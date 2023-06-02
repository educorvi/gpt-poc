import {defineCustomElement} from 'vue';
import Chat from "@/components/Chat.vue";

const simple_websocket_chat = defineCustomElement(Chat);

customElements.define('simple-websocket-chat', simple_websocket_chat);
