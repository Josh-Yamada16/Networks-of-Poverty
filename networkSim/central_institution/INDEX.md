# Central Institution Network Experiment - Documentation Index

## 📖 Reading Guide

Start here based on your interest:

### 🚀 **I just want to run it**
1. Go to `central_institution/` directory
2. Run: `python main.py`
3. Open the generated PNG files
4. Done!

### 📚 **I want to understand the model**
1. Read: [README.md](README.md) - Full technical documentation (2500+ words)
2. Skim: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Architecture overview
3. Explore: [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md) - Example results and interpretation

### ⚙️ **I want to configure and experiment**
1. Quick start: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Parameter presets and examples
2. Edit: `parameters.py` with desired settings
3. Run: `python main.py`
4. Reference: [SETUP_COMPLETE.md](SETUP_COMPLETE.md) - Troubleshooting

### 🔬 **I want to extend the model**
1. Study: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Design decisions
2. Read: [README.md](README.md) section "Extensions & Future Work"
3. Code: Python files are well-documented
4. Modify: `node.py`, `network.py`, or `simulation.py`

### 📊 **I want to analyze results**
1. Learn: [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md) - How to interpret metrics
2. Review: JSON output files (complete data)
3. Create: Custom analyses from JSON data

---

## 📄 Documentation Files

### [README.md](README.md) - **Master Reference**
**Length**: ~2500 words | **Time**: 20-30 min to read
- Model motivation and real-world applications
- Complete mechanism description
- All parameters explained
- All metrics explained with real-world interpretation
- Running instructions
- File structure
- Class descriptions
- References and future work

**Read this if**: You want comprehensive understanding

---

### [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - **Architecture Overview**
**Length**: ~1500 words | **Time**: 10-15 min to read
- What was built (6 core components)
- Design decisions and why
- Experimental results from test run
- How to use the model
- Validation results
- Next steps
- Technical notes

**Read this if**: You want to understand design and are considering modifications

---

### [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - **Practical Guide**
**Length**: ~1000 words | **Time**: 5-10 min to reference
- Quick start command
- Output files explanation
- Metrics table
- Typical evolution pattern
- Parameter presets (conservative/moderate/aggressive)
- Expected results for each preset
- Common questions and solutions
- Troubleshooting table
- Probability curve explanation
- Experiment workflow
- Research ideas

**Read this if**: You want to run experiments and try different parameters

---

### [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md) - **Example Analysis**
**Length**: ~2000 words | **Time**: 15-20 min to read
- Complete results from sample run
- Transformation metrics table
- Initial vs final state comparison
- Timeline of evolution
- Stage-by-stage analysis
- Connection formation dynamics
- Parameter variation expectations
- Practical insights for research
- Visualization descriptions
- Statistical summary

**Read this if**: You want to see what results look like and how to interpret them

---

### [SETUP_COMPLETE.md](SETUP_COMPLETE.md) - **Status & Next Steps**
**Length**: ~2000 words | **Time**: 10-15 min to read
- Implementation status (✓ Complete)
- What you have (files and documentation)
- Quick start
- Your specifications (all ✓ met)
- How it works (30-second version)
- Expected behavior
- Customization guide
- Generated outputs structure
- Next steps (immediate, short-term, medium-term, research)
- Common first questions answered
- Integration with your project

**Read this if**: You're new to the system and want orientation

---

### [THIS FILE](INDEX.md) - **Navigation**
You are here! This is the index/navigation guide for all documentation.

---

## 🗂️ File Organization

```
central_institution/
│
├── 📄 DOCUMENTATION (read these)
│   ├── INDEX.md                    ← You are here
│   ├── README.md                   ← Master reference
│   ├── IMPLEMENTATION_SUMMARY.md   ← Architecture
│   ├── QUICK_REFERENCE.md          ← Practical guide
│   ├── RESULTS_SHOWCASE.md         ← Example analysis
│   └── SETUP_COMPLETE.md           ← Status & next steps
│
├── 🐍 EXECUTABLE CODE (run this)
│   └── main.py                     ← Start here: python main.py
│
├── ⚙️ CONFIGURATION (customize this)
│   └── parameters.py               ← Edit to change experiment
│
├── 🏗️ IMPLEMENTATION (don't modify unless extending)
│   ├── node.py                     ← Node behavior
│   ├── network.py                  ← Network management
│   ├── simulation.py               ← Simulation engine
│   ├── metrics.py                  ← Analysis metrics
│   ├── visualizer.py               ← Plotting
│   └── __init__.py                 ← Package init
│
└── 📊 OUTPUT (auto-generated when you run main.py)
    ├── central_institution_results_*.json     ← Full data
    ├── metrics_evolution_*.png                ← 6-panel chart
    └── degree_distribution_*.png              ← 3-panel chart
```

---

## ⏱️ Time Investment Guide

| Goal | Time Required | Read These | Do This |
|------|---------------|-----------|--------|
| Just run it | 2 min | — | `python main.py` |
| Understand basics | 10 min | SETUP_COMPLETE.md | Run, look at PNG |
| Understand model | 30 min | README.md + RESULTS_SHOWCASE.md | — |
| Try variations | 20 min | QUICK_REFERENCE.md | Edit parameters, run |
| Deep understanding | 60 min | All docs | Read + run experiments |
| Extend model | 90+ min | All docs + code | Modify code |

---

## 🎯 Quick Access by Question

### "How do I run this?"
→ Run: `python main.py`
→ Read: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) first 50 lines

### "What does this model do?"
→ Read: [README.md](README.md) "Overview" and "Model Design" sections
→ See: [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md) "Interpretation"

### "How do I customize it?"
→ Read: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) "Parameter Presets"
→ Edit: `parameters.py`
→ Ref: [README.md](README.md) "Configuration Parameters"

### "What do the results mean?"
→ Read: [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md) "What This Means"
→ Ref: [README.md](README.md) "Metrics Tracked"

### "I want to modify the code"
→ Read: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) "Class Descriptions"
→ Study: Python files (well-commented)
→ Start small: Try one change first

### "How do I integrate this with my other work?"
→ Read: [SETUP_COMPLETE.md](SETUP_COMPLETE.md) "Integration with Your Project"
→ Info: `central_institution` is self-contained package

### "What should I do next?"
→ Read: [SETUP_COMPLETE.md](SETUP_COMPLETE.md) "Your Next Steps"
→ Plan: Choose immediate, short-term, or research goals

---

## 📚 Reading Paths by Background

### If you're a **Network Scientist**
1. [README.md](README.md) - Understand mechanism
2. [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md) - See validation
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Try variations

### If you're an **Economist/Sociologist**
1. [README.md](README.md) "Motivation" section
2. [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md) - Real-world implications
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Research variants

### If you're a **Software Engineer**
1. [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Architecture
2. Python files - Code structure
3. [README.md](README.md) - Full context

### If you're a **Student/Learner**
1. [SETUP_COMPLETE.md](SETUP_COMPLETE.md) - Orientation
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Practice
3. [README.md](README.md) - Deep dive

### If you're a **Policy Researcher**
1. [README.md](README.md) "Real-world applications"
2. [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md) "Practical Insights"
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Run variants

---

## 🔍 Finding Specific Topics

### Connection Formation
- [README.md](README.md) → "Mechanism: Token Exchange"
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) → "Mechanism Summary"
- [node.py](node.py) → `get_connection_probability()` method

### Metrics Explained
- [README.md](README.md) → "Metrics Tracked" (most detailed)
- [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md) → "What This Means"
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → "Key Metrics at a Glance"

### Parameters
- [parameters.py](parameters.py) - Actual values
- [README.md](README.md) → "Configuration Parameters"
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → "Parameter Presets"

### Running & Debugging
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → "Troubleshooting"
- [SETUP_COMPLETE.md](SETUP_COMPLETE.md) → "Common First Questions"
- [main.py](main.py) - Entry point

### Examples
- [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md) - Full example run
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Parameter examples
- [README.md](README.md) → "Extensions & Future Work"

### Code Architecture
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) → "Class Descriptions"
- Python files - Docstrings in each method
- [README.md](README.md) → "File Structure"

---

## 🚀 Recommended Reading Order (First Time)

**15 minutes (minimum)**
1. This INDEX.md file (you're reading it!)
2. Run `python main.py`
3. Look at generated PNG files

**30 minutes (good)**
+ [SETUP_COMPLETE.md](SETUP_COMPLETE.md) - Get oriented
+ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Understanding basics
+ Try changing one parameter in `parameters.py`

**60 minutes (comprehensive)**
+ [README.md](README.md) - Full understanding
+ [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md) - See interpretation
+ Try "Conservative" and "Aggressive" parameter presets

**2+ hours (expert level)**
+ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Architecture
+ Read Python source files
+ Plan extensions or modifications

---

## ✅ Checklist for Getting Started

- [ ] Read this INDEX.md file
- [ ] Run `python main.py` from `central_institution/` directory
- [ ] Look at generated PNG files
- [ ] Read [SETUP_COMPLETE.md](SETUP_COMPLETE.md)
- [ ] Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) parameter section
- [ ] Try editing `parameters.py` and running again
- [ ] Read [README.md](README.md) "Model Design" section
- [ ] Read [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md) completely
- [ ] Review [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- [ ] Plan your first experiment/modification

---

## 💬 Questions?

**If you're wondering...** | **See...**
---|---
What does this do? | [README.md](README.md) Overview
How do I run it? | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) or [SETUP_COMPLETE.md](SETUP_COMPLETE.md)
How do I change parameters? | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) Parameter Presets
What do the results mean? | [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md)
How do I modify code? | [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) + [README.md](README.md)
Why isn't it working? | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) Troubleshooting
What should I try next? | [SETUP_COMPLETE.md](SETUP_COMPLETE.md) Next Steps
What are the files? | [README.md](README.md) File Structure

---

## 📞 Support Resources Within This Package

Each file has specific strengths:

- **ERROR or PROBLEM**: Go to [QUICK_REFERENCE.md](QUICK_REFERENCE.md) Troubleshooting
- **WANT TO UNDERSTAND**: Go to [README.md](README.md)
- **WANT QUICK EXAMPLE**: Go to [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md)
- **WANT TO CUSTOMIZE**: Go to [QUICK_REFERENCE.md](QUICK_REFERENCE.md) or [parameters.py](parameters.py)
- **CONFUSED ABOUT ARCHITECTURE**: Go to [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **NEW TO SYSTEM**: Go to [SETUP_COMPLETE.md](SETUP_COMPLETE.md)

---

## 📊 Documentation Statistics

| Document | Length | Time | Purpose |
|-----------|--------|------|---------|
| INDEX.md (this file) | ~1500 words | 8 min | Navigation |
| README.md | ~2500 words | 20 min | Reference |
| IMPLEMENTATION_SUMMARY.md | ~1500 words | 10 min | Architecture |
| QUICK_REFERENCE.md | ~1000 words | 5 min | Practical tips |
| RESULTS_SHOWCASE.md | ~2000 words | 15 min | Examples |
| SETUP_COMPLETE.md | ~2000 words | 10 min | Status |
| **TOTAL** | **~10,500 words** | **~68 min** | **Complete** |

---

## 🎓 Learning Objectives

After reading the documentation, you should understand:

✓ What the central institution network model simulates
✓ How tokens and connection probability work
✓ What each metric means and why it matters
✓ How to run the simulation
✓ How to customize parameters
✓ How to interpret results
✓ What next experiments to try
✓ How the code is structured
✓ How to extend the model

---

## 🔄 Document Versions

- **Created**: January 30, 2026
- **Status**: Complete and tested
- **Version**: 1.0
- **All files included**: ✓

---

**Start here, then pick a document based on your needs!**

Most common entry points:
1. **Just run it**: `python main.py`
2. **Understand it**: Read [README.md](README.md)
3. **Experiment**: Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
4. **Analyze results**: Read [RESULTS_SHOWCASE.md](RESULTS_SHOWCASE.md)

Enjoy exploring the Central Institution Network model! 🎉
