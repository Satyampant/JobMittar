"""UI utilities for maintaining legacy visual design with modern backend."""

import streamlit as st

# Color palette (exact match from legacy code)
COLORS = {
    # Primary palette
    "primary": "#1C4E80",
    "secondary": "#0091D5",
    "tertiary": "#6BB4C0",

    # Accent colors
    "accent": "#F17300",
    "accent1": "#3E7CB1",
    "accent2": "#44BBA4",
    "accent3": "#F17300",

    # Functional colors
    "success": "#26A69A",
    "warning": "#F9A825",
    "error": "#E53935",
    "info": "#0277BD",

    # Background and text
    "background": "#F5F7FA",
    "card_bg": "#FFFFFF",
    "text": "#FFFFFF",
    "text_dark": "#000000",
    "text_light": "#333333",
    "text_red": "#FF5252",
    "panel_bg": "#F0F5FF"
}


def apply_styling():
    """Apply custom CSS styling (exact match from legacy code)."""
    st.markdown(f"""
    <style>
        /* Global font styling */
        * {{
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif !important;
        }}

        /* Main header styling */
        h1, h2, .main-header {{
            color: white !important;
            background-color: {COLORS['primary']} !important;
            padding: 20px !important;
            border-radius: 8px !important;
            margin-bottom: 20px !important;
            font-weight: bold !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        }}

        /* Blue header panels styling */
        div[style*="background-color: {COLORS['primary']}"],
        div[style*="background-color: rgb(28, 78, 128)"],
        [data-testid="stForm"] h3,
        .blue-header {{
            color: white !important;
            font-size: 1.2rem !important;
            font-weight: bold !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
            padding: 15px !important;
            border-radius: 6px !important;
            margin-bottom: 15px !important;
            background-color: {COLORS['primary']} !important;
        }}

        /* Fix for text in blue panels */
        div[style*="background-color: {COLORS['primary']}"] p,
        div[style*="background-color: {COLORS['primary']}"] span,
        div[style*="background-color: {COLORS['primary']}"] h3,
        div[style*="background-color: {COLORS['primary']}"] h4,
        div[style*="background-color: {COLORS['primary']}"] div {{
            color: white !important;
            font-weight: bold !important;
        }}

        /* Buttons styled */
        .stButton>button,
        button[kind="primary"] {{
            background-color: {COLORS["accent3"]} !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 4px !important;
            padding: 0.5rem 1rem !important;
            border: none !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            font-size: 16px !important;
            height: auto !important;
        }}

        .stButton>button:hover,
        button[kind="primary"]:hover {{
            background-color: #E67E22 !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
            transform: translateY(-1px) !important;
        }}

        /* Tables */
        table, .dataframe, [data-testid="stTable"] {{
            width: 100% !important;
            border-collapse: collapse !important;
            margin-bottom: 20px !important;
            border-radius: 4px !important;
            overflow: hidden !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        }}

        /* Table headers */
        th, thead tr th {{
            background-color: #222222 !important;
            color: white !important;
            font-weight: bold !important;
            padding: 12px 8px !important;
            text-align: left !important;
            border: none !important;
        }}

        /* Table cells */
        td, tbody tr td {{
            padding: 12px 8px !important;
            border-bottom: 1px solid #EEEEEE !important;
            background-color: white !important;
            color: black !important;
        }}

        /* Alternate row styling */
        tbody tr:nth-child(even) td {{
            background-color: #f9f9f9 !important;
        }}

        /* Tab navigation */
        div[data-baseweb="tab-list"] {{
            gap: 0 !important;
            background-color: {COLORS["background"]} !important;
            padding: 10px !important;
            border-radius: 12px !important;
            display: flex !important;
            justify-content: space-between !important;
            width: 100% !important;
            margin-bottom: 20px !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1) !important;
        }}

        div[data-baseweb="tab-list"] button {{
            flex: 1 !important;
            text-align: center !important;
            margin: 0 5px !important;
            height: 60px !important;
            font-size: 16px !important;
            background-color: rgba(255, 255, 255, 0.7) !important;
            color: {COLORS["primary"]} !important;
            border-radius: 8px !important;
            border: 1px solid rgba(0,0,0,0.05) !important;
            transition: all 0.3s ease !important;
        }}

        div[data-baseweb="tab-list"] button[aria-selected="true"] {{
            background-color: {COLORS["primary"]} !important;
            color: white !important;
            border-bottom: 3px solid {COLORS["accent3"]} !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            transform: translateY(-2px) !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def display_resume_analysis_summary(resume_data):
    """Display AI-generated resume summary."""
    if not resume_data:
        st.warning("Resume data is not available.")
        return

    analysis = resume_data.get("analysis", {})
    
    if not analysis or not isinstance(analysis, dict):
        st.warning("Resume analysis is not available. Please re-upload your resume.")
        return

    st.subheader("Resume Analysis Summary")
    
    # Overall Assessment
    if analysis.get("overall_assessment"):
        st.markdown(f"""
        <div style="background-color: {COLORS['primary']}; color: white; padding: 15px; 
        border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
        <h4 style="margin: 0 0 10px 0; color: white;">📊 Overall Assessment</h4>
        <p style="margin: 0; line-height: 1.6;">{analysis['overall_assessment']}</p>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""<h4 style="color: #1A237E; margin-bottom: 10px;">💪 Strengths</h4>""", unsafe_allow_html=True)
        strengths = analysis.get("strengths", [])
        
        if strengths:
            for strength in strengths:
                st.markdown(
                    f"""<div style="background-color: #01579B; color: white; padding: 12px; 
                    border-radius: 6px; margin-bottom: 10px; font-weight: 500;">
                    ✅ {strength}</div>""", 
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """<div style="background-color: #546E7A; color: white; padding: 12px; 
                border-radius: 6px;">Analysis unavailable</div>""", 
                unsafe_allow_html=True
            )

    with col2:
        st.markdown("""<h4 style="color: #B71C1C; margin-bottom: 10px;">🎯 Areas to Improve</h4>""", unsafe_allow_html=True)
        weaknesses = analysis.get("weaknesses", [])
        
        if weaknesses:
            for weakness in weaknesses:
                st.markdown(
                    f"""<div style="background-color: #C62828; color: white; padding: 12px; 
                    border-radius: 6px; margin-bottom: 10px; font-weight: 500;">
                    ⚠️ {weakness}</div>""", 
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """<div style="background-color: #546E7A; color: white; padding: 12px; 
                border-radius: 6px;">Analysis unavailable</div>""", 
                unsafe_allow_html=True
            )

def display_extracted_information(resume_data):
    """Display extracted resume info (exact visual match from legacy)."""
    if not resume_data:
        st.warning("Resume data is not available.")
        return

    st.subheader("Extracted Information")

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        # Contact info
        st.markdown("""<h4 style="color: #333; margin-bottom: 10px;">📞 Contact Information</h4>""", unsafe_allow_html=True)
        contact_info = resume_data.get("contact_info", {})
        contact_html = """<div style="background-color: #1A237E; color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">"""

        if contact_info and (contact_info.get("email") or contact_info.get("phone")):
            if contact_info.get("email"):
                contact_html += f"<p><strong>Email:</strong> {contact_info['email']}</p>"
            if contact_info.get("phone"):
                contact_html += f"<p><strong>Phone:</strong> {contact_info['phone']}</p>"
        else:
            contact_html += "<p>No contact information detected.</p>"

        contact_html += "</div>"
        st.markdown(contact_html, unsafe_allow_html=True)

        # Education
        st.markdown("""<h4 style="color: #333; margin-bottom: 10px;">🎓 Education</h4>""", unsafe_allow_html=True)
        education = resume_data.get("education", [])
        education_html = """<div style="background-color: #4A148C; color: white; padding: 15px; border-radius: 8px;">"""

        if education:
            for edu in education:
                education_html += f"<p>• {edu}</p>"
        else:
            education_html += "<p>No education information detected.</p>"

        education_html += "</div>"
        st.markdown(education_html, unsafe_allow_html=True)

    with info_col2:
        # Skills
        st.markdown("""<h4 style="color: #333; margin-bottom: 10px;">🛠️ Skills</h4>""", unsafe_allow_html=True)
        skills = resume_data.get("skills", [])

        if skills:
            skills_html = """<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px;">"""
            for skill in skills:
                skills_html += f"""<div style="background-color: #0D47A1; color: white; 
                padding: 8px 12px; border-radius: 20px; font-weight: 500; margin-bottom: 8px;">
                {skill}</div>"""
            skills_html += "</div>"
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.markdown(
                """<div style="background-color: #546E7A; color: white; padding: 15px; 
                border-radius: 8px;">No skills detected.</div>""", 
                unsafe_allow_html=True
            )

        # Experience
        st.markdown("""<h4 style="color: #333; margin-bottom: 10px;">💼 Experience</h4>""", unsafe_allow_html=True)
        experience = resume_data.get("experience", [])

        if experience:
            exp_html = """<div style="background-color: #01579B; color: white; padding: 15px; border-radius: 8px;">"""
            for exp in experience[:3]:  # Show top 3
                exp_html += f"<p>• {exp[:100]}...</p>"
            exp_html += "</div>"
            st.markdown(exp_html, unsafe_allow_html=True)
        else:
            st.markdown(
                """<div style="background-color: #546E7A; color: white; padding: 15px; 
                border-radius: 8px;">No experience information detected.</div>""", 
                unsafe_allow_html=True
            )


def display_formatted_analysis(analysis):
    """Display AI-generated formatted resume analysis."""
    if not analysis or not isinstance(analysis, dict):
        st.info("Detailed analysis is not available.")
        return

    section_configs = [
        ("content_improvements", "Content Improvements", "#1b3a4b", "📝"),
        ("format_suggestions", "Format Suggestions", "#4d194d", "🎨"),
        ("ats_optimization", "ATS Optimization", "#54478c", "🤖")
    ]

    for key, title, color, icon in section_configs:
        items = analysis.get(key, [])
        if items:
            st.subheader(f"{icon} {title}")
            content = "\n".join(f"• {item}" for item in items)
            st.markdown(
                f"""<div style='background-color: {color}; color: white; 
                padding: 15px; border-radius: 8px; margin-top: 10px; 
                font-size: 16px; line-height: 1.8;'>{content}</div>""", 
                unsafe_allow_html=True
            )

def format_job_description(description):
    """Format job description (exact visual match from legacy)."""
    if not description:
        return """<div style="background-color: #455A64; color: white; padding: 15px; 
                border-radius: 8px; margin-top: 15px;">No description available</div>"""

    description = description.replace('\n\n', '<br><br>').replace('\n', '<br>')

    formatted_description = f"""
    <div style="background-color: #263238; color: white; padding: 15px; 
    border-radius: 8px; margin-top: 15px; line-height: 1.5; font-size: 16px;">
        {description}
    </div>
    """

    return formatted_description


def display_matching_skills(skills, job_description):
    """Display matching skills (exact visual match from legacy)."""
    if not skills or not job_description:
        st.markdown(
            """<div style="background-color: #455A64; color: white; padding: 12px; 
            border-radius: 6px;">No matching skills could be determined.</div>""", 
            unsafe_allow_html=True
        )
        return

    job_desc = job_description.lower()
    matching_skills = [skill for skill in skills if skill.lower() in job_desc]

    if matching_skills:
        st.markdown("""<h4 style="color: #1A237E; margin-bottom: 10px;">Skills Matching Job Description</h4>""", unsafe_allow_html=True)
        skills_html = """<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px;">"""

        for skill in matching_skills[:5]:
            skills_html += f"""<div style="background-color: #01579B; color: white; 
            padding: 8px 12px; border-radius: 20px; font-weight: 500; margin-bottom: 8px;">
            ✅ {skill}</div>"""

        skills_html += "</div>"
        st.markdown(skills_html, unsafe_allow_html=True)
    else:
        st.markdown(
            """<div style="background-color: #455A64; color: white; padding: 12px; 
            border-radius: 6px;">No matching skills detected.</div>""", 
            unsafe_allow_html=True
        )
