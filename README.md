# Python-Based Integrated Rocket Performance and Mission Analysis System

## 1. Project Overview

This project is a Python-based rocket performance and mission analysis system developed to study the propulsion characteristics and vertical flight behaviour of a multistage rocket.

The program calculates important propulsion parameters and simulates the rocket's vertical trajectory by considering thrust, gravitational acceleration and aerodynamic drag.

## 2. Objectives

- Calculate exhaust velocity using specific impulse.
- Determine propellant mass flow rate and rocket thrust.
- Calculate total impulse and ideal velocity change.
- Analyse individual rocket-stage performance.
- Determine nozzle expansion ratio.
- Simulate vertical rocket motion.
- Analyse altitude, velocity, acceleration, mass and Mach number during flight.
- Visualise simulation results using graphs.

## 3. Key Features

- Multistage rocket performance calculations.
- Propulsion parameter estimation.
- Tsiolkovsky rocket equation implementation.
- Atmospheric pressure and density estimation.
- Aerodynamic drag calculation.
- Vertical trajectory simulation.
- Orbital reference calculations.
- Graphical representation of flight parameters.

## 4. Theoretical Concepts

The project uses the following propulsion and flight mechanics equations:

**Exhaust velocity**

Ve = Isp × g0

**Mass flow rate**

mdot = mp / tb

**Thrust**

F = mdot × Ve

**Ideal velocity change**

ΔV = Isp × g0 × ln(m0 / mf)

**Nozzle expansion ratio**

ε = Ae / At

The trajectory model considers the forces acting on the rocket during vertical flight.

## 5. Technologies Used

- Python 3
- Matplotlib
- Python Math module

## 6. Installation Requirements

Install Python 3 and the required library.

```bash
python -m pip install -r requirements.txt
```

## 7. How to Run the Project

1. Clone or download this repository.
2. Open the project folder in Visual Studio Code or another Python IDE.
3. Install the required dependencies.
4. Execute the following command:

```bash
python Python-Rocket-Performance-Mission-Analysis.py
```

5. Enter the rocket configuration and stage parameters when prompted.
6. Observe the calculated performance parameters and trajectory visualisations.

## 8. Simulation Outputs

The program analyses and visualises:

- Altitude versus time
- Velocity versus time
- Acceleration versus time
- Rocket mass versus time
- Mach number versus time
- Aerodynamic drag versus time
- Thrust versus time

## 9. Model Assumptions and Limitations

- The trajectory simulation considers one-dimensional vertical motion.
- Thrust and specific impulse are assumed constant during each stage burn.
- Atmospheric properties are estimated using a simplified atmospheric lookup table.
- Aerodynamic drag is calculated using a simplified drag model.
- Stage separation is represented by discarding the dry mass of the completed stage.
- Orbital calculations provide reference values and do not represent a complete orbital insertion simulation.

## 10. Project Author

Individual Academic Project  
B.Tech Aerospace Engineering

**Repository:**  
https://github.com/indesh-bit/Python-Rocket-Performance-Mission-Analysis
