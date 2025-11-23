"""
NIYAMR AI - Universal Credit Act 2025 Analyzer
Streamlit Web Interface
"""

import streamlit as st
import json
import os
import re
import PyPDF2
import ollama
from datetime import datetime
import tempfile


class UniversalCreditActAnalyzer:
    def __init__(self, pdf_path: str, model: str = "llama3.2"):
        self.pdf_path = pdf_path
        self.model = model
        self.text = ""
        self.results = {}
        
    def extract_text(self):
        with open(self.pdf_path, 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            pages = []
            
            for page in pdf.pages:
                pages.append(page.extract_text())
            
            self.text = "\n\n".join(pages)
            self.text = re.sub(r'\n{3,}', '\n\n', self.text)
            self.text = re.sub(r' {2,}', ' ', self.text)
        
        return self.text
    
    def summarize(self):
        prompt = f"""Summarize this Act in 5-10 bullet points. Focus on:
- Purpose
- Key definitions
- Eligibility
- Obligations
- Enforcement

Document:
{self.text[:5000]}

Provide only bullet points starting with '-'."""

        response = ollama.generate(model=self.model, prompt=prompt)
        
        bullets = []
        for line in response['response'].split('\n'):
            line = line.strip()
            if line.startswith('-'):
                bullets.append(line)
        
        self.results['summary'] = bullets
        return bullets
    
    def extract_sections(self):
        sections = {}
        section_types = {
            'definitions': ['definition', 'means', 'interpret'],
            'obligations': ['obligation', 'must', 'shall'],
            'responsibilities': ['responsibility', 'duty', 'authority'],
            'eligibility': ['eligible', 'qualify', 'entitle'],
            'payments': ['payment', 'amount', 'calculate', 'benefit'],
            'penalties': ['penalty', 'fine', 'enforce', 'offence'],
            'record_keeping': ['record', 'report', 'maintain']
        }
        
        for section_name, keywords in section_types.items():
            section_text = self._find_section(keywords)
            sections[section_name] = section_text
        
        self.results['sections'] = sections
        return sections
    
    def _find_section(self, keywords):
        text_lower = self.text.lower()
        findings = []
        
        for keyword in keywords:
            pos = text_lower.find(keyword)
            if pos != -1:
                start = max(0, pos - 200)
                end = min(len(self.text), pos + 200)
                findings.append(self.text[start:end])
        
        if findings:
            return " ... ".join(findings[:2])
        return "Not found"
    
    def check_rules(self):
        rules = [
            ("Act must define key terms", "definitions"),
            ("Act must specify eligibility criteria", "eligibility"),
            ("Act must specify responsibilities of the administering authority", "responsibilities"),
            ("Act must include enforcement or penalties", "penalties"),
            ("Act must include payment calculation or entitlement structure", "payments"),
            ("Act must include record-keeping or reporting requirements", "record_keeping")
        ]
        
        results = []
        sections = self.results['sections']
        
        for rule_text, section_key in rules:
            section_content = sections.get(section_key, "")
            has_content = len(section_content) > 50 and "not found" not in section_content.lower()
            
            if has_content:
                status = "pass"
                confidence = 85
            else:
                status = "fail"
                confidence = 40
            
            evidence = self._find_evidence(section_content, section_key)
            
            results.append({
                "rule": rule_text,
                "status": status,
                "evidence": evidence,
                "confidence": confidence
            })
        
        self.results['rule_checks'] = results
        return results
    
    def _find_evidence(self, text, section_type):
        if not text or "not found" in text.lower():
            return "No evidence found"
        
        match = re.search(r'(Section|Part|Article)\s+\d+', text, re.IGNORECASE)
        if match:
            return match.group()
        
        section_names = {
            'definitions': 'Definitions',
            'eligibility': 'Eligibility',
            'responsibilities': 'Responsibilities',
            'penalties': 'Penalties|Enforcement',
            'payments': 'Payments|Benefits',
            'record_keeping': 'Records|Reporting'
        }
        
        pattern = rf'(Section|Part)\s+\d+\s*[-–]\s*({section_names.get(section_type, "")})'
        match = re.search(pattern, self.text, re.IGNORECASE)
        if match:
            return match.group().strip()
        
        return "Evidence found in document"
    
    def generate_report(self):
        report = {
            "metadata": {
                "document": "Universal Credit Act 2025",
                "analyzer": "NIYAMR AI Agent",
                "model": self.model,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "task1_extraction": {
                "status": "completed",
                "characters_extracted": len(self.text)
            },
            "task2_summary": self.results.get('summary', []),
            "task3_sections": self.results.get('sections', {}),
            "task4_rule_checks": self.results.get('rule_checks', [])
        }
        return report


# Streamlit UI
def main():
    st.set_page_config(
        page_title="NIYAMR AI - Document Analyzer",
        page_icon="📄",
        layout="wide"
    )
    
    # Header
    st.title("📄 NIYAMR AI - Legislative Document Analyzer")
    st.markdown("**48-Hour Internship Assignment** | Powered by Ollama")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        model = st.selectbox(
            "Select Ollama Model",
            ["llama3.2", "mistral", "llama2"],
            index=0
        )
        
        st.divider()
        
        st.markdown("### 📋 Tasks")
        st.markdown("""
        - ✅ Task 1: Extract Text
        - ✅ Task 2: Summarize
        - ✅ Task 3: Extract Sections
        - ✅ Task 4: Rule Checks
        """)
        
        st.divider()
        
        st.markdown("### 🔧 About")
        st.markdown("""
        This tool analyzes legislative documents using:
        - **PyPDF2** for extraction
        - **Ollama** for AI processing
        - **Streamlit** for interface
        """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Document")
        uploaded_file = st.file_uploader(
            "Upload Universal Credit Act PDF",
            type=['pdf'],
            help="Upload the legislative document to analyze"
        )
    
    with col2:
        st.header("🎯 Analysis Status")
        status_placeholder = st.empty()
        status_placeholder.info("⏳ Waiting for PDF upload...")
    
    # Process when file is uploaded
    if uploaded_file is not None:
        status_placeholder.success("✅ PDF uploaded successfully!")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        # Analyze button
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            
            with st.spinner("🔄 Processing document..."):
                try:
                    # Initialize analyzer
                    analyzer = UniversalCreditActAnalyzer(tmp_path, model)
                    
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Task 1: Extract
                    status_text.text("📄 Task 1: Extracting text...")
                    analyzer.extract_text()
                    progress_bar.progress(25)
                    
                    # Task 2: Summarize
                    status_text.text("📝 Task 2: Summarizing...")
                    analyzer.summarize()
                    progress_bar.progress(50)
                    
                    # Task 3: Extract sections
                    status_text.text("🔍 Task 3: Extracting sections...")
                    analyzer.extract_sections()
                    progress_bar.progress(75)
                    
                    # Task 4: Rule checks
                    status_text.text("✓ Task 4: Checking rules...")
                    analyzer.check_rules()
                    progress_bar.progress(100)
                    
                    status_text.text("✅ Analysis complete!")
                    
                    # Store results in session state
                    st.session_state['analyzer'] = analyzer
                    st.session_state['report'] = analyzer.generate_report()
                    
                    st.success("🎉 Analysis completed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
    
    # Display results if available
    if 'report' in st.session_state:
        st.divider()
        st.header("📊 Analysis Results")
        
        report = st.session_state['report']
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Summary", 
            "📑 Sections", 
            "✅ Rule Checks", 
            "📄 Full Report",
            "💾 Download"
        ])
        
        with tab1:
            st.subheader("📋 Executive Summary")
            st.markdown(f"**Characters Extracted:** {report['task1_extraction']['characters_extracted']:,}")
            
            st.markdown("### Key Points")
            for bullet in report['task2_summary']:
                st.markdown(bullet)
        
        with tab2:
            st.subheader("📑 Extracted Sections")
            
            sections = report['task3_sections']
            
            for section_name, content in sections.items():
                with st.expander(f"📌 {section_name.replace('_', ' ').title()}", expanded=False):
                    if content and "not found" not in content.lower():
                        st.text_area(
                            label="Content",
                            value=content,
                            height=150,
                            key=f"section_{section_name}",
                            label_visibility="collapsed"
                        )
                    else:
                        st.warning("⚠️ Section not found in document")
        
        with tab3:
            st.subheader("✅ Rule Compliance Checks")
            
            # Summary metrics
            rule_checks = report['task4_rule_checks']
            passed = sum(1 for r in rule_checks if r['status'] == 'pass')
            failed = len(rule_checks) - passed
            
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Total Rules", len(rule_checks))
            metric_col2.metric("Passed", passed, delta=None)
            metric_col3.metric("Failed", failed, delta=None)
            
            st.divider()
            
            # Individual rule results
            for i, rule in enumerate(rule_checks, 1):
                status_color = "green" if rule['status'] == 'pass' else "red"
                status_icon = "✅" if rule['status'] == 'pass' else "❌"
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**{i}. {rule['rule']}**")
                    st.markdown(f"📌 Evidence: _{rule['evidence']}_")
                
                with col2:
                    st.markdown(f"**Status:** {status_icon} {rule['status'].upper()}")
                    st.progress(rule['confidence'] / 100)
                    st.caption(f"Confidence: {rule['confidence']}%")
                
                st.divider()
        
        with tab4:
            st.subheader("📄 Complete JSON Report")
            st.json(report)
        
        with tab5:
            st.subheader("💾 Download Report")
            
            # JSON download
            json_str = json.dumps(report, indent=2)
            st.download_button(
                label="📥 Download JSON Report",
                data=json_str,
                file_name=f"niyamr_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
            
            # Text summary download
            text_summary = f"""NIYAMR AI - Analysis Report
Generated: {report['metadata']['timestamp']}
Model: {report['metadata']['model']}

SUMMARY
=======
{chr(10).join(report['task2_summary'])}

RULE CHECKS
===========
"""
            for rule in report['task4_rule_checks']:
                text_summary += f"\n{rule['status'].upper()}: {rule['rule']}\n"
                text_summary += f"Evidence: {rule['evidence']}\n"
                text_summary += f"Confidence: {rule['confidence']}%\n"
            
            st.download_button(
                label="📄 Download Text Summary",
                data=text_summary,
                file_name=f"niyamr_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            st.success("✅ Reports ready for download!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>NIYAMR AI - 48-Hour Internship Assignment | Powered by Ollama & Streamlit</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()