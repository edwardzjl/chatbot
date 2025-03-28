
export class WorkerManager {
    constructor(idleTimeout = 60000, maxWorkers = 5) {
        this.WORKER_IDLE_TIMEOUT = idleTimeout;
        this.MAX_WORKERS = maxWorkers;
        this.workers = new Map();
        this.workerUrl = new URL("./webworker.mjs", import.meta.url).href + "?worker&url";
        console.log(this.workerUrl)
        this.lastUsedTime = new Map();
        this.initialize();
    }

    async createWorker() {
        console.log("creating worker")
        const worker = new Worker(this.workerUrl, { type: "module" });
        console.log("worker created")
        return new Promise((resolve) => {
            worker.onmessage = (event) => {
                console.log(event)
                if (event.data?.type === "pyodide_ready") {
                    resolve(worker);
                }
            };
            worker.postMessage({ type: "init" });
        });
    }

    async getWorker(workerId) {
        console.log("getting worker")
        let worker = this.workers.get(workerId);
        if (worker) {
            console.log(`Worker found: ${workerId}`);
        }
        if (!worker && this.workers.size < this.MAX_WORKERS) {
            worker = await this.createWorker();
            console.log("worker really created", worker)
            if (worker) {
                this.workers.set(workerId, worker);
                console.log(`Worker created: ${workerId}`);
            } else {
                console.warn(`Failed to create worker: ${workerId}`);
            }
        } else if (!worker) {
            console.warn(`Maximum worker limit reached, cannot create worker: ${workerId}`);
            return null;
        }
        return worker;
    }

    async runPython(workerId, pythonCode) {
        const worker = this.workers.get(workerId);
        if (worker) {
            return new Promise((resolve) => {
                const idWorker = self.crypto.randomUUID();
                const messageListener = (event) => {
                    if (event.data?.id === idWorker) {
                        worker.removeEventListener("message", messageListener);
                        this.markAsUsed(workerId);
                        resolve(event.data);
                    }
                };
                worker.addEventListener("message", messageListener);
                worker.postMessage({ id: idWorker, type: "run_python", code: pythonCode });
            });
        } else {
            return { error: `Worker ${workerId} does not exist.` };
        }
    }

    recycleWorker(workerId) {
        const worker = this.workers.get(workerId);
        if (worker) {
            worker.terminate();
            this.workers.delete(workerId);
            console.log(`Worker recycled: ${workerId}`);
        }
    }

    markAsUsed(workerId) {
        const worker = this.workers.get(workerId);
        if (worker) {
            this.lastUsedTime.set(workerId, Date.now());
        }
    }

    sendHeartbeat(workerId) {
        this.markAsUsed(workerId); // Treat heartbeat as activity
        // console.debug(`Heartbeat received for conversation: ${conversationId}`); // Optional logging
    }

    startIdleWorkerRecycling() {
        setInterval(() => {
            const now = Date.now();
            for (const [workerId] of this.workers.entries()) {
                const lastUsed = this.lastUsedTime.get(workerId);
                if (lastUsed && now - lastUsed > this.WORKER_IDLE_TIMEOUT) {
                    this.recycleWorker(workerId);
                    this.lastUsedTime.delete(workerId);
                }
            }
        }, 5000);
    }

    initialize() {
        this.startIdleWorkerRecycling();
    }
}

// TODO: for demo usage
export const workerManager = new WorkerManager(60000, 5);
