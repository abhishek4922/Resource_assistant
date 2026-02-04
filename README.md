# 🤖 AI Operations Assistant

## Company Intelligence & AI Use-Case Discovery Agent

A sophisticated multi-agent AI system that analyzes companies, discovers relevant AI use-cases, and finds real technical learning resources from arXiv, Hugging Face, Kaggle, and GitHub.

---

## 🌟 Features

### Multi-Agent Architecture
- **Planner Agent**: Converts user requests into structured execution plans
- **Executor Agent**: Orchestrates searches and LLM-based analysis
- **Verifier Agent**: Validates completeness and normalizes outputs

### Real API Integrations
- 🔍 **DuckDuckGo**: Web search for company information
- 📚 **arXiv**: Academic papers and research
- 🤗 **Hugging Face**: Pre-trained models and datasets
- 📊 **Kaggle**: Datasets and notebooks
- 💻 **GitHub**: Code repositories

### AI-Powered Analysis
- Company summarization using LLM
- Automatic AI use-case generation
- Structured JSON outputs
- Schema-constrained prompting

---

## 🏗️ Project Structure

```
ai_ops_assistant/
│
├── agents/
│   ├── planner_agent.py      # Creates execution plans
│   ├── executor_agent.py     # Executes plan steps
│   └── verifier_agent.py     # Validates and normalizes results
│
├── tools/
│   ├── duckduckgo_tool.py    # Web search
│   ├── arxiv_tool.py         # Academic papers
│   ├── huggingface_tool.py   # Models & datasets
│   ├── kaggle_tool.py        # Datasets & notebooks
│   └── github_tool.py        # Code repositories
│
├── llm/
│   └── llm_client.py         # LLM integration (Groq/Llama 3)
│
├── main.py                   # Streamlit UI
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Groq API key (free at [console.groq.com](https://console.groq.com/))
- (Optional) GitHub Personal Access Token for higher rate limits

### 2. Installation

```bash
# Navigate to the project directory
cd ai_ops_assistant

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
GITHUB_TOKEN=your_github_token_here  # Optional
```

### 4. Run the Application

```bash
streamlit run main.py
```

The application will open in your browser at `http://localhost:8501`

---

## 📖 Usage

### Example Task

1. Enter a company name in the text box (e.g., "Swiggy")
2. Click "🚀 Analyze"
3. Wait for the multi-agent system to:
   - Search for company information
   - Generate a summary
   - Propose AI use-cases
   - Find resources from all platforms
4. Explore the results in expandable cards
5. Download JSON or text reports

### Sample Input

```
Analyze company: Swiggy
```

### Sample Output Structure

```json
{
  "company": "Swiggy",
  "company_summary": "Swiggy is India's leading food delivery platform...",
  "ai_use_cases": [
    {
      "use_case": "Demand Forecasting",
      "description": "Predict food demand patterns...",
      "resources": {
        "arxiv": [
          {
            "title": "Deep Learning for Demand Prediction",
            "url": "https://arxiv.org/abs/..."
          }
        ],
        "huggingface": [...],
        "kaggle": [...],
        "github": [...]
      }
    }
  ]
}
```

---

## 🔧 Technical Details

### Agent Workflow

```
User Input → Planner Agent → Executor Agent → Verifier Agent → Final Output
```

1. **Planner Agent**
   - Receives company name
   - Creates structured execution plan
   - Returns JSON with step-by-step actions

2. **Executor Agent**
   - Searches DuckDuckGo for company info
   - Calls LLM to summarize company
   - Generates 3-5 AI use-cases via LLM
   - Searches all 4 platforms for each use-case
   - Returns structured results

3. **Verifier Agent**
   - Checks completeness of results
   - Validates all resources are present
   - Adds placeholders for missing data
   - Normalizes to final schema

### Error Handling

- **Retry Logic**: All API calls retry at least once on failure
- **Partial Results**: System returns partial data if some APIs fail
- **Graceful Degradation**: Placeholder links provided when searches fail
- **Progress Tracking**: Real-time updates during execution

### LLM Configuration

- **Model**: Llama 3.1 70B (via Groq)
- **Temperature**: 0.1 for planning/verification, 0.3 for generation
- **Output Format**: Structured JSON with schema enforcement
- **Fallbacks**: Default responses if LLM fails

---

## 🎨 UI Features

- **Modern Design**: Gradient backgrounds, card layouts, smooth animations
- **Progress Tracking**: Real-time step-by-step updates
- **Expandable Cards**: Organized use-case presentation
- **Tabbed Resources**: Easy navigation between platforms
- **Export Options**: Download JSON or text reports
- **Quick Examples**: One-click analysis of popular companies

---

## 🔑 API Keys & Rate Limits

### Groq (Required)
- **Get Key**: [console.groq.com](https://console.groq.com/)
- **Free Tier**: 30 requests/minute
- **Models**: Llama 3.1 70B, Mixtral, etc.

### GitHub (Optional)
- **Get Token**: [github.com/settings/tokens](https://github.com/settings/tokens)
- **Without Token**: 60 requests/hour
- **With Token**: 5,000 requests/hour

### Other APIs
- **DuckDuckGo**: No API key required
- **arXiv**: No API key required
- **Hugging Face**: No API key required (public API)
- **Kaggle**: Web scraping (no API key)

---

## 🧪 Testing

### Test with Sample Companies

```python
# Food Delivery
"Swiggy", "Zomato", "DoorDash"

# E-commerce
"Amazon", "Flipkart", "Shopify"

# Technology
"Google", "Microsoft", "Tesla"

# Finance
"PayPal", "Stripe", "Razorpay"
```

---

## 🛠️ Customization

### Adjust Number of Results

Edit the tool initialization in `executor_agent.py`:

```python
self.arxiv_tool = ArxivTool(max_results=5)  # Change to desired number
self.hf_tool = HuggingFaceTool(max_results=5)
self.kaggle_tool = KaggleTool(max_results=5)
self.github_tool = GitHubTool(max_results=5)
```

### Change LLM Model

Edit `llm_client.py`:

```python
self.llm = ChatGroq(
    groq_api_key=api_key,
    model_name="llama-3.1-8b-instant",  # Faster, less accurate
    temperature=temperature
)
```

### Modify Use-Case Count

Edit the prompt in `executor_agent.py`:

```python
# Change from "3-5 relevant AI use-cases" to your desired number
system_prompt = """...propose 3-5 relevant AI use-cases..."""
```

---

## 📊 Output Schema

The system guarantees this output structure:

```json
{
  "company": "string",
  "company_summary": "string",
  "ai_use_cases": [
    {
      "use_case": "string",
      "description": "string",
      "resources": {
        "arxiv": [{"title": "string", "url": "string"}],
        "huggingface": [{"name": "string", "url": "string"}],
        "kaggle": [{"title": "string", "url": "string"}],
        "github": [{"name": "string", "url": "string", "stars": number}]
      }
    }
  ]
}
```

---

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
- Ensure `.env` file exists in the project root
- Check that the key is correctly formatted
- Restart the Streamlit app after adding the key

### "GitHub API rate limit exceeded"
- Add a GitHub Personal Access Token to `.env`
- Wait for the rate limit to reset (1 hour)

### "No results found"
- Check your internet connection
- Try a different company name
- Some APIs may be temporarily unavailable

### JSON Parsing Errors
- The system has fallbacks for LLM failures
- Check Groq API status if persistent

---

## 🚀 Future Enhancements

- [ ] Add more resource platforms (Papers with Code, Medium, etc.)
- [ ] Implement caching for faster repeated queries
- [ ] Add user authentication and result history
- [ ] Export to PDF with formatting
- [ ] Batch analysis of multiple companies
- [ ] Custom use-case suggestions from users
- [ ] Integration with company databases (Crunchbase, etc.)

---

## 📝 License

This project is open source and available under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Open an issue on GitHub

---

## 🎯 Project Requirements Met

✅ Multi-agent architecture (Planner, Executor, Verifier)  
✅ Real API integrations (DuckDuckGo, arXiv, Hugging Face, Kaggle, GitHub)  
✅ LLM usage for planning, summarization, and generation  
✅ Schema-constrained outputs  
✅ Error handling with retries  
✅ Streamlit UI with progress tracking  
✅ Structured JSON outputs  
✅ Local execution  
✅ Complete documentation  

---

**Built with ❤️ using Python, Streamlit, and Groq**
