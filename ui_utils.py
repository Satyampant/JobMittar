
import streamlit as st

# Color palette
COLORS = {
    # Primary palette - Gold accent (used sparingly)
    "primary": "#FFB81C",      # Vibrant Gold (strategic accent only)
    "secondary": "#6C63FF",    # Soft Purple (main secondary color)
    "tertiary": "#4A90E2",     # Soft Blue (tertiary accent)

    # Accent colors - Complementary cool tones
    "accent": "#5B7C99",       # Steel Blue
    "accent1": "#7B68EE",      # Medium Slate Blue
    "accent2": "#20B2AA",      # Light Sea Green
    "accent3": "#FF6B9D",      # Soft Pink

    # Functional colors - Status indicators
    "success": "#4CAF50",      # Green (keep for success)
    "warning": "#FF9800",      # Amber warning
    "error": "#F44336",        # Red (keep for errors)
    "info": "#4A90E2",         # Blue for info (changed from gold)

    # Background and text - Dark mode optimized
    "background": "#0E1117",   # Dark background
    "card_bg": "#1F2430",      # Card/container background
    "text": "#FAFAFA",         # Light text
    "text_dark": "#FAFAFA",    # Light text (for dark backgrounds)
    "text_light": "#E0E0E0",   # Slightly dimmed text
    "text_red": "#FF5252",     # Error text
    "panel_bg": "#1A1D23"      # Panel background (darker than card)
}


def apply_styling():
    st.markdown(f"""
    <style>
        /* Global font styling */
        * {{
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif !important;
        }}

        /* Main header styling - Purple to Blue gradient */
        h1, h2, .main-header {{
            color: white !important;
            background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['tertiary']}) !important;
            padding: 20px !important;
            border-radius: 8px !important;
            margin-bottom: 20px !important;
            font-weight: bold !important;
            box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3) !important;
        }}

        /* Gold accent panels (used sparingly) */
        .gold-accent {{
            color: #1A1D23 !important;
            background: linear-gradient(135deg, {COLORS['primary']}, #FFA500) !important;
            padding: 15px !important;
            border-radius: 6px !important;
            box-shadow: 0 2px 8px rgba(255, 184, 28, 0.4) !important;
        }}

        /* Purple panels - new default for important sections */
        div[style*="background-color: {COLORS['primary']}"],
        [data-testid="stForm"] h3,
        .purple-header {{
            color: white !important;
            font-size: 1.2rem !important;
            font-weight: bold !important;
            padding: 15px !important;
            border-radius: 6px !important;
            margin-bottom: 15px !important;
            background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['accent1']}) !important;
            box-shadow: 0 2px 8px rgba(108, 99, 255, 0.4) !important;
        }}

        /* Buttons styled with purple gradient */
        .stButton>button,
        button[kind="primary"] {{
            background: linear-gradient(135deg, {COLORS["secondary"]}, {COLORS["tertiary"]}) !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 6px !important;
            padding: 0.6rem 1.2rem !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(108, 99, 255, 0.4) !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            font-size: 16px !important;
            height: auto !important;
        }}

        .stButton>button:hover,
        button[kind="primary"]:hover {{
            background: linear-gradient(135deg, {COLORS["accent1"]}, {COLORS["secondary"]}) !important;
            box-shadow: 0 6px 16px rgba(108, 99, 255, 0.6) !important;
            transform: translateY(-2px) !important;
        }}

        /* Slider styling - purple accent */
        .stSlider > div > div > div > div {{
            background-color: {COLORS["secondary"]} !important;
        }}

        /* Progress bar - gold kept for visual feedback */
        .stProgress > div > div > div {{
            background: linear-gradient(90deg, {COLORS["primary"]}, {COLORS["secondary"]}) !important;
        }}

        /* Tables */
        table, .dataframe, [data-testid="stTable"] {{
            width: 100% !important;
            border-collapse: collapse !important;
            margin-bottom: 20px !important;
            border-radius: 4px !important;
            overflow: hidden !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        }}

        /* Table headers - Blue gradient instead of gold */
        th, thead tr th {{
            background: linear-gradient(135deg, {COLORS['tertiary']}, {COLORS['accent']}) !important;
            color: white !important;
            font-weight: bold !important;
            padding: 12px 8px !important;
            text-align: left !important;
            border: none !important;
        }}

        /* Table cells */
        td, tbody tr td {{
            padding: 12px 8px !important;
            border-bottom: 1px solid #2A2E38 !important;
            background-color: {COLORS['card_bg']} !important;
            color: {COLORS['text']} !important;
        }}

        /* Alternate row styling */
        tbody tr:nth-child(even) td {{
            background-color: #262A34 !important;
        }}

        /* Tab navigation with purple/blue accents */
        div[data-baseweb="tab-list"] {{
            gap: 0 !important;
            background-color: {COLORS["card_bg"]} !important;
            padding: 10px !important;
            border-radius: 12px !important;
            display: flex !important;
            justify-content: space-between !important;
            width: 100% !important;
            margin-bottom: 20px !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.4) !important;
        }}

        div[data-baseweb="tab-list"] button {{
            flex: 1 !important;
            text-align: center !important;
            margin: 0 5px !important;
            height: 60px !important;
            font-size: 16px !important;
            background-color: #262A34 !important;
            color: {COLORS["text_light"]} !important;
            border-radius: 8px !important;
            border: 1px solid #3A3E48 !important;
            transition: all 0.3s ease !important;
        }}

        div[data-baseweb="tab-list"] button[aria-selected="true"] {{
            background: linear-gradient(135deg, {COLORS["secondary"]}, {COLORS["tertiary"]}) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 16px rgba(108, 99, 255, 0.5) !important;
            transform: translateY(-2px) !important;
        }}

        div[data-baseweb="tab-list"] button:hover:not([aria-selected="true"]) {{
            background-color: #363A44 !important;
            border-color: {COLORS["secondary"]} !important;
        }}

        /* Input fields - subtle blue border on focus */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {{
            background-color: {COLORS['card_bg']} !important;
            color: {COLORS['text']} !important;
            border: 1px solid #3A3E48 !important;
            border-radius: 4px !important;
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: {COLORS['secondary']} !important;
            box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.2) !important;
        }}

        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background-color: {COLORS['card_bg']} !important;
        }}

        /* Links with purple color */
        a {{
            color: {COLORS['secondary']} !important;
            text-decoration: none !important;
        }}

        a:hover {{
            color: {COLORS['tertiary']} !important;
            text-decoration: underline !important;
        }}

        /* Expander with purple accent */
        .streamlit-expanderHeader {{
            background-color: {COLORS['card_bg']} !important;
            border-left: 3px solid {COLORS['secondary']} !important;
        }}

        /* Success/Info/Warning boxes */
        .stAlert {{
            border-left-width: 4px !important;
        }}

        /* Info alert with blue */
        div[data-baseweb="notification"][kind="info"] {{
            background-color: rgba(74, 144, 226, 0.1) !important;
            border-left-color: {COLORS['tertiary']} !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def display_resume_analysis_summary(resume_data):
    if not resume_data:
        st.warning("Resume data is not available.")
        return

    analysis = resume_data.get("analysis", {})
    
    if not analysis or not isinstance(analysis, dict):
        st.warning("Resume analysis is not available. Please re-upload your resume.")
        return

    st.subheader("Resume Analysis Summary")
    
    if analysis.get("overall_assessment"):
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['secondary']}, {COLORS['tertiary']}); 
        color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; 
        box-shadow: 0 4px 16px rgba(108, 99, 255, 0.3);">
        <h4 style="margin: 0 0 10px 0; color: white;">📊 Overall Assessment</h4>
        <p style="margin: 0; line-height: 1.6; font-weight: 500;">{analysis['overall_assessment']}</p>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""<h4 style="color: {COLORS['success']}; margin-bottom: 10px;">💪 Strengths</h4>""", 
                    unsafe_allow_html=True)
        strengths = analysis.get("strengths", [])
        
        if strengths:
            for strength in strengths:
                st.markdown(
                    f"""<div style="background: linear-gradient(135deg, {COLORS['success']}, #45A049); 
                    color: white; padding: 12px; border-radius: 6px; margin-bottom: 10px; 
                    font-weight: 500; box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);">
                    ✅ {strength}</div>""", 
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                f"""<div style="background-color: {COLORS['card_bg']}; color: {COLORS['text_light']}; 
                padding: 12px; border-radius: 6px;">Analysis unavailable</div>""", 
                unsafe_allow_html=True
            )

    with col2:
        st.markdown(f"""<h4 style="color: {COLORS['warning']}; margin-bottom: 10px;">🎯 Areas to Improve</h4>""", 
                    unsafe_allow_html=True)
        weaknesses = analysis.get("weaknesses", [])
        
        if weaknesses:
            for weakness in weaknesses:
                st.markdown(
                    f"""<div style="background: linear-gradient(135deg, {COLORS['warning']}, #FB8C00); 
                    color: white; padding: 12px; border-radius: 6px; margin-bottom: 10px; 
                    font-weight: 500; box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);">
                    ⚠️ {weakness}</div>""", 
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                f"""<div style="background-color: {COLORS['card_bg']}; color: {COLORS['text_light']}; 
                padding: 12px; border-radius: 6px;">Analysis unavailable</div>""", 
                unsafe_allow_html=True
            )


def display_extracted_information(resume_data):
    if not resume_data:
        st.warning("Resume data is not available.")
        return

    st.subheader("Extracted Information")

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.markdown(f"""<h4 style="color: {COLORS['tertiary']}; margin-bottom: 10px;">📞 Contact Information</h4>""", 
                    unsafe_allow_html=True)
        contact_info = resume_data.get("contact_info", {})
        contact_html = f"""<div style="background-color: {COLORS['card_bg']}; color: {COLORS['text']}; 
        padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid {COLORS['tertiary']};">"""

        if contact_info and (contact_info.get("email") or contact_info.get("phone")):
            if contact_info.get("email"):
                contact_html += f"<p><strong style='color: {COLORS['tertiary']}'>Email:</strong> {contact_info['email']}</p>"
            if contact_info.get("phone"):
                contact_html += f"<p><strong style='color: {COLORS['tertiary']}'>Phone:</strong> {contact_info['phone']}</p>"
        else:
            contact_html += "<p>No contact information detected.</p>"

        contact_html += "</div>"
        st.markdown(contact_html, unsafe_allow_html=True)

        st.markdown(f"""<h4 style="color: {COLORS['secondary']}; margin-bottom: 10px;">🎓 Education</h4>""", 
                    unsafe_allow_html=True)
        education = resume_data.get("education", [])
        education_html = f"""<div style="background-color: {COLORS['card_bg']}; color: {COLORS['text']}; 
        padding: 15px; border-radius: 8px; border-left: 4px solid {COLORS['secondary']};">"""

        if education:
            for edu in education:
                education_html += f"<p>• {edu}</p>"
        else:
            education_html += "<p>No education information detected.</p>"

        education_html += "</div>"
        st.markdown(education_html, unsafe_allow_html=True)

    with info_col2:
        st.markdown(f"""<h4 style="color: {COLORS['primary']}; margin-bottom: 10px;">🛠️ Skills</h4>""", 
                    unsafe_allow_html=True)
        skills = resume_data.get("skills", [])

        if skills:
            skills_html = """<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px;">"""
            colors = [
                f"linear-gradient(135deg, {COLORS['primary']}, #FFA500)",
                f"linear-gradient(135deg, {COLORS['secondary']}, {COLORS['accent1']})",
                f"linear-gradient(135deg, {COLORS['tertiary']}, {COLORS['accent']})",
                f"linear-gradient(135deg, {COLORS['accent2']}, #1E90FF)"
            ]
            for idx, skill in enumerate(skills):
                color = colors[idx % len(colors)]
                text_color = "white" if idx % 4 != 0 else "#1A1D23"
                skills_html += f"""<div style="background: {color}; 
                color: {text_color}; padding: 8px 14px; border-radius: 20px; font-weight: 600; 
                margin-bottom: 8px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);">
                {skill}</div>"""
            skills_html += "</div>"
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.markdown(
                f"""<div style="background-color: {COLORS['card_bg']}; color: {COLORS['text_light']}; 
                padding: 15px; border-radius: 8px;">No skills detected.</div>""", 
                unsafe_allow_html=True
            )

        st.markdown(f"""<h4 style="color: {COLORS['accent2']}; margin-bottom: 10px;">💼 Experience</h4>""", 
                    unsafe_allow_html=True)
        experience = resume_data.get("experience", [])

        if experience:
            exp_html = f"""<div style="background-color: {COLORS['card_bg']}; color: {COLORS['text']}; 
            padding: 15px; border-radius: 8px; border-left: 4px solid {COLORS['accent2']};">"""
            for exp in experience[:3]:
                exp_html += f"<p>• {exp[:100]}...</p>"
            exp_html += "</div>"
            st.markdown(exp_html, unsafe_allow_html=True)
        else:
            st.markdown(
                f"""<div style="background-color: {COLORS['card_bg']}; color: {COLORS['text_light']}; 
                padding: 15px; border-radius: 8px;">No experience information detected.</div>""", 
                unsafe_allow_html=True
            )


def display_formatted_analysis(analysis):
    if not analysis or not isinstance(analysis, dict):
        st.info("Detailed analysis is not available.")
        return

    section_configs = [
        ("content_improvements", "Content Improvements", COLORS['accent1'], "📝"),
        ("format_suggestions", "Format Suggestions", COLORS['tertiary'], "🎨"),
        ("ats_optimization", "ATS Optimization", COLORS['accent2'], "🤖")
    ]

    for key, title, color, icon in section_configs:
        items = analysis.get(key, [])
        if items:
            st.subheader(f"{icon} {title}")
            content = "\n".join(f"• {item}" for item in items)
            st.markdown(
                f"""<div style='background: linear-gradient(135deg, {color}, {COLORS["secondary"]}); 
                color: white; padding: 18px; border-radius: 8px; margin-top: 10px; 
                font-size: 16px; line-height: 1.8; font-weight: 500; 
                box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);'>{content}</div>""", 
                unsafe_allow_html=True
            )


def format_job_description(description):
    if not description:
        return f"""<div style="background-color: {COLORS['card_bg']}; color: {COLORS['text_light']}; 
                padding: 15px; border-radius: 8px; margin-top: 15px;">No description available</div>"""

    description = description.replace('\n\n', '<br><br>').replace('\n', '<br>')

    formatted_description = f"""
    <div style="background-color: {COLORS['card_bg']}; color: {COLORS['text']}; 
    padding: 20px; border-radius: 10px; margin-top: 15px; line-height: 1.6; 
    font-size: 16px; border-left: 4px solid {COLORS['secondary']}; 
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
        {description}
    </div>
    """

    return formatted_description