# Rapid Prototype — Conventions & Patterns

Reference for the `rapid-prototype` skill's Interaction Engineer and Accessibility Validator roles. Keep prototypes consistent with these rules.

## Core rules
- **Zero-build.** One self-contained HTML file. Tailwind via CDN, design tokens in the `tailwind.config` block (see `blank_prototype_template.html`). No npm, no bundler.
- **Vanilla JavaScript only.** No frameworks. All JS in a **single `<script>` block at the end of `<body>`**.
- **Use design tokens, not raw hex.** Prefer `bg-accent`, `text-surface-text-weak`, `px-s4`, `rounded-sm`, `text-label-medium` over arbitrary values, so restyling is one config change.
- **Realistic placeholder content.** Use plausible names/data, never "Lorem ipsum".

## Accessibility checklist (required)
- **focus-ring on every interactive element** — buttons, links, inputs, checkboxes, menu triggers.
- **Semantic HTML** — `<header>`, `<nav>`, `<main>`, `<aside>`, one `<h1>` per page, logical heading order.
- **Skip link** as the first focusable element (present in the template).
- **ARIA** — `aria-label` on icon-only buttons; `aria-current="page"` on the active nav item; `aria-expanded` on disclosure toggles; `role="dialog"` + `aria-modal="true"` + `aria-labelledby` on modals.
- **Icons are decorative** — every `<svg>`/decorative image gets `aria-hidden="true"` (or `alt=""`).
- **Inputs have labels** — a `<label for>` or an `aria-label`.
- **Keyboard** — modals/overlays close on `Escape`; focus order follows reading order.

## JavaScript patterns

### Event delegation for lists
```javascript
document.addEventListener("click", function (e) {
  const row = e.target.closest("[data-row-id]");
  if (!row) return;
  // handle row click
});
```

### Tabs
```javascript
document.querySelectorAll(".tab-btn").forEach(function (btn) {
  btn.addEventListener("click", function () {
    const scope = btn.closest("section") || document;
    scope.querySelectorAll(".tab-content").forEach(t => t.classList.add("hidden"));
    scope.querySelector("#" + btn.dataset.tab).classList.remove("hidden");
    scope.querySelectorAll(".tab-btn").forEach(b => {
      b.classList.remove("border-accent", "text-accent");
      b.classList.add("border-transparent", "text-surface-text-weak");
    });
    btn.classList.add("border-accent", "text-accent");
    btn.classList.remove("border-transparent", "text-surface-text-weak");
  });
});
```

### Modal open/close (with Escape + backdrop)
```javascript
window.openModal = (id) => document.getElementById(id)?.classList.remove("hidden");
window.closeModal = (id) => document.getElementById(id)?.classList.add("hidden");
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape")
    document.querySelectorAll(".fixed.z-50:not(.hidden)").forEach(el => el.classList.add("hidden"));
});
// Close on backdrop click
document.addEventListener("click", (e) => {
  if (e.target.matches(".fixed.z-50")) e.target.classList.add("hidden");
});
```

### Checkbox selection → bulk action bar
```javascript
const boxes = () => [...document.querySelectorAll("[data-select]")];
function refreshBulkBar() {
  const n = boxes().filter(b => b.checked).length;
  const bar = document.getElementById("bulk-bar");
  bar.classList.toggle("hidden", n === 0);
  document.getElementById("bulk-count").textContent = n + " selected";
}
document.addEventListener("change", (e) => {
  if (e.target.matches("[data-select]")) refreshBulkBar();
});
```

### Simple form validation
```javascript
document.getElementById("myForm")?.addEventListener("submit", function (e) {
  const email = this.querySelector("[name=email]");
  if (!email.value.includes("@")) {
    e.preventDefault();
    email.setAttribute("aria-invalid", "true");
    // show inline error element
  }
});
```

## Delivery
- Save with a descriptive filename, e.g. `user_management_prototype.html`.
- Tell the user the file path, the key interactions to test, and 2-3 suggested next iterations.
- `open <file>.html` on macOS to preview.
