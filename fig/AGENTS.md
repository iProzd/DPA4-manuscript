# Figure Drawing Guide

This folder contains editable draw.io source files and exported high-resolution PNG figures for the DPA4 paper. 

## Tooling

- Use draw.io desktop CLI for export. On macOS, prefer:

```bash
DRAWIO="/Applications/draw.io.app/Contents/MacOS/draw.io"
"$DRAWIO" -x -f png -s 5 -b 10 -o doc/outisli/figures/sezm/<name>.png doc/outisli/figures/sezm/<name>.drawio
```

- Export only clean PNG previews/finals unless explicitly asked otherwise.
- Do not use `-e` for the normal PNG used in the paper draft. Embedded PNGs can trigger decoder/vision issues and are unnecessary for the current workflow.
- Use scale `-s 5` for final PNG exports.
- Keep the `.drawio` file as the editable source and overwrite the same `.png` on every iteration.

## Visual Style

- Font: `Times New Roman` everywhere.
- Default text color: `#1F2933`.
- Main directed arrows: `#3E4C59`, stroke width `1.7`, block arrowhead.
- Backward/gradient dashed arrows: `#8A8A8A`, stroke width `1.7`, dash pattern `6 6`.
- Residual shortcut arrows: `#5F6C78`, stroke width `1.6`.
- Auxiliary feature arrows should match the source module color and be dashed:
  - Edge/cache path: blue `#4E79A7`, stroke width `1.5`, dash pattern `5 5`.
  - Embedding/radial path: pink `#C85A7C`, stroke width `1.35`, dash pattern `5 5`.
- Module boxes use soft pastel fills and colored strokes, not black thick outlines:
  - Shared cache: fill `#EDF5FF`, stroke `#4E79A7`.
  - Geometry-aware embedding: fill `#FCEDF1`, stroke `#C85A7C`.
  - SO(2) convolution: fill `#F1E9FB`, stroke `#8A6BBE`.
  - Equivariant RMSNorm: fill `#FFF8DC`, stroke `#C49A2C`.
  - Equivariant FFN: fill `#EAF6F0`, stroke `#4E9D76`.
  - Atomic energy head: fill `#FFF2E5`, stroke `#D9862E`.

## Shapes And Sizes

- Rounded module boxes: `rounded=1;arcSize=18`.
- Large repeated-block container: smaller corner radius, `arcSize=8`, fill `#FBFCFE`, stroke `#8FA1B3`.
- Residual and summation circles: `40 × 40`, white fill `#FFFFFF`, stroke `#8FA1B3`, stroke width `1.7`.
- Use `+` for residual add nodes and `Σ` for summation nodes.
- Use single-line labels whenever possible. If a box can be one line, make the box flatter rather than leaving unused vertical space.
- Keep all primary modules centered on the same vertical axis when the figure is a vertical architecture panel.

## Layout Rules

- The main data flow should be a clean vertical spine. Use explicit source/target points when auto-routing causes tiny gaps or diagonal jogs.
- Labels for tensor shapes go next to the corresponding vertical edge, not inside blocks.
- Keep shape labels near their edges, but never let text touch arrowheads or borders.
- Use rotated text for vertical dashed side paths. Keep rotated labels close to their corresponding line.
- Avoid letting labels or arrowheads overlap grid lines visually by leaving at least a few pixels of whitespace around text.
- When the user asks for a local alignment fix, edit the exact XML coordinates instead of regenerating the whole figure.
- After changing a box size or position, update all adjacent connector endpoints in the same edit.

## SeZM Semantic Drawing Rules

- Draw computational ownership, not implementation trivia. A module box should represent a conceptual stage that a reader can explain from the paper.
- Use the main vertical spine for the primary tensor flow.
- Use dashed side paths only for auxiliary information that is reused or injected into a main block.
- If two auxiliary inputs enter the same operator, draw two separate dashed paths with colors matching their source modules.
- Prefer short semantic labels such as `radial`, `rotation`, `attention`, or `gate`; avoid raw variable names unless the figure is explicitly about implementation.
- Backward/gradient paths should be grey dashed loops and should not compete visually with the forward path.
- Use `Σ` circles for reductions/summations instead of wide boxes when the operation is simple.
- Do not embed panel titles, figure numbers, or subfigure labels in the image. The paper text handles those.

## XML Editing Notes

- Every edge must have an expanded `<mxGeometry relative="1" as="geometry">...</mxGeometry>` block.
- For precise alignment, use explicit points:

```xml
<mxPoint x="230" y="775" as="targetPoint" />
```

- For side routes, use waypoints:

```xml
<Array as="points">
  <mxPoint x="430" y="118" />
  <mxPoint x="430" y="425" />
</Array>
```

- Keep a fixed main vertical center within each panel unless deliberately redesigning the panel.

## Visual QA Checklist

Before reporting that a figure is done:

- Export the PNG with `-s 5 -b 12`.
- Read the exported PNG visually.
- Check every main vertical arrow touches the intended box or circle boundary.
- Check side arrows enter the correct side center of the target module.
- Check arrowheads do not land inside circles unless that is intended.
- Check text is not clipped, cramped, or too far from the line it describes.
- Check repeated-block container margins feel balanced around its internal modules.
- Check all module labels use Times New Roman and consistent sizes.
- Check no title or subfigure label is embedded in the image; captions and `(a)` labels are handled in the paper.
