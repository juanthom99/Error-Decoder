# Interface design

Error Decoder uses a dark glass interface that keeps the input, ranked explanations, and model details visually distinct.

- **Typography:** DM Sans for body text; Space Grotesk for headings and branding.
- **Color:** dark navy and charcoal surfaces, soft borders, and lime accents for primary actions and readiness.
- **Layout:** side-by-side input and results on larger screens, stacked panels on phones.
- **Interaction:** built-in examples, selectable match counts, clear loading and empty states, and expandable model details.
- **Accessibility:** labeled inputs, keyboard controls, visible focus states, and reduced-motion support.

The production interface lives in `frontend/src/main.jsx` and `frontend/src/style.css`. Screenshots are in `evidence/screenshots/`.
