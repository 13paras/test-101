
# Marketing Posts AI Crew

An intelligent multi-agent system powered by CrewAI that automates the creation of comprehensive marketing strategies and compelling marketing content. This project demonstrates advanced AI agent collaboration to deliver professional-grade marketing analysis, strategic planning, and creative content generation.

## ✨ Features

- **🔍 Market Research Automation**: AI-powered analysis of competitors, market positioning, and audience insights
- **🎯 Strategic Planning**: Comprehensive marketing strategy formulation with tactics, channels, and KPIs
- **🎨 Creative Content Generation**: Innovative campaign ideas and compelling marketing copy creation
- **🤖 Multi-Agent Collaboration**: Three specialized AI agents working in harmony:
  - **Lead Market Analyst**: Conducts thorough market and competitor research
  - **Chief Marketing Strategist**: Synthesizes insights into actionable marketing strategies
  - **Creative Content Creator**: Develops engaging campaigns and marketing copy
- **📊 Structured Outputs**: JSON-formatted results for easy integration and analysis
- **🔧 Customizable Configuration**: YAML-based agent and task configuration

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Usage Examples](#-usage-examples)
- [Dependencies](#-dependencies)
- [License](#-license)

## 🚀 Installation

### Prerequisites

- Python 3.10 - 3.13
- Access to OpenAI API (GPT-4o by default)
- Optional: Serper API for enhanced web search capabilities

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd marketing_posts
   ```

2. **Install dependencies using uv**:
   ```bash
   # Install uv if you haven't already
   pip install uv
   
   # Install project dependencies
   uv sync
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory with the following variables:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SERPER_API_KEY=your_serper_api_key_here  # Optional for enhanced web search
   NEATLOGS_API_KEY=your_neatlogs_api_key_here  # Optional for logging
   ```

## ⚡ Quick Start

Run the marketing crew with default settings:

```bash
# Using uv
uv run marketing_posts

# Or activate the environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m marketing_posts.main
```

**⚠️ Cost Disclaimer**: This project uses GPT-4o by default, which may incur API costs. Monitor your OpenAI usage to avoid unexpected charges.

## 📁 Project Structure

```
marketing_posts/
├── src/marketing_posts/
│   ├── __init__.py
│   ├── main.py                 # Entry point and execution logic
│   ├── crew.py                 # CrewAI agents and tasks orchestration
│   └── config/
│       ├── agents.yaml         # Agent definitions and personalities
│       └── tasks.yaml          # Task descriptions and expected outputs
├── pyproject.toml              # Project dependencies and metadata
├── uv.lock                     # Locked dependency versions
├── trained_agents_data.pkl     # Trained agent data (generated)
└── README.md
```

### Key Components

- **`main.py`**: Entry point containing the `run()` and `train()` functions
- **`crew.py`**: Core CrewAI implementation with:
  - Agent definitions (Lead Market Analyst, Chief Marketing Strategist, Creative Content Creator)
  - Task orchestration (Research, Strategy, Campaign Ideas, Copy Creation)
  - Pydantic models for structured outputs
- **`config/agents.yaml`**: Agent roles, goals, and backstories
- **`config/tasks.yaml`**: Detailed task descriptions and expected outputs

## ⚙️ Configuration

### Customizing Agents

Edit `src/marketing_posts/config/agents.yaml` to modify agent personalities:

```yaml
lead_market_analyst:
  role: Lead Market Analyst
  goal: Conduct amazing analysis of products and competitors
  backstory: As the Lead Market Analyst at a premier digital marketing firm...
```

### Customizing Tasks

Edit `src/marketing_posts/config/tasks.yaml` to modify task requirements:

```yaml
research_task:
  description: Conduct thorough research about the customer and competitors
  expected_output: A complete report on the customer and competitors
```

### Input Customization

Modify the input parameters in `src/marketing_posts/main.py`:

```python
inputs = {
    'customer_domain': 'your-domain.com',
    'project_description': 'Your project description here...'
}
```

## 💡 Usage Examples

### Basic Usage

```bash
# Run with default CrewAI example
uv run marketing_posts
```

### Training the Crew

```bash
# Train the crew for 5 iterations to improve performance
uv run train 5
```

### Expected Output Structure

The system generates structured JSON outputs:

**Marketing Strategy**:
```json
{
  "name": "Strategy Name",
  "tatics": ["Tactic 1", "Tactic 2"],
  "channels": ["Channel 1", "Channel 2"],
  "KPIs": ["KPI 1", "KPI 2"]
}
```

**Campaign Ideas**:
```json
{
  "name": "Campaign Name",
  "description": "Detailed description",
  "audience": "Target audience",
  "channel": "Primary channel"
}
```

**Marketing Copy**:
```json
{
  "title": "Compelling Title",
  "body": "Engaging marketing copy content"
}
```

## 📦 Dependencies

This project is built with modern Python tooling and AI frameworks:

### Core Dependencies
- **CrewAI** (≥0.152.0): Multi-agent orchestration framework
- **CrewAI Tools** (≥0.58.0): Additional tools for web scraping and search
- **NeatLogs** (≥1.1.6): Advanced logging and monitoring
- **Python** (3.10-3.13): Modern Python runtime

### Tools Integration
- **SerperDevTool**: Enhanced web search capabilities
- **ScrapeWebsiteTool**: Website content extraction
- **OpenAI GPT-4o**: Default language model for agents

### Development Tools
- **uv**: Fast Python package manager and dependency resolver
- **Pydantic**: Data validation and structured outputs

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is released under the MIT License. See the LICENSE file for details.

## 🙋‍♂️ Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Check the [CrewAI documentation](https://docs.crewai.com/)
- Review the configuration files for customization options

---

*Built with ❤️ using CrewAI and modern Python tooling*
