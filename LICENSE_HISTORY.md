# License history and scope

## 2026-10-15 — owner-authored work dedicated to CC0 1.0 Universal

The owner relicensed the repository's **owner-authored work** to CC0 1.0 Universal on
2026-10-15. The current legal code is in [`LICENSE`](LICENSE). This is an additive
history: it preserves the previous legal text and statements rather than erasing their
record.

Copies obtained earlier under **MIT** or **CC BY-SA** stay under those terms for those
holders. This CC0 dedication does not relicense third-party dependencies, cited source
material, or material whose ownership has not been established.

### Previous root license — MIT (full text retained)

The previous root `LICENSE` on `main` contained the following complete legal text:

```text
MIT License

Copyright (c) 2025 JinnZ2

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Previous and mixed statements retained verbatim

The following exact statements were present on current `main` immediately before this
disposition. They are preserved here as historical evidence; active owner-authored
statements have been reconciled to CC0 where ownership was established.

| Path | Exact prior statement | Disposition |
|---|---|---|
| `README.md` | `· Open Architecture – MIT licensed, forkable, adaptable` | Reconciled to CC0 for owner-authored work. |
| `README.md` | `MIT License – no gatekeepers, no proprietary lock-in.` | Reconciled to CC0 for owner-authored work. |
| `package.json` | `"license": "MIT"` | Reconciled to `CC0-1.0`. |
| `package-lock.json` root package record | `"license": "MIT"` | Reconciled by the package-lock generation update; dependency records remain unchanged. |
| `CONTRIBUTING.md` | `- Stick to MIT-compatible components` | Reconciled to preserve third-party component licenses rather than imply an MIT project license. |
| `Waste-management/README.md` | `CC-BY-4.0. Use it, build on it, credit the concept. This is collaborative knowledge - improve it and share what you learn.` | Reconciled to CC0: Git history identifies this active file as JinnZ2/Claude owner-authored work. |
| `Waste-management/README.md` | `: creative commons license (CC-BY-4.0) so AI can legally train on it.` | Reconciled to CC0 for owner-authored material. |
| `docs/roadmap.md` | `- [x] Open source under MIT license` | Retained as a historical Phase I record with an adjacent 2026-10-15 current-scope clarification. |
| `READ_ME_THIS_WAY.md` | `The repository root LICENSE is MIT. CC0 applies only where explicitly declared; no broader relabeling is intended.` | Preserved byte-for-byte under the WO-11 guide-preservation rule; this history records that it predates the current root CC0 disposition. |
| `legacy/pre-2026-refresh/README.md` | `· Open Architecture – MIT licensed, forkable, adaptable` | Retained unchanged as an archived specimen. |
| `legacy/pre-2026-refresh/README.md` | `MIT License – no gatekeepers, no proprietary lock-in.` | Retained unchanged as an archived specimen. |
| `docs/3D_Energy_City_Volumetric_Implementation.md` | `**License**: Open Prototype – Public Use Encouraged` | **Unresolved ownership; retained.** The file identifies `Anonymous Contributor` and `BioGrid Volumetric Implementation Group`; it is excluded from this CC0 dedication pending confirmation. |

Existing owner-authored CC0 declarations in `Meta-README.md`,
`BioGrid_Ontology.json`, and `Electromagnetic-energy-harvesting/README.md` remain
consistent with the present disposition. The existing guide, its prior preamble text,
and archived records were not normalized or removed.

### Third-party / provenance review and exceptions

| Path(s) | License / status | Provenance and treatment |
|---|---|---|
| `package-lock.json` dependency entries | 580 MIT; 37 ISC; 18 BSD-3-Clause; 13 Apache-2.0; 11 BSD-2-Clause; 2 `(MIT OR CC0-1.0)`; 1 Python-2.0; 1 CC-BY-4.0; 1 unspecified (current lockfile metadata) | Generated npm dependency lock metadata, with resolved npm registry URLs. No `node_modules/` code is tracked. These third-party package terms remain unchanged and are not covered by CC0. |
| `REFERENCES.md` and source citations in project documents | External factual/citation provenance; no bundled license text | A bibliography/citation register pointing to external publishers and reports. It is not a vendored copy of those works; external source rights remain with their respective holders. |
| `docs/3D_Energy_City_Volumetric_Implementation.md` | `Open Prototype – Public Use Encouraged` (not a clear standard license) | Self-identifies an anonymous contributor/group. Existing statement retained, current-scope note added, and ownership remains unresolved. |
| Repository tree | No tracked `vendor/`, `third_party/`, `node_modules/`, nested license/notice files, Git submodules, or upstream source directories found | No additional tracked vendored/upstream files were relicensed. |

No statement in this history grants rights in third-party works. Preserve their notices,
licenses, and provenance in future changes.
