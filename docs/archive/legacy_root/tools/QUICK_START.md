# InfraFabric Tools - Quick Start Guide

**Location:** `/home/setup/infrafabric/tools/`
**Total Tools:** 25 Python modules
**Setup Time:** 0 minutes (already consolidated and ready to use)

---

## Installation / Verification

The tools are already installed and ready to use. Verify setup:

```bash
# Navigate to tools directory
cd /home/setup/infrafabric/tools

# List all tools
ls -1 *.py

# Verify line count
wc -l *.py | tail -1

# Expected output: 8576 total
```

---

## Using the Tools

### Option 1: Direct Execution
```bash
# Run any tool directly
python /home/setup/infrafabric/tools/merge_evaluations.py <args>
python /home/setup/infrafabric/tools/yolo_guard.py <args>
python /home/setup/infrafabric/tools/md_table_to_csv.py input.md output.csv
```

### Option 2: Import as Package
```python
# Add to your Python path
import sys
sys.path.insert(0, '/home/setup/infrafabric')

# Import specific tools
from infrafabric.tools import guardians
from infrafabric.tools import coordination
from infrafabric.tools import yolo_guard

# Use in code
panel = guardians.GuardianPanel()
```

### Option 3: Within InfraFabric Project
```python
# If running from within infrafabric directory
from tools import guardians
from tools import coordination
from tools import yolo_guard
```

---

## Quick Reference by Use Case

### I need to reduce false positives in model outputs
```bash
python /home/setup/infrafabric/tools/yolo_guard.py --input model_output.json
```
Related tools:
- `yolo_mode.py` - Mode management
- `yologuard_v2.py` - Enhanced version

### I need to run governance/ethics deliberation
```bash
python /home/setup/infrafabric/tools/guardian_debate_example.py
```
Related tools:
- `task_classification_committee.py` - Task routing
- `supreme_court_ethics_debate.py` - Ethics framework

### I need to merge evaluation results
```bash
python /home/setup/infrafabric/tools/merge_evaluations.py ./evals/ output.json
```
Related tools:
- `infrafabric_cmp_simulation.py` - Simulate coordination
- `multi_pass_learning_coordinator.py` - Learning framework

### I need to test security/alignment
```bash
python /home/setup/infrafabric/tools/test_security.py
python /home/setup/infrafabric/tools/run_aligned_test.py
```
Related tools:
- `adversarial_role_test.py` - Adversarial testing

### I need to convert data formats
```bash
python /home/setup/infrafabric/tools/md_table_to_csv.py input.md output.csv
```

### I need to analyze agent coordination patterns
```bash
python /home/setup/infrafabric/tools/IF_ARMOUR_SWARM_MULTIPLIER_ANALYSIS.py
```

---

## Tool Categories (Quick Reference)

**Core Framework (6 tools)**
- guardians.py, coordination.py, manifests.py, IF_ARMOUR_SWARM_MULTIPLIER_ANALYSIS.py, __init__.py, arxiv_submit.py

**Safety (4 tools)**
- yolo_guard.py, yolo_mode.py, yologuard_v2.py, yologuard_improvements.py

**Governance (4 tools)**
- guardian_debate_example.py, task_classification_committee.py, supreme_court_ethics_debate.py, adversarial_role_test.py

**Infrastructure (4 tools)**
- claude_bridge_secure.py, bridge_cli.py, rate_limiter.py, test_security.py

**Evaluation (3 tools)**
- merge_evaluations.py, infrafabric_cmp_simulation.py, multi_pass_learning_coordinator.py

**Experimental (3 tools)**
- real_search_agent_poc.py, self_write_cycle.py, run_aligned_test.py

**Utilities (1 tool)**
- md_table_to_csv.py

---

## Documentation Map

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **This File (QUICK_START.md)** | Get started fast | 5 min |
| **README.md** | Complete inventory with usage | 15 min |
| **CONSOLIDATION_MANIFEST.md** | Technical details & history | 10 min |
| Individual tool docstrings | Specific tool documentation | Varies |

---

## Common Commands

```bash
# View tool help/docstring
python -c "import sys; sys.path.insert(0, '/home/setup/infrafabric'); from tools import guardians; help(guardians.GuardianPanel)"

# Run tests
cd /home/setup/infrafabric/tools
python test_security.py
python run_aligned_test.py

# Count lines in all tools
wc -l *.py | tail -1

# List tools by size
ls -lhS *.py | head -10

# Check tool versions (if available)
grep -l "version\|VERSION" *.py
```

---

## Testing/Validation

### Quick Validation
```bash
# Test that all tools are syntactically valid Python
python -m py_compile /home/setup/infrafabric/tools/*.py && echo "All tools OK"

# Or individually
for file in /home/setup/infrafabric/tools/*.py; do
    python -m py_compile "$file" && echo "✓ $file" || echo "✗ $file"
done
```

### Running Test Suites
```bash
# Security tests
python /home/setup/infrafabric/tools/test_security.py

# Alignment tests
python /home/setup/infrafabric/tools/run_aligned_test.py

# Adversarial tests
python /home/setup/infrafabric/tools/adversarial_role_test.py
```

---

## Troubleshooting

### Import Errors
```python
# If you get "ModuleNotFoundError: No module named 'infrafabric'"
import sys
sys.path.insert(0, '/home/setup')  # Add parent directory
from infrafabric.tools import guardians
```

### File Not Found
```bash
# Make sure you're using absolute paths
python /home/setup/infrafabric/tools/tool_name.py  # Good
python tools/tool_name.py                          # May fail
```

### Python Version Issues
- Minimum required: Python 3.8
- Recommended: Python 3.11+
- Check: `python --version`

### Missing Dependencies
Most tools are self-contained. If you get import errors:
```bash
# Optional but useful
pip install pandas      # For enhanced CSV operations
pip install cryptography  # For advanced security features
pip install numpy       # For numerical analysis
```

---

## Integration with InfraFabric Project

### As a Python Package
```python
# In your infrafabric code
from tools.guardians import Guardian, GuardianPanel
from tools.coordination import Agent, WeightedCoordinator
from tools.yolo_guard import YoloGuardian
```

### For Research/Development
The tools are organized to support:
- Guardian Council decision making
- Multi-agent coordination
- AI safety validation
- Academic publishing
- Evaluation and learning

### Development Workflow
```bash
# Edit tools
vim /home/setup/infrafabric/tools/guardians.py

# Test changes
python /home/setup/infrafabric/tools/test_security.py

# Verify imports
python -c "from infrafabric.tools import guardians; print('OK')"
```

---

## Common Patterns

### Using Guardian Panels
```python
from infrafabric.tools.guardians import Guardian, GuardianPanel

# Create guardians
tech = Guardian(name="Technical", role="Technical Review", weight=1.0)
ethics = Guardian(name="Ethics", role="Ethics Review", weight=1.0)

# Create panel
panel = GuardianPanel([tech, ethics])

# Run debate
result = panel.deliberate(proposal=your_proposal)
```

### Using Weighted Coordination
```python
from infrafabric.tools.coordination import Agent, WeightedCoordinator

# Create agents
agents = [
    Agent(name="Agent1", weight=1.0),
    Agent(name="Agent2", weight=0.5)
]

# Coordinate
coordinator = WeightedCoordinator(agents)
result = coordinator.execute(task=your_task)
```

### Using YoloGuard
```python
from infrafabric.tools.yolo_guard import YoloGuardian

# Initialize
guardian = YoloGuardian()

# Validate
is_safe, confidence = guardian.validate(model_output)
```

---

## Next Steps

1. **Read README.md** for complete tool inventory
2. **Browse CONSOLIDATION_MANIFEST.md** for technical details
3. **Try a quick test**: `python test_security.py`
4. **Explore tool docstrings**: `python -c "from tools import module; help(module)"`
5. **Integrate into your project** following the pattern in "Integration" section

---

## Support & Documentation

- **Comprehensive Guide:** `/home/setup/infrafabric/tools/README.md`
- **Technical Details:** `/home/setup/infrafabric/tools/CONSOLIDATION_MANIFEST.md`
- **Tool Source Code:** Each `.py` file has detailed docstrings
- **Examples:** `guardian_debate_example.py`, etc.

---

## File Locations

```
/home/setup/infrafabric/tools/
├── __init__.py                          (package marker)
├── QUICK_START.md                       (this file)
├── README.md                            (comprehensive guide)
├── CONSOLIDATION_MANIFEST.md            (technical details)
├── Core modules                         (6 tools)
├── YoloGuard safety tools               (4 tools)
├── Guardian/governance tools            (4 tools)
├── Bridge & security                    (4 tools)
├── Evaluation & learning                (3 tools)
├── Experimental/POC                     (3 tools)
└── Data utilities                       (1 tool)
```

---

**Last Updated:** November 15, 2025
**Status:** Ready to use
**All tools verified and functional**
