# Institutional Network Model - Conceptual Framework

**Date:** January 10, 2026

## Core Idea

Reframe the Reddit network analysis from peer-to-peer communication networks to **institutional mediation networks**, where posts represent institutions/resources and users are resource seekers who form connections through shared institutional participation.

## Conceptual Shift

### Current Model
- **Nodes:** Users
- **Edges:** User A replies to User B (direct replies)
- **Focus:** Peer-to-peer communication patterns
- **Analysis:** Who talks to whom

### Proposed Model
- **Institutions (Posts):** Resource hubs, gathering points, mediums for connection
- **Users:** Resource seekers with connections to institutions
- **Edges:** User ↔ Institution connections, User ↔ User connections formed through shared institutions
- **Focus:** Institutional mediation of social ties and resource access
- **Analysis:** How institutions facilitate network formation and resource distribution

## Why This Reframing Makes Sense

### 1. Alignment with Research Literature
- **"Networking in Weak Institutions" paper:** Directly models how people use social networks to substitute for weak formal institutions
- **"Social Trust, Institution, and Economic Growth":** Examines interplay between informal networks and formal institutions
- **Core hypothesis:** Network effects on poverty operate through institutional access

### 2. Better Reflects Reality of Poverty Subreddits
- **r/assistance:** Posts ARE resource requests (institutions offering help)
- **r/homeless:** Posts represent shared institutional challenges
- **r/povertyfinance:** Posts as knowledge/strategy institutions
- Top-level posts often represent explicit resource needs or institutional information

### 3. Captures Resource Access Patterns
- Who has access to which institutions?
- How do people navigate between different institutional spaces?
- What is the "cost" of institutional access (engagement required)?

## Network Architecture Options

### Option 1: Bipartite Network
```
Users ←→ Posts (Institutions)
```
**Structure:**
- Two distinct node types: users and posts
- Edges only connect different node types (user-to-post)
- No direct user-to-user edges

**Reveals:**
- Which users access which institutions
- Which institutions are most popular/central
- User institutional diversity (how many different institutions accessed)

**Use case:** Understanding institutional access patterns

---

### Option 2: User Projection Network (Recommended Starting Point)
```
Users ←→ Users
(connected through shared posts/institutions)
```
**Structure:**
- Users are nodes
- Users connected if they engage with the same post/institution
- Edge weight = number of shared institutions
- **This is essentially the co-participation network, reframed!**

**Reveals:**
- Emergent social networks formed through institutions
- Which users are "neighbors" in institutional space
- Community clustering around institutional access patterns

**Use case:** Understanding how institutions create social capital

---

### Option 3: Dual-Layer Network (Most Comprehensive)
```
Layer 1: Users → Posts (institutional access)
Layer 2: Users → Users (peer connections formed through institutions)
```
**Structure:**
- Multi-layer network capturing both direct institutional ties AND emergent social connections
- Layer 1: User-institution relationships (participation, replies)
- Layer 2: User-user relationships (replies, co-participation)
- Cross-layer analysis shows how institutional access leads to social capital

**Reveals:**
- Complete picture of institutional mediation
- How institutions bridge communities
- Path from institutional access to social network formation

**Use case:** Comprehensive modeling for simulations

## What This Framework Would Reveal

### Institutional Metrics
1. **Institutional Centrality:** Which posts/institutions are most important network connectors?
2. **Institutional Bridging:** Do some institutions connect different user communities?
3. **Institutional Diversity:** Distribution of institution types (help requests, advice, venting, etc.)
4. **Institutional Effectiveness:** Which institutions generate the most/strongest connections?

### User Metrics
1. **Institutional Access:** How many institutions does each user access?
2. **Institutional Diversity:** Do users access varied or similar institutions?
3. **Brokerage:** Are there users who bridge between different institutional spaces?
4. **Access Patterns:** Sequential vs. simultaneous institutional access

### Network-Level Insights
1. **Resource Access Inequality:** 
   - Do some users have access to more/better institutions?
   - Are there isolated users with limited institutional connections?
   
2. **Network Effects on Poverty:**
   - Does institutional diversity predict better outcomes?
   - Do "institution hubs" create poverty traps or escape routes?
   
3. **Institutional Substitution:**
   - How do informal institutions (Reddit posts) substitute for formal institutions?
   - What types of resources flow through different institutional spaces?

4. **Community Formation:**
   - How do institutions facilitate community clustering?
   - Are there distinct sub-communities around different institutional types?

## Implementation Strategy

### Phase 1: Reframe Existing Data
**Good news:** We already have most of the data needed!

**Co-participation edges** already capture shared institutional access:
```python
# Current: Users who commented on same posts
# Reframe: Users connected through shared institutional participation
```

**What to add:**
1. **Post/Institution attributes:**
   - Institution type (resource request, advice, venting, information)
   - Resource type offered (financial, emotional, information, social capital)
   - Subreddit as institution category
   - Post author as "institutional agent" or resource provider
   - Post metadata: score, engagement level, lifespan

2. **User-Institution relationship attributes:**
   - Type of engagement (top-level comment, nested reply, multiple comments)
   - Temporal pattern (one-time vs. repeated access)
   - Engagement depth (how deeply involved in the institution)

### Phase 2: Create Bipartite Analysis
Create new analysis script: `institutional_network_analysis.py`

**Features:**
- Load existing network data
- Build bipartite graph (users ↔ posts)
- Calculate institutional centrality measures
- Identify key institutions and institutional access patterns
- Export for visualization

### Phase 3: Project to User Network
Enhance `analyze_relationship_strength.py`

**Add institutional perspective:**
- Reframe co-participation as institutional mediation
- Calculate "institutional diversity" for each user
- Identify institutional brokers
- Measure path distances through institutional space

### Phase 4: Integration with Simulations
**networkSim:**
- Institutions as nodes where token exchanges occur
- Users access institutions to trade resources
- Transaction costs vary by institutional type

**socialLadderSim:**
- Institutions provide access to different resource types
  - Financial institutions (r/assistance posts)
  - Knowledge institutions (r/povertyfinance advice)
  - Emotional support institutions (venting/support posts)
- Network traversal costs depend on institutional access
- Resource accumulation through institutional participation

## Key Questions to Answer

### Research Questions
1. **Do users with more diverse institutional access have better outcomes?**
2. **Are there users who act as "institutional brokers" connecting different communities?**
3. **How does institutional access inequality relate to poverty outcomes?**
4. **Do different subreddits represent different institutional environments?**
5. **What is the "cost" of accessing different institutions?**

### Methodological Questions
1. **How do we classify institution types from post content?**
2. **What metrics best capture institutional effectiveness?**
3. **How do we measure the "value" of different institutions?**
4. **What temporal patterns exist in institutional access?**

## Connection to Research Framework

### Bridges Out of Poverty Resources
Map institutions to resource types:
- **Financial institutions:** r/assistance direct help posts
- **Social Capital institutions:** Community engagement posts
- **Knowledge institutions:** Advice and information posts
- **Emotional institutions:** Support and venting posts
- **Relationship institutions:** Posts that create ongoing connections

### Hypothesis Testing
**Original hypothesis:** 
> "Being in poverty means you don't have many connections, your network is shallow, or your network costs a lot to access."

**Institutional reframe:**
> "Being in poverty means you have limited access to effective institutions, access to low-value institutions only, or high costs to access valuable institutions."

## Next Steps

1. **Classify existing posts by institution type** (manual or NLP-based)
2. **Build bipartite network** from existing data
3. **Calculate institutional metrics** (centrality, diversity, effectiveness)
4. **Analyze institutional access patterns** across subreddits
5. **Project to user network** with institutional lens
6. **Compare across subreddits** to see if different communities have different institutional environments
7. **Integrate findings** into simulation models

## Expected Outcomes

### Analytical Outputs
- Bipartite network visualizations (users ↔ institutions)
- Institutional access distribution plots
- User institutional diversity scores
- Institutional effectiveness rankings
- Community clustering around institution types

### Theoretical Contributions
- Framework for understanding poverty through institutional access
- Operationalization of "weak institutions" through network structure
- Empirical evidence of institutional substitution in online communities
- Bridge between network analysis and institutional economics

### Simulation Integration
- Realistic network topologies based on actual institutional access patterns
- Resource flow models grounded in observed institutional mediation
- Cost structures derived from engagement patterns
- Network formation rules based on institutional participation

---

## References to Project Components

- **reddit_scraper.py:** Already captures post-level data and user participation
- **analyze_relationship_strength.py:** Co-participation edges = institutional connections
- **graph_filtering_methods.py:** Could add institution-based filtering
- **reddit_network_full_analysis.py:** Add institutional metrics to existing analysis
- **networkSim/:** Token exchanges through institutional nodes
- **socialLadderSim/:** Resources accessed through institutions

---

*This document captures the conceptual framework for reframing the Reddit network analysis through an institutional lens, where posts represent institutions that mediate social connections and resource access, directly aligning with research on network effects on poverty and institutional economics.*
