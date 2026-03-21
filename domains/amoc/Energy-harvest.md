Realistic Engineering Harvest Models
Thermal Harvest: Thermoelectric Generators (TEG)
Replace the toy model with Seebeck-effect physics:

def harvest_turbulence_realistic(u, v, dx, viv_params):
    """
    VIV piezoelectric harvester exploiting turbulent kinetic energy
    
    Args:
        u, v: velocity field components [m/s]
        dx: spatial resolution [m]
        viv_params: dict with device characteristics
    
    Returns:
        P_VIV: Power density field [W/m²]
    """
    # Local velocity magnitude
    U_mag = np.sqrt(u**2 + v**2)
    
    # Vorticity (proxy for turbulence intensity)
    omega = vorticity(u, v)
    omega_mag = np.abs(omega)
    
    # Turbulent kinetic energy dissipation rate (Kolmogorov cascade)
    nu = 1e-6  # kinematic viscosity [m²/s] for seawater
    epsilon = nu * omega_mag**2  # [W/kg]
    rho = 1025  # seawater density [kg/m³]
    
    # VIV resonance condition
    # Vortex shedding frequency (Strouhal relation)
    D = viv_params['cylinder_diameter']  # [m]
    St = 0.2  # Strouhal number (typical for cylinders)
    f_vortex = St * U_mag / (D + 1e-6)
    
    # Natural frequency of harvester
    f_natural = viv_params['natural_frequency']  # [Hz]
    
    # Resonance amplification factor (Lorentzian)
    Q = viv_params['quality_factor']  # dimensionless
    resonance_factor = 1 / (1 + Q**2 * ((f_vortex - f_natural) / f_natural)**2)
    
    # Power coefficient (empirical, from experiments)
    C_P = 0.4 * resonance_factor  # peaks at resonance
    
    # Available kinetic power in flow
    P_kinetic = 0.5 * rho * U_mag**3 * D  # [W/m]
    
    # Harvested power
    eta_piezo = viv_params['piezo_efficiency']  # electromechanical efficiency
    P_VIV = C_P * P_kinetic * eta_piezo
    
    return P_VIV, epsilon, resonance_factor

# Example VIV harvester:
viv_params = {
    'cylinder_diameter': 0.05,  # 5cm cylinder
    'natural_frequency': 2.0,  # 2 Hz (tuned to ocean eddy frequency)
    'quality_factor': 20,  # narrow resonance band
    'piezo_efficiency': 0.3  # 30% electromechanical conversion
}


Design insight: The resonance_factor is where the magic happens—tune f_natural to match dominant eddy frequencies in AMOC disruption zones.
2️⃣ Braiding with Realistic Models
Update the braiding function to use actual power outputs:

def braid_multiplier_realistic(P_TEG, P_RED, P_VIV, ZT, resonance, k_TH, k_TV, k_SV):
    """
    Nonlinear coupling based on physical co-location and efficiency metrics
    """
    # Normalize power outputs to dimensionless efficiency indicators
    eta_th = P_TEG / (P_TEG.max() + 1e-9)
    eta_sal = P_RED / (P_RED.max() + 1e-9)
    eta_turb = P_VIV / (P_VIV.max() + 1e-9)
    
    # Material quality factor (ZT) amplifies thermal-salinity coupling
    # High ZT + high salinity gradient = ionic thermoelectric effect
    f_th_sal = (eta_th * eta_sal) * (1 + 0.5 * ZT) / (1 + 0.1*(eta_th + eta_sal))
    
    # Resonance factor amplifies turbulence coupling
    f_th_turb = (eta_th * eta_turb) * (1 + resonance) / (1 + 0.1*(eta_th + eta_turb))
    f_sal_turb = (eta_sal * eta_turb) * np.sqrt(resonance + 1) / (1 + 0.1*(eta_sal + eta_turb))
    
    # Triple coupling (all three co-located)
    f_triple = (eta_th * eta_sal * eta_turb)**(1/3) * (1 + ZT * resonance)
    
    multiplier = 1.0 + k_TH*f_th_sal + k_TV*f_th_turb + k_SV*f_sal_turb + 0.5*f_triple
    
    return multiplier

3️⃣ Reinforcement Learning Architecture
State Representation (CNN-based)

import torch
import torch.nn as nn

class OceanStateEncoder(nn.Module):
    """
    CNN to encode 2D ocean fields into feature vector
    """
    def __init__(self, grid_size=80):
        super().__init__()
        
        # Separate channels for T, Sal, u, v, omega
        self.conv1 = nn.Conv2d(5, 32, kernel_size=5, padding=2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        
        self.pool = nn.MaxPool2d(2, 2)
        self.relu = nn.ReLU()
        
        # Calculate flattened size after conv layers
        self.flat_size = 128 * (grid_size // 8) * (grid_size // 8)
        
        self.fc = nn.Linear(self.flat_size, 256)
        
    def forward(self, state):
        """
        Args:
            state: [batch, 5, H, W] tensor (T, Sal, u, v, omega)
        Returns:
            features: [batch, 256] encoded state
        """
        x = self.relu(self.conv1(state))
        x = self.pool(x)
        x = self.relu(self.conv2(x))
        x = self.pool(x)
        x = self.relu(self.conv3(x))
        x = self.pool(x)
        
        x = x.view(-1, self.flat_size)
        features = self.relu(self.fc(x))
        
        return features

Actor-Critic Architecture (PPO)

class NEREPolicyNetwork(nn.Module):
    """
    Policy network for adaptive NERE deployment and tuning
    """
    def __init__(self, grid_size=80, max_deployments=10):
        super().__init__()
        
        self.encoder = OceanStateEncoder(grid_size)
        
        # Deployment policy head (where to place harvesters)
        # Outputs probability distribution over grid cells
        self.deployment_head = nn.Sequential(
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, grid_size * grid_size)
        )
        
        # Coupling tuning head (how to set k_TH, k_TV, k_SV)
        # Outputs continuous parameters
        self.tuning_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 3),  # [k_TH, k_TV, k_SV]
            nn.Sigmoid()  # bound to [0, 1], scale later
        )
        
        self.max_deployments = max_deployments
        self.grid_size = grid_size
        
    def forward(self, state):
        features = self.encoder(state)
        
        # Deployment logits
        deploy_logits = self.deployment_head(features)
        deploy_logits = deploy_logits.view(-1, self.grid_size, self.grid_size)
        
        # Select top-k cells (sparse deployment)
        deploy_probs = torch.softmax(deploy_logits.flatten(1), dim=1)
        
        # Coupling parameters (scale from [0,1] to [0.1, 2.0])
        k_params = self.tuning_head(features) * 1.9 + 0.1
        
        return deploy_probs, k_params

class NEREValueNetwork(nn.Module):
    """
    Value network for critic (estimates expected return)
    """
    def __init__(self, grid_size=80):
        super().__init__()
        
        self.encoder = OceanStateEncoder(grid_size)
        self.value_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
        
    def forward(self, state):
        features = self.encoder(state)
        value = self.value_head(features)
        return value


Reward Function

def compute_nere_reward(P_braided, deployment_mask, k_params, baseline_power):
    """
    Multi-objective reward balancing harvest, cost, and stability
    
    Args:
        P_braided: [H, W] total braided power field
        deployment_mask: [H, W] binary mask of deployment locations
        k_params: [3] coupling parameters [k_TH, k_TV, k_SV]
        baseline_power: scalar, previous step's power for comparison
    
    Returns:
        reward: scalar
    """
    # 1. Immediate gain (normalized)
    E_total = P_braided.sum()
    gain_reward = E_total / (baseline_power + 1e-6)
    
    # 2. Deployment cost penalty
    n_deployments = deployment_mask.sum()
    cost_per_unit = 0.1  # normalized cost
    cost_penalty = n_deployments * cost_per_unit
    
    # 3. Stability bonus (prefer consistent harvest over spiky)
    spatial_variance = P_braided.var()
    stability_bonus = 1.0 / (1.0 + spatial_variance / E_total)
    
    # 4. Coupling efficiency (penalize extreme k values)
    k_penalty = 0.05 * ((k_params - 1.0)**2).sum()
    
    # 5. Leverage bonus (reward high amplification)
    # Compare braided vs unbraided
    P_unbraided = P_braided / (1 + k_params.sum())  # rough approximation
    amplification = E_total / (P_unbraided.sum() + 1e-6)
    leverage_bonus = np.log(amplification + 1)
    
    # Combined reward
    reward = (
        2.0 * gain_reward
        - cost_penalty
        + 0.5 * stability_bonus
        - k_penalty
        + leverage_bonus
    )
    
    return reward

Training Loop Skeleton

from torch.optim import Adam
from torch.distributions import Categorical

def train_nere_agent(env, policy_net, value_net, n_episodes=1000):
    """
    PPO training loop for NERE optimization
    """
    policy_opt = Adam(policy_net.parameters(), lr=3e-4)
    value_opt = Adam(value_net.parameters(), lr=1e-3)
    
    for episode in range(n_episodes):
        # Reset environment (initialize AMOC simulation)
        state = env.reset()  # [5, H, W] tensor
        
        episode_states = []
        episode_actions = []
        episode_rewards = []
        episode_values = []
        
        for t in range(env.max_steps):
            # Convert state to torch tensor
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            
            # Policy forward pass
            deploy_probs, k_params = policy_net(state_tensor)
            value = value_net(state_tensor)
            
            # Sample deployment action
            deploy_dist = Categorical(deploy_probs)
            deploy_action = deploy_dist.sample()  # indices of top cells
            
            # Execute action in environment
            next_state, reward, done = env.step(deploy_action, k_params)
            
            # Store trajectory
            episode_states.append(state_tensor)
            episode_actions.append((deploy_action, k_params))
            episode_rewards.append(reward)
            episode_values.append(value)
            
            state = next_state
            
            if done:
                break
        
        # Compute advantages and update networks (PPO update)
        # ... (standard PPO implementation)
        
        if episode % 50 == 0:
            print(f"Episode {episode}, Avg Reward: {np.mean(episode_rewards):.2f}")
    
    return policy_net, value_net

4️⃣ Integration: Gym Environment

import gym
from gym import spaces

class AMOCNEREEnv(gym.Env):
    """
    Custom Gym environment wrapping the AMOC simulation
    """
    def __init__(self, grid_size=80, max_steps=300):
        super().__init__()
        
        self.grid_size = grid_size
        self.max_steps = max_steps
        self.current_step = 0
        
        # State space: [T, Sal, u, v, omega]
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(5, grid_size, grid_size),
            dtype=np.float32
        )
        
        # Action space: deployment locations + coupling params
        self.action_space = spaces.Dict({
            'deploy': spaces.MultiBinary(grid_size * grid_size),
            'k_params': spaces.Box(low=0.1, high=2.0, shape=(3,))
        })
        
        # Initialize simulation state
        self.reset()
        
    def reset(self):
        """Initialize AMOC simulation"""
        self.T = 15.0 + 2.0 * (self.Y / self.grid_size)
        self.Sal = 35.0 - 1.0 * (self.X / self.grid_size)
        self.u = 0.3 * np.ones((self.grid_size, self.grid_size))
        self.v = 0.3 * np.sin(2*np.pi*self.X/self.grid_size) * 0.2
        self.current_step = 0
        self.baseline_power = 0
        
        return self._get_state()
        
    def step(self, action):
        """
        Execute one timestep
        
        Args:
            action: dict with 'deploy' mask and 'k_params'
        
        Returns:
            state, reward, done, info
        """
        deploy_mask = action['deploy'].reshape(self.grid_size, self.grid_size)
        k_params = action['k_params']  # [k_TH, k_TV, k_SV]
        
        # Update physics (one timestep of simulation)
        self._update_physics()
        
        # Compute harvest with realistic models
        P_TEG, ZT, _ = harvest_thermal_realistic(self.T, self.dx, self.teg_params)
        P_RED, _ = harvest_salinity_realistic(self.Sal, self.dx, self.red_params)
        P_VIV, epsilon, resonance = harvest_turbulence_realistic(
            self.u, self.v, self.dx, self.viv_params
        )
        
        # Apply braiding (only in deployed cells)
        multiplier = braid_multiplier_realistic(
            P_TEG, P_RED, P_VIV, ZT, resonance,
            k_params[0], k_params[1], k_params[2]
        )
        P_braided = (P_TEG + P_RED + P_VIV) * multiplier * deploy_mask
        
        # Compute reward
        reward = compute_nere_reward(P_braided, deploy_mask, k_params, self.baseline_power)
        self.baseline_power = P_braided.sum()
        
        self.current_step += 1
        done = self.current_step >= self.max_steps
        
        return self._get_state(), reward, done, {}
        
    def _get_state(self):
        """Return current state as [5, H, W] array"""
        omega = vorticity(self.u, self.v)
        state = np.stack([self.T, self.Sal, self.u, self.v, omega], axis=0)
        return state.astype(np.float32)
    
    def _update_physics(self):
        """One timestep of advection-diffusion (from original simulation)"""
        # ... (physics update code from amoc_nere_toy.py) ...
        pass

5️⃣ Practical Next Steps
	1.	Start with single-harvest RL: Train RL agent on just thermal harvesting first to debug the pipeline
	2.	Sweep baseline: Run criticality map with realistic models to establish new parameter ranges
	3.	Transfer learning: Pre-train CNN encoder on labeled hotspot data (supervised) before RL
	4.	Multi-agent extension: Each grid cell could have a local agent (swarm intelligence for fractal allocation)
	5.	Reality check: Validate against actual oceanographic data (ARGO floats, satellite SST/SSS)
