
import math
import os
import sys
import matplotlib.pyplot as plt

G0 = 9.80665
EARTH_RADIUS = 6371000
EARTH_MU = 3.986004418e14

ATMOSPHERE = [
    (0, 288.15, 101325, 1.225),
    (1000, 281.65, 89874, 1.112),
    (2000, 275.15, 79495, 1.007),
    (3000, 268.65, 70108, 0.9093),
    (4000, 262.15, 61640, 0.8194),
    (5000, 255.65, 54048, 0.7364),
    (6000, 249.15, 47181, 0.6601),
    (7000, 242.65, 41060, 0.5900),
    (8000, 236.15, 35600, 0.5258),
    (9000, 229.65, 30742, 0.4663),
    (10000, 223.15, 26436, 0.4135),
    (11000, 216.65, 22632, 0.3639),
    (12000, 216.65, 19399, 0.3108),
    (15000, 216.65, 12045, 0.1948),
    (20000, 216.65, 5475, 0.08891),
    (25000, 221.65, 2511, 0.03947),
    (30000, 226.65, 1172, 0.01841),
    (35000, 237.05, 558.9, 0.00857),
    (40000, 250.35, 287.1, 0.003996),
    (50000, 270.65, 79.78, 0.001027)
]


def positive_float(message):
    while True:
        try:
            value = float(input(message))
            if math.isfinite(value) and value > 0:
                return value
            print("Enter a number greater than zero.")
        except ValueError:
            print("Enter a valid number.")


def integer_input(message, minimum, maximum):
    while True:
        try:
            value = int(input(message))
            if minimum <= value <= maximum:
                return value
            print("Enter a value between", minimum, "and", maximum)
        except ValueError:
            print("Enter a valid integer.")


def exhaust_velocity(isp):
    return isp * G0


def mass_flow_rate(propellant_mass, burn_time):
    return propellant_mass / burn_time


def calculate_thrust(propellant_mass, burn_time, isp):
    return mass_flow_rate(propellant_mass, burn_time) * exhaust_velocity(isp)


def calculate_delta_v(isp, initial_mass, final_mass):
    if initial_mass <= final_mass or final_mass <= 0:
        return 0
    return isp * G0 * math.log(initial_mass / final_mass)


def orbital_velocity(altitude):
    radius = EARTH_RADIUS + altitude
    return math.sqrt(EARTH_MU / radius)


def orbital_period(altitude):
    radius = EARTH_RADIUS + altitude
    return 2 * math.pi * math.sqrt(radius ** 3 / EARTH_MU)


def escape_velocity(altitude):
    radius = EARTH_RADIUS + altitude
    return math.sqrt(2 * EARTH_MU / radius)


def gravity(altitude):
    radius = EARTH_RADIUS + altitude
    return EARTH_MU / radius ** 2


def atmosphere(altitude):
    altitude = max(0, altitude)

    if altitude >= 50000:
        return 270.65, 0, 0

    for i in range(len(ATMOSPHERE) - 1):
        h1, t1, p1, rho1 = ATMOSPHERE[i]
        h2, t2, p2, rho2 = ATMOSPHERE[i + 1]

        if h1 <= altitude <= h2:
            fraction = (altitude - h1) / (h2 - h1)

            temperature = t1 + fraction * (t2 - t1)
            pressure = p1 + fraction * (p2 - p1)
            density = rho1 + fraction * (rho2 - rho1)

            return temperature, pressure, density

    return 288.15, 101325, 1.225


def speed_of_sound(temperature):
    return math.sqrt(1.4 * 287.05 * temperature)


def drag_force(altitude, velocity, cd, reference_area):
    temperature, pressure, density = atmosphere(altitude)

    return 0.5 * density * velocity * abs(velocity) * cd * reference_area


def get_stage_data(stage_number):
    print("\n" + "=" * 60)
    print("STAGE", stage_number)
    print("=" * 60)

    dry_mass = positive_float("Dry mass (kg): ")
    propellant_mass = positive_float("Propellant mass (kg): ")
    isp = positive_float("Specific impulse (s): ")
    burn_time = positive_float("Burn time (s): ")
    chamber_pressure = positive_float("Chamber pressure (MPa): ")
    throat_area = positive_float("Nozzle throat area (m^2): ")
    exit_area = positive_float("Nozzle exit area (m^2): ")

    if exit_area < throat_area:
        print("Warning: Exit area is smaller than throat area.")

    return {
        "dry_mass": dry_mass,
        "propellant_mass": propellant_mass,
        "isp": isp,
        "burn_time": burn_time,
        "chamber_pressure": chamber_pressure,
        "throat_area": throat_area,
        "exit_area": exit_area
    }


def calculate_stage_results(stages, payload_mass):
    total_dry_mass = sum(s["dry_mass"] for s in stages)
    total_propellant_mass = sum(s["propellant_mass"] for s in stages)

    initial_mass = payload_mass + total_dry_mass + total_propellant_mass
    current_mass = initial_mass
    total_delta_v = 0
    results = []

    for stage in stages:
        stage_initial_mass = current_mass
        stage_final_mass = stage_initial_mass - stage["propellant_mass"]

        ve = exhaust_velocity(stage["isp"])
        mdot = mass_flow_rate(stage["propellant_mass"], stage["burn_time"])
        thrust = mdot * ve
        impulse = thrust * stage["burn_time"]

        delta_v = calculate_delta_v(
            stage["isp"],
            stage_initial_mass,
            stage_final_mass
        )

        expansion_ratio = stage["exit_area"] / stage["throat_area"]

        results.append({
            "initial_mass": stage_initial_mass,
            "final_mass": stage_final_mass,
            "exhaust_velocity": ve,
            "mass_flow": mdot,
            "thrust": thrust,
            "impulse": impulse,
            "delta_v": delta_v,
            "expansion_ratio": expansion_ratio
        })

        total_delta_v += delta_v
        current_mass = stage_final_mass - stage["dry_mass"]

    return (
        total_dry_mass,
        total_propellant_mass,
        initial_mass,
        total_delta_v,
        results
    )


def trajectory_simulation(stages, payload_mass, cd, reference_area):
    total_dry_mass = sum(s["dry_mass"] for s in stages)
    total_propellant_mass = sum(s["propellant_mass"] for s in stages)

    mass = payload_mass + total_dry_mass + total_propellant_mass

    time = 0.0
    altitude = 0.0
    velocity = 0.0
    dt = 0.5

    trajectory = []

    trajectory.append({
        "time": time,
        "altitude": altitude,
        "velocity": velocity,
        "acceleration": 0.0,
        "mass": mass,
        "mach": 0.0,
        "drag": 0.0,
        "thrust": 0.0
    })

    for stage_number, stage in enumerate(stages, start=1):
        mdot = mass_flow_rate(
            stage["propellant_mass"],
            stage["burn_time"]
        )

        thrust = calculate_thrust(
            stage["propellant_mass"],
            stage["burn_time"],
            stage["isp"]
        )

        remaining_time = stage["burn_time"]

        while remaining_time > 1e-9:
            step = min(dt, remaining_time)

            temperature, pressure, density = atmosphere(altitude)
            sound_speed = speed_of_sound(temperature)

            mach = abs(velocity) / sound_speed if sound_speed > 0 else 0

            drag = drag_force(
                altitude,
                velocity,
                cd,
                reference_area
            )

            gravitational_force = gravity(altitude)

            acceleration = (
                thrust - drag
            ) / mass - gravitational_force

            new_velocity = velocity + acceleration * step
            new_altitude = altitude + new_velocity * step

            if new_altitude < 0:
                new_altitude = 0
                if new_velocity < 0:
                    new_velocity = 0

            mass -= mdot * step
            remaining_time -= step
            time += step

            altitude = new_altitude
            velocity = new_velocity

            trajectory.append({
                "time": time,
                "altitude": altitude,
                "velocity": velocity,
                "acceleration": acceleration,
                "mass": mass,
                "mach": mach,
                "drag": drag,
                "thrust": thrust
            })

        mass -= stage["dry_mass"]

        if mass <= 0:
            raise ValueError("Invalid rocket mass after stage separation.")

        if stage_number < len(stages):
            trajectory.append({
                "time": time,
                "altitude": altitude,
                "velocity": velocity,
                "acceleration": 0.0,
                "mass": mass,
                "mach": trajectory[-1]["mach"],
                "drag": trajectory[-1]["drag"],
                "thrust": 0.0
            })

    return trajectory


def print_stage_report(stages, results):
    for i, (stage, result) in enumerate(zip(stages, results), start=1):
        print("\n" + "=" * 60)
        print("STAGE", i, "PERFORMANCE")
        print("=" * 60)

        print("Initial Mass       :", round(result["initial_mass"], 2), "kg")
        print("Final Mass         :", round(result["final_mass"], 2), "kg")
        print("Specific Impulse   :", stage["isp"], "s")
        print("Exhaust Velocity   :", round(result["exhaust_velocity"], 2), "m/s")
        print("Mass Flow Rate     :", round(result["mass_flow"], 2), "kg/s")
        print("Thrust             :", round(result["thrust"], 2), "N")
        print("Thrust             :", round(result["thrust"] / 1e6, 3), "MN")
        print("Total Impulse      :", round(result["impulse"], 2), "N.s")
        print("Stage Delta-V      :", round(result["delta_v"], 2), "m/s")
        print("Stage Delta-V      :", round(result["delta_v"] / 1000, 3), "km/s")

        print("\nNOZZLE ANALYSIS")
        print("Chamber Pressure   :", stage["chamber_pressure"], "MPa")
        print("Throat Area        :", stage["throat_area"], "m^2")
        print("Exit Area          :", stage["exit_area"], "m^2")
        print("Expansion Ratio    :", round(result["expansion_ratio"], 3))


def print_trajectory_report(trajectory):
    maximum_altitude = max(p["altitude"] for p in trajectory)
    maximum_velocity = max(p["velocity"] for p in trajectory)
    maximum_acceleration = max(p["acceleration"] for p in trajectory)
    maximum_mach = max(p["mach"] for p in trajectory)
    maximum_drag = max(abs(p["drag"]) for p in trajectory)

    print("\n" + "=" * 60)
    print("TRAJECTORY ANALYSIS")
    print("=" * 60)

    print("Maximum Altitude     :", round(maximum_altitude / 1000, 3), "km")
    print("Maximum Velocity     :", round(maximum_velocity, 2), "m/s")
    print("Maximum Velocity     :", round(maximum_velocity / 1000, 3), "km/s")
    print("Maximum Acceleration :", round(maximum_acceleration, 2), "m/s^2")
    print("Maximum Mach Number  :", round(maximum_mach, 3))
    print("Maximum Drag         :", round(maximum_drag, 2), "N")


def plot_all_graphs(trajectory):
    os.makedirs("visualizations", exist_ok=True)

    time = [p["time"] for p in trajectory]

    altitude = [p["altitude"] / 1000 for p in trajectory]
    velocity = [p["velocity"] / 1000 for p in trajectory]
    acceleration = [p["acceleration"] for p in trajectory]
    mass = [p["mass"] / 1000 for p in trajectory]
    mach = [p["mach"] for p in trajectory]
    drag = [p["drag"] / 1000 for p in trajectory]
    thrust = [p["thrust"] / 1e6 for p in trajectory]

    graphs = [
        (altitude, "Altitude vs Time", "Altitude (km)", "altitude_vs_time.png"),
        (velocity, "Velocity vs Time", "Velocity (km/s)", "velocity_vs_time.png"),
        (acceleration, "Acceleration vs Time", "Acceleration (m/s^2)", "acceleration_vs_time.png"),
        (mass, "Mass vs Time", "Mass (tonnes)", "mass_vs_time.png"),
        (mach, "Mach Number vs Time", "Mach Number", "mach_vs_time.png"),
        (drag, "Drag Force vs Time", "Drag Force (kN)", "drag_vs_time.png"),
        (thrust, "Thrust vs Time", "Thrust (MN)", "thrust_vs_time.png")
    ]

    for values, title, y_label, filename in graphs:
        plt.figure(figsize=(9, 5))
        plt.plot(time, values, linewidth=2)
        plt.xlabel("Time (s)")
        plt.ylabel(y_label)
        plt.title(title)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join("visualizations", filename), dpi=300, bbox_inches="tight")

    print("\\nSeven graphs generated and saved in the 'visualizations' folder.")
    plt.show()


def main():
    print("\n" + "=" * 65)
    print(" PYTHON-BASED INTEGRATED ROCKET PERFORMANCE")
    print("          AND MISSION ANALYSIS SYSTEM")
    print("=" * 65)

    rocket_name = input("\nEnter rocket name: ").strip()

    if not rocket_name:
        rocket_name = "Custom Rocket"

    payload_mass = positive_float("Enter payload mass (kg): ")

    number_of_stages = integer_input(
        "Enter number of stages (1-3): ",
        1,
        3
    )

    stages = []

    for i in range(number_of_stages):
        stages.append(get_stage_data(i + 1))

    print("\n" + "=" * 60)
    print("MISSION CONFIGURATION")
    print("=" * 60)

    target_altitude_km = positive_float("Target orbit altitude (km): ")
    cd = positive_float("Rocket drag coefficient (Cd): ")
    reference_area = positive_float("Rocket reference area (m^2): ")

    target_altitude = target_altitude_km * 1000

    (
        total_dry_mass,
        total_propellant_mass,
        initial_mass,
        total_delta_v,
        results
    ) = calculate_stage_results(stages, payload_mass)

    trajectory = trajectory_simulation(
        stages,
        payload_mass,
        cd,
        reference_area
    )

    circular_velocity = orbital_velocity(target_altitude)
    orbital_time = orbital_period(target_altitude)
    escape_speed = escape_velocity(target_altitude)

    gravity_loss = 1500
    drag_loss = 300
    steering_loss = 100

    estimated_losses = gravity_loss + drag_loss + steering_loss
    estimated_required_delta_v = circular_velocity + estimated_losses
    delta_v_margin = total_delta_v - estimated_required_delta_v

    print("\n\n" + "=" * 65)
    print("ROCKET PERFORMANCE REPORT")
    print("=" * 65)

    print("Rocket Name          :", rocket_name)
    print("Number of Stages     :", number_of_stages)
    print("Payload Mass         :", round(payload_mass, 2), "kg")
    print("Total Dry Mass       :", round(total_dry_mass, 2), "kg")
    print("Total Propellant     :", round(total_propellant_mass, 2), "kg")
    print("Initial Rocket Mass  :", round(initial_mass, 2), "kg")

    print_stage_report(stages, results)

    print("\n" + "=" * 60)
    print("TOTAL ROCKET PERFORMANCE")
    print("=" * 60)

    print("Total Ideal Delta-V  :", round(total_delta_v, 2), "m/s")
    print("Total Ideal Delta-V  :", round(total_delta_v / 1000, 3), "km/s")

    temperature, pressure, density = atmosphere(target_altitude)
    sound_speed = speed_of_sound(temperature)

    print("\n" + "=" * 60)
    print("ATMOSPHERIC ANALYSIS AT TARGET ALTITUDE")
    print("=" * 60)

    print("Temperature          :", round(temperature, 2), "K")
    print("Pressure             :", round(pressure, 2), "Pa")
    print("Density              :", round(density, 6), "kg/m^3")
    print("Speed of Sound       :", round(sound_speed, 2), "m/s")

    print("\n" + "=" * 60)
    print("ORBIT ANALYSIS")
    print("=" * 60)

    print("Target Orbit         :", target_altitude_km, "km")
    print("Circular Orbital Speed:", round(circular_velocity, 2), "m/s")
    print("Escape Velocity      :", round(escape_speed, 2), "m/s")
    print("Orbital Period       :", round(orbital_time / 60, 2), "minutes")

    print("\n" + "=" * 60)
    print("SIMPLIFIED DELTA-V BUDGET")
    print("=" * 60)

    print("Ideal Delta-V        :", round(total_delta_v / 1000, 3), "km/s")
    print("Estimated Gravity Loss: 1.500 km/s")
    print("Estimated Drag Loss  : 0.300 km/s")
    print("Estimated Steering Loss: 0.100 km/s")
    print("Estimated Required   :", round(estimated_required_delta_v / 1000, 3), "km/s")
    print("Estimated Margin     :", round(delta_v_margin / 1000, 3), "km/s")

    print("\nNote: Loss allowances are illustrative estimates, not simulated losses.")

    if delta_v_margin >= 0:
        print("Assessment: Ideal Delta-V exceeds the simplified estimate.")
    else:
        print("Assessment: Ideal Delta-V is below the simplified estimate.")

    print_trajectory_report(trajectory)

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    print("Rocket               :", rocket_name)
    print("Initial Mass         :", round(initial_mass, 2), "kg")
    print("Total Propellant     :", round(total_propellant_mass, 2), "kg")
    print("Total Ideal Delta-V  :", round(total_delta_v / 1000, 3), "km/s")
    print("Target Orbit         :", target_altitude_km, "km")
    print("Orbital Velocity     :", round(circular_velocity / 1000, 3), "km/s")

    print("\nGenerating all seven graphs...")

    plot_all_graphs(trajectory)

    print("\nAnalysis completed.")


class TeeOutput:
    """Write console output to both the terminal and a text file."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, message):
        for stream in self.streams:
            stream.write(message)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)

    output_path = os.path.join("outputs", "simulation_results.txt")
    with open(output_path, "w", encoding="utf-8") as output_file:
        original_stdout = sys.stdout
        try:
            sys.stdout = TeeOutput(original_stdout, output_file)
            main()
        finally:
            sys.stdout = original_stdout

    print("\\nProgram output saved to:", output_path)
