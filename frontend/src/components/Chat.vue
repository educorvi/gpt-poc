<template>
  <div id="banner">Gesamtkosten dieser Unterhaltung: {{ Math.round((usage.cost || 0) * 100) / 100 }}$</div>
  <div id="messages">
    <chat-bubble v-for="message in messages" :message="message"></chat-bubble>
    <!--    <div class="bubble-left" v-if="!connected" style="padding: calc(2 * var(&#45;&#45;r) / 3)">-->
    <!--      &lt;!&ndash;      <pixel-spinner&ndash;&gt;-->
    <!--      &lt;!&ndash;          :animation-duration="2000"&ndash;&gt;-->
    <!--      &lt;!&ndash;          :size="22"&ndash;&gt;-->
    <!--      &lt;!&ndash;          color="#0d6efd"&ndash;&gt;-->
    <!--      &lt;!&ndash;      />&ndash;&gt;-->
    <!--      <div class="hollow-dots-spinner">-->
    <!--        <div class="dot"></div>-->
    <!--        <div class="dot"></div>-->
    <!--        <div class="dot"></div>-->
    <!--      </div>-->
    <!--    </div>-->
    <div class="bubble-left" v-if="state!=='done'" style="padding: calc(2 * var(--r) / 3)">
      <div class="status">
        <!--       <pixel-spinner-->
        <!--           v-if="state==='searching'"-->
        <!--           class="status-icon"-->
        <!--           :animation-duration="2000"-->
        <!--           :size="22"-->
        <!--           color="#0d6efd"-->
        <!--       />-->
        <div class="hollow-dots-spinner status-icon" v-if="state==='searching'">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        <span v-else style="color: green;height: 22px; width: 22px; text-align: center"
              class="status-icon">&#10004;</span>
        Suchen nach relevanten Informationen
      </div>
      <div class="status">
        <!--       <pixel-spinner-->
        <!--           class="status-icon"-->
        <!--           :animation-duration="state==='searching'?0:2000"-->
        <!--           :size="22"-->
        <!--           color="#0d6efd"-->
        <!--       />-->
        <div class="hollow-dots-spinner status-icon">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
        Antwort formulieren
      </div>
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

messages.value.push({sender: "assistant", text: `Verbindung wird aufgebaut...`})


const socket = new WebSocket(props.websocket_url);
socket.addEventListener("open", () => {
  messages.value.push({sender: "assistant", text: `Verbindung hergestellt zu ${props.websocket_url}`})
  connected.value = true
});

function addMessage(message: string) {
  messages.value.push({sender: "assistant", text: message});
  nextTick(() => {
    document.getElementById("send_input")?.focus();
    const messages = document.getElementById("messages");
    if (messages) {
      messages.scrollTop = messages.scrollHeight;
    }
  });
}

socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  console.debug(message)
  switch (message.type) {
    case "message":
      state.value = "done";
      addMessage(message.content)
      break;
    case "usage":
      usage.value = message.content;
      break;
    case "event":
      switch (message.content.event) {
        case "tool_end":
          state.value = "writing";
          break;
        case "agent_action":
          addMessage(`Starte ${message.content.data.tool} mit Input '<i>${message.content.data.tool_input}</i>'`)
          break;
        case "llm_error":
        case "chain_error":
        case "tool_error":
          console.error(message.content.data)
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
  align-items: center;

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
  z-index: 2;
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

$size: 22px;

.pixel-spinner, .pixel-spinner * {
  box-sizing: border-box;
}

.pixel-spinner {
  height: 70px;
  width: 70px;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}

.pixel-spinner .pixel-spinner-inner {
  width: calc(70px / 7);
  height: calc(70px / 7);
  background-color: #0d6efd;
  color: #0d6efd;
  box-shadow: 15px 15px 0 0,
  -15px -15px 0 0,
  15px -15px 0 0,
  -15px 15px 0 0,
  0 15px 0 0,
  15px 0 0 0,
  -15px 0 0 0,
  0 -15px 0 0;
  animation: pixel-spinner-animation 2000ms linear infinite;
}

@keyframes pixel-spinner-animation {
  50% {
    box-shadow: 20px 20px 0px 0px,
    -20px -20px 0px 0px,
    20px -20px 0px 0px,
    -20px 20px 0px 0px,
    0px 10px 0px 0px,
    10px 0px 0px 0px,
    -10px 0px 0px 0px,
    0px -10px 0px 0px;
  }
  75% {
    box-shadow: 20px 20px 0px 0px,
    -20px -20px 0px 0px,
    20px -20px 0px 0px,
    -20px 20px 0px 0px,
    0px 10px 0px 0px,
    10px 0px 0px 0px,
    -10px 0px 0px 0px,
    0px -10px 0px 0px;
  }
  100% {
    transform: rotate(360deg);
  }
}

.hollow-dots-spinner, .hollow-dots-spinner * {
  box-sizing: border-box;
}

.hollow-dots-spinner {
  height: 5px;
  width: calc(10px * 3);
}

.hollow-dots-spinner .dot {
  width: 5px;
  height: 5px;
  margin: 0 calc(5px / 2);
  border: calc(5px / 5) solid #0d6efd;
  border-radius: 50%;
  float: left;
  transform: scale(0);
  animation: hollow-dots-spinner-animation 1000ms ease infinite 0ms;
}

.hollow-dots-spinner .dot:nth-child(1) {
  animation-delay: calc(300ms * 1);
}

.hollow-dots-spinner .dot:nth-child(2) {
  animation-delay: calc(300ms * 2);
}

.hollow-dots-spinner .dot:nth-child(3) {
  animation-delay: calc(300ms * 3);

}

@keyframes hollow-dots-spinner-animation {
  50% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}
</style>
