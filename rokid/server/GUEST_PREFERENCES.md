# Demo guest cues (version 2)

The schema supports zero or multiple cues; the current demo assigns just 1-2
total cues per guest. Likes, dislikes and fictional demo allergies are separate lists.
Preview: `output/guest-preferences/index.html`. Database:
`server/data/guest-preferences.sqlite3`. The original data is retained in the
`guest_preferences_v1` table for reference.

## Current icon composition

The twelve main SVGs in `server/preference_icons/` contain no heart or warning
badge. Independent markers live in `server/preference_icons/markers/`:

| Sentiment | Meaning | Marker file |
| --- | --- | --- |
| `prefer` | Likes an item | `heart.svg` |
| `dislike` | Dislikes an item | `dislike.svg` (crossed-out heart) |
| `allergy` | Fictional demo allergy | `warning.svg` |

The preview overlays a marker at the bottom-right, at 36% of the main icon width.
Examples: twin beds + heart; smoking room + crossed-out heart; shrimp + warning.
Every layer is independently reusable. `icon-catalog.json` now contains
`schema_version: 2`, `items`, `markers`, and overlay sizing metadata.

## Current profiles and database

Names come from the current gallery filenames. The seven current profiles have
distinct combinations, with 1-2 total cues per person. All assignments, especially allergies, are fabricated demo examples,
not verified personal or medical facts. Empty lists mean no assigned demo cues,
not a verified absence of allergies.

`GuestPreferenceStore().profiles()` returns each profile's `cues` (all records),
`preferences` (likes only), `dislikes`, and `allergies`. Every cue contains the
item's `code`, `category`, `label`, `icon_file`, `sentiment`, `marker_file`,
`source`, and UTC `updated_at` timestamp.

The current `guest_preferences` table permits multiple items in each category.
Its primary key is `(guest_id,option_code)`, so the same item cannot carry
conflicting like/dislike/allergy markers for one guest. Allergy markers require
food/beverage items. Source is `demo_random_v2` for generated samples; use
`demo_manual` for edits that should survive regeneration.

## Current seeding and migration

From the parent project directory, run:

```powershell
python .\rokid\server\seed_guest_preferences.py
```

The script uses only Python's standard library. It adds new filename-based demo
profiles and preserves existing cues, including intentionally empty profiles.
Removed gallery names are archived with `in_gallery=0` and omitted from current
exports. Their saved data is retained.

To replace generated samples with a varied set for the updated gallery:

```powershell
python .\rokid\server\seed_guest_preferences.py --regenerate-demo
```

This first creates a timestamped `.before-cues-...` SQLite backup beside the DB.
It replaces only `demo_random`/`demo_random_v2` rows; manual rows and non-demo
guests are preserved. Assignments are deterministic for the current gallery.
The original schema migrates automatically: existing rows become `prefer`
cues, and the old table is retained as `guest_preferences_v1`. Edit the current
table and rerun the script to refresh the preview and JSON export.

The server loads profiles into memory at startup and includes a `cues` array
with each recognized face in `/detect`. Unknown or missing profiles get an empty
array. At most two cues are sent, with allergy warnings first. The glasses render
the bundled symbols directly beneath the person's name, with separate corner
markers. They hide icons for Unknown, expired identities, lost/reused tracks,
ambiguous associations, and stopped sessions. Older servers without `cues` still
work but show names only. No extra profile or icon network requests are needed.

Restart the server after editing the database or changing gallery membership.
`GET /health` includes `cue_profile_count`. `GUEST_PREFERENCES_DB` optionally
selects another SQLite file. Unit/API tests use fake recognition results and
temporary databases, never real face matching. Device tests verify the real
HTTP parser and native vector rendering below names, including Unknown suppression.

Android vectors are generated from the shared SVG files. After icon/catalog edits:

```powershell
python .\rokid\server\generate_android_cue_icons.py
```

Rebuild/install the app afterward. The generated catalog contains twelve main
icons and three marker resources; all are bundled for immediate drawing.
