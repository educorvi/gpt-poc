<template>
  <div id="banner">Cost of this conversation: {{ Math.round((usage.cost || 0) * 100) / 100 }}$</div>
  <div id="messages">
    <chat-bubble v-for="message in messages" :message="message"></chat-bubble>
    <div class="bubble-left" v-if="!connected" style="padding: calc(2 * var(--r) / 3)">
      <pixel-spinner
          :animation-duration="2000"
          :size="22"
          color="#0d6efd"
      />
    </div>
    <div class="bubble-left" v-if="state!=='done'" style="padding: calc(2 * var(--r) / 3)">
     <span class="status">
       <pixel-spinner
           v-if="state==='searching'"
           class="status-icon"
           :animation-duration="2000"
           :size="22"
           color="#0d6efd"
       />
       <span v-else style="color: green;height: 22px; width: 22px; text-align: center"
             class="status-icon">&#10004;</span>
     Suchen nach relevanten Informationen
     </span>
      <span class="status">
       <pixel-spinner
           class="status-icon"
           :animation-duration="state==='searching'?0:2000"
           :size="22"
           color="#0d6efd"
       />
     Antwort formulieren
     </span>
    </div>
  </div>
  <div>
    <form id="send_div" @submit="sendMessage">
      <input id="send_input" v-on:keyup.enter="" v-model="input_message" class="form-control"
             :disabled="state!=='done' || !connected" minlength="8" required/>
      <input type="submit" class="btn btn-primary" :disabled="state!=='done' || !connected"/>
    </form>
  </div>
</template>

<script setup lang="ts">
import {nextTick, ref} from "vue";
import ChatBubble from "@/components/ChatBubble.vue";
import {PixelSpinner} from 'epic-spinners';

export type Message = {
  sender: "user" | "assistant",
  text: string
}

const props = defineProps<{
  websocket_url: string
}>()

const connected = ref(false);
const state = ref<"searching" | "writing" | "done">("done");

const input_message = ref("");

const usage = ref<Record<string, any>>({})

const messages = ref<Message[]>([])

messages.value.push({sender: "assistant", text: `Connecting...`})


const socket = new WebSocket(props.websocket_url);
socket.addEventListener("open", () => {
  messages.value.push({sender: "assistant", text: `Connected to ${props.websocket_url}`})
  connected.value = true
});
socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  console.debug(message)
  switch (message.type) {
    case "message":
      state.value = "done";
      messages.value.push({sender: "assistant", text: message.content});
      nextTick(() => {
        document.getElementById("send_input")?.focus();
        const messages = document.getElementById("messages");
        if (messages) {
          messages.scrollTop = messages.scrollHeight;
        }
      });
      break;
    case "usage":
      usage.value = message.content;
      break;
    case "event":
      switch (message.content.event) {
        case "tool_end":
          state.value = "writing";
          break;
        default:
          break;
      }
      break;
    default:
      break;
  }
});
socket.addEventListener("error", console.error);

function sendMessage(event: Event) {
  event.preventDefault();
  state.value = "searching";
  messages.value.push({sender: "user", text: input_message.value});
  socket.send(input_message.value)
  input_message.value = "";
  nextTick(() => {
    const messages = document.getElementById("messages");
    if (messages) {
      messages.scrollTop = messages.scrollHeight;
    }
  });
}
</script>

<style lang="scss">
@import "../assets/bubble";
@import "../assets/bootstrap";

.status {
  display: flex;

  .status-icon {
    margin-right: 10px;
  }
}

#banner {
  position: absolute;
  width: 100%;
  text-align: center;
  background-color: $primary;
  color: $light;
  height: 1.5em;
  z-index: 1000;
  font-size: 1em;
}

#send_div {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  display: -webkit-flex;
  height: 40px;

  input {
    -webkit-flex: 1;
    border-radius: 0;
  }

  input[type="submit"] {
    -webkit-flex: 0;
    border-radius: 0;
    width: min-content;
  }
}

#messages {
  //width: 100%;
  display: grid;
  max-height: 100%;
  height: 100%;
  padding: 2em 10px 40px 10px;
  box-sizing: border-box;
  align-content: flex-start;
  overflow-y: scroll;
  overflow-x: hidden;
  z-index: 0;
}
</style>
