# postSPI — Post-processing for axial soil–pipe interaction (ASPI) by 3D DEM

**postSPI** collects the post-processing scripts used to turn the snapshots of
the axial soil–pipe interaction (ASPI) DEM model into the micro-mechanical
figures of

> **Guo C., Zhou C., Meguid M. A., et al. (2026).** DEM modelling of the axial
> behaviour of underground pipelines buried in unsaturated coarse-grained
> soils. *Computers and Geotechnics* **196**, 108122.
> <https://doi.org/10.1016/j.compgeo.2026.108122>

and

> **Guo C., Zhou C.\*, Meguid M.A. (2025).** Effect of surface roughness on
> axial soil–pipe interaction: a discrete element approach.
> *Computers and Geotechnics* **187**, 107464.
> <https://doi.org/10.1016/j.compgeo.2025.107464>

The numerical model that produces the data post-processed here lives in the
companion repository **mySPI** (<https://github.com/PolyU-GUO/mySPI.git>); the
YADE fork whose source code supplies the engines (and the capillary model) is
**myYade** (<https://github.com/PolyU-GUO/myYade.git>). `postSPI` reads the
`.yade.bz2` snapshots written by that model and derives displacement fields,
force chains and (contact / capillary) pressure fields from them.

---

## Contents

| File | Description |
| --- | --- |
| `setting.py` | Global configuration: model geometry, all post-processing paths, and the `paths.txt` parser. Imported by every script. |
| `myCommonSavers.py` | I/O helpers — `saver` / `reader` (pickle), `checkPath`, `Logger`, CSV writers. |
| `myCommonFunction.py` | Analysis helpers — `mesh_xz` (homogenisation mesh), `draw_half_circle_outline`, `moving_average_2d_with_weight`, `periodicialize`, `principal_stress_and_direction`, … |
| `paths.example.txt` | Template for `paths.txt`, which maps a simulation label to its Log folder. |
| `get_*.py` | **Extract** raw data from the YADE snapshots (run *inside* YADE). |
| `draw_*.py` | **Plot** the extracted data with matplotlib (run with plain `python3`). |
| `README.md` | This document. |
| `LICENSE`, `COPYRIGHT` | GNU GPL v2-or-later and the copyright notices. |

---

## What each script does

The post-processing is split into a *get* stage (raw data out of YADE) and a
*draw* stage (figures from that raw data).

### `get_*` — extract raw data (run inside YADE)

| Script | Extracts |
| --- | --- |
| `get_postionAndRotation.py` | Per-particle displacement `state.displ()` and rotation `state.rot()` for every loading step. |
| `get_pipePostionList.py` | The pipe (shear box) centre position at each step; also builds the combined `sumppPos.data` dictionary. |
| `get_contactForcesZone1.py` | The contact force chains in **Zone 1** (the fine-particle band around the pipe): for each contact touching a Zone-1 particle it stores the two end points and the normal force. |
| `get_pressureMatrixZone5.py` | The contact pressure matrix `(f_n + f_s) ⊗ l` in **Zone 5** (the coarse far field), i.e. the dyadic of the total contact force and the branch vector. |
| `get_pressureMatrixZone5_cap.py` | The same matrix but from the **capillary** force only, `f_cap ⊗ l` (requires the capillary model of myYade). |

### `draw_*` — plot the extracted data (run with python3)

| Script | Figure |
| --- | --- |
| `draw_displacementXZVector.py` | Displacement vector field of the Zone-1 particles in the vertical (X–Z) plane. |
| `draw_displacementYfield.py` | The axial (Y) component of the particle displacement, as a colour field over the sample. |
| `draw_contactForceZone1.py` | The Zone-1 force chains, line thickness / grey level scaled by the normal force. |
| `draw_pressureMatrixZone5.py` | The Zone-5 contact pressure field — vertical (σzz) and horizontal (σxx) components, smoothed by a weighted moving average. |
| `draw_pressureMatrixZone5_cap.py` | The Zone-5 capillary pressure field, vertical and horizontal components. |

---

## Workflow / data flow

```
mySPI (YADE run)
   └─ *.yade.bz2 snapshots  +  post/ folder (boundaryDict, positionList,
                                   sizeList, particlesID, ...)
            │
            │  run inside YADE:
            │     get_postionAndRotation.py
            │     get_pipePostionList.py
            │     get_contactForcesZone1.py
            │     get_pressureMatrixZone5.py
            │     get_pressureMatrixZone5_cap.py
            ▼
        raw *.data files under post/...
            │
            │  run with python3:
            │     draw_displacementXZVector.py
            │     draw_displacementYfield.py
            │     draw_contactForceZone1.py
            │     draw_pressureMatrixZone5.py
            │     draw_pressureMatrixZone5_cap.py
            ▼
        figures (png / svg)
```

The `get_*` scripts are YADE user scripts — YADE injects `O` and the body /
interaction objects into the namespace — so they must be launched by YADE
itself, not by a plain Python interpreter. The `draw_*` scripts are ordinary
Python and only need `numpy` and `matplotlib`.

## Requirements

* **myYade** — the YADE fork whose **source code** you need to build and install
  YADE itself: <https://github.com/PolyU-GUO/myYade.git>. The `get_*` scripts
  run inside YADE, and the `*_cap.py` scripts additionally need the capillary
  (6D) model that myYade adds on top of the upstream YADE tree
  (`CapillaryCohPhys` / `Law2_ScGeom6D_...`, `i.phys.fCap`).
* **mySPI** — the model that produces the **data** post-processed here (the
  `.yade.bz2` snapshots and the `post/` folder):
  <https://github.com/PolyU-GUO/mySPI.git>.
* Python 3 with `numpy` and `matplotlib` for the `draw_*` stage.

## Setup

The scripts locate a simulation through `setting.py`, which reads a small text
file `paths.txt` that maps a label to a Log folder:

```bash
cp paths.example.txt paths.txt     # then edit the paths inside
export TARGET_SIMULATION=R34A025     # label used by setting.py (default)
```

`paths.txt` is **not** part of this repository because it contains absolute
local paths; use `paths.example.txt` as the template.

## How to run

```bash
# 1) extract raw data (inside YADE, from the simulation Log folder)
yade -j4 get_postionAndRotation.py
yade -j4 get_pipePostionList.py
yade -j4 get_contactForcesZone1.py
yade -j4 get_pressureMatrixZone5.py
yade -j4 get_pressureMatrixZone5_cap.py

# 2) plot
python3 draw_displacementXZVector.py
python3 draw_displacementYfield.py
python3 draw_contactForceZone1.py
python3 draw_pressureMatrixZone5.py
python3 draw_pressureMatrixZone5_cap.py
```

Each `get_*` script loops over the `.yade.bz2` snapshots found by `setting.py`
and skips every `gap` steps (edit `gap` in the script to change the sampling);
`cover` controls whether already-saved files are overwritten.

---

## Citation

```bibtex
@article{Guo2026ASPIUnsaturated,
  title   = {DEM modelling of the axial behaviour of underground pipelines
             buried in unsaturated coarse-grained soils},
  author  = {Guo, Chang and Zhou, Chao and Meguid, Mohamed A. and others},
  journal = {Computers and Geotechnics},
  volume  = {196},
  pages   = {108122},
  year    = {2026},
  doi     = {10.1016/j.compgeo.2026.108122}
}

@article{Guo2025ASPI,
  title   = {Effect of surface roughness on axial soil-pipe interaction:
             A discrete element approach},
  author  = {Guo, Chang and Zhou, Chao and Meguid, Mohamed A.},
  journal = {Computers and Geotechnics},
  volume  = {187},
  pages   = {107464},
  year    = {2025},
  doi     = {10.1016/j.compgeo.2025.107464}
}
```

Please also cite the software this repository builds on:

* **YADE** — Šmilauer V., Chareyre B. (2021) *Yade Documentation*, 3rd edition,
  The Yade Project. <https://yade-dem.org>
* **myYade** — <https://github.com/PolyU-GUO/myYade>

## Acknowledgements

The physical modelling and the DEM model were supported by the Research Grants
Council (RGC) of the HKSAR under grant N_PolyU526/23 and AoE/E-603/18, and by
RISUD/PolyU under grant 1-BBWS.

## Licence and copyright

* The scripts and this documentation are **Copyright (C) 2026 Chang GUO** and
  released under the **GNU General Public License, version 2 or later**
  (`LICENSE`). `postSPI` is a set of YADE user scripts and depends on the
  GPL-licensed YADE core and on the myYade capillary/6D suite
  (Copyright (C) 2026 Chang GUO, GPL v2 or later), so the GPL is the only
  licence compatible with this combination.

See `COPYRIGHT` for the full notices.

The software is provided as-is, without warranty of any kind, for research
purposes.
