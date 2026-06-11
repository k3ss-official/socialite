# Product Requirements Document (PRD)

**Product:** Socialite Design  
**Version:** 0.1 (MVP)  
**Date:** May 27, 2026  
**Owner:** Tony / k3ss-official

## 1. Problem

Small tourism and hospitality businesses **worldwide** have active social media presence (especially Facebook and Instagram) but poor or non-existent professional websites. They lose customers to competitors who have modern, fast-loading online presence with clear booking and contact systems.

## 2. Solution

**Socialite Design** is a **global autonomous agent platform** that:

- Identifies businesses with strong social media but weak or missing websites
- Scrapes and analyses their social content
- Generates personalised, high-converting landing page previews
- Performs competitor gap analysis
- Recommends high-value upsells (online booking, local payment integration, etc.)
- Delivers a ready-to-present preview + professional pitch that on-ground teams can use to close deals

The platform is designed as a **global system** from day one. **Pokhara, Nepal** has been selected as the **initial MVP test market** because part of the core team is based there, enabling fast on-ground validation and deal closing during the pilot phase.

## 3. MVP Scope (First Test Market: Pokhara Tourism)

**Target vertical (MVP test):** Hotels, guesthouses, cafes, rafting and trekking operators in Pokhara, Nepal.

**Goals:**
- Generate 15–20 qualified leads per week
- Hybrid model: AI generates content + on-ground validation team validates and closes
- Clean, mobile-friendly internal dashboard (Streamlit) for the validation team

**Positioning note:** Pokhara is the **first test market only**. The system is built from day one as a scalable global platform.

## 4. Tech Stack (Crawl Phase)

- Hermes Agent (self-improving core)
- Scrapling (adaptive scraping + MCP)
- Crawl4AI (clean structured output)
- notebooklm-py (RAG synthesis)
- Streamlit dashboard (internal team use only)

## 5. Success Metrics (MVP – Pokhara Test Market)

- 5+ real qualified leads appear in the dashboard within 48 hours of launch
- ≥12% positive reply rate from on-ground team outreach
- At least 1 closed deal or strong verbal commitment within the first week

## 6. Phase 2 (Post-MVP – Global Rollout)

- Move to full production hosting (managed/white-label infrastructure)
- Expand to other tourism destinations **worldwide** (not limited to Nepal)
- Add payment flows and client self-service options where appropriate
- Revenue model: Per-lead fee or percentage of closed deals

## 7. Risks & Mitigations

- Scraping anti-bot measures → Adaptive scraping (Scrapling) + multiple fallbacks + human review layer
- Low conversion in test market → Strong on-ground team + human touch in the pilot location
- Cost overrun → Hard $2/lead cap with automatic kill switch
- Over-reliance on one geography → Explicit global architecture from day one; Pokhara is only the pilot

## 8. Next Actions

See TODO.md for current sprint tasks.