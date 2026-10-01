# Bible v2 and staff approval

Bible v2 (`schema_version: "2.0"`) is pinned in
[bible-v2.schema.json](../schemas/bible-v2.schema.json). Legacy artifacts keep their original
format. New staff research jobs call [bible_v2.py](../socialite/bible_v2.py); the old `bible`
CLI command remains a legacy synthesis path.

## Data model

- **Coverage** records assessed, partial, unavailable or not-assessed status for identity,
  company, operators, audience, social, reviews, services, brand, credentials and competitors.
- **Evidence** preserves source ID/URL/type, timestamp, prospect/competitor scope, capture
  outcome, saved-file path, hash and excerpt. Canonical source records come from collection;
  model output cannot mint or replace them. Search snippets have distinct source IDs.
- **Claims** carry IDs, field, value, observed/inferred/unknown/conflicted status, confidence,
  citations and notes. Unknown values must be null. Observed claims require evidence;
  unavailable sources cannot establish an observation.
- **Assets** retain source-image URL, capture provenance/hash and unresolved rights by
  default. Staff choose usage and document permission independently.
- **Comparisons** reference both businesses' claims and preserve advantages in either
  direction, parity or unknown. **Roadmap** items carry now/next/later, justified importance,
  benefit, effort, citations, dependencies and optional service mapping.
- **Site** holds proposed palette/type and bindings from page fields to claim IDs. The
  model cannot approve these fields. Required bindings are name, category, story, headline,
  subheadline, about heading/copy, and primary CTA label/type/value. Unsupported bindings
  stay omitted and block the preview until resolved through new sourced research.

The schema checks structure; semantic validation also checks unique IDs, reference
integrity, coverage, unavailable evidence and safe design values. It cannot automatically
prove that prose accurately reflects a source; staff must inspect receipts.

## Review and projection

Reviews live under `data/leads/<id>/review/`: `v<N>.json` is the latest record and
`v<N>-r<R>.json` preserves each revision. Records include the exact Bible hash, reviewer,
timestamp, notes, claim decisions and approved asset permission/role. Optimistic revision
checks prevent concurrent forms silently overwriting decisions. Names are self-reported
in this local prototype.

Only observed claims supported by a captured prospect source are approvable. Snippet-only,
inferred, unknown or conflicted claims remain internal. Every bound public field must be
approved. Asset inclusion requires a declared permission basis and note; changed/missing
approved image bytes require renewed collection and review.

`project()` produces the old build/pitch contract from the approved bindings. It does not
copy unapproved contact/social details from discovery into the page. The builder validates
the projection and includes review revision, business/locale inputs, templates and image
bytes in its hash. Model hypotheses remain in the Bible, outside public site copy.

Review aggregates require separately sourced platform rating/count/date; selected review
quotes do not establish an aggregate. Confirmed gap claims may enter the pitch after review;
unknown capabilities do not become false/missing. Comparative sales language is suppressed
when competitor counts have not been verified.

## Report presentation

The supplied PDF is a format reference only. Its substantive subject matter was excluded.
The printable view uses executive summary → numbered research findings → priority table
→ action roadmap → competitor comparison → confirmation questions → page readiness →
sources appendix. Clear headings, restrained tables, source links and print margins reflect
the example without importing its branding or certainty language.

The report is rendered from the saved Bible, without an additional model call. The staff
review screen remains a separate operational view. Browser printing provides PDF export.

## Next work

Expand collection beyond the current limited source set, choose supported tools/runtime
adapters, and test the prompt with three providers. Compare same-evidence synthesis and
end-to-end research separately. Add authoritative sources and sector-specific plans before
describing the output as a complete deep dive. The report template may evolve without
changing evidence contracts. Hermes integration remains deferred.
