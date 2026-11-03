# Source inspection — micro-frontend-demo

Ngày đọc 03/11/2026. Commit `9a4d33596453d2d76da9d8ebb0b5c9249a0a024d`; working tree sạch. Chỉ đọc source, không build/start/test ứng dụng. SHA-256 tính toàn bộ bytes; trích đoạn giữ số dòng gốc.

Package manager `yarn@3.6.1`, package version `0.1.0`.

## `package.json`

SHA-256: `4b32ee360e406becb0ca4279dea953f30b4611411aec2c0e0fbeecfda5978a61`.

```text
1: {
2:   "name": "micro-frontend-demo",
3:   "version": "0.1.0",
4:   "private": true,
5:   "engines": {
6:     "npm": ">=8.0.0",
7:     "node": ">=16.0.0 "
8:   },
9:   "devDependencies": {
10:     "turbo": "^1.10.12"
11:   },
12:   "scripts": {
13:     "start": "yarn turbo run start",
14:     "build": "yarn turbo run build",
15:     "test": "yarn turbo run test"
16:   },
17:   "workspaces": [
18:     "main",
19:     "cart",
20:     "products"
21:   ],
22:   "eslintConfig": {
23:     "extends": [
24:       "react-app",
25:       "react-app/jest"
26:     ]
27:   },
28:   "browserslist": {
29:     "production": [
30:       ">0.2%",
31:       "not dead",
32:       "not op_mini all"
33:     ],
34:     "development": [
35:       "last 1 chrome version",
```

## `main/src/App.tsx`

SHA-256: `0a951b72bc9033a6019031c53b5a9486457c950d736c1e643f58d0602a83f945`.

```text
1: import React from "react";
2: // @ts-ignore
3: import { BrowserRouter, Route, Routes } from "react-router-dom";
4: import Header from "./components/Header";
5: import StoreHeader from "./components/StoreHeader";
6: import RemoteControls from "./components/RemoteControls";
7: import RemoteComponent from "./components/RemoteComponent";
8: import RemotesProvider from "./context/remotes";
9: import PubSub from "./services/pubsub";
10:
11: // Initialize PubSub Event messaging between apps
12: const events = new PubSub({ persistedTopics: ["cart"] });
13: // Set it at global level for all to consume (also passed as props)
14: // @ts-ignore
15: window.fsEvents = events;
16:
17: export const App = () => {
18:   return (
19:     <RemotesProvider>
20:       <Header />
21:       <RemoteControls />
22:       <div style={{ margin: "10px", border: "1px solid black" }}>
23:         <BrowserRouter>
24:           <>
25:             <StoreHeader />
26:             <div style={{ marginTop: 40 }}>
27:               <Routes>
28:                 <Route
29:                   path="/"
30:                   element={
31:                     <RemoteComponent
32:                       fallback="Loading Products..."
33:                       remote="PRODUCTS"
34:                       component="ProductsList"
35:                     />
36:                   }
37:                 ></Route>
38:                 <Route
39:                   path="/checkout"
40:                   element={
41:                     <RemoteComponent
42:                       fallback="Loading Checkout..."
43:                       remote="CART"
44:                       component="CheckoutPage"
45:                     />
46:                   }
47:                 ></Route>
48:               </Routes>
```

## `main/webpack.config.js`

SHA-256: `2eaf4ac702dca6638eeebf44299ec7b17c875645fa62000d0545629df9285133`.

```text
7: module.exports = (env) => {
8:   const PRODUCTS_HOST = env.PRODUCTS_HOST || "http://localhost:9002";
9:   const CART_HOST = env.CART_HOST || "http://localhost:9002";
10:   return {
11:     mode: "development",
12:     devServer: {
13:       port: 9001,
14:       historyApiFallback: { index: "/", disableDotRule: true },
15:     },
```

```text
49:         name: "MAIN",
50:         remotes: {
51:           // CART: `CART@${CART_HOST}/remoteEntry.js`,
52:           // PRODUCTS: `PRODUCTS@${PRODUCTS_HOST}/remoteEntry.js`,
53:         },
54:         shared: {
55:           ...dependencies,
56:           react: {
57:             eager: true,
58:             singleton: true,
59:             requiredVersion: dependencies["react"],
60:           },
61:           "react-dom": {
62:             eager: true,
63:             singleton: true,
64:             requiredVersion: dependencies["react-dom"],
65:           },
66:         },
67:       }),
68:       new HtmlWebpackPlugin({
69:         template: "./public/index.html",
70:       }),
71:       new webpack.DefinePlugin({
72:         "process.env.PRODUCTS_HOST": JSON.stringify(PRODUCTS_HOST),
73:         "process.env.CART_HOST": JSON.stringify(CART_HOST),
74:       }),
75:     ],
76:     resolve: {
77:       extensions: [".js", ".jsx", ".ts", ".tsx"],
78:     },
```

## `products/webpack.config.js`

SHA-256: `19ca285f8daac9eba625201cad141ef28787a6bb13aa2f27c141dab22d04fdb3`.

```text
58:         shared: {
59:           ...dependencies,
60:           react: {
61:             eager: true,
62:             singleton: true,
63:             requiredVersion: dependencies["react"],
64:           },
65:           "react-dom": {
66:             eager: true,
67:             singleton: true,
68:             requiredVersion: dependencies["react-dom"],
69:           },
70:         },
71:       }),
72:       new HtmlWebpackPlugin({
73:         template: "./public/index.html",
74:       }),
75:     ],
76:     resolve: {
77:       extensions: [".js", ".jsx", ".ts", ".tsx"],
78:     },
79:   };
80: };
```

## `cart/webpack.config.js`

SHA-256: `4b302f86dede0b29ba5612e1b745b49d5cca3ddb789cd48d5d9ddc9adf18e467`.

```text
39:       new Dotenv(),
40:       new ModuleFederationPlugin({
41:         name: "CART",
42:         filename: "remoteEntry.js",
43:         exposes: {
44:           "./Cart": "./src/components/CartButton",
45:           "./CheckoutPage": "./src/features/checkout",
46:         },
47:         remotes: {
48:           PRODUCTS: `PRODUCTS@${PRODUCTS_HOST}/remoteEntry.js`,
49:         },
50:         shared: {
51:           ...dependencies,
52:           react: {
53:             eager: true,
54:             singleton: true,
55:             requiredVersion: dependencies["react"],
56:           },
57:           "react-dom": {
58:             eager: true,
59:             singleton: true,
60:             requiredVersion: dependencies["react-dom"],
61:           },
62:         },
63:       }),
64:       new HtmlWebpackPlugin({
65:         template: "./public/index.html",
66:       }),
67:     ],
68:     resolve: {
69:       extensions: [".js", ".jsx", ".ts", ".tsx"],
70:     },
71:     target: "web",
72:   };
73: };
```

## `main/src/utils/index.ts`

SHA-256: `4e0400b1e541c32bc4f7e01a35b9653b0448c1c2791370ae24ff61a50bb42126`.

```text
1: // @ts-nocheck
2: export const fetchRemote = (url, remoteName) =>
3:   new Promise((resolve, reject) => {
4:     // We define a script tag to use the browser for fetching the remoteEntry.js file
5:     const script = document.createElement("script");
6:     script.src = url;
7:     script.onerror = (err) => {
8:       console.error(err);
9:       reject(new Error(`Failed to fetch remote: ${remoteName}`));
10:     };
11:     // When the script is loaded we need to resolve the promise back to Module Federation
12:     script.onload = () => {
13:       // The script is now loaded on window using the name defined within the remote
14:       const proxy = {
15:         get: (request) => window[remoteName].get(request),
16:         init: (arg) => {
17:           try {
18:             return window[remoteName].init(arg);
19:           } catch (e) {
20:             console.error(e);
21:             console.error(`Failed to initialize remote: ${remoteName}`);
22:             reject(e);
23:           }
24:         },
25:       };
26:       resolve(proxy);
27:     };
28:     // Lastly we inject the script tag into the document's head to trigger the script load
29:     document.head.appendChild(script);
30:   });
31:
32: export const loadComponent =
33:   (remoteName, remoteUrl, moduleName, scope = "default") =>
34:   async () => {
35:     if (!(remoteName in window)) {
36:       // Need to load the remote first
37:       // Initializes the shared scope. Fills it with known provided modules from this build and all remotes
38:       // eslint-disable-next-line no-undef
39:       await __webpack_init_sharing__(scope); // TODO when would you use a different scope?
40:       const fetchedContainer = await fetchRemote(
41:         `${remoteUrl.replace(/\/$/, "")}/remoteEntry.js`,
42:         remoteName
43:       );
44:       // eslint-disable-next-line no-undef
45:       await fetchedContainer.init(__webpack_share_scopes__[scope]);
46:     }
47:     const container = window[remoteName]; // Assuming the remote has been loaded using the above function
48:     const factory = await container.get(moduleName);
49:     const Module = factory();
50:     return Module;
51:   };
```

## `main/src/services/pubsub.ts`

SHA-256: `e04a380854467a7875432510b41d9856ee25253eff287e1f885c083827beef00`.

```text
19: export class PubSub {
20:   constructor({ persistedTopics }: { persistedTopics?: Topic[] } = {}) {
21:     if (persistedTopics && !Array.isArray(persistedTopics)) {
22:       throw new Error("Persisted topics must be an array of topics.");
23:     }
24:     if (persistedTopics) {
25:       this.persistedMessages = persistedTopics.reduce(
26:         (acc: Record<Topic, Message>, cur: Topic) => {
27:           acc[cur] = {};
28:           return acc;
29:         },
30:         {}
```

```text
60:       this.topics[topic] = [subID];
61:     } else {
62:       // Topic exists
63:       this.topics[topic].push(subID);
64:     }
65:     // Store onMessage and topic separately for faster lookup
66:     this.subscriberOnMsg[subID] = onMessage;
67:     this.subscriberTopics[subID] = topic;
68:     // If the topic is persisted and there are existing messages, trigger the onMessage handler immediately
69:     if (topic in this.persistedMessages) {
70:       onMessage(this.persistedMessages[topic]);
71:     }
72:     return subID;
73:   }
```

```text
109:    * @param message The message to send. Only object format is supported.
110:    */
111:   public publish(topic: Topic, message: Record<string, unknown>) {
112:     if (typeof topic !== "string") throw new Error("Topic must be a string.");
113:     if (typeof message !== "object") {
114:       throw new Error("Message must be an object.");
115:     }
116:     // If topic exists post messages
117:     if (topic in this.topics) {
118:       const subIDs = this.topics[topic];
119:       subIDs.forEach((id) => {
120:         if (id in this.subscriberOnMsg) {
121:           this.subscriberOnMsg[id](message);
122:         }
123:       });
124:     }
125:     if (topic in this.persistedMessages) {
126:       this.persistedMessages[topic] = message;
127:     }
128:   }
129: }
```

## `products/src/components/ProductCard/index.tsx`

SHA-256: `53138a21e3b4cc9cbf961269e5329a8a5162de09f791c830c2cd0f923386a8f0`.

```text
33:   useEffect(() => {
34:     // @ts-ignore
35:     const subID = events?.subscribe("cart", function ({ cart }) {
36:       setCart(cart);
37:     });
38:     return () => {
39:       if (subID) {
40:         events?.unsubscribe(subID);
41:       }
42:     };
43:   }, []);
44:   let action = (
45:     <Button
46:       size="small"
47:       variant="contained"
48:       endIcon={<AddShoppingCart />}
49:       sx={{ marginBottom: "40px" }}
50:       onClick={() => {
51:         events?.publish("addItem", { name, price });
52:       }}
53:     >
54:       Add to Cart
55:     </Button>
56:   );
57:   const itemIndex = cart.findIndex((product: Product) => product.name === name);
58:   const isItemInCart = itemIndex > -1;
59:   if (isItemInCart) {
60:     const { quantity } = cart[itemIndex];
61:     action = (
```

```text
66:           alignItems: "center",
67:         }}
68:       >
69:         <div>
70:           <IconButton
71:             onClick={() => {
72:               events?.publish("removeItem", { name, quantity: 1 });
73:             }}
74:           >
75:             <Remove />
76:           </IconButton>
77:           {quantity}
78:           <IconButton
79:             onClick={() => {
80:               events?.publish("addItem", { name });
81:             }}
82:           >
83:             <Add />
84:           </IconButton>
85:         </div>
86:         <Button
87:           size="small"
88:           onClick={() => {
89:             events?.publish("removeItem", { name, quantity });
90:           }}
91:           endIcon={<Delete />}
92:         >
93:           Remove
94:         </Button>
95:       </div>
96:     );
97:   }
98:
```

## `cart/src/store/index.ts`

SHA-256: `8e1f138d6c95bcd2e0fe2b1b9b2ac05728024b78036df6fc3c804f4094155c5c`.

```text
15:   return !!item && typeof item === "object" && typeof item?.name === "string";
16: };
17: const STORAGE_ID = "fruit-shop-cart";
18:
19: // Global event bus for communicating between micro apps
20: // @ts-ignore
21: const eventBus = window.fsEvents;
22:
23: const getLocalState = (): Array<Product> => {
24:   const rawData = localStorage.getItem(STORAGE_ID);
25:   if (rawData) {
26:     const parsed = JSON.parse(rawData);
27:     if (Array.isArray(parsed)) {
28:       return parsed;
29:     }
30:   }
31:   return [];
32: };
33:
34: const updateLocalState = (newCart: Array<Product>): void => {
35:   eventBus.publish("cart", { cart: newCart });
36:   localStorage.setItem(STORAGE_ID, JSON.stringify(newCart));
37: };
38:
39: // Initialize event bus with cart data
40: if (eventBus) {
41:   eventBus.subscribe("addItem", function (item: Product) {
42:     const { getState } = store;
43:     const { addItem } = getState();
44:     addItem(item);
45:   });
46:   eventBus.subscribe("removeItem", function (item: Product) {
47:     const { getState } = store;
48:     const { removeItem } = getState();
49:     removeItem(item.name, item?.quantity);
50:   });
51:   eventBus.publish("cart", { cart: getLocalState() });
52: }
53:
54: export const store = create<State>((set) => ({
55:   cart: getLocalState(),
56:   addItem: (newItem) => {
57:     if (validItem(newItem)) {
58:       set((state) => {
59:         const cart = [...state.cart];
60:         const existingIndex = cart.findIndex(
61:           (item) => item.name === newItem.name
62:         );
63:         if (existingIndex > -1) {
64:           const existing = cart[existingIndex];
65:           cart[existingIndex] = {
66:             ...existing,
67:             quantity: (existing?.quantity || 0) + 1,
68:           };
69:         } else {
70:           cart.push({ quantity: 1, ...newItem });
```

```text
75:     }
76:   },
77:   removeItem: (itemName, quantity = 1) => {
78:     if (itemName && typeof itemName === "string") {
79:       set((state) => {
80:         const cart = [...state.cart];
81:         const existingIndex = cart.findIndex((item) => item.name === itemName);
82:         if (existingIndex > -1) {
83:           const existing = cart[existingIndex];
84:           if (!existing?.quantity || existing?.quantity <= quantity) {
85:             cart.splice(existingIndex, 1);
86:           } else {
87:             cart[existingIndex] = {
88:               ...existing,
89:               quantity: existing.quantity - quantity,
90:             };
91:           }
92:         }
93:         updateLocalState(cart);
94:         return { cart };
95:       });
96:     }
97:   },
98: }));
99: export const useStore = store;
100:
101: export const useCartCount = (product?: string): number => {
102:   const products = useStore((store) => store.cart);
103:   const count = products.reduce((acc, cur) => {
104:     let curCount = acc;
105:     if (!product || product === cur.name) {
106:       curCount += cur?.quantity || 0;
107:     }
108:     return curCount;
109:   }, 0);
110:   return count || 0;
```

## `cart/src/features/checkout/index.tsx`

SHA-256: `9e90f43b2a87d5e317c4ae3393653c3b4b56ce3a5780b4d9eb0e57a891a7e1fd`.

```text
1: import React from "react";
2: // @ts-ignore
3: import { Link } from "react-router-dom";
4: import useStore from "../../store";
5: import RemoteComponent from "../../../../main/src/components/RemoteComponent";
6: // Importing components and list of products from products app directly
7: // to simplify import/export. Products list should be taken care of by a communication layer
8: // And the ProductCard should be a published npm package or shared remote but need
9: // to figure out how to load multiple versions of the same remote in 1 app.
10: import products from "../../../../products/src/products";
11:
12: type Product = {
13:   name: string;
14:   price?: number;
15:   quantity?: number;
16: };
17:
18: type PriceMap = Record<string, number>;
19: // @ts-ignore
20: const priceMap: PriceMap = products.reduce((acc: PriceMap, cur: Product) => {
21:   return { ...acc, [cur.name]: cur.price };
22: }, {});
23: export const CheckoutPage = () => {
24:   const cart = useStore((store) => store.cart);
25:   let total = 0;
26:   for (let i = 0; i < cart.length; i++) {
27:     const product: Product = cart[i];
28:     total = total + (product?.quantity || 1) * priceMap[product.name];
29:   }
30:   return (
31:     <div>
32:       <Link to="/">&larr; Back</Link>
33:       <h1>Checkout</h1>
34:       <p>Total: ${total.toFixed(2)}</p>
35:       <div style={{ display: "flex", flexDirection: "row" }}>
36:         {cart.map(({ name, quantity }) => (
37:           <div key={name} style={{ margin: 20 }}>
38:             <RemoteComponent
39:               fallback="Loading..."
```

## `main/src/context/remotes.tsx`

SHA-256: `c104f6c3dab201fbab0cc42e9688b1c61b05328a0db5b9315c15d92dfcd14632`.

```text
12:
13: const initRemotes = [
14:   { name: "PRODUCTS", url: process.env.PRODUCTS_HOST || "" },
15:   { name: "CART", url: process.env.CART_HOST || "" },
16: ];
17:
18: const initState: Remotes = {
19:   remotes: initRemotes,
20:   updateRemoteUrl: () => {},
21: };
22:
23: export const STORAGE_KEY = "fruit-remotes";
24:
25: const storeRemotes = (remotes: Remote[]) => {
26:   localStorage.setItem(STORAGE_KEY, JSON.stringify(remotes));
27: };
28:
29: const hydrateRemotes = (): Remote[] => {
30:   try {
31:     const raw = localStorage.getItem(STORAGE_KEY);
32:     if (raw) {
33:       const parsed = JSON.parse(raw);
34:       if (Array.isArray(parsed)) {
35:         return parsed;
36:       }
37:     }
38:     return [];
39:   } catch {
40:     return [];
41:   }
42: };
43:
44: export const RemotesContext = createContext(initState);
45:
```

## `main/src/components/RemoteComponent/index.tsx`

SHA-256: `20073adfd955d1e4b3956952d4090223e2399eae42b740e53169a77810bf7ed0`.

```text
20:   ...props
21: }) => {
22:   const [remotes] = useRemotes();
23:   const remoteUrl = findRemoteUrl(remote, remotes);
24:   if (!remoteUrl) return <div>Unable to Fetch: {`${remote}/${component}`}</div>;
25:   const Component = React.lazy(
26:     loadComponent(remote, remoteUrl, `./${component}`, scope)
27:   );
28:   return (
29:     <ErrorBoundary>
30:       <React.Suspense fallback={fallback}>
31:         <Component {...props} />
32:       </React.Suspense>
33:     </ErrorBoundary>
34:   );
35: };
36:
37: export default RemoteComponent;
```

## Khác biệt bản copy

Nguồn chính không có Dockerfile/Compose/Nginx. Bản `source/` trong repo tài liệu có các cấu hình này; không chạy nó trong lượt inspection.
