import { loadPyodide } from "pyodide";

let pyodide = null;

self.onmessage = async (event) => {
    const { type, id, code, context } = event.data;

    if (type === "init") {
        try {
            pyodide = await loadPyodide();
            // pyodide.setStdout({ batched: (msg) => stdout += msg });
            self.postMessage({ type: "pyodide_ready" });
        } catch (error) {
            console.error("Error loading Pyodide in worker:", error);
            self.postMessage({ type: "error", error: error.message });
        }
    } else if (type === "run_python" && pyodide) {
        try {
            await pyodide.loadPackagesFromImports(code);
            let globals;
            if (context) {
                const dict = pyodide.globals.get("dict");
                globals = dict(Object.entries(context));
            }
            const result = await pyodide.runPythonAsync(code, { globals });
            self.postMessage({ result, id });
        } catch (error) {
            self.postMessage({ error: error.message, id });
        }
    }
};
