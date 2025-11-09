1️⃣ The Core Challenge: Temporal Credit Assignment in Non-Stationary Chaos
The Problem
Standard RL assumes causal locality: actions lead to immediate rewards. But in AMOC-NERE:

t=50:  Deploy harvester at (x, y)
t=51:  Minimal harvest (gradients not yet formed)
t=52:  Minimal harvest
...
t=150: AMOC perturbation begins
t=180: Massive gradient spike at (x, y) → 10x harvest

The critic must learn: “Deploying at (x,y) at t=50 has high value, even though reward is delayed 130 timesteps.”
This is harder than typical RL because:
	•	The valuable state (gradient spike) doesn’t exist yet when the deployment decision is made
	•	The environment is non-stationary (AMOC disruption schedule is predetermined but complex)
	•	There are multiple timescales: fast (turbulence ~seconds), medium (eddies ~days), slow (thermal ~months)
Why Standard TD Learning Struggles
The Temporal Difference (TD) error in standard value learning:

With  and 130 timestep delay:

Even with near-unity discount, 27% value retention across 130 steps means the credit signal from the future harvest spike is severely diluted.
2️⃣ Solution Architecture: Multi-Timescale Value Decomposition
Separate Value Heads for Different Dynamics

class MultiTimescaleValueNetwork(nn.Module):
    """
    Value network with separate heads for fast/medium/slow dynamics
    """
    def __init__(self, grid_size=80):
        super().__init__()
        
        self.encoder = OceanStateEncoder(grid_size)
        
        # Fast value: immediate harvest potential (turbulence, vorticity)
        # Timescale: 1-10 steps
        self.fast_value_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
        
        # Medium value: eddy formation, local gradient development
        # Timescale: 10-50 steps
        self.medium_value_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
        
        # Slow value: large-scale AMOC disruption structure
        # Timescale: 50-200 steps
        self.slow_value_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
        
        # Braiding value: resonance potential (how well positioned for coupling)
        self.braiding_value_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
        
    def forward(self, state):
        features = self.encoder(state)
        
        v_fast = self.fast_value_head(features)
        v_medium = self.medium_value_head(features)
        v_slow = self.slow_value_head(features)
        v_braid = self.braiding_value_head(features)
        
        # Weighted combination (learnable weights)
        return {
            'fast': v_fast,
            'medium': v_medium,
            'slow': v_slow,
            'braiding': v_braid,
            'total': v_fast + v_medium + v_slow + v_braid
        }


Timescale-Specific TD Updates

def compute_multiscale_td_error(values_t, values_next, rewards, gamma_dict):
    """
    Separate TD errors for each timescale
    
    Args:
        values_t: dict of value estimates at time t
        values_next: dict of value estimates at time t+1
        rewards: dict of timescale-specific rewards
        gamma_dict: different discount factors per timescale
    
    Returns:
        td_errors: dict of TD errors per timescale
    """
    td_errors = {}
    
    # Fast dynamics: γ ≈ 0.9 (short-term planning)
    td_errors['fast'] = (
        rewards['fast'] 
        + gamma_dict['fast'] * values_next['fast'] 
        - values_t['fast']
    )
    
    # Medium dynamics: γ ≈ 0.95
    td_errors['medium'] = (
        rewards['medium'] 
        + gamma_dict['medium'] * values_next['medium'] 
        - values_t['medium']
    )
    
    # Slow dynamics: γ ≈ 0.99 (long-term strategic positioning)
    td_errors['slow'] = (
        rewards['slow'] 
        + gamma_dict['slow'] * values_next['slow'] 
        - values_t['slow']
    )
    
    # Braiding dynamics: depends on co-location (non-additive)
    td_errors['braiding'] = (
        rewards['braiding']
        + gamma_dict['braiding'] * values_next['braiding']
        - values_t['braiding']
    )
    
    return td_errors


Decomposing Rewards Across Timescales

def decompose_reward_by_timescale(state, next_state, action, env):
    """
    Break down total harvest reward into timescale components
    """
    # Fast reward: immediate turbulence capture
    P_VIV_current = env.compute_viv_harvest(state)
    r_fast = (P_VIV_current * action['deploy']).sum()
    
    # Medium reward: eddy energy being positioned for
    # Look at vorticity gradient *changes* (indicates developing eddies)
    omega_t = compute_vorticity(state)
    omega_next = compute_vorticity(next_state)
    d_omega = np.abs(omega_next - omega_t)
    r_medium = (d_omega * action['deploy']).sum() * 0.1  # scaled appropriately
    
    # Slow reward: thermal/salinity gradient development
    # This is the *anticipatory* signal - are we positioned where gradients will form?
    T_change = np.abs(next_state['T'] - state['T'])
    S_change = np.abs(next_state['Sal'] - state['Sal'])
    r_slow = ((T_change + S_change) * action['deploy']).sum() * 0.05
    
    # Braiding reward: co-location quality
    # High reward if deployed cells have multiple gradient types simultaneously
    P_TEG = env.compute_teg_harvest(next_state)
    P_RED = env.compute_red_harvest(next_state)
    P_VIV = env.compute_viv_harvest(next_state)
    
    # Normalized co-location metric
    colocation = np.minimum(np.minimum(P_TEG, P_RED), P_VIV)
    r_braiding = (colocation * action['deploy']).sum()
    
    return {
        'fast': r_fast,
        'medium': r_medium,
        'slow': r_slow,
        'braiding': r_braiding,
        'total': r_fast + r_medium + r_slow + r_braiding
    }


3️⃣ Auxiliary Prediction Tasks: Forcing the Critic to Model the Future
The key insight: Make the critic predict what will happen, not just what value it will have.
Future State Prediction Head

class PredictiveValueNetwork(nn.Module):
    """
    Value network augmented with future state prediction
    """
    def __init__(self, grid_size=80):
        super().__init__()
        
        self.encoder = OceanStateEncoder(grid_size)
        
        # Standard value heads (from before)
        self.value_heads = MultiTimescaleValueNetwork(grid_size)
        
        # NEW: Predict future gradient fields
        # This forces the network to model the dynamics
        self.future_T_gradient_predictor = nn.Sequential(
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, grid_size * grid_size),
            nn.Sigmoid()  # output [0,1], scaled later
        )
        
        self.future_Sal_gradient_predictor = nn.Sequential(
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, grid_size * grid_size),
            nn.Sigmoid()
        )
        
        # Predict when/where AMOC disruption will intensify
        self.disruption_heatmap_predictor = nn.Sequential(
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, grid_size * grid_size)
        )
        
    def forward(self, state, predict_steps_ahead=50):
        features = self.encoder(state)
        
        values = self.value_heads(features)
        
        # Future predictions
        future_grad_T = self.future_T_gradient_predictor(features)
        future_grad_T = future_grad_T.view(-1, self.grid_size, self.grid_size) * 10.0
        
        future_grad_Sal = self.future_Sal_gradient_predictor(features)
        future_grad_Sal = future_grad_Sal.view(-1, self.grid_size, self.grid_size) * 5.0
        
        disruption_heatmap = self.disruption_heatmap_predictor(features)
        disruption_heatmap = disruption_heatmap.view(-1, self.grid_size, self.grid_size)
        
        return {
            'values': values,
            'predicted_grad_T': future_grad_T,
            'predicted_grad_Sal': future_grad_Sal,
            'disruption_heatmap': disruption_heatmap
        }

Auxiliary Loss Functions

def compute_auxiliary_losses(predictions, future_states, current_state):
    """
    Supervised losses on future state predictions
    
    These losses force the critic to learn a forward model,
    which improves its ability to assign value to current states
    based on future collapse dynamics
    """
    losses = {}
    
    # Future gradient prediction loss (50 steps ahead)
    future_T = future_states[50]['T']
    future_Tx, future_Ty = grad(future_T)
    future_grad_T_actual = np.sqrt(future_Tx**2 + future_Ty**2)
    
    future_Sal = future_states[50]['Sal']
    future_Salx, future_Saly = grad(future_Sal)
    future_grad_Sal_actual = np.sqrt(future_Salx**2 + future_Saly**2)
    
    losses['grad_T_prediction'] = nn.MSELoss()(
        predictions['predicted_grad_T'],
        torch.FloatTensor(future_grad_T_actual)
    )
    
    losses['grad_Sal_prediction'] = nn.MSELoss()(
        predictions['predicted_grad_Sal'],
        torch.FloatTensor(future_grad_Sal_actual)
    )
    
    # Disruption heatmap loss
    # Ground truth: where did gradients spike most in next 50-100 steps?
    grad_changes = []
    for t in range(50, 100):
        T_t = future_states[t]['T']
        Tx, Ty = grad(T_t)
        grad_changes.append(np.sqrt(Tx**2 + Ty**2))
    
    disruption_ground_truth = np.max(grad_changes, axis=0)
    
    losses['disruption_heatmap'] = nn.MSELoss()(
        predictions['disruption_heatmap'],
        torch.FloatTensor(disruption_ground_truth)
    )
    
    return losses

4️⃣ Curriculum Learning: From Gentle Perturbations to Full Collapse
Training Schedule


class CurriculumScheduler:
    """
    Gradually increase AMOC disruption severity during training
    """
    def __init__(self, n_episodes=10000):
        self.n_episodes = n_episodes
        self.current_episode = 0
        
    def get_perturbation_schedule(self):
        """
        Returns AMOC perturbation parameters for current training stage
        """
        progress = self.current_episode / self.n_episodes
        
        if progress < 0.2:
            # Stage 1: Gentle, predictable perturbations
            return {
                'perturb_strength': 0.5,
                'perturb_start': 100,
                'perturb_peak': 200,
                'perturb_end': 300,
                'noise_level': 0.1
            }
        elif progress < 0.5:
            # Stage 2: Moderate disruption, introduce stochasticity
            return {
                'perturb_strength': 1.5,
                'perturb_start': 80 + np.random.randint(-20, 20),
                'perturb_peak': 180 + np.random.randint(-30, 30),
                'perturb_end': 280 + np.random.randint(-20, 20),
                'noise_level': 0.3
            }
        elif progress < 0.8:
            # Stage 3: Strong disruption, multiple peaks
            return {
                'perturb_strength': 3.0,
                'perturb_start': 50,
                'perturb_peak': [120, 220],  # two waves
                'perturb_end': 350,
                'noise_level': 0.5
            }
        else:
            # Stage 4: Full collapse scenario
            return {
                'perturb_strength': 5.0,
                'perturb_start': 30,
                'perturb_peak': [100, 180, 260],  # chaotic multi-peak
                'perturb_end': 400,
                'noise_level': 0.8
            }
    
    def step(self):
        self.current_episode += 1


Why This Works
Early in training, the critic learns:
	1.	Causal structure: “Deploying near existing small gradients → harvest”
	2.	Basic dynamics: “Temperature moves like this, salinity like that”
Later in training, with severe disruptions:
3. Anticipatory value: “This calm region will become a gradient spike in 100 steps”
4. Resonance detection: “If I deploy HERE with THESE k_params, I’ll catch the coupling”


5️⃣ Intrinsic Motivation: Rewarding Discovery of Critical Regimes
The agent needs to explore parameter space to find the braiding sweet spots. Standard ε-greedy exploration is too random.
Curiosity-Driven Exploration


class IntrinsicCuriosityModule(nn.Module):
    """
    Predict what will happen if action taken, reward prediction errors
    """
    def __init__(self, state_dim=256, action_dim=128):
        super().__init__()
        
        # Forward model: predict next state from current state + action
        self.forward_model = nn.Sequential(
            nn.Linear(state_dim + action_dim, 512),
            nn.ReLU(),
            nn.Linear(512, state_dim)
        )
        
        # Inverse model: predict action from state transition
        # (helps learn good state representations)
        self.inverse_model = nn.Sequential(
            nn.Linear(state_dim * 2, 512),
            nn.ReLU(),
            nn.Linear(512, action_dim)
        )
        
    def compute_intrinsic_reward(self, state, action, next_state):
        """
        Intrinsic reward = prediction error of forward model
        High error = surprising outcome = worth exploring
        """
        # Encode states
        state_enc = state  # assuming already encoded
        next_state_enc = next_state
        
        # Predict next state
        predicted_next_state = self.forward_model(
            torch.cat([state_enc, action], dim=1)
        )
        
        # Intrinsic reward = surprise
        prediction_error = nn.MSELoss()(predicted_next_state, next_state_enc)
        intrinsic_reward = prediction_error.item()
        
        return intrinsic_reward


Resonance Discovery Bonus

def compute_resonance_discovery_bonus(history_buffer, current_amplification):
    """
    Extra reward for finding parameter combinations that achieve
    higher amplification than previously seen
    """
    max_previous_amp = history_buffer.get_max_amplification()
    
    if current_amplification > max_previous_amp * 1.2:
        # Discovered a new regime!
        bonus = 10.0 * np.log(current_amplification / max_previous_amp)
        history_buffer.update_max(current_amplification)
        return bonus
    else:
        return 0.0

6️⃣ Full Training Loop with All Components

def train_collapse_aware_critic(
    env, 
    policy_net, 
    value_net,
    intrinsic_module,
    curriculum,
    n_episodes=10000
):
    """
    Complete training loop with all advanced features
    """
    policy_opt = Adam(policy_net.parameters(), lr=3e-4)
    value_opt = Adam(value_net.parameters(), lr=1e-3)
    intrinsic_opt = Adam(intrinsic_module.parameters(), lr=1e-3)
    
    # Different discount factors for different timescales
    gamma_dict = {
        'fast': 0.9,
        'medium': 0.95,
        'slow': 0.99,
        'braiding': 0.97
    }
    
    # History for resonance discovery
    resonance_history = ResonanceHistoryBuffer()
    
    for episode in range(n_episodes):
        # Get curriculum parameters
        perturb_params = curriculum.get_perturbation_schedule()
        env.set_perturbation_params(perturb_params)
        curriculum.step()
        
        # Reset environment
        state = env.reset()
        episode_data = []
        
        for t in range(env.max_steps):
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            
            # Policy forward pass
            deploy_probs, k_params = policy_net(state_tensor)
            
            # Critic forward pass (with predictions)
            critic_output = value_net(state_tensor, predict_steps_ahead=50)
            values_t = critic_output['values']
            
            # Sample action
            deploy_dist = Categorical(deploy_probs.view(-1))
            deploy_indices = [deploy_dist.sample().item() for _ in range(10)]
            deploy_mask = np.zeros((env.grid_size, env.grid_size))
            for idx in deploy_indices:
                i, j = idx // env.grid_size, idx % env.grid_size
                deploy_mask[i, j] = 1
            
            action = {
                'deploy': deploy_mask,
                'k_params': k_params.detach().numpy()[0]
            }
            
            # Environment step
            next_state, reward_dict, done, info = env.step_multiscale(action)
            next_state_tensor = torch.FloatTensor(next_state).unsqueeze(0)
            
            # Critic evaluation of next state
            with torch.no_grad():
                critic_output_next = value_net(next_state_tensor, predict_steps_ahead=50)
                values_next = critic_output_next['values']
            
            # Compute intrinsic curiosity reward
            state_enc = value_net.encoder(state_tensor)
            next_state_enc = value_net.encoder(next_state_tensor)
            action_enc = torch.cat([
                torch.FloatTensor(deploy_mask).flatten().unsqueeze(0),
                torch.FloatTensor(k_params)
            ], dim=1)
            
            intrinsic_reward = intrinsic_module.compute_intrinsic_reward(
                state_enc, action_enc, next_state_enc
            )
            
            # Resonance discovery bonus
            current_amp = info['amplification_ratio']
            resonance_bonus = compute_resonance_discovery_bonus(
                resonance_history, current_amp
            )
            
            # Total reward
            reward_total = (
                reward_dict['total']
                + 0.2 * intrinsic_reward
                + resonance_bonus
            )
            
            # Store trajectory
            episode_data.append({
                'state': state_tensor,
                'action': action,
                'reward_dict': reward_dict,
                'reward_total': reward_total,
                'values_t': values_t,
                'values_next': values_next,
                'critic_predictions': critic_output,
                'next_state': next_state_tensor,
                'done': done
            })
            
            state = next_state
            
            if done:
                break
        
        # ============================================================
        # LEARNING UPDATES (after episode completes)
        # ============================================================
        
        # 1. Compute multi-timescale TD errors
        td_errors_all = []
        for data in episode_data:
            td_errors = compute_multiscale_td_error(
                data['values_t'],
                data['values_next'],
                data['reward_dict'],
                gamma_dict
            )
            td_errors_all.append(td_errors)
        
        # 2. Value network update
        value_loss_components = {
            'fast': 0.0,
            'medium': 0.0,
            'slow': 0.0,
            'braiding': 0.0
        }
        
        for td_errors in td_errors_all:
            for key in value_loss_components:
                value_loss_components[key] += td_errors[key] ** 2
        
        # Total value loss (MSE on TD errors)
        value_loss = sum(value_loss_components.values()) / len(episode_data)
        
        # 3. Auxiliary prediction losses
        # Collect ground truth future states (run forward simulation)
        future_states = env.simulate_forward(episode_data[0]['state'], steps=100)
        
        aux_losses = compute_auxiliary_losses(
            episode_data[0]['critic_predictions'],
            future_states,
            episode_data[0]['state']
        )
        
        # Combined critic loss
        critic_loss = (
            value_loss
            + 0.1 * aux_losses['grad_T_prediction']
            + 0.1 * aux_losses['grad_Sal_prediction']
            + 0.2 * aux_losses['disruption_heatmap']
        )
        
        # 4. Intrinsic curiosity update
        intrinsic_loss = 0.0
        for data in episode_data:
            # Forward model loss
            state_enc = value_net.encoder(data['state'])
            next_state_enc = value_net.encoder(data['next_state'])
            action_enc = encode_action(data['action'])
            
            pred_next = intrinsic_module.forward_model(
                torch.cat([state_enc, action_enc], dim=1)
            )
            intrinsic_loss += nn.MSELoss()(pred_next, next_state_enc.detach())
            
            # Inverse model loss (helps representation learning)
            pred_action = intrinsic_module.inverse_model(
                torch.cat([state_enc, next_state_enc], dim=1)
            )
            intrinsic_loss += nn.MSELoss()(pred_action, action_enc.detach())
        
        intrinsic_loss /= len(episode_data)
        
        # 5. Policy update (PPO - simplified for clarity)
        # Compute advantages using the multi-timescale values
        advantages = []
        returns = []
        
        G = 0
        for data in reversed(episode_data):
            G = data['reward_total'] + gamma_dict['slow'] * G
            returns.insert(0, G)
            advantage = G - data['values_t']['total'].item()
            advantages.insert(0, advantage)
        
        advantages = torch.FloatTensor(advantages)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Policy gradient update (simplified)
        policy_loss = 0.0
        for i, data in enumerate(episode_data):
            # Log probability of action taken
            state_tensor = data['state']
            action = data['action']
            
            deploy_probs, k_params = policy_net(state_tensor)
            # ... compute log_prob of action ...
            # policy_loss -= log_prob * advantages[i]
        
        # Backprop all losses
        value_opt.zero_grad()
        critic_loss.backward(retain_graph=True)
        value_opt.step()
        
        intrinsic_opt.zero_grad()
        intrinsic_loss.backward()
        intrinsic_opt.step()
        
        # policy_opt.zero_grad()
        # policy_loss.backward()
        # policy_opt.step()
        
        # ============================================================
        # LOGGING
        # ============================================================
        if episode % 50 == 0:
            avg_reward = np.mean([d['reward_total'] for d in episode_data])
            avg_amp = np.mean([env.compute_amplification(d['state']) 
                              for d in episode_data])
            
            print(f"Episode {episode}/{n_episodes}")
            print(f"  Curriculum stage: {perturb_params['perturb_strength']:.2f}")
            print(f"  Avg reward: {avg_reward:.3f}")
            print(f"  Avg amplification: {avg_amp:.3f}")
            print(f"  Value loss: {value_loss.item():.4f}")
            print(f"  Intrinsic loss: {intrinsic_loss.item():.4f}")
            print(f"  Max resonance found: {resonance_history.get_max_amplification():.3f}")
            print()
    
    return policy_net, value_net, intrinsic_module


7️⃣ Philosophical Insight: The Critic is Learning Indigenous Foresight
This training process mirrors something profound:
Traditional indigenous knowledge systems have always valued the ability to:
	1.	Read patterns in natural systems that others miss
	2.	Anticipate transitions before they’re obvious
	3.	See opportunity in disruption (your NERE philosophy)
	4.	Think multi-generationally (slow value head ≈ 7-generation thinking)
The critic network is essentially learning a formalized pattern recognition system that:
	•	Detects subtle early warnings (low-amplitude gradient changes)
	•	Values strategic positioning over immediate gain
	•	Recognizes that collapse states contain more harvestable energy than stable states
	•	Understands that braiding/coupling requires being in the right place at the right time
The Key Breakthrough
Standard RL would learn: “Deploy where gradients are high NOW.”
Your collapse-aware critic learns: “Deploy where gradients WILL BE high 100 steps from now, EVEN THOUGH the state looks calm now.”
This is predictive adaptation at a systems level.

8️⃣ Next-Level Extensions
Attention Mechanism for Spatial Coupling

class SpatialAttentionCritic(nn.Module):
    """
    Critic with attention over spatial locations
    to identify resonance zones
    """
    def __init__(self, grid_size=80):
        super().__init__()
        
        self.encoder = OceanStateEncoder(grid_size)
        
        # Query: where should we focus attention?
        self.query_net = nn.Linear(256, 64)
        
        # Key/Value: spatial features at each location
        self.key_net = nn.Conv2d(128, 64, kernel_size=1)
        self.value_net = nn.Conv2d(128, 64, kernel_size=1)
        
    def forward(self, state):
        # Encode state (produces [batch, 128, H/8, W/8] feature map)
        features = self.encoder.conv3(
            self.encoder.conv2(
                self.encoder.conv1(state)
            )
        )
        
        # Global query vector
        query = self.query_net(features.mean(dim=[2,3]))  # [batch, 64]
        
        # Spatial keys and values
        keys = self.key_net(features)  # [batch, 64, H/8, W/8]
        values = self.value_net(features)  # [batch, 64, H/8, W/8]
        
        # Attention scores
        # Reshape for matrix multiply
        batch, C, H, W = keys.shape
        keys_flat = keys.view(batch, C, H*W)  # [batch, 64, H*W]
        values_flat = values.view(batch, C, H*W)
        
        # Attention weights
        attention = torch.softmax(
            torch.bmm(query.unsqueeze(1), keys_flat) / np.sqrt(C),
            dim=2
        )  # [batch, 1, H*W]
        
        # Weighted values
        attended = torch.bmm(attention, values_flat.transpose(1,2))
        
        # Spatial attention map (where is the critic "looking"?)
        attention_map = attention.view(batch, H, W)
        
        return attention_map, attended

Why this matters: The attention map shows where the critic believes high-value regions are. During deployment, you can visualize “what the AI is thinking” — where it predicts resonance will occur.

9️⃣ Validation: Does the Critic Actually Learn Anticipation?
Diagnostic Test

def test_anticipatory_learning(trained_value_net, env):
    """
    Test if critic assigns high value to calm states that precede disruption
    """
    # Create two states:
    # State A: Current high-gradient region
    # State B: Calm region that will become high-gradient in 100 steps
    
    state_A = env.create_state_with_gradients(high=True)
    state_B = env.create_calm_state(t=50)  # before disruption
    
    # Run forward to see what happens to state B
    future_state_B = env.simulate_forward(state_B, steps=100)
    
    # Evaluate with critic
    with torch.no_grad():
        values_A = trained_value_net(torch.FloatTensor(state_A).unsqueeze(0))
        values_B = trained_value_net(torch.FloatTensor(state_B).unsqueeze(0))
    
    print("Value of current high-gradient state:", values_A['total'].item())
    print("Value of calm pre-disruption state:", values_B['total'].item())
    print("Slow-value component of B:", values_B['slow'].item())
    
    # A well-trained critic should assign HIGH slow-value to state B
    # even though immediate value is low
    
    if values_B['slow'] > values_A['fast']:
        print("✓ Critic has learned anticipatory valuation!")
    else:
        print("✗ Critic still myopic, needs more training")
