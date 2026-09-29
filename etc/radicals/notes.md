**[Download the Codex integration prompt](sandbox:/mnt/data/IMPLEMENT-RADICALIZE.md)**

Save it as **`radicals/IMPLEMENT-RADICALIZE.md`**, alongside the support files. Then give Codex:

```text
Read radicals/IMPLEMENT-RADICALIZE.md and implement it in this repository.
```

The prompt uses the existing **`\RadicalMicrobook{stable-id}`** interface rather than creating another heading system, and preserves the approved **100 microbooks / 70 characters**, with conventional-book emblems kept separate.  

The configuration contract is explicit: **`radicalized` enables the headings; `in radicalized` disables them**, with that internal space preserved literally. Disabled is the default, and external build overrides must work.

Most importantly, “disabled” means **nothing happens**: no heading, extra space, paragraph break, page-break decision, invisible anchor, label, contents entry, or counter/state change. The existing support currently performs several of those operations unconditionally, so the prompt specifically requires gating the entire operation—not merely hiding its text. 

It also requires the actual Hebrew verse/clause mapping, explicit handling of the **1 Samuel 4:1** split, stable numbering in subset builds, and comparison against the pre-change manuscript to verify that disabling the feature restores the original layout. 

