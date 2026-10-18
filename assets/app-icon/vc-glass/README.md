# VC glass icon

User-approved spaced-v2 artwork, 2026-10-18. Deep brown full-bleed background,
amber glass V and C paths with increased spacing and a centered composition.
The SVG contains original letter outlines and simulated static highlights.
SVGs and PNGs were exported with VectorCraft CLI; editable VectorCraft projects
remain in the deployment archive. License and attribution are in LICENSE.txt and ASSETS.md.

- vc-glass.svg: editable full-bleed master for Web and system-masked icons.
- vc-glass-rounded.svg: same artwork clipped for the in-app texture.
- titlebar-128.png: rounded transparent-corner app bar and About mark.
- web/: full-bleed 180/192/512 PNGs, 32 px favicon and a relative standalone manifest.

Trunk copies web/ to the site's icons/ directory. Both manifest scope and start URL
resolve to the application directory, so a sub-path deployment works.
The app's brand module includes the rounded 128 px mark in WebAssembly.
The inherited desktop packaging assets remain archived under the parent directory;
this Web build uses the approved VC assets from this folder.
