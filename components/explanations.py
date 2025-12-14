"""Text explanation generators."""
import streamlit as st


def show_caveat_banner(mode='full'):
    """Display caveat banner.
    
    Args:
        mode: 'full' for detailed warning (landing page), 'compact' for brief reminder (other pages)
    """
    if mode == 'full':
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255, 140, 60, 0.12) 0%, rgba(255, 180, 80, 0.08) 100%);
                    padding: 20px; 
                    border-radius: 8px; 
                    border: 1px solid rgba(255, 160, 80, 0.4);
                    border-left: 4px solid #ff8c3c;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
                    backdrop-filter: blur(10px);">
            <strong style="color: #ffb366; font-size: 1.1rem;">⚠️ Note:</strong> 
            <span style="color: #e0e0e8;">This analysis shows <strong style="color: #fff;">correlation, not causation</strong>. 
            Effects are small, and other factors (weather, seasons, holidays) could explain observed patterns.
            See Methodology for limitations.</span>
        </div>
        """, unsafe_allow_html=True)
    else:  # compact
        st.info("Note: These are correlations, not causal relationships. See Methodology for limitations.")


def explain_correlation():
    """Explain what correlation means."""
    with st.expander("What is correlation?"):
        st.markdown("""
        Correlation measures how two variables move together, ranging from -1 to +1:
        
        - **+1**: Perfect positive (when one increases, other always increases)
        - **0**: No relationship (variables move independently)
        - **-1**: Perfect negative (when one increases, other decreases)
        
        Observed correlations (~0.1-0.2) are weak, indicating slight tendency to move together 
        with substantial noise. Correlation does not imply causation.
        """)


def explain_p_value():
    """Explain what p-value means."""
    with st.expander("What is a p-value?"):
        st.markdown("""
        The p-value indicates the probability of observing this pattern if no true relationship exists.
        
        - **p < 0.05**: Statistically significant (unlikely due to chance alone)
        - **p ≥ 0.05**: Not statistically significant
        
        Most observed p-values are below 0.05. Note that statistical significance does not 
        imply large effect size or causation.
        """)


def explain_kp_index():
    """Explain the Kp index."""
    st.markdown("""
    ### What's a Kp Index?
    
    The **Kp index** measures how much Earth's magnetic field is being 
    disturbed by solar activity. It's measured every 3 hours at observatories around the world.
    
    - **Kp 0-4:** Normal conditions (most of the time)
    - **Kp 5+:** Geomagnetic storm (this is what we're studying)
    - **Kp 7+:** Strong storm (can affect power grids, GPS)
    - **Kp 9:** Extreme (rare, maybe once per solar cycle)
    
    During our study period (2018-2025), the average Kp was about 1.7, with storms 
    (Kp ≥ 5) occurring in roughly 1 out of every 10 measurement intervals.
    """)


def explain_mmwr_week():
    """Explain MMWR weeks."""
    with st.expander("📖 What is an MMWR week?"):
        st.markdown("""
        **MMWR** stands for "Morbidity and Mortality Weekly Report" from the CDC.
        
        MMWR weeks are standardized epidemiological weeks that:
        - Always end on Saturday
        - Are numbered 1-52 (or 53 in some years)
        - Allow consistent year-over-year comparisons
        
        We use MMWR weeks because that's how the CDC reports mortality data.
        """)


def explain_outcome_types():
    """Explain the 4 outcome types being analyzed."""
    with st.expander("📖 Why these 4 outcomes?"):
        st.markdown("""
        We analyze 4 different health outcomes to test the specificity of magnetic-health correlations:
        
        **1. Suicide (X60-X84)** - Primary behavioral outcome
        - Deaths by intentional self-harm
        - Our main outcome of interest
        - Tests acute mental health effects
        
        **2. Violence/Assault (X85-Y09)** - Impulsivity toward others
        - Deaths from assault and homicide
        - Tests if impulsive harm extends beyond self
        - Similar behavioral pathway as suicide
        
        **3. Overdose (X40-X49 + Y10-Y19)** - Acute poisoning
        - Accidental + undetermined intent poisonings
        - May involve impaired judgment
        - Could reflect acute distress or confusion
        
        **4. Cardiovascular (I20-I25 + I60-I69)** - Physiological control
        - Heart attacks (I20-I25) + Strokes (I60-I69)
        - Tests acute physiological stress pathway
        - Helps distinguish mental vs physical effects
        
        **Why this design?** If magnetic activity truly affects mental health, we'd expect:
        - Strong effects on suicide (mental/behavioral)
        - Possibly on violence (also behavioral)
        - Weaker or no effects on cardiovascular (physical pathway)
        
        If *all* outcomes correlate strongly, it might suggest confounding factors rather than specific effects.
        """)


def explain_mixed_results():
    """Explain why only suicide shows positive correlation."""
    with st.expander("Why only suicide shows positive correlation?"):
        st.markdown("""
        If all outcomes showed identical correlations, measurement artifact or confounding 
        would be likely. Mixed patterns suggest outcome-specific mechanisms:
        
        **Suicide (positive correlation)**
        
        Possible pathway: Circadian/melatonin disruption
        - Geomagnetic activity → melatonin suppression → sleep disturbance
        - Sleep problems → mood deterioration in vulnerable individuals
        - Internally-directed harm
        
        **Violence (negative correlation)**
        
        Possible explanations:
        - Storms → lethargy → reduced impulsive aggression
        - Weather → people stay indoors → less interpersonal contact
        - Externally-directed harm requires energy and opportunity
        
        **Cardiovascular (negative correlation)**
        
        Likely confounding:
        - Storms often accompany cooler weather → fewer heat-related cardiac events
        - Reduced physical exertion during storms
        
        **Overdose (no correlation)**
        
        Different drivers:
        - Primarily driven by substance use disorders
        - Less sensitive to short-term environmental changes
        
        ---
        
        **Interpretation:**
        
        Outcome-specific patterns suggest:
        1. Not simple measurement artifact
        2. Potential biological specificity for mood-related outcomes
        3. Complex interactions with environmental and behavioral factors
        
        This complexity underscores the exploratory nature of ecological studies and the 
        need for controlled research before drawing causal conclusions.
        """)


def show_methodology_summary():
    """Display brief methodology summary."""
    st.markdown("""
    ### Data Sources
    - **Mortality:** CDC WONDER Provisional Mortality Statistics (2018-2025)
        - 4 outcomes: Suicide, Violence, Overdose, Cardiovascular
        - United States, national aggregate
        - [Data source](https://wonder.cdc.gov/controller/datarequest/D176)
    - **Geomagnetic:** GFZ German Research Centre for Geosciences
        - Kp and ap indices, measured every 3 hours
        - [Data source](https://kp.gfz.de/app/files/Kp_ap_since_1932.txt)
    
    ### Method
    1. Aggregated 3-hour geomagnetic measurements into weekly summaries
    2. Merged with weekly mortality data (identical method for all 4 outcomes)
    3. Computed correlations between storm metrics and each outcome
    4. Tested for statistical significance (Pearson & Spearman)
    """)


def show_limitations():
    """Display study limitations - concise version."""
    st.error("""
    ### ⚠️ Important Limitations
    
    This is an **exploratory ecological study**. Key limitations:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **1. Correlation ≠ Causation**
        - We found variables move together
        - Did NOT prove causation
        - Other factors could explain patterns
        
        **2. Ecological Fallacy**
        - Population-level data only
        - Cannot make individual-level claims
        - National trends ≠ personal risk
        """)
    
    with col2:
        st.markdown("""
        **3. Temporal Limitations**
        - Weekly bins may obscure acute effects
        - Daily data would be much stronger
        
        **4. Uncontrolled Confounders**
        - Weather, seasons, holidays
        - Economic factors
        - COVID-19 pandemic
        - Geographic variation
        """)
    
    with st.expander("📖 What would stronger evidence require?"):
        st.markdown("""
        To establish causality, we would need:
        - **Daily mortality data** (not just weekly)
        - **Individual-level data** with dates and locations
        - **Control for confounders** (weather, season, etc.)
        - **Geographic analysis** (test if effects stronger at high latitudes)
        - **Replication** in other countries/time periods
        - **Pre-registration** of analysis plan
        
        Our analysis is a reasonable **first step** for exploratory purposes, but much more 
        work is needed before any causal claims can be made.
        """)

