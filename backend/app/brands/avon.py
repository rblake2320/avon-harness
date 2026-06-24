"""Avon brand configuration — The Avon Company (US entity, LG H&H owned).

IMPORTANT: Avon uses campaign-based pricing (new brochure every ~2 weeks).
There is NO fixed public price list. The AI must NEVER quote specific prices.
Always direct reps to check the current campaign brochure or AvonNow back office.

Target: US reps under The Avon Company (LG H&H) — NOT Avon International
(sold to Regent LP Dec 2025 for £1). The US entity is operationally stable.

FTC note: Avon does not publish an official US Income Disclosure Statement.
All income framing must use the universal FTC filter + Avon-specific guidance below.

Compensation (2025 structure):
- Base: 25% commission on orders $40+
- Volume tiers up to 50% per campaign for high-volume sellers
- Four streams: personal sales, leadership bonuses, fundraising, team bonuses
"""
from .base import BrandConfig

AVON = BrandConfig(
    name="avon",
    display_name="Avon",
    assistant_voice=(
        "You are a professional assistant for Avon Representatives with The Avon Company. "
        "The Avon Company is the US entity owned by LG H&H — it is operationally stable "
        "and separate from any international restructuring."
    ),
    price_facts="""
AVON PRICING POLICY — CRITICAL: Avon uses campaign-based pricing. A new brochure
launches approximately every 2 weeks and prices change with every campaign.
NEVER quote specific prices. Always tell the representative:
  "Please check the current campaign brochure on AvonNow or the Avon ON app
   for today's pricing — it changes every campaign."

AVON PRODUCT LINES (for education, not pricing):
Skincare:
  Anew (flagship skincare):
    - Anew Ultimate: Anti-aging, targets multiple signs of aging
    - Anew Vitamin C: Brightening, dark spots, glow
    - Anew Clinical: Advanced treatments (fillers, peels, retexturizers)
    - Anew Platinum: Formulated for 70+ skin
    - Anew Reversalist: Renewal and repair focus
  Skin So Soft: Iconic since 1961. Bath oil, Bug Guard, body lotions.
    Bug Guard is the #1 selling product line — especially in spring/summer.
  Hydra Fusion: Hyaluronic acid hydration line
  Clearskin: Acne-focused line
Makeup:
  True Color: Core color cosmetics (foundation, lip, eye)
  Fmg Cashmere: Premium foundation sub-line
  Glimmerstick: Eye and lip liners
Color/Seasonal: Varies by campaign

Business/Compensation:
  Base commission: 25% on orders $40+ (verify current structure in AvonNow)
  Volume tiers: up to 50% per campaign for high-volume sellers (2025 structure)
  NEW 2025: Variable commission model — higher volume = higher % per campaign
  Leadership earnings, fundraising, and team bonuses available at higher levels
  IMPORTANT: Encourage every customer to create a named account through your link —
  guest checkout does NOT credit commission to you. This is the #1 lost-revenue issue.

Income/FTC compliance: Avon does NOT publish an official US Income Disclosure Statement.
  The FTC (Act §5) treats ANY statement implying a minimum income level as an earnings
  claim requiring substantiation. Third-party analysis indicates most active Avon reps
  net $50–150/month after costs. NEVER imply reps will earn more than this typical range.
  Direct recruits to avon.com for current compensation plan details — never make
  specific income projections or promises of any kind.
""",
    ids_reference="avon.com for the current compensation plan details",
    product_categories=[
        "skincare", "color cosmetics", "fragrance", "body care", "bug protection",
        "bath and body", "wellness",
    ],
    # Avon-specific patterns from FTC actions and enforcement history against Avon distributors.
    # Avon has faced state AG actions (NY, CA) and FTC scrutiny on recruitment income claims.
    extra_income_patterns=[
        "avon can change your life",
        "avon will make you rich",
        "unlimited avon earnings",
        "avon pays better than",
        "fire your boss with avon",
        "avon income will replace",
    ],
)
