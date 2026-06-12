# 🚗 REAL - Requirements Engineering for mAchines tha Learn (and Fail)

[![Python](https://img.shields.io/badge/Python-84.4%25-blue)](https://www.python.org/)
[![Scenic](https://img.shields.io/badge/Scenic-5.8%25-green)](https://scenic-lang.readthedocs.io/)
[![Java](https://img.shields.io/badge/Java-5.6%25-orange)](https://www.java.com/)
[![License](https://img.shields.io/badge/License-Open%20Source-brightgreen)](LICENSE)

> An intelligent system for automated test case generation and requirement validation in autonomous vehicle scenarios using evolutionary computation and domain-specific languages.

## 🌟 Overview

REAL is a requirements engineering platform for adaptive learning that bridges the gap between natural language requirements and executable test scenarios for autonomous systems. By leveraging grammatical evolution, domain-specific languages (DSL), and simulation environments, REAL automatically generates and validates test cases for complex automotive scenarios to improve their requirements specification.

### 🎯 Key Capabilities

- **🔍 Requirement Parsing**: Natural language requirement analysis using custom DSL grammar
- **🧬 Evolutionary Test Generation**: Automated test case generation using Grammatical Evolution (GE)
- **🚙 Scenario Simulation**: Integration with CARLA simulator for realistic autonomous vehicle testing  
- **🔧 API-Driven Architecture**: RESTful API for seamless integration with external tools
- **📊 MLOps Integration**: Experiment tracking and model management with MLflow
- **🎭 Scenic Integration**: Support for probabilistic programming languages for scenario description

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Requirements  │    │   DSL Parser    │    │  Test Generator │
│   (Natural Lang)│───▶│   (Grammar)     │───▶│   (Evolutionary)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
        ▲                                              │
        │                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Requirement     │◀───│   Validation    │◀───│   CARLA Sim     │
│ Refinement      │    │   (Fitness)     │    │   (Scenarios)   │
│ (Analyst)       │    └─────────────────┘    └─────────────────┘
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Redis Server
- CARLA Simulator (0.9.15)
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/DoubleBlinded1/REAL.git
   cd REAL
   ```

2. **Set up the environment**
   ```bash
   chmod +x setup_env.sh
   ./setup_env.sh
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Redis server**
   ```bash
   redis-server
   ```

5. **Launch the API server**
   ```bash
   python api_app.py
   ```

The API will be available at `http://127.0.0.1:7999`

## 💡 Usage Examples

### 1. Verify a Requirement

```bash
curl "http://127.0.0.1:7999/verify_requirement?requirement=The vehicle should maintain safe distance"
```

**Response:**
```json
{
  "parsed_grammar": "...",
  "STATUS": "OK"
}
```

### 2. Generate Test Cases

```bash
curl "http://127.0.0.1:7999/get_testcases?requirement=Emergency braking in urban scenario"
```

**Response:**
```json
{
  "testcases": [
    "{speed: 60, distance: 20, weather: clear}",
    "{speed: 45, distance: 15, weather: rain}"
  ],
  "STATUS": "OK"
}
```

### 3. Validate Test Cases

```bash
curl "http://127.0.0.1:7999/validate?testcase={speed: 50, distance: 25, weather: fog}"
```

## 📁 Project Structure

```
REAL/
├── 📄 api_app.py              # FastAPI application server
├── 📄 ge.py                   # Grammatical Evolution implementation
├── 🎯 app.py                  # Streamlit web interface
├── 📁 scripts/
│   ├── 🧬 evolve/             # Evolutionary algorithms
│   ├── 🔧 redsl/              # Requirements DSL parser
│   ├── 🎭 templates/          # Scenario templates
│   ├── 🚗 simulations/        # CARLA integration
│   ├── 📊 mlops/              # MLflow integration
│   └── 🏗️ scenarios/          # Test scenarios
├── 📁 grammar/                # DSL grammar definitions
│   ├── 📁 example/            # Example grammars
│   └── 📁 kaos/               # KAOS methodology support
├── 📁 Scenic/                 # Scenic language submodule
├── 📁 VerifAI/                # Verification framework
└── 📁 infra/                  # Infrastructure configurations
```

## 🔬 Research Features

### Grammatical Evolution Engine
- **Population-based search** with configurable parameters
- **Multi-objective optimization** for test case quality
- **Grammar-guided evolution** ensuring syntactically valid outputs
- **Diversity preservation** mechanisms

### Domain-Specific Language (DSL)
- **Natural language processing** for requirement extraction
- **Formal grammar definitions** using BNF notation
- **Semantic validation** of requirement specifications
- **Template-based code generation**

### Simulation Integration
- **CARLA simulator** integration for realistic testing
- **Scenic language** support for probabilistic scenarios
- **Multi-process execution** with timeout handling
- **Fitness evaluation** based on simulation outcomes

## 🛠️ Configuration

### Environment Variables
```bash
export MLFLOW_TRACKING_URI="http://127.0.0.1:5000"
export CARLA_ROOT="/path/to/carla"
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
```

### Grammar Configuration
Customize DSL grammars in the `scripts/templates/` directory:
- `old/old.bnf` - Legacy grammar format
- Custom grammar files for domain-specific requirements

## 📊 Monitoring & MLOps

REAL integrates with MLflow for experiment tracking:

1. **Start MLflow server**
   ```bash
   mlflow ui --host 127.0.0.1 --port 5000
   ```

2. **View experiments** at `http://127.0.0.1:5000`

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Format code
black .
isort .
```



## 🔗 Related Projects

- **[Scenic](https://github.com/BerkeleyLearnVerify/Scenic)** - Probabilistic programming language for scenarios
- **[VerifAI](https://github.com/BerkeleyLearnVerify/VerifAI)** - Verification framework for AI systems
- **[CARLA](https://carla.org/)** - Autonomous driving simulator
- **[GRAPE](https://github.com/bdsul/grape)** - Grammatical Evolution library

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Berkeley LearnVerify team for Scenic and VerifAI
- CARLA development team
- GRAPE grammatical evolution library contributors

---

<div align="center">


Made with ❤️ for the Requirements Engineering research community

</div>
