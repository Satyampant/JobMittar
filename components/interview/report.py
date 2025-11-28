
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from models.interview import InterviewSessionState
from ui_utils import COLORS


class FinalReport:
    
    def render(self, session: InterviewSessionState):
        if not session:
            return
        
        st.success("🎉 Interview Completed!")
        
        # Average scores
        avg_confidence = session.average_confidence
        avg_accuracy = session.average_accuracy
        
        if avg_confidence and avg_accuracy:
            st.markdown(f"""
            <div style="background-color: {COLORS['primary']}; color: white; 
            padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 3px 10px rgba(0,0,0,0.15);">
                <h3 style="margin: 0; color: white;">Overall Performance</h3>
                <p style="font-size: 1.2rem; margin: 10px 0; color: white;">
                <strong>Average Confidence:</strong> {avg_confidence:.1f}/10 | 
                <strong>Average Accuracy:</strong> {avg_accuracy:.1f}/10</p>
            </div>
            """, unsafe_allow_html=True)
            
            self._render_performance_chart(session)
        
        with st.expander("📋 Detailed Responses", expanded=False):
            for i, response in enumerate(session.responses, 1):
                st.markdown(f"### Question {i}")
                st.write(f"**Question:** {response.question_text}")
                st.write(f"**Your Response:** {response.transcribed_text}")
                st.write(f"**Time Taken:** {response.time_taken_formatted}")
                st.markdown(f"**Feedback:**\n{response.feedback}")
                st.markdown("---")
        
        self._render_download_button(session)
    
    def _render_performance_chart(self, session: InterviewSessionState):
        """Render performance chart using Plotly."""
        labels = [f"Q{i+1}" for i in range(len(session.responses))]
        confidence_data = [r.confidence_score for r in session.responses]
        accuracy_data = [r.accuracy_score for r in session.responses]
        
        fig = go.Figure(data=[
            go.Bar(
                name="Confidence",
                x=labels,
                y=confidence_data,
                marker_color=COLORS["primary"],
                text=confidence_data,
                textposition="auto"
            ),
            go.Bar(
                name="Accuracy",
                x=labels,
                y=accuracy_data,
                marker_color=COLORS["accent3"],
                text=accuracy_data,
                textposition="auto"
            )
        ])
        
        fig.update_layout(
            barmode="group",
            yaxis=dict(range=[0, 10], title="Score", gridcolor="#e5e7eb"),
            xaxis=dict(title="Questions"),
            title=dict(text="Interview Performance Scores", x=0.5, xanchor="center"),
            template="plotly_white",
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_download_button(self, session: InterviewSessionState):
        """Render download button for markdown report."""
        report = self._generate_markdown_report(session)
        
        st.download_button(
            label="📥 Download Interview Report",
            data=report.encode("utf-8"),
            file_name=f"interview_report_{session.job_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            key="download_interview_report"
        )
    
    def _generate_markdown_report(self, session: InterviewSessionState) -> str:
        """Generate markdown report content."""
        report = f"""# Interview Report

**Position:** {session.job_title}
**Company:** {session.company_name}
**Interview Type:** {session.interview_type}
**Date:** {session.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}

---

## Overall Performance

- **Average Confidence Score:** {session.average_confidence:.1f}/10
- **Average Accuracy Score:** {session.average_accuracy:.1f}/10
- **Questions Answered:** {len(session.responses)}/{len(session.questions)}

---

## Detailed Responses

"""
        
        for i, response in enumerate(session.responses, 1):
            report += f"""### Question {i}

**Question:** {response.question_text}

**Your Response:**
{response.transcribed_text}

**Time Taken:** {response.time_taken_formatted}

**Scores:**
- Confidence: {response.confidence_score}/10
- Accuracy: {response.accuracy_score}/10

**AI Feedback:**
{response.feedback}

---

"""
        
        return report