# References

Every quantitative claim added or corrected in the 2026 science refresh resolves to an
entry here. Source keys match those used in `data/cost_basis_2026.json`, so a number in
the economics derivation can be traced to a citation without leaving the repository.

**How to read this file.** Entries are grouped by domain. Each carries the figure the
repository actually uses, so a reader can check whether a document has drifted from its
source without opening the source. Figures were captured from these sources in **August
2026**; several are annual publications that will move. Anything not listed here is not
sourced, and the documents now say so explicitly rather than implying otherwise.

> **On paywalled and moving sources.** Lazard, BNEF and NREL ATB publish annually and
> revise. Where a primary PDF was not directly retrievable, the figure is attributed to
> the publisher and a retrievable secondary report is given alongside. Re-verify against
> the primary before citing externally.

---

## Energy cost and performance

**`lazard_lcoe_v18`** — Lazard, *Levelized Cost of Energy+*, version 18.0, June 16 2025.
Unsubsidized LCOE, USD/MWh: utility-scale solar PV **$38–78**; onshore wind **$37–86**;
gas combined cycle **$48–109**. Fuel assumptions: gas **$3.45/MMBtu**, coal
**$1.47/MMBtu**, nuclear **$0.85/MMBtu**. Solar and wind have been the lowest-cost
new-build generation for ten consecutive years; new-build CCGT capital cost reached a
ten-year high.
<https://www.lazard.com/research-insights/levelized-cost-of-energyplus/> ·
[press release](https://www.lazard.com/news-announcements/lazard-releases-2025-levelized-cost-of-energyplus-report-pr/) ·
[secondary, with ranges](https://www.pv-tech.org/us-utility-scale-solar-pv-lcoe-tightens-to-us38-78-mwh-in-2025-lazard/)

**`eia_capacity_factors_2025`** — U.S. Energy Information Administration, *Electric Power
Monthly*. 2025 U.S. annual average capacity factors: wind **34.2%**, utility-scale solar
**24.4%**, natural gas **58.4%**, coal **48.7%**, nuclear **91.0%**.
<https://www.eia.gov/electricity/monthly/>

**`eia_wind_solar_record_2025`** — EIA, *Wind and solar generated a record 17% of U.S.
electricity in 2025*. Wind **464,000 GWh** (+3% y/y); utility-scale solar **296,000 GWh**
(+34% y/y); combined **760,000 GWh**.
<https://www.eia.gov/todayinenergy/detail.php?id=67367>

**`eia_steo_2026`** — EIA, *Short-Term Energy Outlook*, August 2026. U.S. generation
forecast **4,327 billion kWh** in 2026, **+2.4%** year over year.
<https://www.eia.gov/outlooks/steo/>

**`eia_aeo_2026`** — EIA, *Annual Energy Outlook 2026*, April 2026. Installed generating
capacity grows **50–90% by 2050** across cases; gas, solar and wind supply about **80% of
generation** by 2050 in most cases; demand grows **0.9–1.6%/yr** through 2050, with data
centre load the dominant driver.
<https://www.eia.gov/outlooks/aeo/pdf/AEO_Narrative.pdf>

**`bnef_battery_survey_2025`** — BloombergNEF, *Lithium-Ion Battery Price Survey*,
December 2025. Global average pack price **$108/kWh** (−8% y/y). Stationary-storage packs
fell to **$70/kWh**, down **45%** y/y — the steepest decline of any segment, making
stationary storage the lowest-priced segment for the first time. Utility-scale **installed
system** cost, including balance of system, engineering and installation, runs
**$150–250/kWh**.
<https://about.bnef.com/insights/clean-transport/lithium-ion-battery-pack-prices-fall-to-108-per-kilowatt-hour-despite-rising-metal-prices-bloombergnef/> ·
[secondary](https://www.ess-news.com/2025/12/09/bnef-lithium-ion-battery-pack-prices-fall-to-108-kwh-stationary-storage-becomes-lowest-price-segment/)

**`nrel_atb`** — NREL, *Annual Technology Baseline*. As of August 2026 the most recent
published electricity edition remains the 2024 release (data updated April 2025); there is
no 2025 electricity ATB. Battery cost projections were updated separately in early 2025:
for a 60 MW / 4-hour system, CAPEX falls **18% (Conservative)**, **37% (Moderate)** or
**52% (Advanced)** between 2022 and 2035.
<https://atb.nrel.gov/> · [battery projections](https://docs.nrel.gov/docs/fy25osti/93281.pdf)

**`perovskite_record`** — NREL, *Best Research-Cell Efficiency Chart*. Perovskite–silicon
tandem: **34.85%** NREL-certified (LONGi, 18 April 2025) on a ~1 cm² device — the
citable benchmark as of 2026. Large-area (260.9 cm²) tandem **33.0%**. Commercial tandem
modules ship at **24.5%** (Oxford PV), a 7–10 point gap between laboratory record and
product.
<https://www.nrel.gov/pv/cell-efficiency.html>

---

## Transmission and grid

**`eia_hvdc_study`** — EIA, *Assessing HVDC Transmission for Impacts of Non-Dispatchable
Generation*. Per-mile HVDC project cost **$1.17M–$8.62M**, expressed in **2017 dollars**
— escalate before use.
<https://www.eia.gov/analysis/studies/electricity/hvdctransmission/pdf/transmission.pdf> ·
[summary](https://www.eia.gov/todayinenergy/detail.php?id=36393)

**`eei_underground_conversion`** — Edison Electric Institute, overhead-to-underground
conversion costs, as compiled in utility and industry filings. Minimum
**$536,760–$1,100,000/mile**; maximum **$6,000,000–$12,000,000/mile**. The low range is
distribution-class; the high range is the correct reference class for high-voltage
transmission and is what `data/cost_basis_2026.json` uses.
[Xcel comparison](https://cdn.xcelenergytransmission.com/blobvizxe609304b0a5/wp-content/uploads/2024/07/WWTConnection-Underground-Oct-2023.pdf) ·
[NextGen Highways buried HVDC](https://nextgenhighways.org/wp-content/uploads/2023/01/NGH_Buried-HVDC-Cost-Competitive.pdf)

**`iet_transmission_comparison`** — Institution of Engineering and Technology, *A
comparison of electricity transmission technologies: costs and characteristics* (2025).
Buried cable costs roughly **4.5×** the equivalent overhead line. Notes that HVDC cable
and converter-station supply chains have inflated faster than general construction
indices since 2021.
<https://www.theiet.org/impact-society/sustainability-and-climate-change/iet-electricity-transmission-technologies-report>

**`tse_hvdc_economics`** — Thunder Said Energy, *HVDC power transmission: the economics*.
Reference project **~$1,700/kW** for ~3 GW over ~1,500 km at 500 kV. Converter stations
are **30–40%** of total project capex — a fixed cost that makes HVDC uneconomic at short
distances regardless of line cost.
<https://thundersaidenergy.com/downloads/high-voltage-direct-current-power-transmission-hvdc-the-economics/>

**`miso_mtep25`** — MISO, *Transmission Cost Estimation Guide for MTEP25* (June 2025). The
appropriate reference class for substation and line cost estimation in this region. Used
here as a pointer for anyone replacing the repository's assumed substation costs with real
ones; MTEP26 is in stakeholder review.
<https://cdn.misoenergy.org/MISO%20Transmission%20Cost%20Estimation%20Guide%20for%20MTEP25337433.pdf>

**`brattle_transmission_2025`** — Brattle Group, *Transmission Landscape and Outlook:
Proactive Planning for a More Cost-effective and Affordable Energy Transition* (October
2025). Establishes that transmission investment is justified through multi-value
benefit-cost analysis — reliability, avoided generation capex, congestion relief — not
through a single return-on-investment percentage.
<https://www.brattle.com/wp-content/uploads/2025/10/Transmission-Landscape-and-Outlook-Proactive-Planning-for-a-More-Cost-effective-and-Affordable-Energy-Transition.pdf>

**`lbnl_ice`** — Lawrence Berkeley National Laboratory, *Interruption Cost Estimate (ICE)
Calculator*. The standard U.S. tool for monetising reliability improvements. The
repository's reliability claims are not currently quantified with it; this is the tool to
use if they are to be.
<https://icecalculator.com/>

**`ieee_2800`** — IEEE Std 2800-2022 and amendment 2800a, *Interconnection and
Interoperability of Inverter-Based Resources*. The amendment reduces technical barriers
for IBRs with grid-forming capability. Grid-forming inverters establish voltage and
frequency autonomously and provide synthetic inertia, unlike grid-following inverters
which require an existing grid reference.
<https://standards.ieee.org/ieee/2800a/12386/>

**`doe_gfm_specs`** — U.S. Department of Energy, *Specifications for Grid-forming
Inverter-based Resources, Version 1* (September 2023).
<https://www.energy.gov/sites/default/files/2023-09/Specs%20for%20GFM%20IBRs%20Version%201.pdf>

---

## Compute

**`nvidia_gb200_nvl72`** — NVIDIA, GB200 NVL72 platform documentation. Rack contains **72
Blackwell GPUs**, draws **120 kW nominal** (**130–132 kW** observed at full load), against
an industry-average rack of **7.6 kW**. GB200 Superchip package **1,200 W**; B200 GPU
**1,000 W** air-cooled or **1,200 W** liquid-cooled. Integrated direct liquid cooling
captures **~98%** of heat. NVIDIA claims **25× the performance of air-cooled H100 at equal
power**. For comparison, a DGX H100 (8 GPUs) draws **10–11 kW**.
<https://www.nvidia.com/en-us/data-center/gb200-nvl72/>

**`eia_datacenter_load`** — EIA, *Data center server energy use grows across the commercial
building stock*. Data centre load is the dominant driver of long-term U.S. electricity
growth. EIA revised ERCOT 2026 growth from 15.7% down to 9.6%; PJM grows 3.3% in both 2025
and 2026 — a caution that data-centre load forecasts are volatile.
<https://www.eia.gov/todayinenergy/detail.php?id=67704>

---

## Employment and regional economics

**`peri_employment_multipliers`** — Political Economy Research Institute, UMass Amherst
(Pollin et al.), *Employment Impacts of New U.S. Clean Energy, Manufacturing, and
Infrastructure Laws* (2023). Multipliers of **12.9–16 job-years per $1 million** invested,
inclusive of direct, indirect and induced effects; the lower end applies to capital
upgrades. The combined BIL, IRA and CHIPS investments support **~3 million jobs per year**
and **19 million job-years** in total. **These are job-years, not simultaneous headcount** —
the distinction the repository's original job figures did not make.
<https://www.peri.umass.edu/wp-content/uploads/joomla/images/publication/BIL_IRA_CHIPS_9-18-23-1.pdf>

**`eia_state_profiles`** — EIA, *State Electricity Profiles*, 2024 data. Minnesota retail
sales **64,562,108 MWh** at **12.35 ¢/kWh**; Wisconsin **68,291,424 MWh** at **12.72
¢/kWh**. These are the denominators against which the pilot's benefit claims are tested.
<https://www.eia.gov/electricity/state/minnesota/> ·
<https://www.eia.gov/electricity/state/wisconsin/>

---

## Ocean and climate

**`amoc_rapid_mccarthy_2025`** — McCarthy, G. D. et al. (2025), *Signal and Noise in the
Atlantic Meridional Overturning Circulation at 26°N*, **Geophysical Research Letters**.
RAPID array observes **1.0 [0.4–1.6] Sv per decade** weakening over 2004–2023 — consistent
with climate-model projections and **not** consistent with collapse in the mid-21st
century. Trends are not expected to become statistically "unfamiliar" (S/N > 2) until the
**2040s**, or "unknown" (S/N > 3) until the **2060s**.
DOI [10.1029/2025GL115055](https://doi.org/10.1029/2025GL115055)

**`amoc_sciadv_2025`** — *Observational constraints project a ~50% AMOC weakening by the
end of this century*, **Science Advances** (2025). Observationally constrained projection
of roughly **50% weakening by 2100** under high-emissions scenarios — substantial decline,
distinct from abrupt collapse.
DOI [10.1126/sciadv.adx4298](https://doi.org/10.1126/sciadv.adx4298)

**`amoc_opinion_2026`** — *Opinion: The AMOC is weakening — time to take the evidence
seriously*, EGUsphere preprint (2026). Argues for a larger decline at 26°N (**2.6 ± 0.7 Sv
per decade**, ~20 Sv falling to ~15 Sv). **Preprint, not peer-reviewed**, and in tension
with `amoc_rapid_mccarthy_2025`. Cited to show the magnitude is actively contested, not to
settle it.
<https://egusphere.copernicus.org/preprints/2026/egusphere-2026-2110/>

**`amoc_eddying_2026`** — *Weak 21st-century AMOC response to Greenland meltwater in a
strongly eddying ocean model* (2026). Eddy-resolving models show weaker meltwater
sensitivity than coarse models — relevant because meltwater-driven collapse is the
mechanism the repository's AMOC framework assumes.
<https://arxiv.org/abs/2602.17235>

**`nanoplastics_nature_2025`** — Nanoplastic concentrations across the North Atlantic,
**Nature**, 9 July 2025 (NIOZ / Utrecht). **27 million tonnes** of nanoplastics in the
North Atlantic — about **nine times** all larger plastic debris in every ocean combined;
**11.73–15.20 Mt** in the surface mixed layer alone. Concentrations **18.1 mg/m³** at the
surface, **10.9 mg/m³** at ~1 km, **5.5 mg/m³** near the seabed. Sampled at 12 stations.
Authors call the estimate conservative — some common polymers were not detectable by their
method.
DOI [10.1038/s41586-025-09218-1](https://doi.org/10.1038/s41586-025-09218-1)

---

## Materials, biology and waste

**`petase_acscatal_2023`** — *Assessment of Four Engineered PET Degrading Enzymes
Considering Large-Scale Industrial Applications*, **ACS Catalysis** (2023). Carbios'
**LCC-ICCG** converts **98% of PET to monomers in 24 hours**, outperforming both IsPETase
variants and PES-H1. Optimisation cut enzyme loading **3×** and reaction temperature from
**72 °C to 68 °C**. PES-H1(L92F/Q94Y) reached 80%.
DOI [10.1021/acscatal.3c02922](https://doi.org/10.1021/acscatal.3c02922)

**`mycelium_jof_2025`** — *The Fungus Among Us: Innovations and Applications of
Mycelium-Based Composites*, **Journal of Fungi** 11(8):549 (2025). Review of mycelium
composites across construction, manufacturing, agriculture and biomedicine.
DOI [10.3390/jof11080549](https://doi.org/10.3390/jof11080549)

**`mycelium_ann_2025`** — *Artificial Neural Network Prediction of Mechanical Properties in
Mycelium-Based Biocomposites*, **Polymers** 17(18):2506 (2025). ANN predicts internal
bonding at **R² = 0.992** and compressive strength at **R² = 0.979**.
DOI [10.3390/polym17182506](https://doi.org/10.3390/polym17182506)

**`mycelium_buildings_2025`** — *Development and Evaluation of Mycelium-Based Composites
from Agroforestry Residues*, **Buildings** 15(11):1764 (2025). Pre-cultured mixtures reach
compressive strength **≥ 0.08 MPa** and flexural strength **≥ 11 N**. **These are
insulation-class numbers, roughly four orders of magnitude below structural concrete** —
the constraint that governs where mycelium composites can be used.
<https://www.mdpi.com/2075-5309/15/11/1764>

**`mycelium_architecture_2025`** — *A Review of Mycelium-Based Composites in Architectural
and Design Applications*, **Sustainability** 17(24):11350 (2025). Thermal insulation,
acoustic absorption and fire performance are where these materials compete; load-bearing
structure is not.
<https://www.mdpi.com/2071-1050/17/24/11350>

**`physarum_review`** — Sun, Y., *Physarum-inspired Network Optimization: A Review*.
Physarum-derived algorithms solve shortest path, minimum-risk path, network design, and
Voronoi/Delaunay construction by reinforcing high-load links and pruning unused ones.
<https://arxiv.org/abs/1712.02910>

**`physarum_viscosity_2025`** — *A mathematical model to predict network growth in Physarum
polycephalum as a function of extracellular matrix viscosity* (2025). Higher matrix
viscosity slows network expansion but **does not change final network complexity** —
fractal dimension converges across all viscosity conditions. Directly relevant to any
claim that a physical substrate limits achievable network topology.
<https://pubmed.ncbi.nlm.nih.gov/40037543/>

**`physarum_microtubular_2025`** — *Physarum polycephalum-inspired adaptive optimization
design of artificial microtubular networks*, **Science China Chemistry** (2025).
DOI [10.1007/s11426-024-2305-8](https://doi.org/10.1007/s11426-024-2305-8)

---

## Storage physics

**`caes_nature_reviews_2026`** — *Technologies and prospects for compressed air energy
storage*, **Nature Reviews Clean Technology** (2026). Global cost analysis shows a **15%
experience rate** as capacity scaled from 10 to 100 MW.
DOI [10.1038/s44359-026-00150-9](https://doi.org/10.1038/s44359-026-00150-9)

**`caes_iscience_2025`** — *Cost-reducing adiabatic compressed air energy storage for long
duration energy-storage applications*, **iScience** (2025). Adiabatic CAES is viable for
**10–100 hour** storage durations — the regime where lithium-ion is uneconomic.
<https://www.cell.com/iscience/fulltext/S2589-0042(25)02228-X>

**`caes_efficiency_2025`** — Measured and modelled CAES round-trip efficiencies: liquid
piston adiabatic with packed-bed thermal storage **72.6%**; underwater adiabatic **64.1%**
under real operating conditions; gravity-assisted isobaric shaft system **87.1% energy
efficiency / 70.1% exergy efficiency** under optimised conditions (**modelled, not
built**). Compressors reach **>84.4%** adiabatic efficiency off-design.
[gravity-isobaric study](https://www.sciencedirect.com/science/article/pii/S2214157X25004654) ·
[summary](https://www.pv-magazine.com/2025/07/18/compressed-air-energy-storage-enhanced-by-gravity/)

---

## RF energy harvesting

**`rectenna_review_2025`** — *Advancements in Antenna and Rectifier Systems for RF Energy
Harvesting: A Systematic Review and Meta-Analysis*, **Applied Sciences** 15(14):7773
(2025). Reported power conversion efficiency up to **97.18%** with antenna gain 7.31 dBi.
**This peak is measured at high input power in a controlled setup and is not
representative of ambient harvesting.**
DOI [10.3390/app15147773](https://doi.org/10.3390/app15147773)

**`rectenna_broadband_2025`** — *Broadband compact rectenna system using a Wilkinson power
divider*, **Scientific Reports** (2025). Average PCE **32% across 2–18 GHz at −5 dBm** —
the realistic ambient-power figure, and the one any energy-harvesting design should be
sized against. Principal loss mechanisms: rectifier diode non-linearity, transmission-line
attenuation, antenna–rectifier impedance mismatch.
DOI [10.1038/s41598-025-02555-1](https://doi.org/10.1038/s41598-025-02555-1)

---

## Air quality and material degradation

**`ozone_acp_2025`** — *A comprehensive review of tropospheric background ozone*,
**Atmospheric Chemistry and Physics** 25:15145 (2025). Regional background O₃ ranges
**33–48 ppb** (meta-analysis mean 41 ppb), with an increasing trend.
DOI [10.5194/acp-25-15145-2025](https://doi.org/10.5194/acp-25-15145-2025)

**`epa_ozone_trends`** — U.S. EPA, *Trends in Ozone Adjusted for Weather Conditions*.
Weather-adjusted U.S. ozone has fallen about **10 ppb** in May–September average and about
**20 ppb** at the 98th percentile since 2002 — U.S. ozone exposure is **declining**, which
runs opposite to the assumption in the repository's air-quality cascade module.
<https://www.epa.gov/air-trends/trends-ozone-adjusted-weather-conditions>

**`ozone_elastomer_testing`** — JIS K 6259-1:2015. Accelerated ozone testing of vulcanised
rubber uses **250–2,000 ppb**, i.e. **5–50× ambient background**. Degradation rates from
accelerated tests must not be applied directly to field conditions without a transfer
function.

---

## Land and soil

**`lal_drylands`** — Lal, R., *Carbon Sequestration in Dryland Ecosystems*, **Environmental
Management**. Drylands cover **6.15 billion ha / 47.2%** of land area, of which **3.5–4.0
Bha (57–65%)** are desertified or prone to it. Dryland soils hold **241 Pg** of soil
organic carbon — **15.5%** of the global 1,550 Pg to 1 m depth. Desertification has caused
**20–30 Pg** of historic carbon loss; assuming two-thirds is recoverable gives a
sequestration potential of **12–20 Pg C over 50 years**, or roughly **1 Pg C/yr globally**
and **50 Tg C/yr** for the United States.
DOI [10.1007/s00267-003-9110-9](https://doi.org/10.1007/s00267-003-9110-9)

**`ldn_soil_carbon_2025`** — *Soil Carbon Sequestration Potential in Achieving Land
Degradation Neutrality* (2025). Current framing of UNCCD Land Degradation Neutrality
targets against soil-carbon potential.
DOI [10.1007/978-981-96-3392-0_9](https://doi.org/10.1007/978-981-96-3392-0_9)

**`dryland_restoration_2024`** — *Ecological restoration enhances dryland carbon stock by
reducing surface soil carbon loss due to wind erosion*. Finds grazing exclusion more
effective than afforestation for restoring soil organic carbon on severely desertified
land — a directly actionable result for the `Desertification/` module.
<https://pmc.ncbi.nlm.nih.gov/articles/PMC11573679/>

---

## Citation policy for this repository

1. A figure in any document either resolves to an entry above, or is explicitly labelled
   as an assumption. There is no third category.
2. Ranges are reported as the source reports them. Where a source gives low–high bounds
   (Lazard, EEI), those are **not** confidence intervals and are not treated as such.
3. Laboratory records and field performance are never presented as the same number. Where
   both exist — perovskite tandems, rectenna efficiency, CAES round-trip — both are given.
4. Preprints are marked as preprints. `amoc_opinion_2026` is retained specifically because
   it disagrees with the peer-reviewed observation record; suppressing the disagreement
   would misrepresent the state of the field.
5. Modelled results are distinguished from built systems. The 87.1%-efficient
   gravity-isobaric CAES system has not been constructed.
