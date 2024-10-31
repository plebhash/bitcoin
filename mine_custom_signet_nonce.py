import time
from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
from threading import Thread, Event

def mine_nonce_range(timestamp, bits, version, reward, start_nonce, end_nonce, hashes_done, stop_event):
    target = int(bits, 16)

    for nonce in range(start_nonce, end_nonce):
        if stop_event.is_set():
            return None  # Exit if a solution is found in another thread

        # Prepare the header and hash it twice (Bitcoin's standard)
        header = (str(version) + str(timestamp) + str(bits) + str(nonce) + str(reward)).encode('utf-8')
        hash_result = sha256(sha256(header).digest()).hexdigest()

        # Increment the shared hash count
        hashes_done[0] += 1  

        # Check if the hash meets the target difficulty
        if int(hash_result, 16) < target:
            stop_event.set()  # Signal other threads to stop
            return nonce, timestamp, hash_result  # Return result if found

    return None  # No valid nonce found in this range

def report_hashrate(hashes_done, stop_event, report_interval=5):
    start_time = time.time()
    while not stop_event.is_set():
        time.sleep(report_interval)  # Wait for the next report interval
        elapsed_time = time.time() - start_time
        hashrate = hashes_done[0] / elapsed_time if elapsed_time > 0 else 0
        print(f"Global Hashrate: {hashrate:.2f} H/s")

def mine_genesis_block_multithreaded(initial_timestamp, bits, version, reward):
    max_nonce = 2**32  # Range for nonce
    timestamp = int(initial_timestamp)  # Start from initial timestamp
    cores = cpu_count() // 2  # Use half of available cores
    nonce_step = max_nonce // cores  # Split the nonce space across threads
    hashes_done = [0]  # Shared counter for the total hashes done
    stop_event = Event()  # Event to signal threads to stop when a solution is found

    print(f"Starting multithreaded mining with {cores} threads...")

    while True:
        # Start the hash rate reporting thread
        reporter_thread = Thread(target=report_hashrate, args=(hashes_done, stop_event))
        reporter_thread.start()

        # Start mining across threads
        with ThreadPoolExecutor(max_workers=cores) as executor:
            futures = [
                executor.submit(mine_nonce_range, timestamp, bits, version, reward, i * nonce_step, (i + 1) * nonce_step, hashes_done, stop_event)
                for i in range(cores)
            ]

            # Check each thread's result
            for future in as_completed(futures):
                result = future.result()
                if result:
                    nonce, final_timestamp, genesis_hash = result
                    print(f"Successfully mined genesis block!")
                    print(f"Timestamp: {final_timestamp}")
                    print(f"Nonce: {nonce}")
                    print(f"Hash: {genesis_hash}")
                    stop_event.set()  # Stop all threads and reporting
                    reporter_thread.join()  # Ensure reporter thread stops
                    return nonce, final_timestamp, genesis_hash

        # If no valid nonce is found, increment timestamp and reset hash counter
        print(f"No valid nonce found at timestamp {timestamp}. Rolling timestamp...")
        timestamp += 1
        hashes_done[0] = 0  # Reset hash count for the next timestamp
        stop_event.clear()  # Reset the stop event for the next round
        reporter_thread.join()  # Ensure the reporter thread stops before restarting

# Set parameters for mining
initial_timestamp = "1598918400"  # Starting timestamp for genesis block
bits = "0x1a225009"               # Difficulty target for the initial desired hashrate + average blocktime
version = 1
reward = 50 * 100000000           # Reward in Satoshis

# Run the multithreaded mining function
nonce, final_timestamp, genesis_hash = mine_genesis_block_multithreaded(initial_timestamp, bits, version, reward)
if genesis_hash:
    print(f"Genesis hash: {genesis_hash}")
    print(f"Nonce: {nonce}")
    print(f"Final Timestamp: {final_timestamp}")
