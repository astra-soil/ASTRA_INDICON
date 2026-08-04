# IMD raw response captures — 04 August 2026

This directory holds the raw JSON responses returned by IMD's live API
endpoints on 04 August 2026, referenced by Section IV-E of the paper.

**Files to place here** (author will commit before repo goes public):

- `cityforecastloc.json` — full response of
  `GET https://api.imd.gov.in/api/v1/cityforecastloc`
  captured at ~18:59 IST on 04 August 2026.
  1,274 station forecasts, ~1.86 MB.
  Source of the Jammu-City record shown in the paper's Table III.

- `districtwarning.json` — full response of
  `GET https://api.imd.gov.in/api/v1/districtwarning`
  captured at ~13:58 IST on 04 August 2026.
  730 district warnings.
  Source of the Jammu district Y/Y/O/O/O sequence reported in Section IV-E.

These files are exactly what the API returned; no transformation has
been applied. Reviewers can therefore verify the paper's parsed values
end-to-end without their own IMD API access.

Note that IMD may impose per-request rate limits and IP whitelisting;
reviewers wishing to reproduce a live call themselves will need their
own IMD credentials.
