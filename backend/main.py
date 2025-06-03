from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pdfplumber
import os
import json
import tempfile
import uvicorn
from dotenv import load_dotenv
import anthropic
from typing import List, Dict, Any
import logging
from app.routers import rag  # Add this import
import traceback
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Smart Contract Analyzer API",
    description="AI-powered legal contract analysis",
    version="1.0.0"
)

# Add CORS middleware - More permissive for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rag.router)  # Add this line

# Initialize Anthropic client
try:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY not found in environment variables")
        raise ValueError("ANTHROPIC_API_KEY is required")
    
    client = anthropic.Anthropic(api_key=api_key)
    logger.info("Anthropic client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Anthropic client: {e}")
    client = None

@app.get("/")
async def root():
    return {"message": "Smart Contract Analyzer API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    anthropic_status = "connected" if client else "not configured"
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "anthropic_api": anthropic_status,
        "endpoints": ["/", "/health", "/analyze"]
    }

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF using pdfplumber"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file_content)
            tmp_file.flush()
            
            text = ""
            with pdfplumber.open(tmp_file.name) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num}")
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            os.unlink(tmp_file.name)
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
                
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text.strip()
            
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(
            status_code=400, 
            detail=f"Error extracting text from PDF: {str(e)}. Please ensure the PDF contains readable text and is not corrupted."
        )

def analyze_contract_with_claude(contract_text: str) -> List[Dict[str, Any]]:
    """Analyze contract using Claude"""
    
    if not client:
        raise HTTPException(
            status_code=500, 
            detail="Anthropic API client not configured. Please set ANTHROPIC_API_KEY environment variable."
        )

    prompt = f"""
You are an expert legal analyst specializing in contract review for non-lawyers.
Your job is to make complex legal language accessible and highlight potential risks.

Analyze the following contract and break it down into numbered clauses.
For each significant clause, return a JSON object with the structure shown below.

Important guidelines:
1. Focus on the most important clauses (aim for 5-15 clauses total)
2. Skip boilerplate sections like signatures, dates, and standard formatting
3. Prioritize clauses that involve rights, obligations, payments, termination, liability, etc.
4. For risk_flag, use "Yes" only for genuine concerns that a non-lawyer should be aware of
5. Keep explanations clear and accessible to non-lawyers

Return ONLY a valid JSON array in this exact format:

[
  {{
    "clause_number": 1,
    "original_clause": "The exact text of the clause from the contract",
    "explanation": "Clear explanation in plain English of what this clause means",
    "risk_flag": "Yes or No",
    "risk_reason": "Explanation of the risk (only include if risk_flag is Yes)"
  }}
]

Contract text to analyze:

{contract_text[:8000]}  # Limit to prevent token overflow
    """

    try:
        logger.info("Sending request to Claude API")
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text
        logger.info(f"Received response from Claude API: {len(response_text)} characters")

        # Attempt to extract JSON from Claude response
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1

        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            parsed_result = json.loads(json_str)
            
            # Validate the structure
            if not isinstance(parsed_result, list):
                raise ValueError("Response is not a JSON array")
            
            for item in parsed_result:
                required_fields = ["clause_number", "original_clause", "explanation", "risk_flag"]
                for field in required_fields:
                    if field not in item:
                        raise ValueError(f"Missing required field: {field}")
            
            logger.info(f"Successfully parsed {len(parsed_result)} clauses")
            return parsed_result
        else:
            logger.error("No JSON array found in Claude's response")
            raise ValueError("No valid JSON array found in AI response")

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        logger.error(f"Raw response: {response_text[:500]}...")
        raise HTTPException(
            status_code=500, 
            detail="Error parsing AI response. The AI may have returned malformed JSON."
        )
    except anthropic.APIError as e:
        logger.error(f"Anthropic API Error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Claude API Error: {str(e)}. Please check your API key and usage limits."
        )
    except Exception as e:
        logger.error(f"Unexpected error in Claude analysis: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error analyzing contract: {str(e)}"
        )

@app.post("/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    """Main endpoint to analyze uploaded contract"""
    
    logger.info(f"Received file upload: {file.filename}")

    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported. Please upload a PDF document."
        )

    # Read file and validate size
    try:
        file_content = await file.read()
        max_size = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB default
        
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size is {max_size // 1024 // 1024}MB"
            )
        
        logger.info(f"File size: {len(file_content)} bytes")
        
    except Exception as e:
        logger.error(f"Error reading uploaded file: {e}")
        raise HTTPException(
            status_code=400, 
            detail="Error reading uploaded file. Please try again."
        )

    try:
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(file_content)
        
        if not extracted_text or len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract meaningful text from PDF. Please ensure it's a text-based PDF, not a scanned image."
            )

        # Analyze with Claude
        analysis_result = analyze_contract_with_claude(extracted_text)

        response_data = {
            "success": True,
            "filename": file.filename,
            "extracted_text_length": len(extracted_text),
            "clauses_found": len(analysis_result),
            "analysis": analysis_result
        }
        
        logger.info(f"Analysis completed successfully for {file.filename}")
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error during analysis: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    print("🔥 ERROR IN GLOBAL EXCEPTION HANDLER:")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"}
    )

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY environment variable not set!")
        print("Please set it using: export ANTHROPIC_API_KEY=your_api_key_here")
    
    print("Starting Smart Contract Analyzer API...")
    print("Backend will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")