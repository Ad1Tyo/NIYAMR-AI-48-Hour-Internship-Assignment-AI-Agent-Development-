"""
NIYAMR AI - Universal Credit Act 2025 Analyzer (Simplified)
Uses Ollama for local LLM processing
"""

import json
import os
import re
import PyPDF2
import ollama


class UniversalCreditActAnalyzer:
    def __init__(self, pdf_path: str, model: str = "llama3.2"):
        self.pdf_path = pdf_path
        self.model = model
        self.text = ""
        self.results = {}
        
    def extract_text(self):
        """Task 1: Extract text from PDF"""
        print("📄 Task 1: Extracting text from PDF...")
        
        with open(self.pdf_path, 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            pages = []
            
            for page in pdf.pages:
                pages.append(page.extract_text())
            
            self.text = "\n\n".join(pages)
            # Clean up extra spaces
            self.text = re.sub(r'\n{3,}', '\n\n', self.text)
            self.text = re.sub(r' {2,}', ' ', self.text)
        
        print(f"✅ Extracted {len(self.text)} characters")
        return self.text
    
    def summarize(self):
        """Task 2: Summarize the Act"""
        print("\n📝 Task 2: Summarizing the Act...")
        
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
        
        # Extract bullet points
        bullets = []
        for line in response['response'].split('\n'):
            line = line.strip()
            if line.startswith('-'):
                bullets.append(line)
        
        self.results['summary'] = bullets
        print(f"✅ Generated {len(bullets)} bullet points")
        return bullets
    
    def extract_sections(self):
        """Task 3: Extract key sections"""
        print("\n🔍 Task 3: Extracting key sections...")
        
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
        
        # Extract each section by finding relevant text
        for section_name, keywords in section_types.items():
            section_text = self._find_section(keywords)
            sections[section_name] = section_text
        
        self.results['sections'] = sections
        print("✅ Extracted all sections")
        return sections
    
    def _find_section(self, keywords):
        """Find text related to keywords"""
        text_lower = self.text.lower()
        findings = []
        
        for keyword in keywords:
            pos = text_lower.find(keyword)
            if pos != -1:
                # Get 400 characters around the keyword
                start = max(0, pos - 200)
                end = min(len(self.text), pos + 200)
                findings.append(self.text[start:end])
        
        if findings:
            return " ... ".join(findings[:2])  # Take first 2 matches
        return "Not found"
    
    def check_rules(self):
        """Task 4: Check 6 rules"""
        print("\n✓ Task 4: Applying rule checks...")
        
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
            
            # Check if section exists and has content
            has_content = len(section_content) > 50 and "not found" not in section_content.lower()
            
            if has_content:
                status = "pass"
                confidence = 85
            else:
                status = "fail"
                confidence = 40
            
            # Find evidence (section reference)
            evidence = self._find_evidence(section_content, section_key)
            
            results.append({
                "rule": rule_text,
                "status": status,
                "evidence": evidence,
                "confidence": confidence
            })
        
        self.results['rule_checks'] = results
        print(f"✅ Completed {len(results)} rule checks")
        return results
    
    def _find_evidence(self, text, section_type):
        """Extract evidence from text"""
        if not text or "not found" in text.lower():
            return "No evidence found"
        
        # Look for section numbers
        match = re.search(r'(Section|Part|Article)\s+\d+', text, re.IGNORECASE)
        if match:
            return match.group()
        
        # Look in full document for section headers
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
    
    def generate_report(self, output_path="output_report.json"):
        """Generate final JSON report"""
        print(f"\n📊 Generating report...")
        
        report = {
            "metadata": {
                "document": "Universal Credit Act 2025",
                "analyzer": "NIYAMR AI Agent",
                "model": self.model
            },
            "task1_extraction": {
                "status": "completed",
                "characters_extracted": len(self.text),
                "extracted_text": self.text  # Save full extracted text
            },
            "task2_summary": self.results.get('summary', []),
            "task3_sections": self.results.get('sections', {}),
            "task4_rule_checks": self.results.get('rule_checks', [])
        }
        
        # Save to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Report saved to {output_path}")
        
        # Also save a pretty-printed summary file
        summary_path = output_path.replace('.json', '_summary.txt')
        self._save_summary_file(summary_path)
        
        return report
    
    def _save_summary_file(self, output_path):
        """Save a human-readable summary file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("NIYAMR AI - UNIVERSAL CREDIT ACT 2025 ANALYSIS\n")
            f.write("="*60 + "\n\n")
            
            # Metadata
            f.write(f"Model: {self.model}\n")
            f.write(f"Characters Extracted: {len(self.text):,}\n\n")
            
            # Task 2: Summary
            f.write("-"*60 + "\n")
            f.write("TASK 2: SUMMARY\n")
            f.write("-"*60 + "\n")
            for bullet in self.results.get('summary', []):
                f.write(f"{bullet}\n")
            f.write("\n")
            
            # Task 3: Sections
            f.write("-"*60 + "\n")
            f.write("TASK 3: EXTRACTED SECTIONS\n")
            f.write("-"*60 + "\n")
            sections = self.results.get('sections', {})
            for section_name, content in sections.items():
                f.write(f"\n[{section_name.upper().replace('_', ' ')}]\n")
                f.write(f"{content}\n")
            f.write("\n")
            
            # Task 4: Rule Checks
            f.write("-"*60 + "\n")
            f.write("TASK 4: RULE COMPLIANCE CHECKS\n")
            f.write("-"*60 + "\n\n")
            
            for i, rule in enumerate(self.results.get('rule_checks', []), 1):
                status_icon = "✅ PASS" if rule['status'] == 'pass' else "❌ FAIL"
                f.write(f"{i}. {rule['rule']}\n")
                f.write(f"   Status: {status_icon}\n")
                f.write(f"   Evidence: {rule['evidence']}\n")
                f.write(f"   Confidence: {rule['confidence']}%\n\n")
            
            f.write("="*60 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*60 + "\n")
        
        print(f"📄 Summary saved to {output_path}")
    
    def run(self, output_path="output_report.json"):
        """Run all tasks"""
        print("🚀 Starting Analysis\n" + "="*60)
        
        self.extract_text()
        self.summarize()
        self.extract_sections()
        self.check_rules()
        report = self.generate_report(output_path)
        
        print("\n" + "="*60)
        print("✅ All tasks completed!")
        print(f"📄 Report: {output_path}")
        
        return report


def main():
    # Configuration
    PDF_PATH = r"C:\Users\LENOVO\Desktop\Wesourceu\ukpga_20250022_en.pdf"
    OUTPUT_PATH = "output_report.json"
    MODEL = "llama3.2"
    
    # Check PDF exists
    if not os.path.exists(PDF_PATH):
        print(f"❌ PDF not found: {PDF_PATH}")
        return
    
    # Run analyzer
    analyzer = UniversalCreditActAnalyzer(PDF_PATH, MODEL)
    analyzer.run(OUTPUT_PATH)
    
    # Display summary
    print("\n📋 Summary:")
    print(f"   - Bullet Points: {len(analyzer.results['summary'])}")
    print(f"   - Sections: {len(analyzer.results['sections'])}")
    print(f"   - Rule Checks: {len(analyzer.results['rule_checks'])}")
    
    # Display rule results
    print("\n🔍 Rule Check Results:")
    for rule in analyzer.results['rule_checks']:
        icon = "✅" if rule['status'] == 'pass' else "❌"
        print(f"   {icon} {rule['rule']}")
        print(f"      Status: {rule['status'].upper()}")
        print(f"      Evidence: {rule['evidence']}")
        print(f"      Confidence: {rule['confidence']}%\n")


if __name__ == "__main__":
    main()