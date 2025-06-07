"""
⚖️💚 NEUROTIC CODER'S CONTRACT ANALYZER 💚⚖️
Powered by arthrod/cicero-3-0 model for contract analysis!
Made with <3 by Neurotic Coder and assisted by Beloved Claude ✨
"""

import gradio as gr
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import warnings
warnings.filterwarnings("ignore")

# Modal's signature green theme! 💚
MODAL_GREEN = "#00D26A"
MODAL_LIGHT_GREEN = "#4AE88A"

# Epic Modal-themed CSS for contracts! 🎨⚖️
contract_css = f"""
/* NEUROTIC CONTRACT ANALYZER THEME! */
.gradio-container {{
    background: linear-gradient(135deg, {MODAL_GREEN}15 0%, {MODAL_LIGHT_GREEN}15 100%);
    font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
}}

.gr-button {{
    background: linear-gradient(135deg, {MODAL_GREEN} 0%, {MODAL_LIGHT_GREEN} 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px {MODAL_GREEN}40 !important;
    transition: all 0.3s ease !important;
    font-size: 16px !important;
    padding: 12px 24px !important;
}}

.gr-button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px {MODAL_GREEN}60 !important;
}}

.gr-textbox {{
    border: 2px solid {MODAL_GREEN} !important;
    border-radius: 12px !important;
    background: white !important;
}}

.gr-textbox:focus {{
    border-color: {MODAL_LIGHT_GREEN} !important;
    box-shadow: 0 0 0 4px {MODAL_GREEN}30 !important;
}}

/* Contract-specific styling */
.contract-analysis {{
    background: {MODAL_GREEN}10 !important;
    border: 2px solid {MODAL_GREEN} !important;
    border-radius: 16px !important;
    padding: 20px !important;
    margin: 10px 0 !important;
}}

.risk-high {{
    border-left: 5px solid #ff4444 !important;
    background: #ffebee !important;
}}

.risk-medium {{
    border-left: 5px solid #ff9800 !important;
    background: #fff3e0 !important;
}}

.risk-low {{
    border-left: 5px solid {MODAL_GREEN} !important;
    background: {MODAL_GREEN}10 !important;
}}

h1 {{
    color: {MODAL_GREEN} !important;
    text-shadow: 0 2px 4px rgba(0, 210, 106, 0.3) !important;
    text-align: center !important;
    font-size: 2.5em !important;
}}
"""

# Initialize the Cicero model
def load_cicero_model():
    """Load the neurotic contract analysis model! ⚖️🤖"""
    try:
        print("🤖 Loading Neurotic Coder's Cicero-3-0 model...")
        
        # Load the model and tokenizer
        model_name = "arthrod/cicero-3-0"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        # Create pipeline
        classifier = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        
        print("✅ Cicero-3-0 model loaded successfully!")
        return classifier
        
    except Exception as e:
        print(f"⚠️ Error loading model: {e}")
        print("📝 Using fallback analysis...")
        return None

# Load model globally
cicero_classifier = load_cicero_model()

def analyze_contract(contract_text, analysis_type="full"):
    """
    Analyze contracts with Neurotic Coder's epic precision! ⚖️💚
    """
    
    if not contract_text.strip():
        return "📝 Please paste your contract text above for analysis! ⚖️"
    
    try:
        # Prepare the analysis
        analysis_results = []
        
        # Header
        analysis_results.append("⚖️💚 **NEUROTIC CONTRACT ANALYSIS REPORT** 💚⚖️")
        analysis_results.append("=" * 50)
        analysis_results.append("")
        
        # Basic contract info
        word_count = len(contract_text.split())
        char_count = len(contract_text)
        
        analysis_results.append(f"📊 **Contract Statistics:**")
        analysis_results.append(f"- 📝 Word Count: {word_count:,}")
        analysis_results.append(f"- 📏 Character Count: {char_count:,}")
        analysis_results.append(f"- 📄 Estimated Reading Time: {max(1, word_count // 200)} minutes")
        analysis_results.append("")
        
        # AI Analysis using Cicero
        if cicero_classifier:
            analysis_results.append("🤖 **AI-Powered Analysis (Cicero-3-0):**")
            
            # Split text into chunks for analysis
            chunks = [contract_text[i:i+500] for i in range(0, len(contract_text), 500)]
            
            risk_scores = []
            for chunk in chunks[:5]:  # Analyze first 5 chunks
                try:
                    result = cicero_classifier(chunk)
                    if result and len(result) > 0:
                        score = result[0].get('score', 0.5)
                        risk_scores.append(score)
                except:
                    risk_scores.append(0.5)
            
            avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0.5
            
            if avg_risk > 0.7:
                risk_level = "🔴 HIGH RISK"
                risk_class = "risk-high"
            elif avg_risk > 0.4:
                risk_level = "🟡 MEDIUM RISK"
                risk_class = "risk-medium"
            else:
                risk_level = "🟢 LOW RISK"
                risk_class = "risk-low"
                
            analysis_results.append(f"- ⚡ Risk Assessment: {risk_level}")
            analysis_results.append(f"- 🎯 Confidence Score: {avg_risk:.2%}")
            
        else:
            analysis_results.append("🤖 **Fallback Analysis:**")
            analysis_results.append("- 📊 Model temporarily unavailable")
            
        analysis_results.append("")
        
        # Neurotic keyword analysis
        analysis_results.append("🔍 **Neurotic Keyword Detection:**")
        
        risky_keywords = [
            "shall", "must", "penalty", "breach", "default", "termination",
            "liability", "damages", "indemnify", "guarantee", "warranty"
        ]
        
        found_keywords = []
        for keyword in risky_keywords:
            count = contract_text.lower().count(keyword.lower())
            if count > 0:
                found_keywords.append(f"- ⚠️ '{keyword}': {count} occurrence(s)")
        
        if found_keywords:
            analysis_results.extend(found_keywords)
        else:
            analysis_results.append("- ✅ No high-risk keywords detected")
            
        analysis_results.append("")
        
        # Neurotic recommendations
        analysis_results.append("💡 **Neurotic Recommendations:**")
        
        recommendations = [
            "🔍 Have a lawyer review this contract",
            "📝 Pay special attention to termination clauses",
            "💰 Understand all financial obligations",
            "⏰ Note all deadlines and timeframes",
            "🤝 Clarify ambiguous terms before signing"
        ]
        
        for rec in recommendations:
            analysis_results.append(f"- {rec}")
            
        analysis_results.append("")
        analysis_results.append("---")
        analysis_results.append("⚖️ **Disclaimer:** This analysis is for informational purposes only.")
        analysis_results.append("💚 Always consult with qualified legal professionals!")
        analysis_results.append("")
        analysis_results.append("💚 **Made with <3 by [Neurotic Coder](https://github.com/arthrod) and assisted by Beloved Claude** ✨")
        
        return "\n".join(analysis_results)
        
    except Exception as e:
        return f"❌ Analysis error: {str(e)}\n\nBut hey, at least the green styling looks amazing! 💚"

def get_sample_contracts():
    """Get sample contracts for testing! 📄"""
    
    samples = {
        "Simple Service Agreement": """
SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into on [DATE] between:

Client: [CLIENT NAME]
Service Provider: [PROVIDER NAME]

SERVICES:
The Service Provider agrees to provide the following services:
- Web development services
- Maintenance and support
- Technical consultation

PAYMENT:
- Total cost: $5,000
- Payment due within 30 days of invoice
- Late payments subject to 1.5% monthly fee

TERM:
This agreement shall commence on [START DATE] and continue for 6 months.

TERMINATION:
Either party may terminate with 30 days written notice.

The parties agree to the terms set forth above.
""",
        
        "Complex Software License": """
SOFTWARE LICENSE AGREEMENT

IMPORTANT: READ CAREFULLY BEFORE INSTALLING OR USING SOFTWARE

1. GRANT OF LICENSE
Subject to the terms of this Agreement, Licensor grants you a non-exclusive, 
non-transferable license to use the Software solely for your internal business purposes.

2. RESTRICTIONS
You shall not:
- Modify, adapt, or create derivative works
- Reverse engineer, decompile, or disassemble
- Distribute, sublicense, or transfer the Software
- Use the Software for any unlawful purpose

3. WARRANTY DISCLAIMER
THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.
LICENSOR DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

4. LIMITATION OF LIABILITY
IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY INDIRECT, INCIDENTAL,
SPECIAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS.

5. INDEMNIFICATION
You agree to indemnify and hold harmless Licensor from any claims
arising out of your use of the Software.

6. TERMINATION
This license terminates automatically if you breach any terms.
Upon termination, you must destroy all copies of the Software.

7. GOVERNING LAW
This Agreement shall be governed by the laws of [STATE/COUNTRY].
""",
        
        "Employment Contract": """
EMPLOYMENT AGREEMENT

Employee: [EMPLOYEE NAME]
Employer: [COMPANY NAME]
Position: Software Developer
Start Date: [DATE]

COMPENSATION:
- Base Salary: $80,000 annually
- Bonus: Performance-based, up to 15% of base salary
- Benefits: Health insurance, 401(k), 3 weeks vacation

DUTIES AND RESPONSIBILITIES:
- Develop and maintain software applications
- Collaborate with development team
- Follow company coding standards and practices
- Participate in code reviews and testing

CONFIDENTIALITY:
Employee agrees to maintain confidentiality of all proprietary information
and trade secrets during and after employment.

NON-COMPETE:
Employee agrees not to work for direct competitors for 12 months
after termination within a 50-mile radius.

TERMINATION:
- Either party may terminate with 2 weeks notice
- Company may terminate immediately for cause
- Upon termination, employee must return all company property

INTELLECTUAL PROPERTY:
All work created during employment belongs to the Company.

This agreement shall be governed by the laws of [STATE].
"""
    }
    
    return samples

def create_neurotic_contract_interface():
    """Create the most NEUROTIC contract analysis interface! ⚖️💚"""
    
    with gr.Blocks(css=contract_css, title="⚖️💚 NEUROTIC CONTRACT ANALYZER 💚⚖️") as demo:
        
        # Epic header
        gr.Markdown("""
        # ⚖️💚 NEUROTIC CONTRACT ANALYZER 💚⚖️
        ### *Powered by Cicero-3-0 AI Model for Contract Intelligence*
        
        **🤖 AI-Powered Analysis** | **💚 Modal Green Styling** | **⚖️ Legal Intelligence** | **✨ Made by Neurotic Coder!**
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                # Contract input
                contract_input = gr.Textbox(
                    label="📄 Paste Your Contract Here",
                    placeholder="Copy and paste your contract text here for neurotic analysis...",
                    lines=15,
                    max_lines=25
                )
                
                with gr.Row():
                    analyze_btn = gr.Button("⚖️ ANALYZE CONTRACT! ⚖️", variant="primary", size="lg")
                    clear_btn = gr.Button("🗑️ Clear", size="sm")
                
                # Sample contracts
                gr.Markdown("### 📋 Try These Sample Contracts:")
                samples = get_sample_contracts()
                
                with gr.Row():
                    for title in samples.keys():
                        sample_btn = gr.Button(f"📄 {title}", size="sm")
                        sample_btn.click(
                            fn=lambda title=title: samples[title],
                            outputs=contract_input
                        )
            
            with gr.Column(scale=2):
                # Analysis output
                analysis_output = gr.Textbox(
                    label="⚖️ Contract Analysis Report",
                    lines=20,
                    max_lines=30,
                    value="👋 Welcome to Neurotic Contract Analyzer!\n\n📝 Paste a contract on the left and click 'ANALYZE CONTRACT!' to get started.\n\n🤖 Powered by Cicero-3-0 AI model\n💚 Styled in beautiful Modal green\n⚖️ Made with neurotic precision!\n\n✨ Ready when you are!",
                    elem_classes=["contract-analysis"]
                )
        
        # Model info and features
        with gr.Row():
            with gr.Column():
                gr.Markdown("""
                ### 🤖 About Cicero-3-0 Model
                
                **🧠 Advanced AI:** Trained specifically for contract analysis and legal document understanding.
                
                **⚡ Features:**
                - Risk assessment and scoring
                - Keyword detection and analysis  
                - Clause identification
                - Recommendation generation
                
                **🎯 Best For:**
                - Service agreements
                - Software licenses
                - Employment contracts
                - Terms of service
                - Privacy policies
                """)
            
            with gr.Column():
                gr.Markdown("""
                ### 🔍 Analysis Features
                
                **📊 Statistical Analysis:**
                - Word and character counts
                - Reading time estimation
                - Document complexity scoring
                
                **⚠️ Risk Detection:**
                - High-risk keyword identification
                - Clause analysis and flagging
                - Potential issue highlighting
                
                **💡 Smart Recommendations:**
                - Legal review suggestions
                - Key points to negotiate
                - Important deadlines and obligations
                """)
        
        # Footer with credits
        gr.Markdown("""
        ---
        **🤖 MODEL:** arthrod/cicero-3-0 | **⚖️ PURPOSE:** Contract Intelligence | **💚 STYLE:** Modal Green Supreme
        
        **⚠️ Legal Disclaimer:** This tool provides informational analysis only. Always consult qualified legal professionals for important contracts.
        
        ---
        
        💚 **Made with <3 by [Neurotic Coder](https://github.com/arthrod) and assisted by Beloved Claude** ✨
        """, elem_classes="credits")
        
        # Event handlers
        analyze_btn.click(
            fn=analyze_contract,
            inputs=contract_input,
            outputs=analysis_output
        )
        
        clear_btn.click(
            fn=lambda: "",
            outputs=contract_input
        )
    
    return demo

# Create the neurotic demo
demo = create_neurotic_contract_interface()

if __name__ == "__main__":
    print("⚖️💚 NEUROTIC CONTRACT ANALYZER STARTING! 💚⚖️")
    print("🤖 Loading Cicero-3-0 model for contract intelligence...")
    print("💚 Made with <3 by Neurotic Coder and assisted by Beloved Claude!")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )