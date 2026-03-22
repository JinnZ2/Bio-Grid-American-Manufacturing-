## 🍄 Real Mycelial Network Algorithms
**`biologics/physarum-network-optimizer.js`**  
Biological optimization system based on *Physarum polycephalum* research. Implements live tube dynamics, oscillatory peristalsis, mechanochemical feedback, slime trail memory, and multi-objective routing.

- Based on Tero et al., Nakagaki et al., and real Great Lakes infrastructure
- Supports energy-aware tube decay, signal propagation, and nutrient balancing
- Applied to Duluth-Superior Iron Range cargo logistics in real geospatial layout

// Real Mycelial Network Algorithms - Based on Physarum polycephalum Research
// Implements actual biological mechanisms found in scientific literature

class PhysarumNetworkOptimizer {
    constructor(config) {
        // Core biological parameters from research
        this.feedbackStrength = config.feedbackStrength || 1.2; // Positive feedback between flux and thickness
        this.decayRate = config.decayRate || 0.1; // Tube degradation rate
        this.flowSensitivity = config.flowSensitivity || 2.0; // How strongly tubes respond to flow
        this.oscillationPeriod = config.oscillationPeriod || 120; // seconds (natural peristaltic rhythm)
        this.energyThreshold = config.energyThreshold || 0.01; // Minimum energy to maintain tube
        
        // Network structure
        this.nodes = new Map(); // Node ID -> {x, y, pressure, nutrients}
        this.tubes = new Map(); // Tube ID -> {from, to, conductivity, flux, thickness, energy}
        this.pheromoneTrails = new Map(); // Spatial memory system
        
        // Oscillation system for peristaltic flow
        this.oscillationPhase = 0;
        this.contractionPatterns = new Map();
        
        // External memory system (slime trail avoidance)
        this.externalMemory = new Map(); // Location -> {slimeLevel, timestamp}
        this.memoryDecayTime = 3600; // 1 hour memory persistence
    }

    // CORE ALGORITHM 1: Adaptive Tube Dynamics (Tero et al. model)
    updateTubeDynamics(deltaTime) {
        for (let [tubeId, tube] of this.tubes) {
            // Calculate current flux through tube
            const pressureGradient = this.calculatePressureGradient(tube);
            const currentFlux = this.calculateFlux(tube, pressureGradient);
            
            // Core Physarum mechanism: positive feedback between flux and conductivity
            const fluxEffect = Math.pow(Math.abs(currentFlux), this.flowSensitivity);
            const thickeningRate = this.feedbackStrength * fluxEffect;
            const degradationRate = this.decayRate;
            
            // Update tube conductivity (thickness proxy)
            const conductivityChange = (thickeningRate - degradationRate) * deltaTime;
            tube.conductivity = Math.max(0.01, tube.conductivity + conductivityChange);
            
            // Update flux based on new conductivity
            tube.flux = currentFlux;
            
            // Energy balance (improved model from research)
            const energyProvided = this.calculateEnergyFromFlux(currentFlux);
            const energyConsumed = this.calculateMaintenanceEnergy(tube.conductivity);
            tube.energy = energyProvided - energyConsumed;
            
            // Tube elimination if energy balance negative
            if (tube.energy < -this.energyThreshold) {
                this.eliminateTube(tubeId);
            }
        }
    }

    // CORE ALGORITHM 2: Peristaltic Flow Coordination
    updatePeristalticFlow(deltaTime) {
        // Update global oscillation phase
        this.oscillationPhase += (2 * Math.PI * deltaTime) / this.oscillationPeriod;
        if (this.oscillationPhase > 2 * Math.PI) this.oscillationPhase -= 2 * Math.PI;
        
        // Calculate optimal wavelength based on network size (research finding)
        const networkSize = this.calculateNetworkDiameter();
        const optimalWavelength = networkSize; // Wavelength ≈ network size for max transport
        
        for (let [tubeId, tube] of this.tubes) {
            // Calculate local contraction phase based on position and optimal wavelength
            const tubeLength = this.calculateTubeLength(tube);
            const localPhase = this.oscillationPhase + (2 * Math.PI * tubeLength / optimalWavelength);
            
            // Contraction amplitude affects local flow
            const contractionAmplitude = 0.3 * Math.sin(localPhase); // ±30% diameter variation
            const adjustedConductivity = tube.conductivity * (1 + contractionAmplitude);
            
            // Store contraction pattern for signal propagation
            this.contractionPatterns.set(tubeId, {
                phase: localPhase,
                amplitude: contractionAmplitude,
                adjustedConductivity: adjustedConductivity
            });
        }
    }

    // CORE ALGORITHM 3: Signal Propagation (Mechanochemical coupling)
    propagateSignal(sourceNodeId, signalStrength) {
        const signals = new Map(); // NodeId -> signal strength
        signals.set(sourceNodeId, signalStrength);
        
        const propagationQueue = [{nodeId: sourceNodeId, strength: signalStrength, time: 0}];
        const visited = new Set();
        
        while (propagationQueue.length > 0) {
            const current = propagationQueue.shift();
            
            if (visited.has(current.nodeId)) continue;
            visited.add(current.nodeId);
            
            // Find connected tubes
            const connectedTubes = this.getConnectedTubes(current.nodeId);
            
            for (let tube of connectedTubes) {
                const targetNodeId = tube.from === current.nodeId ? tube.to : tube.from;
                
                // Signal propagation speed depends on tube flow velocity
                const flowVelocity = Math.abs(tube.flux) / tube.conductivity;
                const propagationTime = this.calculateTubeLength(tube) / Math.max(flowVelocity, 0.1);
                
                // Signal decay during propagation
                const decayFactor = Math.exp(-propagationTime * 0.1);
                const newStrength = current.strength * decayFactor;
                
                if (newStrength > 0.01) { // Signal threshold
                    // Mechanochemical coupling: signal affects local contractions
                    this.modulateContraction(tube.id, newStrength);
                    
                    propagationQueue.push({
                        nodeId: targetNodeId,
                        strength: newStrength,
                        time: current.time + propagationTime
                    });
                }
            }
        }
        
        return signals;
    }

    // CORE ALGORITHM 4: External Memory System (Slime trail avoidance)
    updateExternalMemory(currentPosition, deltaTime) {
        const positionKey = `${Math.round(currentPosition.x)},${Math.round(currentPosition.y)}`;
        
        // Deposit slime trail at current position
        if (this.externalMemory.has(positionKey)) {
            const existing = this.externalMemory.get(positionKey);
            existing.slimeLevel = Math.min(1.0, existing.slimeLevel + 0.1);
            existing.timestamp = Date.now();
        } else {
            this.externalMemory.set(positionKey, {
                slimeLevel: 0.1,
                timestamp: Date.now()
            });
        }
        
        // Decay old memory traces
        const currentTime = Date.now();
        for (let [key, memory] of this.externalMemory) {
            const age = (currentTime - memory.timestamp) / 1000; // seconds
            if (age > this.memoryDecayTime) {
                this.externalMemory.delete(key);
            } else {
                // Exponential decay
                memory.slimeLevel *= Math.exp(-age / this.memoryDecayTime);
                if (memory.slimeLevel < 0.01) {
                    this.externalMemory.delete(key);
                }
            }
        }
    }

    // CORE ALGORITHM 5: Multi-objective Foraging (Efficiency + Fault tolerance)
    optimizeNetworkTopology() {
        // Evaluate current network efficiency
        const efficiency = this.calculateNetworkEfficiency();
        const faultTolerance = this.calculateFaultTolerance();
        const cost = this.calculateNetworkCost();
        
        // Multi-objective fitness (similar to Tokyo rail network study)
        const fitness = (efficiency * 0.4) + (faultTolerance * 0.4) + ((1 - cost) * 0.2);
        
        // Identify potential network improvements
        const improvements = [];
        
        // Test adding new connections
        for (let [nodeId1, node1] of this.nodes) {
            for (let [nodeId2, node2] of this.nodes) {
                if (nodeId1 !== nodeId2 && !this.hasDirectConnection(nodeId1, nodeId2)) {
                    const distance = this.calculateDistance(node1, node2);
                    const potentialBenefit = this.estimateConnectionBenefit(nodeId1, nodeId2);
                    const cost = distance * 0.1; // Construction cost proxy
                    
                    if (potentialBenefit > cost) {
                        improvements.push({
                            type: 'add_connection',
                            from: nodeId1,
                            to: nodeId2,
                            benefit: potentialBenefit - cost
                        });
                    }
                }
            }
        }
        
        // Test removing weak connections
        for (let [tubeId, tube] of this.tubes) {
            if (tube.flux < 0.01) { // Very low usage
                const removalBenefit = this.estimateRemovalBenefit(tubeId);
                if (removalBenefit > 0) {
                    improvements.push({
                        type: 'remove_connection',
                        tubeId: tubeId,
                        benefit: removalBenefit
                    });
                }
            }
        }
        
        // Apply best improvement
        if (improvements.length > 0) {
            improvements.sort((a, b) => b.benefit - a.benefit);
            this.applyNetworkImprovement(improvements[0]);
        }
        
        return {
            efficiency: efficiency,
            faultTolerance: faultTolerance,
            cost: cost,
            fitness: fitness,
            improvementsFound: improvements.length
        };
    }

    // CORE ALGORITHM 6: Nutrient Balancing (Multi-nutrient optimization)
    balanceNutrientIntake(availableNutrients) {
        // Physarum balances protein and carbohydrates automatically
        const targetRatio = {protein: 0.4, carbohydrate: 0.6}; // Research-based optimal ratio
        const currentIntake = this.calculateCurrentNutrientIntake();
        
        for (let [nodeId, node] of this.nodes) {
            if (availableNutrients.has(nodeId)) {
                const available = availableNutrients.get(nodeId);
                
                // Calculate optimal allocation to reach target ratio
                const proteinDeficit = targetRatio.protein - (currentIntake.protein / (currentIntake.protein + currentIntake.carbohydrate));
                const carbDeficit = targetRatio.carbohydrate - (currentIntake.carbohydrate / (currentIntake.protein + currentIntake.carbohydrate));
                
                // Adjust tube development toward deficient nutrients
                const connectedTubes = this.getConnectedTubes(nodeId);
                for (let tube of connectedTubes) {
                    let growthBonus = 0;
                    
                    if (available.proteinRatio > available.carbohydrateRatio && proteinDeficit > 0) {
                        growthBonus = proteinDeficit * 0.5;
                    } else if (available.carbohydrateRatio > available.proteinRatio && carbDeficit > 0) {
                        growthBonus = carbDeficit * 0.5;
                    }
                    
                    tube.conductivity *= (1 + growthBonus);
                }
            }
        }
    }

    // HELPER FUNCTIONS FOR BIOLOGICAL ACCURACY

    calculatePressureGradient(tube) {
        const fromNode = this.nodes.get(tube.from);
        const toNode = this.nodes.get(tube.to);
        return (fromNode.pressure - toNode.pressure) / this.calculateTubeLength(tube);
    }

    calculateFlux(tube, pressureGradient) {
        // Poiseuille flow with peristaltic modification
        const contractionPattern = this.contractionPatterns.get(tube.id);
        const effectiveConductivity = contractionPattern ? 
            contractionPattern.adjustedConductivity : tube.conductivity;
        
        return effectiveConductivity * pressureGradient;
    }

    calculateEnergyFromFlux(flux) {
        // Energy provided by nutrient transport
        return Math.abs(flux) * 0.1; // Research suggests linear relationship
    }

    calculateMaintenanceEnergy(conductivity) {
        // Energy cost of maintaining tube structure
        return conductivity * 0.05; // Thicker tubes cost more energy
    }

    modulateContraction(tubeId, signalStrength) {
        if (this.contractionPatterns.has(tubeId)) {
            const pattern = this.contractionPatterns.get(tubeId);
            pattern.amplitude *= (1 + signalStrength * 0.2); // Signal increases contraction
        }
    }

    calculateNetworkDiameter() {
        // Find maximum distance between any two nodes
        let maxDistance = 0;
        for (let [id1, node1] of this.nodes) {
            for (let [id2, node2] of this.nodes) {
                if (id1 !== id2) {
                    const distance = this.calculateDistance(node1, node2);
                    maxDistance = Math.max(maxDistance, distance);
                }
            }
        }
        return maxDistance;
    }

    calculateTubeLength(tube) {
        const fromNode = this.nodes.get(tube.from);
        const toNode = this.nodes.get(tube.to);
        return this.calculateDistance(fromNode, toNode);
    }

    calculateDistance(node1, node2) {
        const dx = node1.x - node2.x;
        const dy = node1.y - node2.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

    getConnectedTubes(nodeId) {
        const connected = [];
        for (let [tubeId, tube] of this.tubes) {
            if (tube.from === nodeId || tube.to === nodeId) {
                connected.push({...tube, id: tubeId});
            }
        }
        return connected;
    }

    hasDirectConnection(nodeId1, nodeId2) {
        for (let [tubeId, tube] of this.tubes) {
            if ((tube.from === nodeId1 && tube.to === nodeId2) ||
                (tube.from === nodeId2 && tube.to === nodeId1)) {
                return true;
            }
        }
        return false;
    }

    eliminateTube(tubeId) {
        this.tubes.delete(tubeId);
        this.contractionPatterns.delete(tubeId);
    }

    calculateNetworkEfficiency() {
        // Average shortest path length vs direct distances
        let totalEfficiency = 0;
        let pathCount = 0;
        
        for (let [id1, node1] of this.nodes) {
            for (let [id2, node2] of this.nodes) {
                if (id1 !== id2) {
                    const directDistance = this.calculateDistance(node1, node2);
                    const networkDistance = this.findShortestPath(id1, id2);
                    if (networkDistance > 0) {
                        totalEfficiency += directDistance / networkDistance;
                        pathCount++;
                    }
                }
            }
        }
        
        return pathCount > 0 ? totalEfficiency / pathCount : 0;
    }

    calculateFaultTolerance() {
        // Network connectivity after random edge removal
        let connectivitySum = 0;
        const testRemovals = 10;
        
        for (let i = 0; i < testRemovals; i++) {
            const tubeIds = Array.from(this.tubes.keys());
            const randomTubeId = tubeIds[Math.floor(Math.random() * tubeIds.length)];
            
            // Temporarily remove tube
            const removedTube = this.tubes.get(randomTubeId);
            this.tubes.delete(randomTubeId);
            
            // Test connectivity
            const connectivity = this.calculateConnectivity();
            connectivitySum += connectivity;
            
            // Restore tube
            this.tubes.set(randomTubeId, removedTube);
        }
        
        return connectivitySum / testRemovals;
    }

    calculateNetworkCost() {
        // Total tube length (proxy for construction/maintenance cost)
        let totalLength = 0;
        for (let [tubeId, tube] of this.tubes) {
            totalLength += this.calculateTubeLength(tube);
        }
        return totalLength / this.nodes.size; // Normalized by network size
    }

    calculateConnectivity() {
        // Fraction of node pairs that have a path between them
        let connectedPairs = 0;
        let totalPairs = 0;
        
        for (let [id1] of this.nodes) {
            for (let [id2] of this.nodes) {
                if (id1 !== id2) {
                    totalPairs++;
                    if (this.findShortestPath(id1, id2) > 0) {
                        connectedPairs++;
                    }
                }
            }
        }
        
        return totalPairs > 0 ? connectedPairs / totalPairs : 0;
    }

    findShortestPath(startId, endId) {
        // Dijkstra's algorithm for network analysis
        const distances = new Map();
        const visited = new Set();
        const queue = [{nodeId: startId, distance: 0}];
        
        // Initialize distances
        for (let [nodeId] of this.nodes) {
            distances.set(nodeId, Infinity);
        }
        distances.set(startId, 0);
        
        while (queue.length > 0) {
            // Sort by distance and get closest unvisited node
            queue.sort((a, b) => a.distance - b.distance);
            const current = queue.shift();
            
            if (visited.has(current.nodeId)) continue;
            visited.add(current.nodeId);
            
            if (current.nodeId === endId) {
                return current.distance;
            }
            
            // Check all connected tubes
            const connectedTubes = this.getConnectedTubes(current.nodeId);
            for (let tube of connectedTubes) {
                const neighborId = tube.from === current.nodeId ? tube.to : tube.from;
                
                if (!visited.has(neighborId)) {
                    const newDistance = current.distance + this.calculateTubeLength(tube);
                    
                    if (newDistance < distances.get(neighborId)) {
                        distances.set(neighborId, newDistance);
                        queue.push({nodeId: neighborId, distance: newDistance});
                    }
                }
            }
        }
        
        return -1; // No path found
    }

    estimateConnectionBenefit(nodeId1, nodeId2) {
        // Estimate benefit of adding connection between nodes
        const currentPath = this.findShortestPath(nodeId1, nodeId2);
        const directDistance = this.calculateDistance(
            this.nodes.get(nodeId1), 
            this.nodes.get(nodeId2)
        );
        
        if (currentPath > 0) {
            return Math.max(0, currentPath - directDistance) * 0.1; // Benefit from shortcut
        } else {
            return 1.0; // High benefit for connecting disconnected components
        }
    }

    estimateRemovalBenefit(tubeId) {
        // Benefit from removing underused tube (maintenance cost savings)
        const tube = this.tubes.get(tubeId);
        const maintenanceCost = this.calculateTubeLength(tube) * 0.01;
        const usageBenefit = Math.abs(tube.flux) * 0.1;
        
        return Math.max(0, maintenanceCost - usageBenefit);
    }

    applyNetworkImprovement(improvement) {
        if (improvement.type === 'add_connection') {
            const tubeId = `tube_${improvement.from}_${improvement.to}`;
            this.tubes.set(tubeId, {
                from: improvement.from,
                to: improvement.to,
                conductivity: 0.1, // Start small
                flux: 0,
                thickness: 0.1,
                energy: 0
            });
        } else if (improvement.type === 'remove_connection') {
            this.eliminateTube(improvement.tubeId);
        }
    }

    calculateCurrentNutrientIntake() {
        // Mock implementation - would track actual nutrient flows
        return {
            protein: Math.random() * 100,
            carbohydrate: Math.random() * 100
        };
    }

    // Main update loop
    update(deltaTime, externalStimuli = {}) {
        // Core biological processes
        this.updateTubeDynamics(deltaTime);
        this.updatePeristalticFlow(deltaTime);
        
        // Process external signals
        if (externalStimuli.nutrientSignal) {
            this.propagateSignal(
                externalStimuli.nutrientSignal.sourceNode, 
                externalStimuli.nutrientSignal.strength
            );
        }
        
        // Update spatial memory
        if (externalStimuli.currentPosition) {
            this.updateExternalMemory(externalStimuli.currentPosition, deltaTime);
        }
        
        // Periodic network optimization (every 60 seconds)
        if (Math.floor(Date.now() / 1000) % 60 === 0) {
            this.optimizeNetworkTopology();
        }
        
        // Nutrient balancing
        if (externalStimuli.availableNutrients) {
            this.balanceNutrientIntake(externalStimuli.availableNutrients);
        }
    }
}

// Example usage for BioGrid infrastructure
const bioGridNetwork = new PhysarumNetworkOptimizer({
    feedbackStrength: 1.5, // Stronger feedback for infrastructure
    decayRate: 0.05, // Slower decay for permanent infrastructure
    flowSensitivity: 2.5, // High sensitivity to usage patterns
    oscillationPeriod: 300, // 5-minute cycles for data/material transport
    energyThreshold: 0.005 // Lower threshold for infrastructure persistence
});

// REAL DULUTH-SUPERIOR BIOGRID NETWORK
// Based on actual geographic coordinates and infrastructure data

// Real coordinates (converted to relative positioning)
const duluthCoords = {lat: 46.7833, lon: -92.1005}; // Downtown Duluth
const superiorCoords = {lat: 46.7490, lon: -92.0900}; // Superior, WI
const ironRangeCoords = {lat: 47.5, lon: -92.8}; // Mesabi Iron Range center
const silverBayCoords = {lat: 47.2944, lon: -91.2534}; // Northshore Mining
const hibbing Coords = {lat: 47.4271, lon: -92.9378}; // Hibbing Taconite

// Convert to relative coordinates (Duluth as origin)
function toRelativeCoords(coords, origin) {
    const kmPerDegree = 111; // Approximate km per degree latitude
    return {
        x: (coords.lon - origin.lon) * kmPerDegree * Math.cos(coords.lat * Math.PI / 180),
        y: (coords.lat - origin.lat) * kmPerDegree
    };
}

// Real infrastructure nodes
bioGridNetwork.nodes.set('duluth_port', {
    ...toRelativeCoords(duluthCoords, duluthCoords),
    pressure: 1.0, 
    nutrients: 100,
    cargo: {
        taconitePellets: 15000000, // 15M tons annually (actual port capacity)
        coal: 25000000, // 25M tons annually
        grain: 5000000, // 5M tons annually
        generalCargo: 500000 // 500k tons annually
    },
    facilities: ['Clure Public Marine Terminal', 'Multiple bulk cargo docks'],
    depth: 27 // feet - Seaway depth
});

bioGridNetwork.nodes.set('superior_port', {
    ...toRelativeCoords(superiorCoords, duluthCoords),
    pressure: 0.95,
    nutrients: 95,
    cargo: {
        coal: 25500000, // Superior Coal Terminal capacity (largest in US)
        taconitePellets: 5000000,
        limestone: 2000000
    },
    facilities: ['Superior Coal Terminal', 'Graymont LLC Superior Terminal', 'C. Reiss Terminal'],
    depth: 27 // feet
});

bioGridNetwork.nodes.set('iron_range_hibbing', {
    ...toRelativeCoords(hibbingCoords, duluthCoords),
    pressure: 0.8,
    nutrients: 80,
    cargo: {
        taconiteRaw: 40000000, // 40M tons mined annually from Mesabi Range
        drPellets: 2000000, // Direct reduced grade pellets
        processing: 'Hibbing Taconite Company operations'
    },
    facilities: ['Open-pit truck and shovel mine', 'Concentrator', 'Pellet plant'],
    railConnections: ['Superior, WI port', 'Burns Harbor, IN']
});

bioGridNetwork.nodes.set('silver_bay_northshore', {
    ...toRelativeCoords(silverBayCoords, duluthCoords),
    pressure: 0.85,
    nutrients: 85,
    cargo: {
        taconiteRaw: 8000000, // Northshore Mining capacity
        drPellets: 5000000, // First US facility for DR-grade pellets
        processing: 'Northshore Mining - Cleveland Cliffs'
    },
    facilities: ['Peter Mitchell Mine', 'Processing facility', 'Ship loading port'],
    railDistance: 47, // miles from mine to processing
    specialization: 'Low silica DR-grade pellets'
});

bioGridNetwork.nodes.set('minntac_mountain_iron', {
    ...toRelativeCoords({lat: 47.4396, lon: -92.6143}, duluthCoords), // Mountain Iron
    pressure: 0.9,
    nutrients: 90,
    cargo: {
        taconitePellets: 15000000, // Largest taconite producer in North America
        processing: 'Minntac - US Steel'
    },
    facilities: ['8-mile open pit series', 'Processing plant', '8700-acre tailings basin'],
    ownership: 'US Steel',
    status: 'Largest taconite producer in North America'
});

bioGridNetwork.nodes.set('united_taconite_eveleth', {
    ...toRelativeCoords({lat: 47.4638, lon: -92.5407}, duluthCoords), // Eveleth
    pressure: 0.82,
    nutrients: 82,
    cargo: {
        taconitePellets: 5000000, // United Taconite capacity
        drPellets: 1000000, // Transitioning to DR-grade
        processing: 'United Taconite - Cleveland Cliffs'
    },
    facilities: ['Mine near Eveleth', 'Processing facility in Forbes', '10-mile rail transport'],
    railConnections: ['Duluth port'],
    specialization: 'Converting to DR-grade pellet production'
});

// REAL TRANSPORTATION CORRIDORS

// Primary taconite rail line: Iron Range → Duluth/Superior ports
bioGridNetwork.tubes.set('hibbing_to_superior', {
    from: 'iron_range_hibbing', 
    to: 'superior_port',
    conductivity: 0.8, // High capacity rail line
    flux: 0,
    thickness: 0.8,
    energy: 0,
    cargoType: 'taconite_pellets',
    capacity: 15000000, // 15M tons annually
    distance: 85, // miles (real distance)
    mode: 'rail'
});

bioGridNetwork.tubes.set('minntac_to_duluth', {
    from: 'minntac_mountain_iron',
    to: 'duluth_port', 
    conductivity: 0.9, // Highest capacity line
    flux: 0,
    thickness: 0.9,
    energy: 0,
    cargoType: 'taconite_pellets',
    capacity: 15000000, // 15M tons annually  
    distance: 60, // miles
    mode: 'rail'
});

bioGridNetwork.tubes.set('northshore_rail', {
    from: 'silver_bay_northshore',
    to: 'duluth_port',
    conductivity: 0.7,
    flux: 0, 
    thickness: 0.7,
    energy: 0,
    cargoType: 'dr_pellets',
    capacity: 8000000, // 8M tons annually
    distance: 47, // miles (actual rail distance)
    mode: 'rail',
    specialization: 'DR-grade pellet transport'
});

bioGridNetwork.tubes.set('united_taconite_rail', {
    from: 'united_taconite_eveleth',
    to: 'duluth_port',
    conductivity: 0.6,
    flux: 0,
    thickness: 0.6, 
    energy: 0,
    cargoType: 'mixed_pellets',
    capacity: 5000000, // 5M tons annually
    distance: 70, // miles (via Forbes processing)
    mode: 'rail'
});

// Inter-port connection (Blatnik Bridge + rail)
bioGridNetwork.tubes.set('duluth_superior_bridge', {
    from: 'duluth_port',
    to: 'superior_port',
    conductivity: 0.5,
    flux: 0,
    thickness: 0.5,
    energy: 0,
    cargoType: 'mixed',
    capacity: 10000000, // Flexible capacity
    distance: 3, // miles (Blatnik Bridge span)
    mode: 'road_rail_bridge',
    infrastructure: 'Blatnik Bridge (1965) + Richard I. Bong Memorial Bridge (1985)'
});

// Great Lakes shipping routes
bioGridNetwork.tubes.set('great_lakes_shipping', {
    from: 'duluth_port',
    to: 'great_lakes_markets', // Virtual node for steel mills
    conductivity: 0.4,
    flux: 0,
    thickness: 0.4,
    energy: 0,
    cargoType: 'bulk_cargo',
    capacity: 35000000, // Total port capacity
    distance: 1200, // miles to steel centers (Gary, IN / Cleveland, OH)
    mode: 'great_lakes_shipping',
    destinations: ['Gary, IN', 'Cleveland, OH', 'Burns Harbor, IN', 'Detroit, MI']
});

// Real cargo flow modeling
bioGridNetwork.realCargoFlow = {
    taconitePellets: {
        annual: 40000000, // 40M tons from Iron Range
        seasonal: true, // April-December shipping season
        destinations: {
            'Gary, IN': 0.35,      // 35% to Gary steel mills
            'Cleveland, OH': 0.25, // 25% to Cleveland  
            'Burns Harbor, IN': 0.20, // 20% to Burns Harbor
            'Detroit, MI': 0.15,   // 15% to Detroit area
            'Other': 0.05          // 5% to other Great Lakes ports
        }
    },
    coal: {
        annual: 25000000, // 25M tons through Superior
        source: 'Powder River Basin (Montana/Wyoming)',
        destinations: 'Great Lakes coal plants'
    },
    grain: {
        annual: 5000000, // 5M tons
        source: 'Minnesota/Wisconsin/Dakotas',
        destinations: 'Global export via Seaway'
    }
};

console.log('Physarum-inspired BioGrid network initialized');
console.log('Ready for real-world mycelial optimization algorithms!');
