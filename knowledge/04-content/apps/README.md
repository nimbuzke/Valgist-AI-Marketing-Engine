# Mini-apps

Reusable single-file HTML tools, built by the profiles on request (shared skill
`build-mini-app`). Each app is one self-contained `.html` file — inline CSS/JS,
no build step — carrying the metadata contract the galleries read:

```html
<title>App name</title>
<meta name="description" content="What it does, for whom.">
<meta name="valgist-profile" content="authoring-profile-id">
```

Open them from the WebUI's 🧩 Mini-apps rail button (:8787) or the Admin
Dashboard's Mini-apps tab (:8321). Apps run in a sandboxed iframe: scripts
execute, but they get no cookies, no parent frame and no workspace access at
runtime — anything an app needs is baked into the file.

`utm-link-builder.html` ships as a working example of the contract.
