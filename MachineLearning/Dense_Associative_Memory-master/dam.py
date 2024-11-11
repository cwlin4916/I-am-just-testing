import scipy.io
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

def prepare_data(samples_per_class=5000, test_samples_per_class=900):
    """
    Prepare fixed-size training and test sets from MNIST
    """
    mat = scipy.io.loadmat('mnist_all.mat')
    N = 784    # Input dimension
    Nc = 10    # Number of classes

    # Process training data
    M = np.zeros((0,N))
    Lab = np.zeros((Nc,0))
    for i in range(Nc):
        class_data = mat['train'+str(i)][:samples_per_class]
        M = np.concatenate((M, class_data), axis=0)
        lab1 = -np.ones((Nc, samples_per_class))
        lab1[i,:] = 1.0
        Lab = np.concatenate((Lab, lab1), axis=1)
    M = 2*M/255.0-1
    M = M.T

    # Process test data
    MT = np.zeros((0,N))
    LabT = np.zeros((Nc,0))
    for i in range(Nc):
        class_data = mat['test'+str(i)][:test_samples_per_class]
        MT = np.concatenate((MT, class_data), axis=0)
        lab1 = -np.ones((Nc, test_samples_per_class))
        lab1[i,:] = 1.0
        LabT = np.concatenate((LabT, lab1), axis=1)
    MT = 2*MT/255.0-1
    MT = MT.T

    print(f"Total training samples: {M.shape[1]} (should be {Nc*samples_per_class})")
    print(f"Total test samples: {MT.shape[1]} (should be {Nc*test_samples_per_class})")
    print(f"Feature dimension: {M.shape[0]} (should be {N})")
    print(f"Number of classes: {Lab.shape[0]} (should be {Nc})")
    
    return M, Lab, MT, LabT

def train_DAM(K, M_train, Lab_train, params):
    """
    Train Dense Associative Memory model
    """
    N = M_train.shape[0]
    Nc = Lab_train.shape[0]
    Num = params['Num']
    
    # Initialize weights
    np.random.seed(42)  # For reproducibility
    KS = np.random.normal(params['mu'], params['sigma'], (K, N+Nc))
    VKS = np.zeros((K, N+Nc))
    
    # Prepare auxiliary matrix for labels
    aux = -np.ones((Nc, Num*Nc))
    for d in range(Nc):
        aux[d,d*Num:(d+1)*Num] = 1.
    
    # Training loop
    for nep in tqdm(range(params['Nep']), desc=f"Training K={K}"):
        eps = params['eps0'] * params['f']**nep
        
        # Temperature scheduling
        if nep <= params['thresh_pret']:
            Temp = params['Temp_in'] + (params['Temp_f']-params['Temp_in'])*nep/params['thresh_pret']
        else:
            Temp = params['Temp_f']
        beta = 1./Temp**params['n']
        
        # Shuffle training data
        perm = np.random.permutation(M_train.shape[1])
        M_train = M_train[:,perm]
        Lab_train = Lab_train[:,perm]
        
        # Mini-batch training
        for k in range(M_train.shape[1]//Num):
            # Prepare batch data
            v = M_train[:,k*Num:(k+1)*Num]
            t_R = Lab_train[:,k*Num:(k+1)*Num]
            t = np.reshape(t_R,(1,Nc*Num))
            
            # Forward pass
            u = np.concatenate((v, -np.ones((Nc,Num))), axis=0)
            uu = np.tile(u,(1,Nc))
            vv = np.concatenate((uu[:N,:],aux),axis=0)
            
            KSvv = np.maximum(np.dot(KS,vv),0)
            KSuu = np.maximum(np.dot(KS,uu),0)
            Y = np.tanh(beta*np.sum(KSvv**params['n']-KSuu**params['n'], axis=0))
            Y_R = np.reshape(Y,(Nc,Num))
            
            # Compute gradients and update weights
            d_KS = np.dot(np.tile((t-Y)**(2*params['m']-1)*(1-Y)*(1+Y), (K,1))*KSvv**(params['n']-1),vv.T) - \
                   np.dot(np.tile((t-Y)**(2*params['m']-1)*(1-Y)*(1+Y), (K,1))*KSuu**(params['n']-1),uu.T)
            
            VKS = params['p']*VKS + d_KS
            nc = np.amax(np.absolute(VKS),axis=1).reshape(K,1)
            nc[nc<params['prec']] = params['prec']
            ncc = np.tile(nc,(1,N+Nc))
            KS += eps*VKS/ncc
            KS = np.clip(KS, a_min=-1., a_max=1.)
    
    return KS

def evaluate_recovery(KS, data, labels, params):
    """
    Evaluate model's recovery performance by computing average bit differences
    """
    N = data.shape[0]
    Nc = labels.shape[0]
    Num = params['Num']
    beta = 1./params['Temp_f']**params['n']
    all_diffs = []
    
    aux = -np.ones((Nc, Num*Nc))
    for d in range(Nc):
        aux[d,d*Num:(d+1)*Num] = 1.
    
    for k in range(data.shape[1]//Num):
        v = data[:,k*Num:(k+1)*Num]
        
        # Forward pass
        u = np.concatenate((v, -np.ones((Nc,Num))), axis=0)
        uu = np.tile(u,(1,Nc))
        vv = np.concatenate((uu[:N,:],aux),axis=0)
        
        KSvv = np.maximum(np.dot(KS,vv),0)
        KSuu = np.maximum(np.dot(KS,uu),0)
        Y = np.tanh(beta*np.sum(KSvv**params['n']-KSuu**params['n'], axis=0))
        Y_R = np.reshape(Y,(Nc,Num))
        
        # For each pattern in the batch
        for i in range(Num):
            v_original = v[:,i]
            
            # Get recovered pattern
            u_i = np.concatenate((v_original.reshape(-1,1), -np.ones((Nc,1))), axis=0)
            uu_i = np.tile(u_i, (1,Nc))
            vv_i = np.concatenate((uu_i[:N,:], aux[:,:Nc]), axis=0)
            
            KSvv_i = np.maximum(np.dot(KS,vv_i),0)
            KSuu_i = np.maximum(np.dot(KS,u_i),0)
            
            recovered = np.dot(KS[:,:N].T, KSvv_i).mean(axis=1)
            recovered = np.sign(recovered)

            # Count different bits
            diff = np.sum(v_original != recovered)
            all_diffs.append(diff)
    
    return np.mean(all_diffs), np.std(all_diffs)


def main():
    # Model parameters
    params = {
        'n': 3,               # Power of DAM energy function (>2 for DAM)
        'm': 3,               # Power of loss function
        'eps0': 4.0e-2,      # Initial learning rate
        'f': 0.998,          # Learning rate decay
        'p': 0.6,            # Momentum
        'Nep': 50,          # Number of epochs, 300 
        'Temp_in': 540.,     # Initial temperature
        'Temp_f': 540.,      # Final temperature
        'thresh_pret': 200,  # Temperature ramp length
        'Num': 100,          # Batch size
        'mu': -0.3,          # Weight initialization mean
        'sigma': 0.3,        # Weight initialization std
        'prec': 1.0e-30     # Weight update precision
    }
    
    # Prepare data
    M, Lab, MT, LabT = prepare_data(samples_per_class=1000, test_samples_per_class=100)
    N = M.shape[0]
    print(f"Pattern dimension (N): {N}")
    
    # Test different K values
    # K_values = np.arange(50, 1550, 50)
    K_values=[50] # Test only one value for now (for faster execution) 
    results = []
    
    for K in K_values:
        # Train model
        KS = train_DAM(K, M, Lab, params)
        
        # Evaluate model
        train_mean_diff, train_std_diff = evaluate_recovery(KS, M, Lab, params)
        test_mean_diff, test_std_diff = evaluate_recovery(KS, MT, LabT, params)
        
        results.append({
            'K': K,
            'train_mean_diff': train_mean_diff,
            'train_std_diff': train_std_diff,
            'test_mean_diff': test_mean_diff,
            'test_std_diff': test_std_diff
        })
        
        print(f"K={K}:")
        print(f"  Train: mean diff = {train_mean_diff:.1f} ± {train_std_diff:.1f} bits")
        print(f"  Test:  mean diff = {test_mean_diff:.1f} ± {test_std_diff:.1f} bits")
    
    # Plot results
    plt.figure(figsize=(12, 5))
    
    # Plot 1: K vs Training Differences
    plt.subplot(121)
    plt.errorbar([r['K'] for r in results], 
                [r['train_mean_diff'] for r in results],
                yerr=[r['train_std_diff'] for r in results],
                fmt='bo-', label='Train')
    plt.xlabel('K (Memory size)')
    plt.ylabel('Average Bit Differences')
    plt.title(f'Training Set Bit Differences (n={params["n"]})')
    plt.grid(True)
    
    # Plot 2: K vs Test Differences
    plt.subplot(122)
    plt.errorbar([r['K'] for r in results], 
                [r['test_mean_diff'] for r in results],
                yerr=[r['test_std_diff'] for r in results],
                fmt='ro-', label='Test')
    plt.xlabel('K (Memory size)')
    plt.ylabel('Average Bit Differences')
    plt.title('Test Set Bit Differences')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # Save results
    results_array = np.array([(r['K'], r['train_mean_diff'], r['train_std_diff'],
                              r['test_mean_diff'], r['test_std_diff']) for r in results])
    np.savetxt(f'dam_diff_results_n{params["n"]}.csv', results_array, 
               header='K,train_mean,train_std,test_mean,test_std',
               delimiter=',', 
               fmt='%d,%.1f,%.1f,%.1f,%.1f')

if __name__ == "__main__":
    main()