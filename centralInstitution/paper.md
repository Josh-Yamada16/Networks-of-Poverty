# Central Institution Model - Research Notes

## Core Model

- Base off of two behaviors
- Open world setting
- Central institution has job to change to a different behavior that decreases inequity
- Measure how many people change behavior

## Behavior Model (CC Model)

- Behavior A is stationary
- Behavior B is adding edges
- Central institution is helping to change behavior

## Decision Models

- Absolute model (safety)
- Fractional threshold ("Is this what people like me do?")
- Expected utility

## Independent Variables

- Network type
- Behavior B
- Edge budget
- Thresholds

## How Behavior Spreads - Damon Centola
- contagions should be able to spread through weak ties like how viruses spread through the vulnerable population

 ## Central Institution behavior
 - More institutions are added with constant amount of connections
 - Institution grows in connections
    - connections to other random nodes
    - conenctions to neighbors of already connected nodes
- Insitution moves around in the graph

## Experiments

- Infection threshold: try 0.45 to 0.70
- Initial infected fraction: try 0.02 to 0.15
- Central institution connection percentage: try 0.20 to 0.60
- Number of iterations before intervention condition
- Network community strength knobs (inter-block and within-block connectivity)
- Hub-leaf knobs (hub fraction, hub-leaf probability, leaf-leaf probability)
- Initial infection type (random vs block-seeded vs dispersed)

- Suggested sweep:
    - threshold: 0.50, 0.55, 0.60
    - initial infected: 0.03, 0.07, 0.10
    - CI connection: 0.20, 0.35, 0.50
    - record infection at intervention time, final infection, delta after intervention, and iterations to convergence
