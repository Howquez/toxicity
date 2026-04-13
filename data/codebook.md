# Codebook: DICE Feed Experiment

**Study:** Advertising in Toxic Feeds: Ad Effectiveness & Brand Safety  
**Export source:** `DICE/custom_export` (oTree)  
**Unit of analysis:** One row per participant per post (long format). Participant-level variables repeat across all rows for the same participant.  
**Missing value convention:** Empty cells indicate the value was not recorded or not applicable (e.g., `dwell_time` is empty if the post never entered the viewport; `reply` is empty if the participant did not compose a reply).

---

## Participant-level variables

These variables take one value per participant and repeat across all post-level rows for that participant.

---

### session_code

| Field | Value |
|---|---|
| Type | String |
| Example | `cp3xw8a1` |
| Description | Unique identifier for the oTree session in which the participant took part. Distinguishes data collected in separate deployments or waves. |
| Missing | Never missing |

---

### participant_code

| Field | Value |
|---|---|
| Type | String |
| Example | `p8zqk2lm` |
| Description | Unique identifier assigned to the participant by oTree. Serves as the primary key for linking participant-level records across tables. |
| Missing | Never missing |

---

### participant_label

| Field | Value |
|---|---|
| Type | String |
| Example | `5e3f2a1b8c9d4e6f` |
| Description | External participant identifier passed to oTree via URL parameter at recruitment (Prolific ID). Used to link oTree records to Prolific and Qualtrics survey data. Empty if the participant accessed the study without a label parameter. |
| Missing | Empty if participant accessed without a Prolific label |

---

### condition

| Field | Value |
|---|---|
| Type | String |
| Description | Discrete feed condition label inherited from a legacy condition-column design. Not used in the current dose-response design; retained for backward compatibility with earlier data collections. |
| Missing | Empty in current design |

---

### feed_toxicity

| Field | Value |
|---|---|
| Type | Numeric (float) |
| Range | 0.0 -- 1.0 |
| Unit | Proportion |
| Example | `0.44` |
| Description | Realized proportion of toxic posts (Perspective API score $\geq$ 0.6) in the participant's feed, excluding the fixed-position sponsored post. Computed as the mean of the binary `is_toxic` indicator across the 25 sampled regular posts. This is the primary treatment variable. Doses are drawn from a uniform grid across participants and randomly assigned, so the distribution of `feed_toxicity` across participants is approximately uniform. |
| Missing | Empty if feed sampling was not activated (i.e., `feed_size` not configured) |

---

### lottery_signup

| Field | Value |
|---|---|
| Type | Boolean |
| Valid values | `True`, `False` |
| Description | Indicates whether the participant entered a lottery draw presented within the feed. Serves as a behavioral measure of active engagement with the sponsored content. |
| Missing | Empty if participant did not reach the feed submission step |

---

### time_on_feed

| Field | Value |
|---|---|
| Type | Numeric (float) |
| Unit | Seconds |
| Example | `47.32` |
| Description | Total time elapsed between the feed preloader disappearing and the participant clicking "Done browsing." Captures overall browsing duration regardless of which posts were viewed. |
| Missing | Empty if timing data were not recorded |

---

### device_type

| Field | Value |
|---|---|
| Type | String |
| Valid values | `mobile`, `tablet`, `desktop` |
| Description | Participant's device category, classified from browser screen width at the time of feed exposure. Used as a covariate because feed rendering and dwell-time measurement differ across device types. |
| Missing | Empty if device detection script did not execute |

---

### is_touch_device

| Field | Value |
|---|---|
| Type | Boolean |
| Valid values | `True`, `False` |
| Description | Indicates whether the participant used a touch-capable device. Complements `device_type` as touch interaction affects scrolling behavior and dwell-time measurement. |
| Missing | Empty if device detection script did not execute |

---

### screen_resolution

| Field | Value |
|---|---|
| Type | String |
| Format | `<width>x<height>` in pixels |
| Example | `1440x900` |
| Description | Browser viewport dimensions at the time of feed exposure. Used to assess whether post heights and focal-line crossings are comparable across participants. |
| Missing | Empty if device detection script did not execute |

---

### time_started

| Field | Value |
|---|---|
| Type | Datetime string |
| Format | `YYYY-MM-DD HH:MM:SS` (UTC) |
| Example | `2026-03-15 14:03:22` |
| Description | Timestamp at which the participant began the oTree session. Used for wave identification and exclusion of incomplete or interrupted sessions. |
| Missing | Empty if session start timestamp was not recorded |

---

### completed_feed

| Field | Value |
|---|---|
| Type | Boolean |
| Valid values | `True`, `False` |
| Description | Indicates whether the participant submitted the feed page. Participants who dropped out before clicking "Done browsing" have `False`. Rows with `completed_feed = False` should be excluded from primary analyses. |
| Missing | Defaults to `False` if not explicitly set |

---

## Post-level variables

These variables take one value per post per participant. Each participant contributes as many rows as posts in their feed (25 regular posts plus the sponsored post).

---

### doc_id

| Field | Value |
|---|---|
| Type | Integer |
| Example | `42` |
| Description | Unique identifier for the post, corresponding to the `doc_id` column in the stimulus corpus. Links post-level behavioral records back to post-level stimulus attributes (text, toxicity score, `is_toxic` flag, etc.). |
| Missing | Never missing |

---

### displayed_sequence

| Field | Value |
|---|---|
| Type | Integer |
| Range | 1 -- 26 (for a feed of 25 regular posts plus 1 sponsored post) |
| Description | Position at which the post appeared in the feed as displayed to the participant (1 = topmost post). Reflects the randomized display order, including the insertion of the fixed-position sponsored post. Used to construct adjacency covariates (toxicity of posts immediately above and below the sponsored post). |
| Missing | Never missing |

---

### dwell_time

| Field | Value |
|---|---|
| Type | Numeric (float) |
| Unit | Seconds |
| Example | `3.241` |
| Description | Total time the post was visible within the participant's browser viewport, summed across all viewport entry and exit events. A post accumulates dwell time whenever any part of it is within the visible scroll area, regardless of whether the participant was actively reading it. Zero or empty indicates the post was never scrolled into view. |
| Missing | Empty if the post never entered the viewport |

---

### focal_dwell_time

| Field | Value |
|---|---|
| Type | Numeric (float) |
| Unit | Seconds |
| Example | `1.804` |
| Description | Cumulative time the post spent crossing the focal line, a horizontal reference line positioned at one-third of the viewport height from the top. A post registers focal dwell time only while it occupies the focal line position, providing a stricter measure of sustained central attention than viewport dwell time alone. |
| Missing | Empty if the post never crossed the focal line |

---

### liked

| Field | Value |
|---|---|
| Type | Boolean |
| Valid values | `True`, `False` |
| Description | Indicates whether the participant clicked the like button on this post. Serves as a measure of active positive engagement at the post level. |
| Missing | Empty if engagement data were not recorded |

---

### reply

| Field | Value |
|---|---|
| Type | String |
| Description | Text of the reply the participant composed for this post, if any. Free-text field; empty if the participant did not reply. |
| Missing | Empty if no reply was composed |

---

### has_reply

| Field | Value |
|---|---|
| Type | Boolean |
| Valid values | `True`, `False` |
| Description | Indicates whether the participant composed any reply text for this post, regardless of content. Derived from `reply`; provided as a convenience indicator for engagement analyses that do not require the reply text itself. |
| Missing | Empty if engagement data were not recorded |

---

### post_height_px

| Field | Value |
|---|---|
| Type | Integer |
| Unit | Pixels |
| Example | `312` |
| Description | Rendered height of the post element in the participant's browser. Varies across participants due to differences in screen width, device type, and font rendering. Used to normalize dwell-time measures and to verify that post heights are consistent within device type. |
| Missing | Empty if height measurement was not captured |

---

### creative_image

| Field | Value |
|---|---|
| Type | String |
| Example | `creatives/disney_plus_ad.jpg` |
| Description | File path or URL of the creative image assigned to this post, if any. A random subset of posts in each feed is assigned a creative image drawn from the creatives pool. Empty for posts that were displayed as text-only. For the sponsored post, the creative is fixed and identical across all participants. |
| Missing | Empty if no creative image was assigned to this post |
