import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from tqdm import tqdm
from time import time
from torchvision import datasets, transforms
import torch
import os
class HopfieldMNISTAnalysis:
    def _init_(self, N: int = 784, recovery_threshold: float = 0.8):
        self.N = N
        self.recovery_threshold = recovery_threshold
        self.mnist_data = None
        self.mnist_targets = None
        print(f"\n{'='*50}")
        print(f"Initializing MNIST-based Hopfield Network Analysis")
        print(f"Network Configuration:")
        print(f"- Neurons (N): {N}")
        print(f"- Recovery Threshold: {recovery_threshold*100}%")
        print(f"{'='*50}\n")
        self._load_mnist()
    def _load_mnist(self):
        if not os.path.exists('./data'):
            os.makedirs('./data')
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Lambda(lambda x: x.view(-1))
        ])
        mnist_train = datasets.MNIST('./data', train=True, download=True,
                                   transform=transform)
        self.mnist_data = []
        self.mnist_targets = []
        print("Processing MNIST data...")
        for i, (data, target) in enumerate(tqdm(mnist_train)):
            binary_data = torch.where(data > 0.5, 1.0, -1.0).numpy()
            self.mnist_data.append(binary_data)
            self.mnist_targets.append(target)
            # if i >= 9999:  # Only use first 10000 images
            #     break
        self.mnist_data = np.array(self.mnist_data)
        self.mnist_targets = np.array(self.mnist_targets)
        print(f"Loaded {len(self.mnist_data)} MNIST images")
    def select_patterns(self, K: int) -> Tuple[np.ndarray, np.ndarray]:
        indices = np.random.choice(len(self.mnist_data), K, replace=False)
        return self.mnist_data[indices], self.mnist_targets[indices]
    def update_state(self, state: np.ndarray, patterns: np.ndarray, n_power: int = 3) -> np.ndarray:
        field = np.zeros(self.N)
        for pattern in patterns:
            overlap = np.dot(pattern, state)
            field += pattern * (overlap ** (n_power - 1))
        return np.sign(field)
    def evolve_until_convergence(self, init_state: np.ndarray,
                               patterns: np.ndarray,
                               max_steps: int = 100) -> Tuple[np.ndarray, int]:
        state = init_state.copy()
        for step in range(max_steps):
            new_state = self.update_state(state, patterns)
            if np.array_equal(new_state, state):
                return new_state, step
            state = new_state
        return state, max_steps
    def visualize_patterns(self, patterns: np.ndarray, n_samples: int = 5):
        plt.figure(figsize=(15, 3))
        for i in range(min(n_samples, len(patterns))):
            plt.subplot(1, n_samples, i + 1)
            plt.imshow(patterns[i].reshape(28, 28), cmap='gray')
            plt.axis('off')
        plt.tight_layout()
        plt.show()
    def test_recovery(self, patterns: np.ndarray, n_samples: int) -> Dict:
        results = {
            'successful_recoveries': 0,
            'total_steps': 0,
            'max_steps': 0,
            'overlaps': [],
            'recovery_rates': []
        }
        for _ in tqdm(range(n_samples), desc="Testing patterns"):
            idx = np.random.choice(len(patterns))
            init_state = patterns[idx].copy()
            original_pattern = patterns[idx].copy()
            # Add 30% noise
            noise_mask = np.random.rand(self.N) < 0.3
            init_state[noise_mask] *= -1
            final_state, steps = self.evolve_until_convergence(init_state, patterns)
            recovery_rate = np.sum(final_state == original_pattern) / self.N
            results['recovery_rates'].append(recovery_rate)
            overlaps = np.abs([np.dot(pattern, final_state)/self.N for pattern in patterns])
            results['overlaps'].append(max(overlaps))
            results['total_steps'] += steps
            results['max_steps'] = max(results['max_steps'], steps)
            if recovery_rate >= self.recovery_threshold:
                results['successful_recoveries'] += 1
        return results
    def analyze_capacity(self, K_range: List[int], n_samples: int = 100) -> Dict[int, Dict]:
        print("\nStarting Capacity Analysis")
        results = {}
        start_time = time()
        for K in K_range:
            print(f"\nTesting K = {K}:")
            patterns, _ = self.select_patterns(K)
            test_results = self.test_recovery(patterns, n_samples)
            success_rate = test_results['successful_recoveries'] / n_samples
            avg_steps = test_results['total_steps'] / n_samples
            avg_recovery = np.mean(test_results['recovery_rates'])
            results[K] = {
                'success_rate': success_rate,
                'avg_steps': avg_steps,
                'max_steps': test_results['max_steps'],
                'overlaps': test_results['overlaps'],
                'recovery_rates': test_results['recovery_rates'],
                'avg_recovery_rate': avg_recovery
            }
            print(f"Results:")
            print(f"- Success rate ({self.recovery_threshold*100}% threshold): {success_rate:.4f}")
            print(f"- Average recovery rate: {avg_recovery:.4f}")
            print(f"- Average steps: {avg_steps:.2f}")
        return results
    def plot_results(self, results: Dict[int, Dict]):
        K_values = list(results.keys())
        success_rates = [res['success_rate'] for res in results.values()]
        recovery_rates = [res['avg_recovery_rate'] for res in results.values()]
        plt.figure(figsize=(15, 10))
        # K vs Success Rate and Recovery Rate
        plt.subplot(221)
        plt.plot(K_values, success_rates, 'bo-', label=f'Success Rate ({self.recovery_threshold*100}% threshold)')
        plt.plot(K_values, recovery_rates, 'go-', label='Avg Recovery Rate')
        plt.axhline(y=self.recovery_threshold, color='r', linestyle='--',
                   label=f'{self.recovery_threshold*100}% threshold')
        plt.grid(True)
        plt.xlabel('K (Number of Patterns)')
        plt.ylabel('Rate')
        plt.title('Memory Capacity Analysis')
        plt.legend()
        # Convergence Steps
        plt.subplot(222)
        avg_steps = [res['avg_steps'] for res in results.values()]
        plt.plot(K_values, avg_steps, 'g.-')
        plt.grid(True)
        plt.xlabel('K (Number of Patterns)')
        plt.ylabel('Average Steps')
        plt.title('Convergence Analysis')
        # Recovery Rate Distribution
        plt.subplot(223)
        plt.hist(results[K_values[-1]]['recovery_rates'], bins=30, density=True)
        plt.axvline(x=self.recovery_threshold, color='r', linestyle='--',
                   label=f'{self.recovery_threshold*100}% threshold')
        plt.grid(True)
        plt.xlabel('Recovery Rate')
        plt.ylabel('Density')
        plt.title(f'Recovery Rate Distribution (K={K_values[-1]})')
        plt.legend()
        # K/N Ratio Analysis
        plt.subplot(224)
        ratio_values = [K/self.N for K in K_values]
        plt.plot(ratio_values, success_rates, 'mo-')
        plt.axhline(y=self.recovery_threshold, color='r', linestyle='--')
        plt.grid(True)
        plt.xlabel('K/N Ratio')
        plt.ylabel('Success Rate')
        plt.title('Storage Capacity Ratio Analysis')
        plt.tight_layout()
        plt.show()
        # Print summary
        K_threshold = None
        for K, res in results.items():
            if res['success_rate'] < 0.5:
                K_threshold = K
                break
        if K_threshold:
            print("\nCapacity Analysis Summary:")
            print(f"- K threshold: {K_threshold}")
            print(f"- Storage capacity ratio: {K_threshold/self.N:.2f}N")
def main():
    # Set random seed for reproducibility
    np.random.seed(42)
    torch.manual_seed(42)
    # Parameters
    N = 784
    recovery_threshold = 0.89
    K_range = list(range(50, 59001, 1000))
    n_samples = 1000
    print("Starting MNIST Hopfield Network Experiment")
    print(f"Parameters:")
    print(f"- Network size (N): {N}")
    print(f"- Recovery threshold: {recovery_threshold*100}%")
    print(f"- K range: {K_range}")
    print(f"- Samples per K: {n_samples}\n")
    experiment = HopfieldMNISTAnalysis(N, recovery_threshold)
    results = experiment.analyze_capacity(K_range, n_samples)
    experiment.plot_results(results)
if _name_ == "_main_":
    main()



