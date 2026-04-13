# Pre-Registration: Feed-Level Toxicity and Advertising Effectiveness on Social Media

> **Pilot study.** This study is explicitly designed as a pilot. The primary goals are to (1) validate the stimulus materials and DICE interface, and (2) obtain preliminary estimates of effect sizes and functional forms to power a confirmatory study. Analytical degrees of freedom are marked **[pilot d.f.]** throughout.

---

## 1. Research Questions and Hypotheses

**H1:** The effect of feed-level toxicity on feed engagement (total dwell time, time on feed) is characterized by an inverted-U relationship: engagement increases with the proportion of toxic posts up to a moderate threshold and decreases beyond it.

**H2:** The effect of feed-level toxicity on ad engagement (ad dwell time, ad clickthrough rate, ad recall) mirrors H1 and is characterized by an inverted-U relationship: engagement increases with the proportion of toxic posts up to a moderate threshold and decreases beyond it.

**RQ1 (exploratory):** How does feed-level toxicity affect brand attitude toward the co-located advertiser?

---

## 2. Study Design

Participants are exposed to a single simulated social media feed implemented in DICE (an oTree application). The feed displays 25 posts about the movie *Avatar: Fire and Ash*, drawn from a pool of AI-generated posts with Perspective API toxicity scores ranging from approximately 0 to 0.93. Feed-level toxicity is manipulated continuously: each participant is assigned a toxicity target drawn from a uniform distribution across the full range, and posts are sampled using a Gaussian-weighted algorithm that selects 25 posts whose mean toxicity approximates that target. Post sets therefore vary across participants, which is intentional — the randomness in stimulus sampling cancels out latent confounds (e.g., specific post content) and supports causal inference about the toxicity dose.

A single sponsored post (by the brand M&M's) is embedded at feed position 14 as a fixed-position ad. It does not contribute to the toxicity target calculation.

After browsing the feed, participants complete a Qualtrics survey.

---

## 3. Measures

### 3.1 Feed Engagement (oTree, behavioral)
- **Time spent on feed**: seconds from preloader dismissal to submit click
- **Scroll depth**: display position of the furthest post with dwell time > 0, expressed as a proportion of the feed (furthest post rank / 25); posts that never reached 75% visibility receive dwell time = 0 and are treated as not reached

### 3.2 Ad Engagement (oTree + Qualtrics)
- **Ad dwell time**: dwell time (s) logged for the M&M's sponsored post, using a 75%-visibility threshold
- **Ad click (CTR)**: binary indicator of whether the participant clicked the ad's call-to-action button (lottery sign-up), recorded in oTree as `lottery_signup`; aggregated as the proportion of participants who clicked across toxicity levels
- **Unaided recall**: open-text brand recall ("list any brands from which you recall seeing an ad")
- **Aided recall**: multiple-choice brand recognition

### 3.3 Brand Attitude (Qualtrics)
- Brand attitude: scale (Grewal et al. 2025) 
- Brand trust: single item (Grewal et al. 2025)
- Brand commitment: multi-item scale (Grewal et al. 2025)
- Purchase intent: slider (Bernritter et al. 2025)
- Brand choice: forced-choice item (Bernritter et al. 2025)

### 3.4 Covariates
- Mood and arousal (post-feed)
- Attribution of ad placement responsibility
- Prior movie exposure and liking
- Social media usage frequency
- Brand familiarity
- Demographics (age, gender, ethnicity)

---

## 4. Analysis Plan

This is a dose-response design: feed-level toxicity is continuous and each participant receives a different dose, which provides rich data on the shape of the relationship across the full toxicity range. With N = 200, the primary goal is not confirmatory hypothesis testing but rather learning about effect sizes, functional forms, and the location of any inflection point.

The analyses for H1 and H2 are oriented around the two-lines test (Simonsohn 2018), which assesses whether the relationship between toxicity dose and an outcome first increases and then decreases — without assuming a parabolic form. Results will be treated as indicative rather than confirmatory. For RQ1, brand attitude outcomes are plotted and modeled against the toxicity dose in the same exploratory spirit.


---

## 5. Participants and Recruitment

Participants are recruited via Prolific. Max concurrent participants is capped at 20 to avoid server overload. Target sample: **N = 200**.

Eligibility criteria: **[pilot d.f. — to be confirmed from Prolific screening settings before launch]**

---

## 6. Implementation

- Platform: oTree 5.x, deployed on Heroku
- Survey: Qualtrics (redirected after feed exposure, with `PROLIFIC_PID` passed as URL parameter)
- Completion code: assigned via Prolific upon redirect
