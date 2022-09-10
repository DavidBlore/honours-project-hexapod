from hexapod.controllers.reference_controller import Controller, reshape
from hexapod.controllers.cpg_controller import CPGController
from hexapod.controllers.cpg_controller import CPGParameterHandlerMAPElites
from hexapod.simulator import Simulator
import time
import numpy as np

def evaluate_gait_cpg(x, duration=5, visualiser=False, collision_fatal=True, failed_legs=[], delay=0):
    """Responsible for testing the gait parameters and returning the descriptor and performance/fitness for the CPG controller.

    NOTE: THIS IS FOR THE CPG CONTROLLER ONLY

    Args:
        x (np.array): Array of 156 parameters between 0.0 and 1.0.
            First 12 = intrinsic amplitudes, Next 144 = phase biases.
        duration (float): Duration of the simulation in seconds.
        visualiser: If true, dispaly simuluation in GUI
        collision_fatal: If true, collisions are deemed fatal and given 0.0 fitness
        failed_legs: which legs to fail/break
        delay: number of seconds to delay after each step (slows down simulator)

    Returns:
        (float, np.array): Fitness and Descriptor.
    """
    intrinsic_amplitudes = x[:12]
    intrinsic_amplitudes = CPGParameterHandlerMAPElites.scale_intrinsic_amplitudes(x[:12]) # convert from 12 intrinsic amps in range [0-1]
    phase_biases = CPGParameterHandlerMAPElites.scale_phase_biases(x[12:]) # convert from 144 phase biases in range [0-1]
    fitness = 0.0
    contact_sequence = np.zeros(6)
    try:
        controller = CPGController(
            intrinsic_amplitudes=intrinsic_amplitudes,
            phase_biases=phase_biases,
            seconds=duration,
            velocity=0,
            crab_angle=0
        )
        simulator = Simulator(controller=controller, visualiser=visualiser, collision_fatal=collision_fatal,failed_legs=failed_legs)
        contact_sequence = np.full((6, 0), False)
        t=0
        while t<(240*duration)-1:
            simulator.step()
            time.sleep(delay)
            contact_sequence = np.append(contact_sequence, simulator.supporting_legs().reshape(-1,1), axis=1)
            t=t+1
        fitness = simulator.base_pos()[0] # distance travelled along x axis
        simulator.terminate()
    except:
        """Collision detected, return a fitness of 0.0 and a descriptor of 0s."""
        # print("collision!!!!!!!!!!!!")
        return 0.0, np.zeros(6)
    # summarise descriptor
    descriptor = np.nan_to_num(np.sum(contact_sequence, axis=1) / np.size(contact_sequence, axis=1), nan=0.0, posinf=0.0, neginf=0.0)
    
    # print('fitness',fitness,'descriptor', descriptor) # FOR DEBUG
    return fitness, descriptor

def evaluate_gait_ref(x, duration=5, visualiser=False, collision_fatal=True, failed_legs=[], delay=0):
    """Responsible for testing the gait parameters and returning the descriptor and performance/fitness for the Reference controller.

    NOTE: THIS IS FOR THE REFERENCE CONTROLLER ONLY

    Args:
        x (np.array): Array of 156 parameters between 0.0 and 1.0.
            First 12 = intrinsic amplitudes, Next 144 = phase biases.
        duration (float): Duration of the simulation in seconds.
        visualiser: If true, dispaly simuluation in GUI
        collision_fatal: If true, collisions are deemed fatal and given 0.0 fitness
        failed_legs: which legs to fail/break
        delay: number of seconds to delay after each step (slows down simulator)

    Returns:
        (float, np.array): Fitness and Descriptor.
    """
    body_height, velocity, leg_params = reshape(x)
    try:
        controller = Controller(leg_params, body_height=body_height, velocity=velocity, period=1.0, crab_angle=-np.pi/6)
    except:
        return 0, np.zeros(6)
    simulator = Simulator(controller=controller, visualiser=visualiser, collision_fatal=collision_fatal, failed_legs=failed_legs)
    contact_sequence = np.full((6, 0), False)
    for t in np.arange(0, duration, step=simulator.dt):
        try:
            simulator.step()
            time.sleep(delay)
        except RuntimeError as collision:
            # print("collision")
            return 0, np.zeros(6)
        contact_sequence = np.append(contact_sequence, simulator.supporting_legs().reshape(-1,1), axis=1)
    fitness = simulator.base_pos()[0] # distance travelled along x axis
    # summarise descriptor
    descriptor = np.nan_to_num(np.sum(contact_sequence, axis=1) / np.size(contact_sequence, axis=1), nan=0.0, posinf=0.0, neginf=0.0)
    simulator.terminate()
    # print('fitness',fitness,'descriptor', descriptor) # FOR DEBUG
    return fitness, descriptor


def read_in_individuals(filenames):
    """
    Read in the individuals from files.

    Args:
        filename (str): The filename to read in from.

    Returns:
        ([np.array]): The individuals.
    """
    individuals = []
    for filename in filenames:
        with open(filename, 'r') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if lines[i].startswith('phase_biases:'):
                    # intrinsic_amplitudes
                    intrinsic_amplitudes = lines[i+3][1:-3].split(", ")
                    intrinsic_amplitudes = np.array(intrinsic_amplitudes)
                    intrinsic_amplitudes = CPGParameterHandlerMAPElites.sigmoid_intrinsic_amplitudes(intrinsic_amplitudes.astype(float))
                    # phase_biases
                    phase_biases = np.array(lines[i+1].replace('[','').replace(']','').replace(' ','').replace("None", "0.0").split(','))
                    phase_biases = CPGParameterHandlerMAPElites.sigmoid_phase_bias(phase_biases.astype(float))
                    individuals.append(np.concatenate((intrinsic_amplitudes,phase_biases)))
    return individuals

