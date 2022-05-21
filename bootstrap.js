if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js').then(registration => {
//        console.log('sw updating');
//        registration.update();
//        console.log('sw updated');
    })
};

python_files = {};
let all_py_files_loaded = [];
pyodideapp_www_files.forEach(path => {
    if (/.py$/.test(path)) {
        all_py_files_loaded.push(fetch(path).then(response => response.text()).then(source => python_files[path] = source));
    }
});

window.onload = function() {
    languagePluginLoader.then(() => {
        return pyodide.loadPackage(pyodide_packages)
    }).then(() => Promise.all(all_py_files_loaded)).then(() => {
        return fetch('./fetchimport.py'); // pre-fetch import hook impl
    }).then((response) => {
        return response.text();
    }).then((source) => {
        pyodide.runPython(source);
        // return fetch('./httpimport.py'); // dynamic http import hook impl
    //}).then(response => {
    //    return response.text();
    //}).then(source => {
        // pyodide.runPython(source); TODO temporarily disabled dynamic http import hook impl
        pyodide.runPython('import main');
    });
}