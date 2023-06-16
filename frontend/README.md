# gpt-frontend

A simple frontend that displays a basic chat ui and connects to gpt-poc-backend via a websocket.

Can be included as a webcomponent:

```html
<simple-websocket-chat websocket_url="ws://your-websocket-url"></simple-websocket-chat>
...

<script src="https://unpkg.com/@educorvi/gpt-frontend/webcomponent_dist/simple-websocket-chat.js"></script>

```
## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Type-Check, Compile and Minify for Production

```sh
npm run build
```
