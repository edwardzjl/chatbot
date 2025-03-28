// Modified based on <https://pyodide.org/en/stable/usage/webworker.html>
import { loadPyodide } from "pyodide";

const pyodideReadyPromise = loadPyodide();

self.onmessage = async (event) => {
    // make sure loading is done
    const pyodide = await pyodideReadyPromise;
    const { id, code, context } = event.data;
    // Now load any packages we need, run the code, and send the result back.
    await pyodide.loadPackagesFromImports(code);
    // make a Python dictionary with the data from `context`
    let globals;
    if (context) {
        const dict = pyodide.globals.get("dict");
        globals = dict(Object.entries(context));
    }
    try {
        // Execute the python code in this context
        const result = await pyodide.runPythonAsync(code, { globals });
        self.postMessage({ result, id });
    } catch (error) {
        self.postMessage({ error: error.message, id });
    }
};
