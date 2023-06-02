<template>
    <div id="messages">
        <chat-bubble v-for="message in messages" :message="message"></chat-bubble>
        <div class="bubble-left" v-if="disabled_send">
            <div class="load-3">
                <div class="line"></div>
                <div class="line"></div>
                <div class="line"></div>
            </div>
        </div>
    </div>
    <div id="send_div">
        <input id="send_input" v-on:keyup.enter="sendMessage" v-model="input_message" class="form-control"
               :disabled="disabled_send"/>
        <button @click="sendMessage" class="btn btn-primary" :disabled="disabled_send">Send</button>
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

const disabled_send = ref(true);

const input_message = ref("");

const messages = ref<Message[]>([])

messages.value.push({sender: "assistant", text: `Connecting...`})


const socket = new WebSocket(props.websocket_url);
socket.addEventListener("open", () => {
    messages.value.push({sender: "assistant", text: `Connected to ${props.websocket_url}`})
    disabled_send.value = false
});
socket.addEventListener("message", (event) => {
    messages.value.push({sender: "assistant", text: event.data});
    disabled_send.value = false;
    nextTick(() => {
        document.getElementById("send_input")?.focus();
        const messages = document.getElementById("messages");
        if (messages) {
            messages.scrollTop = messages.scrollHeight;
        }
    });
});
socket.addEventListener("error", console.error);

function sendMessage() {
    disabled_send.value = true;
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
@import "../assets/loading_animation.css";
@import "../assets/bootstrap";

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

  button {
    border-radius: 0;
  }
}

#messages {
  //width: 100%;
  display: grid;
  max-height: 100%;
  padding: 10px 10px 40px;
  overflow-y: scroll;
  overflow-x: hidden;
}
</style>
