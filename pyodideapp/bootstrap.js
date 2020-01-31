languagePluginLoader.then(() => {
    return pyodide.loadPackage(pyodide_packages)
}).then(() => {
    return fetch('./httpimport.py'); // fetch HTTP import hook impl
}).then((response) => {
    return response.text();
}).then((source) => {
    pyodide.runPython(source);
    pyodide.runPython('import main');
});