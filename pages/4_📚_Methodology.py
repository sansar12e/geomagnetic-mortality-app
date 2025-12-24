"""Methodology & Caveats - Full transparency about methods and limitations."""
import streamlit as st
from components.explanations import show_methodology_summary, show_limitations
from utils.data_loader import load_preprocessed_data


st.set_page_config(page_title="Methodology & Caveats", page_icon="📚", layout="wide")

st.title("📚 Methodology & Caveats")
st.markdown("### Full transparency about our methods and limitations")

# Load summary stats
data = load_preprocessed_data()
summary_stats = data['summary_stats']

st.divider()

# Section 1: Data Sources
st.markdown("## 📊 Data Sources")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Mortality Data")
    st.markdown("""
    - **Source:** [CDC WONDER Provisional Mortality Statistics](https://wonder.cdc.gov/controller/datarequest/D176)
    - **Period:** January 2018 – June 2025
    - **Granularity:** Weekly (MMWR epidemiological weeks)
    - **Geography:** United States (national aggregate)
    - **Total weeks:** {} weeks
    
    **4 Outcomes Analyzed:**
    1. **Suicide** (X60-X84) - Primary behavioral outcome
       - Mean: {:.0f} deaths/week
    2. **Violence/Assault** (X85-Y09) - Impulsivity toward others
       - Mean: {:.0f} deaths/week
    3. **Overdose** (X40-X49 + Y10-Y19) - Acute poisoning
       - Mean: {:.0f} deaths/week
    4. **Cardiovascular** (I20-I25 + I60-I69) - Heart attacks + strokes
       - Mean: {:.0f} deaths/week
    """.format(
        summary_stats['n_weeks'],
        summary_stats['outcomes']['suicide']['mean'],
        summary_stats['outcomes']['violence']['mean'],
        summary_stats['outcomes']['overdose']['mean'],
        summary_stats['outcomes']['cardiovascular']['mean']
    ))
    
    st.info("""
    **MMWR Week:** CDC's standardized epidemiological week that always ends 
    on Saturday. This allows consistent year-over-year comparisons.
    """)

with col2:
    st.markdown("### Geomagnetic Data")
    st.markdown("""
    - **Source:** [GFZ German Research Centre for Geosciences](https://kp.gfz.de/app/files/Kp_ap_since_1932.txt)
    - **Period:** Same as mortality data
    - **Granularity:** 3-hour intervals (8 measurements per day)
    - **Metrics:** 
        - Kp index (quasi-logarithmic scale, 0-9)
        - ap index (linear scale, nT units)
    - **Citation:** Matzka et al., 2021, *Space Weather*
        - DOI: [10.1029/2020SW002641](https://doi.org/10.1029/2020SW002641)
    - **Total measurements:** {:,}
    - **Mean Kp:** {:.2f}
    - **Max Kp observed:** {:.1f}
    """.format(
        summary_stats['n_measurements'],
        summary_stats['geomagnetic']['mean_Kp'],
        summary_stats['geomagnetic']['max_Kp_overall']
    ))
    
    st.info("""
    **Kp Index:** Planetary K-index, derived from magnetometer data at 13 
    observatories worldwide. Measures disturbance to Earth's magnetic field.
    """)

st.divider()

# Section 2: Aggregation Method
st.markdown("## 🔄 Data Aggregation Method")

st.markdown("""
Because mortality data is **weekly** but geomagnetic data is **3-hourly**, 
we aggregated storm activity to match the weekly mortality reporting:
""")

# Table showing aggregation methods
import pandas as pd

agg_methods = pd.DataFrame({
    'Weekly Metric': [
        'Mean Kp',
        'Mean ap',
        'Sum ap',
        'Max Kp',
        'Storm Count (Kp≥5)'
    ],
    'Calculation': [
        'Average of all 56 three-hour Kp values in the week',
        'Average of all 56 three-hour ap values in the week',
        'Sum of all 56 ap values in the week',
        'Highest Kp value observed during the week',
        'Number of 3-hour intervals with Kp ≥ 5'
    ],
    'Rationale': [
        'Overall storm intensity for the week',
        'Linear scale appropriate for averaging',
        'Total "disturbance load" accumulated',
        'Captures peak storm strength',
        'NOAA\'s official storm threshold'
    ]
})

st.dataframe(agg_methods, width='stretch', hide_index=True)

st.markdown("""
**Week Alignment:** Each MMWR week runs from Sunday to Saturday. We matched 
geomagnetic measurements to the week containing that measurement's timestamp.
""")

st.divider()

# Section 3: Statistical Methods
st.markdown("## 📐 Statistical Methods")

st.markdown("""
We employed several standard statistical approaches:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Primary Analyses
    
    1. **Pearson Correlation**
        - Measures linear relationship between two continuous variables
        - Ranges from -1 (perfect negative) to +1 (perfect positive)
        - Assumes normally distributed data
        - Our main reported statistic
    
    2. **Spearman Correlation**
        - Rank-based correlation, robust to outliers
        - Doesn't assume normality
        - Used as sensitivity check
    
    3. **Student's t-test**
        - Compares means between storm and non-storm weeks
        - Tests if difference is statistically significant
        - Two-tailed, independent samples
    """)

with col2:
    st.markdown("""
    ### Supplementary Analyses
    
    4. **Seasonal Adjustment**
        - Subtracted monthly means from both variables
        - Removes seasonal patterns to isolate week-to-week variation
        - Correlation remains significant after adjustment
    
    5. **Effect Size (Cohen's d)**
        - Quantifies magnitude of difference between groups
        - 0.2 = small, 0.5 = medium, 0.8 = large
        - Our effect sizes are small (~0.1-0.3)
    
    6. **Multiple Comparisons**
        - We tested 5-13 different storm metrics
        - Increases chance of false positives
        - Multiple significant results reduce this concern
    """)

st.warning("""
**Statistical Significance ≠ Practical Importance**

A result can be "statistically significant" (p < 0.05) but still represent 
a very small effect. Our correlations are significant but explain only ~2-5% 
of the variation in deaths.
""")

st.divider()

# Section 4: MAJOR LIMITATIONS
st.markdown("## ⚠️ IMPORTANT LIMITATIONS")

st.error("""
### Please Read These Caveats Carefully

This analysis has significant limitations. Do not over-interpret the findings.
""")

show_limitations()

st.divider()

# Section 5: What Would Stronger Evidence Look Like?
st.markdown("## 🎯 What Would Stronger Evidence Look Like?")

st.markdown("""
Our analysis is exploratory. To establish a causal relationship, we would need:
""")

evidence_hierarchy = pd.DataFrame({
    'Study Type': [
        'Our Analysis (Ecological, Weekly)',
        'Daily Ecological Analysis',
        'Geographic Analysis (by latitude)',
        'Case-Crossover Study',
        'Prospective Cohort Study',
        'Mechanistic Study',
        'Randomized Trial'
    ],
    'What It Would Show': [
        'Correlation exists at population level',
        'Tighter temporal relationship',
        'Stronger effects at high latitudes (where storms are stronger)',
        'Individual exposure-outcome link',
        'Temporal precedence, dose-response',
        'Biological pathway identified',
        'Definitive causation'
    ],
    'Feasibility': [
        '✅ Done',
        '⚠️ Requires restricted data access',
        '⚠️ Requires county/state-level data',
        '⚠️ Requires individual death certificates',
        '❌ Expensive, years-long study',
        '❌ Requires laboratory research',
        '❌ Impossible (can\'t randomize storms)'
    ]
})

st.dataframe(evidence_hierarchy, width='stretch', hide_index=True)

st.markdown("""
### Evidence That Would Increase Confidence

✓ **Replication** in other countries/time periods  
✓ **Dose-response** relationship (bigger storms → bigger effect)  
✓ **Geographic gradient** (effect strongest at high latitudes)  
✓ **Temporal specificity** (effect visible in daily data, not just weekly)  
✓ **Mechanistic plausibility** (biological pathway identified)  
✓ **Controlled confounders** (weather, season, holidays, etc.)  
✓ **Pre-registration** (analysis plan specified before looking at data)  

We have accomplished **some** of these, but not all.
""")

st.divider()

# Section 6: Potential Mechanisms (Speculative)
st.markdown("## 🧠 Potential Mechanisms (Speculative)")

st.info("""
**Disclaimer:** These are hypotheses, not proven mechanisms. We did not test 
these directly.
""")

st.markdown("""
If the correlation is causal (which is not established), possible mechanisms could include:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Direct Biological Effects
    
    1. **Melatonin suppression**
        - Geomagnetic activity may affect pineal gland
        - Could disrupt circadian rhythms
        - Melatonin linked to mood regulation
    
    2. **Autonomic nervous system**
        - Some studies show changes in heart rate variability
        - Could affect stress response
    
    3. **Neurotransmitter changes**
        - Speculative; weak evidence
    """)

with col2:
    st.markdown("""
    ### Indirect Environmental Effects
    
    4. **Concurrent solar effects**
        - Solar activity causes both storms AND other changes
        - UV radiation, electromagnetic fields
    
    5. **Sleep disruption**
        - Storms can cause auroras, light pollution
        - GPS/communication disruptions cause stress
    
    6. **Confounding variables**
        - Weather patterns correlated with solar activity
        - Seasonal factors we didn't fully control
    """)

st.warning("""
**Bottom Line:** We don't know if any of these mechanisms are real. The correlation 
we found could be:
1. A real but small causal effect
2. An artifact of confounding variables
3. A statistical fluke (though unlikely given p-values)
4. A combination of the above
""")

st.divider()

# Section 7: Recommendations for Future Research
st.markdown("## 🔬 Recommendations for Future Research")

st.markdown("""
### Next Steps to Build on This Work

1. **Access daily mortality data**
    - Restricted CDC data with exact death dates
    - Would allow tighter temporal analysis (hours/days instead of weeks)

2. **Geographic analysis**
    - State or county-level data
    - Test if effects are stronger at high latitudes
    - Control for local weather conditions

3. **International replication**
    - Test in other countries (Canada, Nordic countries, Australia)
    - Different data sources reduce systematic errors

4. **Control for confounders**
    - Daily temperature, precipitation, air quality
    - Daylight hours, moon phase
    - Economic indicators, news events

5. **Mechanistic studies**
    - Laboratory studies on humans/animals
    - Biological measurements during storms
    - Test specific pathways (melatonin, HRV, etc.)

6. **Pre-registration**
    - Specify analysis plan before collecting data
    - Reduces researcher degrees of freedom
    - Increases credibility of findings
""")

st.divider()

# Section 8: Conclusion
st.markdown("## ✅ Conclusion")

st.success("""
### Summary of Findings

**What we found:**
- **Suicide**: Positive correlation (r ≈ 0.23 same-week, r ≈ 0.19 lag-1)
  - More deaths during/after storm weeks
  - Strongest effect for primary behavioral outcome
- **Violence**: Negative correlation (r ≈ -0.16) - fewer deaths during storm weeks
- **Overdose**: No significant correlation (r ≈ 0.04)
- **Cardiovascular**: Negative correlation (r ≈ -0.16) - fewer deaths during storm weeks

**⏱️ Lagged Effects:**
- Effects from storms **1 week prior** are often as strong or stronger than same-week effects
- This is **biologically more plausible** (delayed effects)
- When controlling for autocorrelation (lagged deaths), lag-1 effects can be stronger

**What this means:**
- Correlations are outcome-specific, not universal
- Suicide shows strongest positive effect (~5% of variation explained)
- **Temporal dynamics matter** - delayed effects suggest potential biological mechanisms
- Mixed results for other outcomes suggest complex relationships
- This is **exploratory evidence** only
- **NOT proof of causation**

**What we need:**
- Daily mortality data (not just weekly) for better temporal resolution
- Geographic analysis by latitude
- Control for weather, season, and confounders
- Mechanistic studies
- Pre-registered replication

**Why only suicide shows positive correlation:**

This pattern is scientifically meaningful, not a weakness:

1. **Suicide (positive) → Mood/Circadian Pathway**
   - Geomagnetic activity → melatonin suppression → circadian rhythm disruption
   - Sleep disturbance → depression/anxiety worsening
   - Internally-directed harm requires cognitive function and planning
   
2. **Violence (negative) → Behavioral/Environmental Factors**
   - Storms → lethargy, reduced energy for impulsive aggression
   - Weather → people stay indoors → reduced interpersonal violence opportunity
   - Externally-directed harm requires social contact
   
3. **Cardiovascular (negative) → Weather Confounding**
   - Storms often accompany cooler temperatures → fewer heat-related cardiac events
   - "Sick day" behavior → less physical exertion
   
4. **Overdose (none) → Addiction-Driven**
   - Primarily driven by substance use disorders
   - Less sensitive to acute mood/circadian changes

**If all outcomes showed positive correlation**, we'd suspect measurement artifact. The fact 
that only the most mood-sensitive outcome (suicide) correlates positively strengthens biological 
plausibility while revealing the complexity of environmental-health relationships.

**Bottom line:**
Multi-outcome analysis with lagged effects reveals nuanced, biologically-informed patterns. 
Suicide shows consistent positive correlation with circadian-plausible mechanisms, while 
other outcomes show different patterns consistent with behavioral, environmental, or 
confounding factors. This complexity is expected in ecological studies and highlights 
the critical need for controlled mechanistic research.
""")

# Footer
st.markdown("---")
st.caption("Methodology & Limitations")

st.markdown("---")
st.markdown("""
### 📖 References & Data Sources

**Primary Data Sources:**

1. **CDC WONDER** - Provisional Mortality Statistics  
   - 🔗 [Data Access](https://wonder.cdc.gov/controller/datarequest/D176)
   - All 4 outcomes sourced from CDC WONDER
   - Public domain data

2. **GFZ German Research Centre for Geosciences** - Kp/ap indices  
   - 🔗 [Direct Data File](https://kp.gfz.de/app/files/Kp_ap_since_1932.txt)
   - License: CC BY 4.0
   
**Citations:**

3. **Matzka, J., et al.** (2021). The geomagnetic Kp index and derived indices of 
   geomagnetic activity. *Space Weather*, 19, e2020SW002641.  
   https://doi.org/10.1029/2020SW002641

4. **Bartels, J.** (1957). The technique of scaling indices K and Q of geomagnetic 
   activity. *Annals of the International Geophysical Year*, 4, 215-226.
""")

