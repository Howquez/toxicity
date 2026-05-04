# Codebook: Stimulus Rating Study

**Study:** Advertising in Toxic Feeds — Toxicity Validation of Stimulus Corpus  
**Export source:** `ratings/custom_export` (oTree)  
**Unit of analysis:** One row per post per participant (long format). Participant-level variables repeat across all rows for the same participant.  
**Missing value convention:** Empty cells indicate the value was not recorded or not applicable.

---

## Design overview

Participants rated 38 posts on perceived toxicity (0–100 slider): 36 posts sampled from the stimulus corpus (stratified across 10 Perspective API score bins, 3–4 posts per bin) plus 2 embedded attention checks at fixed positions. After completing the rating task, participants answered three closing questions. Each participant completed 6 rating pages of 6–7 posts each.

**Attention check thresholds:**  
- Civil check post: must receive a rating ≤ 40 to pass  
- Toxic check post: must receive a rating ≥ 60 to pass  
- Participants who fail either check have `failed_attention = True`

---

## Participant-level variables

These variables take one value per participant and repeat across all post-level rows for that participant.

---

### session_code

| Field | Value |
|---|---|
| Type | String |
| Example | `cp3xw8a1` |
| Description | Unique identifier for the oTree session. Distinguishes data collected in separate deployment waves. |
| Missing | Never missing |

---

### participant_code

| Field | Value |
|---|---|
| Type | String |
| Example | `p8zqk2lm` |
| Description | Unique participant identifier assigned by oTree. Primary key for linking records within this dataset. |
| Missing | Never missing |

---

### valid_participant

| Field | Value |
|---|---|
| Type | Integer |
| Valid values | `1`, `0` |
| Description | Indicates whether the participant accessed the study via a valid Prolific recruitment link (`1`) or as a test/admin session without a Prolific ID (`0`). Rows with `valid_participant = 0` should be excluded from all analyses. The original Prolific participant ID is not included in this dataset to protect participant privacy. |
| Missing | Never missing |

---

### attn_civil_rating

| Field | Value |
|---|---|
| Type | Integer |
| Range | 0–100 |
| Description | Participant's toxicity rating (0 = not at all toxic, 100 = extremely toxic) for the civil attention-check post. Participants who rate this post above 40 are flagged as failing the attention check. |
| Missing | Empty if participant did not reach the attention-check page |

---

### attn_toxic_rating

| Field | Value |
|---|---|
| Type | Integer |
| Range | 0–100 |
| Description | Participant's toxicity rating for the toxic attention-check post. Participants who rate this post below 60 are flagged as failing the attention check. |
| Missing | Empty if participant did not reach the attention-check page |

---

### failed_attention

| Field | Value |
|---|---|
| Type | Boolean |
| Valid values | `True`, `False` |
| Description | Composite attention-check flag. `True` if `attn_civil_rating > 40` or `attn_toxic_rating < 60`; `False` if the participant passed both checks. Rows with `failed_attention = True` should be excluded from primary analyses. |
| Missing | Empty if attention-check data were not recorded |

---

### film_familiarity

| Field | Value |
|---|---|
| Type | Integer |
| Valid values | `1`, `2`, `3` |
| Labels | 1 = Never heard of it; 2 = Heard of it but have not seen it; 3 = Have seen it |
| Description | Participant's self-reported familiarity with the film *Avatar: Fire and Ash* (2025), the topic context of the stimulus corpus. Collected as a post-task closing question. |
| Missing | Empty if participant did not complete the closing questions |

---

### task_difficulty

| Field | Value |
|---|---|
| Type | Integer |
| Range | 1–7 |
| Labels | 1 = Very easy; 7 = Very difficult |
| Description | Participant's self-reported difficulty of the rating task. Collected as a post-task closing question. |
| Missing | Empty if participant did not complete the closing questions |

---

### open_feedback

| Field | Value |
|---|---|
| Type | String |
| Description | Optional free-text field for participant comments on the study. Empty if the participant did not provide feedback. |
| Missing | Empty if no feedback was provided |

---

## Post-level variables

These variables take one value per post per participant. Each participant contributes 38 rows (36 sampled posts plus 2 attention-check posts).

---

### doc_id

| Field | Value |
|---|---|
| Type | Integer or String |
| Example | `42`, `attn_civil`, `attn_toxic` |
| Description | Unique post identifier corresponding to the `doc_id` column in the stimulus corpus. The values `attn_civil` and `attn_toxic` identify the two attention-check posts, which are not part of the stimulus corpus. |
| Missing | Never missing |

---

### display_position

| Field | Value |
|---|---|
| Type | Integer |
| Range | 1–38 |
| Description | Position at which the post appeared in the 38-item sequence shown to the participant (1 = first post rated). Attention checks are inserted at fixed positions (civil check at position 9; toxic check at position 25). |
| Missing | Never missing |

---

### human_rating

| Field | Value |
|---|---|
| Type | Integer |
| Range | 0–100 |
| Labels | 0 = Not at all toxic; 100 = Extremely toxic |
| Description | Participant's perceived toxicity rating for the post, recorded via a continuous slider. The primary outcome of the rating study; used to validate the Perspective API and GPT-4o-mini scores against human judgment. |
| Missing | Empty if the participant did not submit a rating for this post |

---

### realism_rating

| Field | Value |
|---|---|
| Type | Integer |
| Range | 0–100 |
| Labels | 0 = Not at all realistic; 100 = Extremely realistic |
| Description | Intended to capture perceived realism for a random subsample of 3 posts per participant. The column is present in the export but contains no data: a recording error prevented values from being written to the database. This field should not be used. |
| Missing | Always empty |

---

### perspective_toxicity

| Field | Value |
|---|---|
| Type | Numeric (float) |
| Range | 0.0–1.0 |
| Description | Toxicity score assigned to the post by the Perspective API. Values above 0.6 were used to classify posts as toxic for the main experiment. Taken directly from the stimulus corpus; identical for all participants who rated the same post. Empty for attention-check posts, which are not part of the corpus. |
| Missing | Empty for attention-check posts |

---

### gpt_toxicity

| Field | Value |
|---|---|
| Type | Numeric (float) |
| Range | 0.0–1.0 |
| Description | Toxicity score assigned to the post by GPT-4o-mini. Taken directly from the stimulus corpus. Provides a second algorithmic benchmark for comparison with human ratings and the Perspective API. Empty for attention-check posts and any corpus posts for which the GPT-4o-mini score was not obtained. |
| Missing | Empty for attention-check posts or posts with missing GPT scores |