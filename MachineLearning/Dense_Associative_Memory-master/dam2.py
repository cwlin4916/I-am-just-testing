import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from tqdm import tqdm
from time import time

class HopfieldCapacityAnalysis:
    def __init__(self, N: int, epsilon: float = 0):
        """Initialize the capacity analysis experiment"""
        self.N = N
        self.epsilon = epsilon
        print(f"\n{'='*50}")
        print(f"Initializing Hopfield Network Capacity Analysis")
        print(f"Network Configuration:")
        print(f"- Neurons (N): {N}")
        print(f"- Error tolerance (ε): {epsilon}")
        print(f"{'='*50}\n")
        
    def generate_patterns(self, K: int) -> np.ndarray:
        """Generate K random binary patterns of length N"""
        patterns = np.random.choice([-1, 1], size=(K, self.N))
        return patterns
        
    def update_state(self, state: np.ndarray, patterns: np.ndarray, n_power: int = 3) -> np.ndarray:
        """Single update step of the network"""
        field = np.zeros(self.N)
        for pattern in patterns:
            overlap = np.dot(pattern, state)
            field += pattern * (overlap ** (n_power - 1))
        return np.sign(field)
        
    def evolve_until_convergence(self, init_state: np.ndarray, 
                               patterns: np.ndarray,
                               max_steps: int = 100) -> Tuple[np.ndarray, int]:
        """Evolve state until convergence"""
        state = init_state.copy()
        for step in range(max_steps):
            new_state = self.update_state(state, patterns)
            if np.array_equal(new_state, state):
                return new_state, step
            state = new_state
        return state, max_steps
        
    def compute_recovery_score(self, final_state: np.ndarray, 
                             patterns: np.ndarray) -> float:
        """Compute RecK(x) - maximum overlap with stored patterns"""
        overlaps = np.abs([np.dot(pattern, final_state) for pattern in patterns])
        return np.max(overlaps)
        
    def compute_alpha_K(self, K: int, n_samples: int = 1000) -> Dict:
        """
        Compute αK and related statistics for given K
        """
        print(f"\nAnalyzing K = {K}:")
        print(f"- Generating {K} random patterns...")
        patterns = self.generate_patterns(K)
        
        results = {
            'perfect_recoveries': 0,
            'total_steps': 0,
            'max_steps': 0,
            'overlaps': []
        }
        
        print(f"- Testing {n_samples} random initial states...")
        for _ in tqdm(range(n_samples), desc=f"Processing K={K}", ncols=80):
            init_state = np.random.choice([-1, 1], size=self.N)
            final_state, steps = self.evolve_until_convergence(init_state, patterns)
            rec_score = self.compute_recovery_score(final_state, patterns)
            
            results['overlaps'].append(rec_score/self.N)
            results['total_steps'] += steps
            results['max_steps'] = max(results['max_steps'], steps)
            
            if abs(rec_score - self.N) <= self.epsilon:
                results['perfect_recoveries'] += 1
        
        alpha_K = results['perfect_recoveries'] / n_samples
        avg_steps = results['total_steps'] / n_samples
        
        print(f"Results for K = {K}:")
        print(f"- Perfect recovery rate (αK): {alpha_K:.4f}")
        print(f"- Average convergence steps: {avg_steps:.2f}")
        print(f"- Maximum convergence steps: {results['max_steps']}")
        print(f"- Average overlap: {np.mean(results['overlaps']):.4f}")
        print(f"- Overlap std dev: {np.std(results['overlaps']):.4f}")
        
        return {
            'alpha_K': alpha_K,
            'avg_steps': avg_steps,
            'max_steps': results['max_steps'],
            'overlaps': results['overlaps']
        }
        
    def analyze_capacity(self, K_range: List[int], n_samples: int = 1000) -> Dict[int, Dict]:
        """Analyze capacity across different K values"""
        print(f"\n{'='*50}")
        print("Starting Capacity Analysis")
        print(f"- Testing K values from {min(K_range)} to {max(K_range)}")
        print(f"- Using {n_samples} samples per K")
        print(f"{'='*50}\n")
        
        start_time = time()
        results = {}
        
        for K in K_range:
            results[K] = self.compute_alpha_K(K, n_samples)
            
            # Estimate remaining time
            elapsed_time = time() - start_time
            progress = K_range.index(K) + 1
            total = len(K_range)
            remaining_time = (elapsed_time / progress) * (total - progress)
            
            print(f"Progress: {progress}/{total} K values tested")
            print(f"Elapsed time: {elapsed_time/60:.1f} minutes")
            print(f"Estimated remaining time: {remaining_time/60:.1f} minutes\n")
            
        return results
        
    def plot_results(self, results: Dict[int, Dict]):
        """Plot comprehensive analysis results"""
        print("\nGenerating analysis plots...")
        
        # Create a figure with multiple subplots
        plt.figure(figsize=(15, 10))
        
        # Plot 1: K vs αK
        plt.subplot(221)
        K_values = list(results.keys())
        alpha_values = [res['alpha_K'] for res in results.values()]
        plt.plot(K_values, alpha_values, 'bo-')
        plt.axhline(y=0.5, color='r', linestyle='--', label='α = 0.5 (K₁/₂)')
        plt.grid(True)
        plt.xlabel('K (Number of Patterns)')
        plt.ylabel('αK (Perfect Recovery Rate)')
        plt.title('Memory Capacity Analysis')
        plt.legend()
        
        # Plot 2: Convergence Steps
        plt.subplot(222)
        avg_steps = [res['avg_steps'] for res in results.values()]
        max_steps = [res['max_steps'] for res in results.values()]
        plt.plot(K_values, avg_steps, 'g.-', label='Average Steps')
        plt.plot(K_values, max_steps, 'r.-', label='Maximum Steps')
        plt.grid(True)
        plt.xlabel('K (Number of Patterns)')
        plt.ylabel('Convergence Steps')
        plt.title('Convergence Analysis')
        plt.legend()
        
        # Plot 3: Overlap Distribution for selected K values
        plt.subplot(223)
        selected_K = [K_values[0], K_values[len(K_values)//2], K_values[-1]]
        for K in selected_K:
            overlaps = results[K]['overlaps']
            plt.hist(overlaps, bins=50, alpha=0.5, label=f'K={K}', density=True)
        plt.xlabel('Normalized Overlap')
        plt.ylabel('Density')
        plt.title('Overlap Distribution')
        plt.legend()
        
        # Plot 4: K/N ratio vs αK
        plt.subplot(224)
        ratio_values = [K/self.N for K in K_values]
        plt.plot(ratio_values, alpha_values, 'mo-')
        plt.axhline(y=0.5, color='r', linestyle='--', label='α = 0.5')
        plt.grid(True)
        plt.xlabel('K/N Ratio')
        plt.ylabel('αK')
        plt.title('Storage Capacity Ratio Analysis')
        plt.legend()
        
        plt.tight_layout()
        plt.show()
        
        # Find and print K₁/₂
        K_half = None
        for K, res in results.items():
            if res['alpha_K'] < 0.5:
                K_half = K
                break
        
        if K_half:
            print("\nCapacity Analysis Summary:")
            print(f"- K₁/₂ ≈ {K_half}")
            print(f"- Storage capacity ratio: {K_half/self.N:.2f}N")
            
            # Analyze high-load regime
            high_load_K = [K for K in K_values if K > 2*K_half]
            if high_load_K:
                print("\nHigh-load Regime Analysis (K > 2K₁/₂):")
                for K in high_load_K:
                    print(f"K = {K} (K/N = {K/self.N:.2f}):")
                    print(f"- αK = {results[K]['alpha_K']:.4f}")
                    print(f"- Average steps = {results[K]['avg_steps']:.2f}")

def main():
    # Parameters
    N = 100
    epsilon = 0
    K_range = list(range(50, 1501, 50))  # 50 to 1500 in steps of 50
    n_samples = 1000
    
    # Create experiment instance
    experiment = HopfieldCapacityAnalysis(N, epsilon)
    
    # Run analysis
    results = experiment.analyze_capacity(K_range, n_samples)
    
    # Plot and analyze results
    experiment.plot_results(results)

if __name__ == "__main__":
    main()