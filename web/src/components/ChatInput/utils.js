const removeQueryParams = (url) => {
    try {
        const urlObject = new URL(url);
        urlObject.search = "";
        return urlObject.toString();
    } catch (error) {
        console.error("Invalid URL:", error);
        return url;
    }
}

/**
 * Uploads a file to a specified URL with progress updates.
 *
 * @param {File} file The file to upload.
 * @param {string} url The URL to upload the file to.
 * @param {string} [method="PUT"] The HTTP method to use for the upload (e.g., "POST", "PUT"). Defaults to "PUT".
 * @param {function(File, XMLHttpRequest): void} [onStart=()=>{}] Callback function called when the upload starts. Receives the file and the XMLHttpRequest object as arguments.
 * @param {function(string, number): void} [onProgress=()=>{}] Callback function called during the upload progress. Receives the filename and the progress percentage (0-100) as arguments.
 * @param {function(string): void} [onFinish=()=>{}] Callback function called when the upload is successfully finished. Receives the filename as an argument.
 * @returns {Promise<void>} A Promise that resolves when the upload is successful and rejects if there's an error.
 */
export const uploadFile = (file, url, method = "PUT", onStart = () => { }, onProgress = () => { }, onFinish = () => { }) => {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const filename = file.name;
        onStart(file, xhr);

        xhr.open(method, url);

        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
                const progress = Math.round((event.loaded / event.total) * 100);
                onProgress(filename, progress);
            }
        };

        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                onProgress(filename, 100);
                onFinish(filename, removeQueryParams(url));
                resolve();
            } else {
                const errorMessage = `Error uploading ${filename}. Status: ${xhr.status}`;
                console.error("Error uploading file", file, errorMessage);
                reject(new Error(errorMessage));
            }
        };

        xhr.onerror = () => {
            const errorMessage = `Network error uploading ${filename}.`;
            console.error("Network error uploading file", file, errorMessage);
            reject(new Error(errorMessage));
        };

        xhr.onabort = () => {
            reject(new Error("Upload aborted"));
        };

        xhr.send(file);
    });
};
