from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Google Gemini AI with fallback
def init_ai():
    try:
        # Try to get from environment first
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            # Fallback to hardcoded key (as in your Colab code)
            api_key = "AIzaSyDRFakJBQnFAHv3kf_Mb-XIHUrGOURQGUs"
        
        genai.configure(api_key=api_key)
        # Use the latest model as in your Colab code
        return genai.GenerativeModel(model_name="gemini-2.5-pro")
    except Exception as e:
        logger.error(f"Error in init_ai: {e}")
        raise

model = None
try:
    model = init_ai()
    logger.info("AI model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AI: {e}")

# HTML Template (embedded to keep everything in one file)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Resume Builder</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { font-size: 1.1rem; opacity: 0.9; }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
            min-height: 600px;
        }
        .input-section {
            padding: 30px;
            border-right: 1px solid #eee;
        }
        .output-section {
            padding: 30px;
            background: #f8f9fa;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        textarea {
            width: 100%;
            min-height: 300px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            resize: vertical;
        }
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .resume-output {
            background: white;
            border-radius: 10px;
            padding: 20px;
            min-height: 400px;
            border: 1px solid #e0e0e0;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
        }
        .loading {
            text-align: center;
            color: #667eea;
            font-style: italic;
        }
        .error {
            color: #e74c3c;
            background: #ffeaea;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            .input-section {
                border-right: none;
                border-bottom: 1px solid #eee;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Elite Resume Builder</h1>
            <p>Transform your career description into an elite, ATS-optimized resume</p>
        </div>
        
        <div class="main-content">
            <div class="input-section">
                <h2>Career Description</h2>
                <div class="form-group">
                    <label for="description">Describe your professional background, skills, and experience:</label>
                    <textarea 
                        id="description" 
                        placeholder="Example: I am a senior software engineer with 8 years of experience in Python, JavaScript, and cloud technologies. I have led multiple teams, built scalable web applications, worked with AWS, Docker, and have experience in agile methodologies. I graduated from XYZ University with a Computer Science degree..."
                    ></textarea>
                </div>
                <button class="btn" onclick="generateResume()">Generate Elite Resume</button>
            </div>
            
            <div class="output-section">
                <h2>Generated Resume</h2>
                <div id="resumeOutput" class="resume-output">
                    Your elite resume will appear here...
                </div>
            </div>
        </div>
    </div>

    <script>
        async function generateResume() {
            const description = document.getElementById('description').value.trim();
            const output = document.getElementById('resumeOutput');
            const btn = document.querySelector('.btn');
            
            if (!description) {
                alert('Please enter your career description');
                return;
            }
            
            if (description.length < 50) {
                alert('Please provide more detailed description (at least 50 characters)');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = 'Generating...';
            output.innerHTML = '<div class="loading">🤖 AI is crafting your elite resume...</div>';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ description: description })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    output.innerHTML = data.resume;
                } else {
                    output.innerHTML = `<div class="error">❌ Error: ${data.error}</div>`;
                }
            } catch (error) {
                output.innerHTML = `<div class="error">❌ Network error: ${error.message}</div>`;
            } finally {
                btn.disabled = false;
                btn.textContent = 'Generate Elite Resume';
            }
        }
        
        // Auto-resize textarea
        document.getElementById('description').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    </script>
</body>
</html>
'''

def generate_elite_resume(description):
    """Generate elite resume using AI"""
    if not model:
        raise Exception("AI model not initialized. Check your GOOGLE_API_KEY.")
    
    prompt = f"""
    Create a professional, elite-level resume from this description. Format it as plain text with clear sections.
    
    Description: {description}
    
    Create a resume with these sections:
    1. PROFESSIONAL SUMMARY (3-4 powerful lines)
    2. TECHNICAL SKILLS (organized by category)
    3. PROFESSIONAL EXPERIENCE (with achievements and metrics)
    4. EDUCATION
    5. KEY PROJECTS (if applicable)
    6. CERTIFICATIONS (if applicable)
    
    Use powerful action verbs like: Architected, Spearheaded, Delivered, Optimized, Scaled
    Include metrics and quantifiable achievements where possible.
    Make it ATS-friendly and executive-level.
    
    Format as plain text, well-structured and professional.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        raise Exception(f"Failed to generate resume: {str(e)}")

@app.route('/')
def home():
    """Serve the main application"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Elite Resume Builder",
        "timestamp": datetime.utcnow().isoformat(),
        "ai_status": "ready" if model else "not_initialized"
    })

@app.route('/api/generate', methods=['POST'])
def generate_resume_api():
    """Generate elite resume API endpoint"""
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({"error": "Missing 'description' field"}), 400
        
        description = data['description'].strip()
        if not description:
            return jsonify({"error": "Description cannot be empty"}), 400
        
        if len(description) < 20:
            return jsonify({"error": "Description too short. Please provide more details."}), 400
        
        logger.info(f"Generating resume for description length: {len(description)}")
        
        elite_resume = generate_elite_resume(description)
        
        logger.info("Resume generated successfully")
        
        return jsonify({
            "success": True,
            "resume": elite_resume,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Elite Resume Builder on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

