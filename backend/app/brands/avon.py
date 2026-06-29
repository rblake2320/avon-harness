"""Avon brand configuration — The Avon Company (US entity, LG H&H owned).

Last verified: June 24, 2026. Update this header whenever facts are re-verified.

ENTITY STRUCTURE (current as of June 2026):
  The Avon Company   — US/Canada/Puerto Rico — owned by LG H&H (Korean beauty co.)
                       OPERATIONALLY STABLE. North America +35% Q1 2026.
                       New CEO Lee Sun-ju (ex-L'Oreal, appointed Sept 2025).
                       This is the entity our reps belong to.
  Avon International — Europe/Africa/Asia — sold to Regent LP, Dec 31 2025 for £1.
                       Still operating as of June 2026; strategy opaque.
                       $25M Natura credit line expires Dec 2026 — first pressure point.
  Avon Latin America — Retained by Natura&Co. Strong growth (Brazil +5%).
  Avon Russia        — Sold to Arnest Group ~€26.9M, Feb 2026.
  Avon Products Inc. — The bankrupt US parent. LIQUIDATION TRUST effective Oct 7, 2025.
                       No longer a business. US entity (LG H&H) was never part of it.

PRICING: Campaign-based (~every 2 weeks). NO fixed price list. Never quote prices.

ANELE: Avon's own built-in AI assistant in the Avon ON app (v3.1.3, Mar 2026).
  Known to be broken — login errors, argues with users, broken social sharing.
  3.96/5 from 26,000 reviews. We are better than this. Do not mention Anele.

FTC: No official US Income Disclosure Statement published by Avon.
"""
from .base import BrandConfig

AVON = BrandConfig(
    name="avon",
    display_name="Avon",
    assistant_voice=(
        "You are a professional assistant for Avon Representatives with The Avon Company "
        "(US entity, owned by LG H&H). The US business is separate from any international "
        "Avon entities and is fully operational."
    ),
    price_facts="""
AVON PRICING — CRITICAL RULE: Avon uses campaign-based pricing. Brochure prices
change every campaign (~2 weeks). NEVER quote specific prices under any circumstances.
Always direct the rep to: "Check the current campaign brochure on AvonNow or the
Avon ON app — prices change every campaign."

AVON PRODUCT LINES (education only — no prices):
Skincare:
  Anew (flagship line — lead with this):
    Anew Ultimate     — Multi-performance anti-aging, retinol
    Anew Vitamin C    — Brightening, dark spots, luminosity
    Anew Clinical     — Advanced treatments: peels, gap fillers, retexturizers
    Anew Platinum     — Designed for 70+ skin, lifting and firming
    Anew Reversalist  — Cell renewal and repair
  Skin So Soft       — Iconic since 1961. Bath oil, Bug Guard, body lotions.
    Bug Guard is the highest-volume product seasonally (spring/summer).
    Lead with Bug Guard for outdoor lifestyle customers.
  Hydra Fusion       — Hyaluronic acid hydration line
  Clearskin          — Acne and oily skin concern line
  AVON CHI ESSENTIALS — Haircare line, launched late 2025 (newer addition)
Makeup:
  True Color         — Core cosmetics: foundation, lip, eye
  Fmg Cashmere       — Premium foundation sub-line
  Glimmerstick       — Precision eye and lip liners
Fragrance:
  Far Away, Imari, Today, Haiku — core fragrance lines; campaign-exclusive launches frequent
Fashion & Home:
  Lower commission tier (25% max) — de-prioritize vs. Beauty/Jewelry for earnings

BUSINESS / COMPENSATION (verified June 2026 — per-campaign, resets each campaign):
  Beauty & Jewelry commission tiers (per-campaign order total):
    $40  – $119   →  20%
    $120 – $349   →  30%
    $350 – $1,499 →  40%
    $1,500 – $6,499 → 45%
    $6,500+       →  50%
  Fashion & Home: max 25% regardless of volume
  CRITICAL: $40 minimum per campaign — below $40 earns ZERO commission
  CRITICAL: 3 campaigns without an order = automatic account deactivation
  Additional income: leadership bonuses, fundraising commissions, team bonuses

GUEST CHECKOUT — THE #1 REP COMPLAINT (June 2026):
  When a customer checks out as a guest through the rep's link, Avon keeps the
  commission — the rep earns nothing. ALWAYS coach reps to:
  "Ask every customer to create an Avon account using your link before checkout.
   Guest checkout loses your commission entirely."

Income/FTC compliance: Avon does NOT publish an official US Income Disclosure Statement
  as of June 2026. The FTC (Act §5) treats ANY statement implying a minimum income
  level as an earnings claim requiring substantiation. Independent analysis indicates
  most active Avon reps net $50–150/month after brochure, bag, and delivery costs.
  NEVER imply reps will earn more than typical. Direct recruits to avon.com for the
  current compensation plan — never make income projections of any kind.
  The $40/campaign floor and 3-campaign deactivation rule mean income is inconsistent
  for part-time sellers; be honest about this if asked.
""",
    ids_reference="avon.com for the current compensation plan details",
    avg_order_value_usd=55.0,
    follow_up_coaching=(
        " AVON GUEST CHECKOUT — include naturally in every follow-up: coach the customer "
        "to create an Avon account through the rep's personal link before placing an order. "
        "Guest checkout means the rep earns zero commission. Weave this in as helpful advice "
        "for the customer ('logging in gets you order history, easier returns, exclusive member "
        "pricing') — never as a complaint about Avon's checkout."
    ),
    product_categories=[
        "skincare", "color cosmetics", "fragrance", "body care", "bug protection",
        "bath and body", "wellness", "haircare",
    ],
    # Avon-specific patterns from FTC scrutiny and state AG actions against Avon distributors.
    extra_income_patterns=[
        "avon can change your life",
        "avon will make you rich",
        "unlimited avon earnings",
        "avon pays better than",
        "fire your boss with avon",
        "avon income will replace",
    ],
)
